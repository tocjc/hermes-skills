---
name: cross-file-relationship-mining
description: "跨文件关联挖掘 — 当多个独立的 Excel 文件描述同一物理系统的不同视角（如设备级明细 + 站点级汇总 + 网络拓扑互联），需要通过 name fuzzy match、bridge table 发现和数据交叉验证来找出隐藏关系。**触发场景**：①用户给出 2+ 个文件，明确要求\"找出数据之间的联系\"；②多个文件看似独立但出自同一采集体系（相同日期/子网/地域）；③分析涉及\"设备级\"+\"站点级\"+\"拓扑级\"三层数据的关联；④用户要求\"深度挖掘\"数据间的关系，而不是对单个文件的统计分析。"
---

# Cross-File Relationship Mining

跨文件关联挖掘：当多份独立 Excel 文件描述同一物理系统的不同视角时，找出它们之间的隐藏联系。

## 适用场景

典型的**三视图分析模式**：

| 视角 | 数据特征 | 典型文件内容 |
|------|---------|------------|
| **设备级** | 大量行（千-万级），每个设备一条记录 | 设备温度、进口/出口温度、功耗 |
| **站点级** | 中等行（百级），每个站点一条汇总 | 站点通信状态、告警、汇总温度 |
| **拓扑级** | 行数可变，每条是一条连接关系 | 光路/链路互联、两端的设备/站点名 |

## Workflow

### Step 1 — 文件探查（轻量级）

先对每个文件做最小侵入的探查：Sheet 数、行数、列数。**不要一次性全部读取**。

```python
import openpyxl
for f in file_paths:
    wb = openpyxl.load_workbook(f, read_only=True, data_only=True)
    for name in wb.sheetnames:
        ws = wb[name]
        rc = sum(1 for _ in ws.iter_rows(min_row=1, values_only=True))
        print(f"{f.name}: Sheet [{name}]: {rc} rows")
    wb.close()
```

### Step 2 — 识别文件角色

从文件名和表头推断每个文件在系统中的角色：

- **设备级明细**: 行数较多（千+），有具体设备名/编号，数值字段多
- **站点级汇总**: 行数较少（百内），每个站点一行，有汇总指标和状态标记
- **拓扑级连接**: 包含两端端点信息（A端→B端），用于描述互联关系

### Step 3 — 提取关联键（Key Extraction）

每个文件的站点/设备命名规则不同，必须为每个文件写独立的 extractor 函数：

```python
import re

def extract_key_1660(name):
    """从 'TS_QianGangDianDiao_1660CSS16' 中提取 'qiangangdiandiao'"""
    s = str(name).replace('1660CSS16','').replace('CSS16','').replace('CSS-16','')
    m = re.search(r'TS_([A-Za-z0-9]+)', s)
    if m: return m.group(1).lower()
    return s.split('_')[0].lower() if '_' in s else s.lower()

def extract_key_1678(name):
    """从 'TS_FengRunXianJu_1678' 中提取 'fengrunxianju'"""
    s = str(name).replace('TS_','').replace('_1678','').replace('_1','').replace('_2','')
    return s.lower().strip()

def extract_endpoint_key(endpoint):
    """从光路端点 'FengNan_DaQi_1660CSS16/P8S4S1-1-11' 提取设备类型 + 站点key"""
    ep = str(endpoint)
    if '1660CSS' in ep or 'CSS16' in ep:
        dev_type = 'CSS16'
        m = re.search(r'([A-Za-z_]+?)(?:_1660CSS|CSS-16|1660)', ep)
        site = m.group(1).replace('TS_','').lower() if m else ep.lower()
    elif '1678' in ep:
        dev_type = '1678'
        m = re.search(r'TS_([A-Za-z_]+?)(?:_1678|/)', ep)
        site = m.group(1).lower() if m else ep.lower()
    else:
        dev_type = 'unknown'
        m = re.search(r'TS[_-]([A-Za-z]+)', ep)
        site = m.group(1).lower() if m else ep.lower()
    return dev_type, site
```

### Step 4 — 直接匹配 vs Bridge Table 发现

**直接匹配（direct match）**：如果在不同文件的站点键间有交集，说明它们描述同一组站点。

**Bridge Table 发现（关键模式）**：当直接匹配的交集为 0 时，用第三份拓扑文件作桥接：

```
文件A (设备级)  --[名称嵌入在拓扑文件端点中]--> 拓扑文件(光路表) <--[名称嵌入在拓扑文件端点中]-- 文件B (站点级)
```

这种方法可以发现两个数据集的**隐含互联关系**，即使它们没有直接共享相同的站点名称。

```python
# 从拓扑文件的两端提取所有站点key
sites_a = set(topology['A端key'].unique())
sites_b = set(topology['B端key'].unique())
all_sites = sites_a | sites_b

# 分别匹配到两个明细数据集
matches_A = key_fileA & all_sites  # 文件A在拓扑中的站点
matches_B = key_fileB & all_sites  # 文件B在拓扑中的站点

# 跨类型互联 = 拓扑行中A端是文件A的设备、B端是文件B的设备
cross = topology[topology['A端类型'] != topology['B端类型']]
```

### Step 5 — 数据交叉验证

对于桥接发现的关联，做数值交叉验证以确认关联成立：

```python
# 温度交叉: 文件A中的[站点, 温度] vs 文件B中同站点的温度
# 通信状态交叉: 文件B中通信异常的站点 → 拓扑中其关联光路的状态
# 性能交叉: 拓扑中带宽使用率高的光路 → 两端站点的温度/告警状态
```

### Step 6 — 综合判断

输出结论时按以下层级组织：

1. **文件间的关系定位** — 每个文件的角色和它们在系统中的位置
2. **直接发现的关联** — 跨文件的匹配站点和共享数据
3. **桥接发现的隐含关联** — 通过拓扑文件揭示的连接
4. **异常传播链** — 一个文件中的异常（如通信故障）可能影响另一个文件的哪些记录
5. **数值矛盾或数据缺口** — 哪些站点出现在一个文件中但不在另一个文件中

## Pitfalls

### ❌ 文件命名规则不统一
同一站点在不同文件中可能以完全不同格式出现（`TS_FengRunXianJu_1678` vs. `FengRunXianJu_1660CSS16` vs. `fengrunxianju_1678/S18P1`）。每个文件需要独立的 regex key extractor。

### ❌ 直接匹配失败不代表无关联
当文件A和文件B的站名标准化后交集为 0，不要停止。用第三份文件做 bridge table 发现隐含互联。

### ❌ 数值解析中的非数值标记
光路表中的收光功率、温度值常以 `--`、`-`、`空字符串` 表示缺省。解析时必须先过滤再转为 float：
```python
def parse_optical(val):
    if pd.isna(val) or str(val).strip() in ['--','']:
        return np.nan
    m = re.search(r'(-?\d+(?:\.\d+)?)', str(val))
    return float(m.group(1)) if m else np.nan
```

### ❌ 输出信息过载
跨文件关联挖掘的输出极易膨胀（1000+ 行）。必须对输出做三层控制：
- 汇总层：关键数字和结论
- 示例层：选取 Top-N 典型关联展示
- 详情层：使用 DataFrame 打印或写入文件，而非直接打印到终端

## References

- `references/three-view-analysis-pattern.md` — 三视图分析（设备级+站点级+拓扑级）的完整案例，含唐山 SDH 传输网三表关联的实战代码和模式提取