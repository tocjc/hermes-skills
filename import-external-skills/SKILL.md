---
name: import-external-skills
description: "从 GitHub 等外部源批量导入已有技能包到 Hermes Agent 技能库。步骤：探索仓库结构→克隆→识别 SKILL.md→分类复制到 ~/.hermes/skills/→验证注册→git commit & push。不适用于新技能创作，那属于 skill-authoring 技能范围。"
---

# Import External Skills

从 GitHub 或其他外部源批量导入已有技能包到 Hermes Agent 技能库。

> **适用场景**：用户说"学习这个技能：https://github.com/xxx/yyy"、"导入 xxx 技能"、"把这个仓库搬过来"、"把 xxx 做成 Hermes 技能"

## 前置条件

- GitHub 仓库的 SKILL.md 已有合法 frontmatter（`name`、`description`）
- 可选：`~/.hermes/skills/` 是 git 仓库（推荐用于版本追踪，但非必需——核心导入流程完全独立于 git）

## 网络受限环境工作流

当 `git clone` 因代理/TLS/限速失败时（常见于国内服务器或受限网络环境），使用以下降级策略：

### 降级策略 A：GitHub API 树 + 批量下载（推荐）

对需要批量下载技能的场景，先用 GitHub API 获取完整仓库树（curl 直接访问 API 通常可行），再从 raw.githubusercontent.com 逐个下载：

```bash
# 1. 获取仓库完整文件树（不需要 clone）
curl -sL --max-time 60 \
  "https://api.github.com/repos/<org>/<repo>/git/trees/<branch>?recursive=1" \
  -o /tmp/repo-tree.json

# 2. 解析树结构，定位所有 SKILL.md（JSON 格式）
python3 -c "
import json
with open('/tmp/repo-tree.json') as f:
    tree = json.load(f)['tree']
for item in tree:
    if item['path'].endswith('SKILL.md') and item['type'] == 'blob':
        print(item['path'])
"
```

**已知可用的基础设施**：
- `raw.githubusercontent.com` — 通常直连可用（即使 git clone 失败），且 TLS 正常
- `api.github.com` — REST API 通常可用（注意速率限制 60 req/hr 未认证）
- `raw.githubusercontent.com` 返回原始文件内容，无需代理

### 降级策略 B：逐文件下载（适合少量技能或单个文件）

```bash
# 下载单个 SKILL.md
url="https://raw.githubusercontent.com/<org>/<repo>/main/<path>/SKILL.md"
curl -sL --max-time 30 -o ~/.hermes/skills/<skill-name>/SKILL.md "$url"

# 检查是否成功下载（小于 20 字节说明是 404 或失败）
size=$(stat -c%s ~/.hermes/skills/<skill-name>/SKILL.md)
if [ "$size" -ge 20 ]; then echo "OK"; else echo "FAILED"; fi
```

### 降级策略 C：批量下载整个技能包

对于技能数量多（20+）的情况，编写批量下载脚本：

```bash
BASE="https://raw.githubusercontent.com/<org>/<repo>/main"
SKILLS_DIR="$HOME/.hermes/skills"

for s in skill1 skill2 skill3; do
    mkdir -p "$SKILLS_DIR/$s"
    size=$(curl -sL --max-time 30 -o "$SKILLS_DIR/$s/SKILL.md" -w "%{size_download}" \
        "$BASE/sn-da-excel-workflow/capability/$cap/$s/SKILL.md")
    if [ "$size" -ge 20 ]; then
        echo "  ✅ $s ($size bytes)"
    else
        echo "  ❌ $s"
    fi
done
```

### 降级策略 D：稀疏 checkout（适合仓库结构简单、git clone 能连但速度慢）

```bash
git init /tmp/temp-skill-repo
cd /tmp/temp-skill-repo
git remote add origin https://github.com/<org>/<repo>.git
git config core.sparseCheckout true
echo "desired-path/*" >> .git/info/sparse-checkout
git pull --depth 1 origin main
```

