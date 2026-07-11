---
name: text-to-cad
description: Text-to-CAD skills library — generate parametric 3D CAD models from natural language using build123d Python. Create STEP/STL/3MF/GLB parts and assemblies, DXF 2D drawings, URDF/SRDF/SDF robot descriptions, G-code slicing, and 3D printer workflows. Also includes CAD Viewer for browser preview, step.parts catalog lookup, SendCutSend preflight, and Bambu Lab print handoff.
---

# Text-to-CAD 技能库

Provenance: [earthtojake/text-to-cad](https://github.com/earthtojake/text-to-cad) — 一个 CAD、机器人和硬件设计的代理技能库。

## 用途

从自然语言描述生成参数化 3D CAD 模型，输出为 **STEP**（主格式）、STL、3MF、GLB。核心工具链：

- **build123d** — Python 参数化 CAD 库（类似 cadquery，但更灵活）
- **cadpy** — 共享 STEP/GLB 几何生成运行时
- **CAD Viewer** — 浏览器端 3D 预览（Three.js 渲染）
- **step.parts API** — 标准件 STEP 文件目录搜索/下载

## 安装

```bash
# 克隆仓库
git clone https://github.com/earthtojake/text-to-cad.git
cd text-to-cad

# 安装 Python 依赖（核心 CAD 技能）
pip install -e ./skills/cad/scripts/packages/cadpy
pip install build123d cadquery-ocp playwright

# 或通过 Skills CLI 安装（官方路径）
npx skills install earthtojake/text-to-cad
```

## 技能总览（11 个）

| 技能 | 说明 |
|------|------|
| **cad** | 核心：从文字/图片生成参数化 STEP 模型，含 inspection/snapshot 验证 |
| **cad-viewer** | 浏览器 3D 预览 STEP/STL/GLB/G-code/URDF/SRDF/SDF/DXF |
| **step-parts** | 搜索/下载 off-the-shelf 标准件 STEP（螺丝、轴承、电机等） |
| **dxf** | 生成 2D DXF 图纸（轮廓、模板、垫片、激光/水切排版） |
| **urdf** | 生成机器人 URDF 描述文件（link/joint/limit/inertial） |
| **srdf** | MoveIt 语义 SRDF（planning group/end effector/collision） |
| **sdf** | SDFormat 仿真模型和世界描述（sensor/light/plugin） |
| **gcode** | 调用 OrcaSlicer/PrusaSlicer/CuraEngine 生成 FDM G-code |
| **sendcutsend** | 上传前检查 DXF/STEP 是否符合 SendCutSend.com 下单要求 |
| **bambu-labs** | LAN FTPS/MQTT 上传和启动 Bambu Lab 打印机打印 |
| **implicit-cad** | 实验性 GLSL 隐式 SDF 建模（浏览器内 raymarch 渲染） |

## 核心 CAD 工作流

### 1. 写 CAD Brief

将用户需求转换为建模笔记：尺寸、单位、坐标系、特征、输出路径、验证目标。

```text
CAD brief:
- Model: mounting_plate, single STEP part.
- Units: millimeters.
- Origin: center of plate; base plane XY; +Z is thickness direction.
- Body: rounded rectangular plate, 100 × 60 × 6 mm.
- Holes: four 4.5 mm M4 clearance through-holes, 10 mm from each corner.
- Validation: bbox 100 × 60 × 6 mm, four holes, label.
```

### 2. 编写 build123d Python 源文件

```python
from build123d import *
from cadpy.assembly import AssemblyHelper, label_shape

# Parameters
width = 100.0
depth = 60.0
thickness = 6.0
hole_dia = 4.5
hole_offset = 10.0
corner_radius = 3.0

def gen_step():
    with BuildPart() as part:
        # Base plate
        Box(width, depth, thickness)

        # Fillet BEFORE holes — hole edges are short, fillet fails on them
        top_edges = part.edges().group_by(Axis.Z)[0]
        bottom_edges = part.edges().group_by(Axis.Z)[-1]
        fillet(top_edges + bottom_edges, radius=corner_radius)

        # Four M4 clearance holes
        with Locations(
            (hole_offset, hole_offset, 0),
            (width - hole_offset, hole_offset, 0),
            (hole_offset, depth - hole_offset, 0),
            (width - hole_offset, depth - hole_offset, 0),
        ):
            CounterSinkHole(hole_dia, hole_dia * 0.5)

        label_shape(part.part, "mounting_plate")
    return part.part
```

### 3. 生成 STEP 文件

```bash
# 从 CAD 技能目录运行
python skills/cad/scripts/step path/to/part.py
# 或自定义输出路径
python skills/cad/scripts/step path/to/part.py -o output/part.step
# 多文件
python skills/cad/scripts/step a.py=out/a.step b.py=out/b.step
```

**注意**：命令从当前工作目录解析路径。keep STEP 输出和 .py 源文件在同目录、同 basename。

### 4. 几何验证

```bash
# 基准检查：facts + planes + positioning
python skills/cad/scripts/inspect refs path/to/model.step --facts --planes --positioning

# 尺寸测量
python skills/cad/scripts/inspect measure path/to/model.step \
  --from '#o1.f1' --to '#o1.f2' --axis z

# 对齐检查（装配体）
python skills/cad/scripts/inspect align path/to/assembly.step \
  --moving '#child_face' --target '#parent_face' --mode flush --axis z
```

# 快照审查（强制） — 使用 --input 和 --output 标志

```bash
# 单张快照
python skills/cad/scripts/snapshot --input path/to/model.step --output /tmp/review.png

# 多视角包（JSON job 格式）
python skills/cad/scripts/snapshot --job - <<'JSON'
{
  "input": "path/to/model.step",
  "appearance": "workbench",
  "sizeProfile": "assembly",
  "outputs": [
    { "path": "/tmp/review_iso.png", "camera": "iso" },
    { "path": "/tmp/review_front.png", "camera": "front" },
    { "path": "/tmp/review_top.png", "camera": "top" },
    { "path": "/tmp/review_right.png", "camera": "right" }
  ]
}
JSON
```

每个生成的 STEP 都必须做视觉快照审查。JSON job 支持 `input`, `outputs[]`, `appearance` (workbench), `camera` (iso/front/top/right), `sizeProfile` (simple/diagnostic/assembly/orbit)。

### 6. CAD Viewer 交接

```bash
# 启动 CAD Viewer
npm --prefix skills/cad-viewer/scripts/viewer run agent:start \
  -- --host 127.0.0.1 --dir $(pwd)/models

# 生成预览链接
# http://127.0.0.1:<port>/?dir=/path/to/models&file=model.step
```

### 7. 导出其他格式

```bash
# STL（必须指定输出路径）
python skills/cad/scripts/step path/to/part.py --stl model.stl
# 3MF
python skills/cad/scripts/step path/to/part.py --3mf model.3mf
# GLB
python skills/cad/scripts/step path/to/part.py --glb model.glb
```

## build123d 常见陷阱

**从本次实战中总结的 6 个必知陷阱：**

### 1. Fillet 必须在打孔之前

```python
# ❌ 失败：打孔后再 fillet，孔边缘的短边会导致 BRep_API: command not done
with BuildPart() as p:
    Box(100, 60, 10)
    with Locations(...): CounterSinkHole(6.5, 2)
    fillet(p.edges().group_by(Axis.Z)[0], radius=4)  # 失败！

# ✅ 正确：先 fillet 再打孔
with BuildPart() as p:
    Box(100, 60, 10)
    fillet(p.edges().group_by(Axis.Z)[0], radius=4)  # 先倒角
    with Locations(...): CounterSinkHole(6.5, 2)      # 后打孔
```

### 2. 装配体必须用 .moved() 实际移动几何

`cadpy.assembly.AssemblyHelper.add(shape, name)` 不参数 location 参数
或 `asm.add(shape, name, location)` 只存 label 字符串不移动几何。

```python
# ✅ 正确：用 .moved(location) 实际变换形状
left_bracket = make_motor_bracket().moved(
    Location((0, -18, 35)))
asm.add(left_bracket, "motor_bracket_left")
```

### 3. assembly.compound 是方法不是属性

```python
# ❌ asm.compound → <class 'method'>
# ✅ 正确
return asm.compound()   # → <class 'Compound'>
```

### 4. label 要用 label_shape()

```python
from cadpy.assembly import label_shape
label_shape(part.part, "my_part")   # ✅
# part.part.label = "my_part"       # 也可以
```

### 5. Bore() 不存在 — 用 Cylinder + SUBTRACT

```python
# ❌ Bore(14, 10) 不是一个 build123d API
# ✅ 正确
bore_hole = Cylinder(radius=7, height=12)
with Locations((0, 0, 30)):
    add(bore_hole, mode=Mode.SUBTRACT)
```

### 6. CounterBoreHole 的参数顺序

```python
CounterBoreHole(hole_dia, cbore_dia, cbore_depth)
# 不是 (hole_dia, cbore_dia, total_depth)
```

## 装配体模式

使用 `cadpy.assembly.AssemblyHelper` + `.moved()` 定位：

```python
from cadpy.assembly import AssemblyHelper

def make_base():
    with BuildPart() as p:
        Box(120, 80, 20)
    return p.part

def make_lid():
    with BuildPart() as p:
        Box(120, 80, 3)
    return p.part

def gen_step():
    asm = AssemblyHelper("enclosure")
    base = asm.add(make_base(), "base")
    # .moved() 是必须的 — AssemblyHelper 不自动应用位置
    lid = make_lid().moved(Location((0, 0, 20)))
    asm.add(lid, "lid")
    return asm.compound()
```

## 调试流程

1. 先单独测试 `gen_step()` 返回值类型：
   ```bash
   python -c "exec(open('part.py').read()); r=gen_step(); print(type(r))"
   ```
   应为 `build123d.topology.composite.Compound` 或 `Solid` 或 `Part`。

2. 再生成 STEP：`python scripts/step part.py`

3. 验证：`python scripts/inspect refs part.step --facts --planes --positioning`

4. 量化测量：`python scripts/inspect measure part.step --from '#o1.f1' --to '#o1.f2' --axis x`

## 参考文档（渐进加载）

仅当对应场景触发时加载：

- `references/cad-brief.md` — 将文字/图片/工程图转为建模需求
- `references/build123d-modeling.md` — build123d 建模模式、拓扑、选择器
- `references/step-generation.md` — STEP 生成 CLI 细节
- `references/inspection-and-validation.md` — 验证流程、measure/align/diff/frame
- `references/snapshot-review.md` — 快照策略和审查规则
- `references/positioning.md` — 装配定位、datums、joints
- `references/supported-exports.md` — STL/3MF/GLB 侧边输出
- `references/session-recipe-motor-base.md` — 已验证的实战配方（电机底座，含完整避坑代码）

## 关于毅力号探测车的参考资料

| 维度 | 值 |
|------|-----|
| 车体尺寸 | 约 2.9m × 2.7m × 2.2m |
| 轮距 | 约 2.0m |
| 轮径 | 约 52.5cm |
| 悬架 | 摇臂转向架式（rocker-bogie） |
| 车重 | 约 1025kg |
| 最高速度 | 约 0.14km/h（实际 0.01-0.04km/h） |
| 机械臂自由度 | 5 |
| 有效载荷 | 约 7 个科学仪器 |

## 关于 Iris 月球车的关键参数

| 维度 | 值 |
|------|-----|
| 尺寸（车身） | 约 1.3m × 1.25m × 0.8m |
| 轴距 | 约 1.0m |
| 轮间距 | 约 0.8m |
| 离地间隙 | 约 0.3m |
| 质量 | 约 410kg |
| 最高速度 | 约 0.4m/s（约 1.44km/h） |
| 悬架 | 摇臂转向架式（rocker-bogie） |
| 驱动方式 | 6×6 全轮驱动，4 轮转向 |
| 转向方式 | 阿克曼转向（Ackermann steering），前后轮转向 |
| 通信模式 | UHF 频段与地面站通信，S 频段传输图像 |
| 视觉系统 | 导航相机（NavCam）+ 避障相机（HazCam），立体视觉 |

## 关键约定

- **默认单位**：毫米
- **基准平面**：XY
- **拉伸方向**：+Z
- **原点**：零件中心或匹配基准
- **STEP 结构**：单个闭合实体 / 实体 Compound / 标记装配体
- **默认壁厚**：2.0-3.0 mm（未指定时）
- **默认圆角**：1.0-3.0 mm
- **M3/M4/M5 通孔**：3.4/4.5/5.5 mm

## 注意事项

1. **不要直接编辑生成的 STEP** — 总是编辑生成器 `.py` 源文件，重新生成
2. **文件操作最后** — 圆角和倒角最容易失败，排在最后
3. **布尔工具要过量** — 切割工具要比被切面长 ~1mm，共面/共线是经典内核失败
4. **Snapshots 是强制的** — 确定性检查通过不代表视觉上正确
5. **所有生成物都要交接给 CAD Viewer** — 生成后必须提供预览链接
6. **装配体始终用 AssemblyHelper** — 不要丢失 occurrence labels
7. 不要在一个技能中引用其他技能的源文件 — 各技能独立运行