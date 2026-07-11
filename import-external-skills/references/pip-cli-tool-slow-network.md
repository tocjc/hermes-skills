# Python CLI 工具安装：国内服务器慢速网络工作流

当技能（如 `browser-act`）的 SKILL.md 中声明需要安装 Python CLI 工具时，标准命令（`uv tool install` 或 `pip install`）可能因网络限速而失败。以下工作流已验证可行。

## 诊断步骤

```bash
# 1. 检查 uv 是否可用
uv --version

# 2. 检查 Python 版本要求（browser-act-cli 要求 ==3.12.*）
uv python list | grep "3.12"
# 输出：cpython-3.12.13-linux-x86_64-gnu  <-- 已缓存，直接使用

# 3. 检查 wheel 兼容标签
source venv/bin/activate
python -c "import sysconfig; print(sysconfig.get_platform())"
# 验证 wheel 的 cp312-cp312-manylinux_2_17_x86_64 是否兼容
```

## 工作流

### 步骤 1：下载主 wheel（断点续传）

PyPI 包名可能与 CLI 命令名不同（如 `browser-act-cli` 的 pip 包是 `browser_act_cli`）。先用 PyPI 简单索引找到正确的 wheel URL：

```bash
# 找到正确的版本和 wheel URL
curl -sL "https://pypi.org/simple/browser-act-cli/" | grep -oP 'href="([^"]+)"' | grep manylinux_x86_64
```

使用 `wget -c` 断点续传（比 curl 更适合大文件）：

```bash
wget -c --timeout=120 \
  "https://files.pythonhosted.org/packages/.../browser_act_cli-0.1.6-cp312-cp312-manylinux_2_17_x86_64.whl" \
  -O /tmp/browser_act_cli-0.1.6-cp312-cp312-manylinux_2_17_x86_64.whl
```

验证完整性：

```bash
# 对比 SHA256（从 PyPI 页面获取）
echo "<expected_sha256>  /tmp/xxx.whl" | sha256sum -c -
# 验证 ZIP 结构
unzip -t /tmp/xxx.whl | grep "No errors"
```

### 步骤 2：创建 Python 3.12 虚拟环境

```bash
uv venv -p 3.12 /tmp/tool-venv
# 注意：此时 venv 中没有 pip，但 uv pip install 可以直接用
```

### 步骤 3：使用 uv pip install + 镜像下载依赖

依赖解析会需要下载大量包（browser-act-cli 依赖 100+ 个包，~100MB）。

**关关键步骤**：使用 `pypi.tuna.tsinghua.edu.cn` 镜像代替官方 PyPI：

```bash
uv pip install \
  /tmp/browser_act_cli-0.1.6-cp312-cp312-manylinux_2_17_x86_64.whl \
  -p /tmp/tool-venv \
  -i https://pypi.tuna.tsinghua.edu.cn/simple
```

注意：
- `-p /tmp/tool-venv` 指定 venv 路径
- `-i` 指定镜像源
- 依赖解析阶段可能需 2-3 分钟
- 下载阶段视网速而定（国内限速 ~100KB/s，~100MB 约 15-20 分钟）

如果解析超时，重试即可——清华镜像有缓存，第二次会快很多。

### 步骤 4：验证安装

```bash
source /tmp/tool-venv/bin/activate
# 在 PATH 中检查
which browser-act
browser-act --help | head -5
```

### 步骤 5：注册到 PATH（可选）

如需全局可用，将 venv 的 bin 目录加入 PATH，或创建 symlink：

```bash
ln -sf /tmp/tool-venv/bin/browser-act /usr/local/bin/browser-act
```

## 已知问题

### uv venv --seed 超时

`uv venv --seed` 会尝试下载 pip/setuptools，在慢速网络下也会超时。不需要——`uv pip install` 不依赖 pip。

### PEP 668（externally-managed-environment）

uv 管理的 Python 3.12 标记为外部管理环境，无法直接用 pip 修改。始终使用 `uv pip install -p <venv>` 或创建独立 venv。

### 清华镜像缺少特定包

清华镜像同步 PyPI 约滞后数小时，新发布的包可能暂不可用。此时回退到 PyPI 官方源：

```bash
# 先尝试镜像，失败则切换官方
pip install --default-timeout=300 \
  -i https://pypi.tuna.tsinghua.edu.cn/simple \
  package-name ||\
pip install --default-timeout=600 package-name
```

### 版本不匹配

`browser-act-cli` 要求 `==3.12.*`。如果系统只有 Python 3.11，uv 会自动下载 3.12——等下载完成即可。

### ⚠️ SKILL.md 版本号 ≠ CLI 包版本号

upstream 仓库的 SKILL.md 可能声明一个高版本号（如 `version: "2.0.2"`），但实际 PyPI 包版本很低（如 `0.1.6`）。**这是常见陷阱**：SKILL.md 是技能工作流文档，其 `version` 字段不代表 pip 包版本。

**应对**：安装后先 `browser-act --version` 确认实际版本，不要依赖 SKILL.md 的 frontmatter。

### ⚠️ 服务端强制最低版本

即使安装了旧版本 CLI，服务器可能拒绝服务并要求升级：

```
[Upgrade Required] Minimum required version: 0.1.18 (current: 0.1.6)
```

**应对**：安装后检查 `--help` 或运行一次测试命令，看是否有版本升级提示。若有，直接升级到最新版：

```bash
uv pip install --upgrade browser-act-cli==<latest> \
  -p /tmp/tool-venv \
  -i https://pypi.tuna.tsinghua.edu.cn/simple
```

找到最新版的方法：查询镜像索引的 JSON API：

```bash
curl -sL "https://pypi.tuna.tsinghua.edu.cn/simple/browser-act-cli/json" | \
  python3 -c "import sys,json;d=json.load(sys.stdin);print(max(d['releases'].keys()))"
```

### ⚠️ API Key 注册是独立于 pip install 的步骤

CLI 装完后**不能直接使用**——需先注册获取 API Key：

```bash
# 1. 尝试运行任意命令获取注册链接
browser-act browser list
# 输出：API key required. Register at https://www.browseract.com/quick-register?session=xxx

# 2. 在浏览器中打开注册链接，完成注册
# 3. 设置 API Key
browser-act auth set <API_KEY>
# 4. 验证
browser-act browser list
```

注册链接是 openapi 格式，需要在能访问外网的浏览器中打开。服务器自身可能无法访问该 URL。

### ⚠️ 大依赖包需要后台安装

像 `opencv-python` (69MB)、`av` (34MB) 这类大包会显著拖慢安装。升级版本时这些依赖可能变化（0.1.x 内的升级），需要用 `uv pip install --upgrade` 重新解析依赖。建议在后台运行，避免阻塞对话：

```bash
# 后台安装，完成后通知
terminal(command="uv pip install ...", background=True, notify_on_complete=True)
```