### 已知陷阱：git 代理配置重定向

某些环境在 `.gitconfig` 中配置了镜像代理（如 `mirror.ghproxy.com`），导致 `git clone` 变慢或超时：

```bash
# 检查是否配置了代理
git config --global --list | grep -i proxy
cat ~/.gitconfig 2>/dev/null

# 临时禁用代理进行 clone（务必在完成后恢复）
git config --global --unset url."https://mirror.ghproxy.com/https://github.com".insteadOf
git clone --depth 1 https://github.com/<org>/<repo>.git /tmp/repo
# 恢复代理配置
git config --global url."https://mirror.ghproxy.com/https://github.com".insteadOf "https://github.com"
```

注意：即使禁用代理，`git clone` 仍可能因 TLS 问题失败（`GnuTLS recv error`）。此时必须回退到降级策略 A 或 B。

### 复杂目录结构处理

有些技能仓库有嵌套子目录（如 `sn-da-excel-workflow/capability/{category}/{skill_name}/SKILL.md`）。解析树结构时，注意深度嵌套路径：

```python
# 用 Python 从 repo-tree.json 中提取目标子技能
for item in tree:
    p = item["path"]
    if "parent-skill/capability" in p and p.endswith("SKILL.md"):
        parts = p.split("/")
        skill_name = parts[-2]  # 子技能名在倒数第二层
        # 构建 raw 下载 URL
        raw_url = f"https://raw.githubusercontent.com/<org>/<repo>/main/{p}"
```

### 支持文件下载的取舍

当批量安装大量技能（20+）时，权衡下载支持文件（references/templates/agents）的代价：

| 场景 | 策略 |
|------|------|
| 少量技能（<5） | 完整下载全部支持文件 |
| 中等数量（5-20） | 下载 SKILL.md + 核心 references/，跳过 assets/ 和大型二进制文件 |
| 大量技能（20+） | **仅下载 SKILL.md**，支持文件可后续按需补充 |

大量文件逐一下载会超时（>600s），应设置合理的超时和重试机制。

### 批量下载速率控制

批量下载 20+ 个技能时，注意 GitHub API 未认证速率限制（60 req/hr）和 raw.githubusercontent.com 的突发限制。在循环中加 `time.sleep(0.3~1)`：

```python
import time, urllib.request

for skill_name, repo_path in new_skills:
    url = f"https://raw.githubusercontent.com/{org}/{repo}/main/{repo_path}/SKILL.md"
    # download...
    time.sleep(0.5)  # 避免突发限流
```

如果 Python 脚本耗时较长，设置 `timeout=300`（5 分钟）防止中途中断。

## 工作流程

### 步骤 1：探索仓库结构

**两种方式任选其一：**

**方式 A — GitHub API（推荐，无需浏览器）：**
```bash
curl -sL --max-time 60 \
  "https://api.github.com/repos/<org>/<repo>/git/trees/<branch>?recursive=1" \
  -o /tmp/repo-tree.json
```
然后用 Python 解析 JSON 提取所有 SKILL.md 路径。这种方式对纯代码仓库（无动态渲染）更快、更稳定。

**方式 B — 浏览器：**
```markdown
browser_navigate("https://github.com/<org>/<repo>")
```

重点了解：
- **仓库结构**（几个技能包，尤其注意是否有配套/生态系统技能）
- **每个技能包的文件清单**（SKILL.md + 附属文件）
- **是否有共享层**（_shared / shared protocols）
- **仓库规模**（文件数、总大小）

**注意**：对于文件大小，在浏览器页面看 approximate，clone 后用 `du -sh` 精确。

### 步骤 1b：识别配套/生态系统技能

当用户说"学习这个技能：`github.com/org/repo/tree/main/a`"时，**不要只下载 a**。先通过递归树扫描整个 repo，识别与 a 配套的兄弟技能：

