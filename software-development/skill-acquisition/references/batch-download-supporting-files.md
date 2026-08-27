# 批量下载外部技能的支持文件

## 问题
从 GitHub 仓库批量下载技能时，仅下载 SKILL.md 是不够的——很多技能附带 `agents/`、`references/`、`scripts/`、`templates/` 等支持文件。如果缺少这些文件，技能可能无法正常工作（如 `agents/openai.yaml` 缺失导致模型路由配置丢失）。

## 解决方案

### 方法一：遍历树并下载所有 blob（推荐）

```python
TREE_FILE = '/tmp/repo-tree.json'
BASE_URL = 'https://raw.githubusercontent.com/<user>/<repo>/main'
SKILLS_DIR = os.path.expanduser('~/.hermes/skills')

with open(TREE_FILE) as f:
    tree = json.load(f)['tree']

# 跳过已安装的技能
existing = {s for s in os.listdir(SKILLS_DIR) if os.path.isdir(os.path.join(SKILLS_DIR, s))}

for item in tree:
    if item['type'] != 'blob':
        continue
    p = item['path']  # e.g. skills/engineering/ask-matt/SKILL.md
    if not p.startswith('skills/'):
        continue
    
    parts = p.split('/')
    skill_name = parts[2]
    
    # 跳过已存在的技能
    if skill_name in existing and p.endswith('SKILL.md'):
        continue
    
    # 目标路径: ~/.hermes/skills/<skill_name>/<rest_of_path>
    rel = '/'.join(parts[2:])
    target = os.path.join(SKILLS_DIR, rel)
    os.makedirs(os.path.dirname(target), exist_ok=True)
    
    url = f'{BASE_URL}/{p}'
    subprocess.run(['curl', '-sL', '--max-time', '30', '-o', target, url])
```

### 方法二：分步下载（先 SKILL.md，再补充文件）
1. 先下载所有 SKILL.md
2. 再遍历同一技能目录下的所有其他文件（agents/、references/、scripts/ 等）
3. 对每个技能，下载其全部附属文件

### 注意事项
- **顺序下载慢**：50+ 文件时，curl 顺序下载可能需要 5-10 分钟。使用 `background=true` + `notify_on_complete=true` 启动，避免阻塞
- **遗漏检查**：下载完成后，对比树中 `SKILL.md` 数量与实际安装数量，确保无遗漏（如 `firecrawl-research-index` 可能被漏掉）
- **支持文件类型**：除了 SKILL.md，常见附属文件包括：
  - `agents/openai.yaml` — 模型路由配置
  - `references/*.md` — 参考文档
  - `scripts/*.sh` / `scripts/*.py` — 可执行脚本
  - `templates/*` — 模板文件
  - `*.cjs` / `*.config.js` — 配置文件（如 dependency-cruiser）
- **`execute_code` 的超时问题**：用 `execute_code` 批量下载大量文件时，5 分钟限制可能不够。改用 `terminal(background=true)` 运行 Python 脚本。 

## 验证示例
```bash
# 检查所有 SKILL.md 是否到齐
find ~/.hermes/skills -name "SKILL.md" | wc -l

# 检查特定技能的支持文件
ls ~/.hermes/skills/<skill-name>/
# 应包含：SKILL.md + 可能的 agents/ references/ scripts/ 等子目录
```