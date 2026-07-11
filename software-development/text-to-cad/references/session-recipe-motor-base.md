# 实战配方：电机安装底座

本文件记录了一次完整的 text-to-cad 实战经验，包含经过验证的可工作代码和 CLI 使用模式。

## 需求

矩形底座，四个安装孔，两个电机支架。

## CAD Brief

```
Model: motor_mount_assembly (assembly)
Units: millimeters
Origin: base plate center, XY base plane, +Z up
Base plate: 150 × 100 × 10 mm, R4 corner fillet
Mounting holes: 4× M6 (6.5mm) countersunk through-holes, 12mm from edges
Brackets: 2× vertical, 40 × 8 × 60 mm each, on ±Y side of base
Motor bore: Ø14 mm shaft clearance at bracket center
Motor bolts: 4× M4 (4.5mm) counterbored, Ø24 BCD bolt circle per bracket
Bracket Z: bracket bottom flush with base top face (Z=+5)
```

## 已验证的工作代码

关键知识点（全部在实战中踩过坑）：

### 生成器结构

```python
from build123d import *
from cadpy.assembly import AssemblyHelper, label_shape
import math

def gen_step():
    asm = AssemblyHelper("motor_mount_assembly")
    base = asm.add(make_base_plate(), "base_plate")

    bracket_z = PLATE_THICKNESS / 2 + MOUNT_HEIGHT / 2  # bracket bottom on base top
    left_bracket = make_motor_bracket().moved(
        Location((0, -PLATE_DEPTH / 2 + MOUNT_Y_OFFSET, bracket_z)))
    asm.add(left_bracket, "motor_bracket_left")

    right_bracket = make_motor_bracket().moved(
        Location((0, PLATE_DEPTH / 2 - MOUNT_Y_OFFSET, bracket_z)))
    asm.add(right_bracket, "motor_bracket_right")

    return asm.compound()
```

### 底座函数（fillet 先于 holes）

```python
def make_base_plate():
    with BuildPart() as base:
        Box(PLATE_WIDTH, PLATE_DEPTH, PLATE_THICKNESS)
        # fillet BEFORE holes！
        top_edges = base.edges().group_by(Axis.Z)[0]
        bottom_edges = base.edges().group_by(Axis.Z)[-1]
        fillet(top_edges + bottom_edges, radius=CORNER_RADIUS)

        x_off = PLATE_WIDTH / 2 - MOUNT_HOLE_INSET
        y_off = PLATE_DEPTH / 2 - MOUNT_HOLE_INSET
        with Locations((-x_off, -y_off), (x_off, -y_off),
                       (-x_off, y_off), (x_off, y_off)):
            CounterSinkHole(MOUNT_HOLE_DIA, MOUNT_HOLE_DIA * 0.3)

        label_shape(base.part, "motor_base_plate")
    return base.part
```

### 支架函数（Bore 不存在）

```python
def make_motor_bracket():
    with BuildPart() as bracket:
        Box(MOUNT_WIDTH, MOUNT_THICKNESS, MOUNT_HEIGHT)

        # fillet BEFORE holes
        top_edges = bracket.edges().group_by(Axis.Z)[-1]
        fillet(top_edges, radius=1.5)

        # Bore() 不存在 → 用 Cylinder + SUBTRACT
        bore_hole = Cylinder(radius=MOTOR_BORE_DIA / 2, height=MOUNT_THICKNESS + 2)
        with Locations((0, 0, MOUNT_HEIGHT / 2)):
            add(bore_hole, mode=Mode.SUBTRACT)

        # 螺栓孔
        bcd_r = MOTOR_BCD / 2
        for i in range(4):
            angle = 45 + i * 90
            bx = bcd_r * math.cos(math.radians(angle))
            bz = MOUNT_HEIGHT / 2 + bcd_r * math.sin(math.radians(angle))
            with Locations((bx, 0, bz)):
                CounterBoreHole(MOTOR_BOLT_DIA, MOTOR_BOLT_DIA, MOUNT_THICKNESS - 2)

        label_shape(bracket.part, "motor_bracket")
    return bracket.part
```

## CLI 工作流

```bash
# 1. 快速测试 Python 源
python -c "exec(open('motor_base.py').read()); r=gen_step(); print(type(r).__name__)"

# 2. 生成 STEP
python /path/to/text-to-cad/skills/cad/scripts/step motor_base.py

# 3. 几何验证
python /path/to/text-to-cad/skills/cad/scripts/inspect refs motor_base.step --facts --planes --positioning

# 4. 视觉快照（多视角 JSON job）
python /path/to/text-to-cad/skills/cad/scripts/snapshot --job - <<'JSON'
{
  "input": "motor_base.step",
  "appearance": "workbench",
  "sizeProfile": "assembly",
  "outputs": [
    { "path": "/tmp/iso.png", "camera": "iso" },
    { "path": "/tmp/front.png", "camera": "front" },
    { "path": "/tmp/top.png", "camera": "top" },
    { "path": "/tmp/right.png", "camera": "right" }
  ]
}
JSON

# 5. 导出 STL
python /path/to/text-to-cad/skills/cad/scripts/step motor_base.py --stl motor_base.stl
```

## 验证结果

```
装配体: motor_mount_assembly
BBox: (-75, -50, -5) ~ (75, 50, 65)
尺寸: 150 × 100 × 70 mm
Occurrences: 4 (3 leaf)
Faces: 102, Edges: 224
Base plate: Z=-5 to +5 (10mm thick)
Brackets: Z=+5 to +65 (60mm tall), centered on base
```