```python
# 常见配套模式：
#   core + forge           — browser-act + browser-act-skill-forge
#   entry + implement      — sn-ppt-entry + sn-ppt-creative
#   orchestrator + sub     — sn-da-excel-workflow + 44 capability skills
#   skill + shared         — academic-* + academic-shared
```

判断标准：
- **依赖链**：SKILL.md metadata 或内容明确引用另一个 skill → 必须一起装
- **配套工具**：同一 repo 的兄弟技能，命名相近（`browser-act` / `browser-act-skill-forge`），各自独立但互补 → 告知用户后一起装
- **解决方案生态**：repo 下有 `solutions/` 目录含大量预置脚本 → 告知用户存在，按需安装

执行后告知用户发现：`"这个仓库还有 N 个配套技能（forge, shared...），需要一起安装吗？"`

### 步骤 2：非侵入式评估（如果可以）

先在原地探索文件结构，确认 SKILL.md 的 frontmatter 是否合法：

```bash
# 用 git clone 到临时目录
cd /tmp
git clone --depth 1 https://github.com/<org>/<repo>.git <repo>

# 统计 SKILL.md 和总文件数
find <repo> -name "SKILL.md" | wc -l
find <repo> -type f | wc -l

# 总大小
du -sh <repo>/

# 检查 frontmatter 完整性
find <repo> -name "SKILL.md" -exec head -5 {} \;
```

### 步骤 3：确定分类组织方案

如果源仓库是多技能包结构（如 nature-skills 有 10 个技能），需要决定：

1. **Flat import**：直接复制完整目录树到 `~/.hermes/skills/<category>/〈技能名〉/`，保留所有附属文件
2. **Split import**：拆分为多个独立 Hermes 技能（适用于源仓库有多个独立 agent/team 的）
3. **Shared layer**：共享层（shared protocols/schemas/contracts）作为独立 skill，供其他技能引用

判断依据：
- 如果源仓库每个子目录是独立 agent/team → **Split**
- 如果源仓库所有文件耦合在一个 SKILL.md 下 → **Flat**
- 如果源仓库有独立的 shared/protocols 目录 → 单独一个 `*-shared` 技能

### 步骤 4：复制文件到技能库

```bash
# 创建目标分类目录
mkdir -p ~/.hermes/skills/<category>/

# 复制整个目录树
cp -a /tmp/<repo>/<skill-dir> ~/.hermes/skills/<category>/

# 如果是 flat 复制整个 repo
cp -a /tmp/<repo>/* ~/.hermes/skills/<category>/
```

### 步骤 5：验证 Hermes 注册

**方法 A** — 检查 skills_list 输出中是否出现了新技能名：

```markdown
skills_list()
```

**方法 B** — 确认 SKILL.md 前 3 行有合法 frontmatter：

```bash
for f in ~/.hermes/skills/imported-category/*/SKILL.md; do
  name=$(head -1 "$f" | grep -oP '(?<=name: ).*' 2>/dev/null || echo "❌ no name")
  desc=$(head -3 "$f" | grep -oP '(?<=description: ).*' 2>/dev/null || echo "❌ no desc")
  echo "$f: name=$name, desc=$desc"
done
```

如果某些子目录没有 SKILL.md（如 `image/` 子目录只有引用图片），**不要创建空的 SKILL.md**。Hermes 会自动忽略没有 SKILL.md 的目录，它们作为附属文件被父级 SKILL.md 引用即可。

### 步骤 6：Git 提交与推送（可选）

> ⚠️ 仅当 `~/.hermes/skills/` 是 git 仓库时才执行此步骤。如果不是，直接跳到「验证 Hermes 注册」步骤即可，导入已完成。

```bash
cd ~/.hermes/skills

git add -A
git status --short  # review before commit
git commit -m "feat: import <org>/<repo> as N skills (X files)"
git push
```

## 更新技能库

如果用户主动合并或删除技能，或者把旧的技能手工重命名/重组了，必须在 memory 中更新文件计数。git 仓库的追踪文件数也需要同步更新：

```bash
# 验证最新状态
cd ~/.hermes/skills
find . -name "SKILL.md" | wc -l
find . -type f | wc -l
du -sh .
git rev-parse --short HEAD
```

更新 memory 中的数字（文件计数、SKILL.md 计数、技能列表总数）。注意：`skills_list` 显示的是 Hermes 全局注册的技能总数，`find . -name 'SKILL.md' | wc -l` 显示的是本地文件数，两者可能不同（Hermes 内置技能不在 flat dir 中）。两个数字都记录。同时更新当前已导入技能的来源摘要（哪些仓库的批量、哪些来自单独下载）。

## 关键 Pitfalls

### ❌ 忽略技能配套/生态系统
当用户要求安装某个技能时（如 `browser-act`），同 repo 可能有配套技能（如 `browser-act-skill-forge`）。总是先通过递归树扫描全 repo，识别配套/兄弟技能并询问用户是否需要一起安装（见步骤 1b）。

### ❌ Python CLI 工具依赖安装失败
有些技能（如 browser-act）的 SKILL.md 要求安装 CLI 工具（`uv tool install browser-act-cli`），但依赖多达 100+ 个包，在慢速网络中会超时。参见 `references/pip-cli-tool-slow-network.md` 获取完整工作流（wget 断点续传 + 清华镜像 + uv pip install）。

### ❌ 不要创建空的 SKILL.md 来"占位"

如果子目录只有资源文件（图片、模板等）且被父级技能引用，不要自作主张写一个 SKILL.md。Hermes 会注册它并试图加载，但实际内容为空或指向不足，造成噪音。

### ❌ 不要相信浏览器页面显示的文件数

GitHub 网页显示的"X files"可能不准确。始终 clone 后用 `find` 和 `du` 精确统计。

### ❌ 不要在 SKILL.md frontmatter 中放置非法的 YAML

Hermes 使用标准的 SKILL.md frontmatter。如果源仓库的 frontmatter 使用了 Hermes 不认识的字段（如 `tags:`, `version:`, `maturity:`, `systems:`），它们会被静默忽略，不影响功能。但如果 frontmatter 格式错误（缩进问题、冒号后缺空格），Hermes 会拒绝加载该技能。

### ❌ 不要创建空目录

如果复制时源目录是空的（只有 `_assets/` 或 `_images/` 等空结构），直接用 `mkdir -p` 会导致技能列表中有空目录。检查后再创建或跳过。

### ❌ 技能名冲突：重名 ≠ 重复安装

下载前先用 `skills_list()` 检查目标技能名是否已被 Hermes 注册（可能来自其他源或不同路径的安装）。特别注意**命名不一致的重复**——仓库中的技能名可能与已有技能不同但功能重叠。常见模式：

- `audiocraft` ↔ `audiocraft-audio-generation`
- `vllm` ↔ `serving-llms-vllm`
- `lm-evaluation-harness` ↔ `evaluating-llms-harness`
- `segment-anything` ↔ `segment-anything-model`

**建议流程**：
1. 用 GitHub API 获取仓库的所有 SKILL.md 列表
2. 调 `skills_list()` 获取已注册的所有技能名
3. 对比差集确定真正新增的技能
4. 对重名（不同名但可能重叠）的技能，快速审视其 description 做最终判断：如果描述明显与已有技能重叠，跳过并注明

不要盲目下载所有 SKILL.md 文件——下载前先过滤可以避免磁盘垃圾和注册噪音。

### ❌ 不要假设技能库是 git 仓库

`~/.hermes/skills/` 可能不是 git 仓库（尤其是首次创建或从其他环境迁移时）。步骤 6（git 提交与推送）是可选优化，不是必须步骤。核心导入流程只依赖 `mkdir -p ~/.hermes/skills/<skill_name>/` → 写入 `SKILL.md` → `skills_list()` 验证三步。
