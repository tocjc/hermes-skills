---
name: "atfx-analyzer"
description: "Parses ASAM ODS ATFX files and associated BTF binary data, generates statistical tables and visualization charts. Invoke when user wants to analyze, visualize, or compare ATFX format files."
---

# ATFX Format File Analyzer

Analyzes ASAM ODS ATFX (ASAM Transport Format XML) files with associated BTF binary data files. Extracts measurement metadata, reads binary waveform data, computes statistics, and generates comprehensive HTML reports with charts.

## When to Invoke

- User provides `.atfx` files and wants analysis, visualization, or comparison
- User asks to read/parse/analyze ATFX format data
- User mentions ASAM ODS, NVH data, Simcenter Testlab exports
- User wants to compare multiple ATFX files (e.g., idle vs WOT, before/after)

## ATFX File Structure Background

ATFX is an ASAM ODS standard data exchange format:
- **ATFX file (XML)**: Contains metadata — application model, measurement definitions, channel info, unit/dimension definitions, and references to binary data
- **BTF file (Binary)**: Stores actual measurement data as raw binary (typically `float32`)
- The XML uses `ExternalComponent` elements to point into BTF files with `filename_url`, `start_offset`, `component_length`, and `value_type`

### Key XML Elements (namespace: `http://www.asam.net/ODS/5.3.1/Schema`)

| Element | Purpose |
|---------|---------|
| `Environment` | Test environment metadata |
| `Measurement` | Measurement group with timestamp, references Submatrices |
| `Submatrix` | Data block with `number_of_rows`, contains LocalColumns |
| `MeasurementQuantity` | Channel definition with name, data type, min/max, unit reference |
| `LocalColumn` | Column in submatrix: axis type, sequence representation |
| `ExternalComponent` | Binary data reference: BTF filename, byte offset, length, data type |
| `Dimension` / `Unit` | Physical dimension and unit definitions |

### Sequence Representations

- **`implicit_linear`**: Time axis — only `generation_parameters` (start, step) stored; values computed as `y = start + n * step`
- **`external_component`**: Actual data stored in BTF file, referenced by `ExternalComponentId`

## Workflow

### Step 1: Discover ATFX Files

Scan the user-specified directory for `*.atfx` files. For each ATFX file, check for associated BTF files (referenced in the XML or co-located with matching names).

### Step 2: Parse ATFX XML Metadata

Use Python `xml.etree.ElementTree` to parse. Extract:

```python
NS = {'a': 'http://www.asam.net/ODS/5.3.1/Schema'}

# 1. Measurement info
for meas in root.findall('.//a:Measurement', NS):
    name = meas.find('a:Name', NS).text
    begin = meas.find('a:MeasurementBegin', NS).text  # timestamp

# 2. Submatrix info (data blocks)
for sm in root.findall('.//a:Submatrix', NS):
    rows = int(sm.find('a:number_of_rows', NS).text)
    column_ids = sm.find('a:LocalColumnId', NS).text.split()  # channel IDs

# 3. MeasurementQuantity (channel metadata with min/max)
for mq in root.findall('.//a:MeasurementQuantity', NS):
    name = mq.find('a:Name', NS).text
    min_val = mq.find('a:Min', NS).text  # if exists
    max_val = mq.find('a:Max', NS).text  # if exists
    unit_id = mq.find('a:UnitId', NS).text

# 4. LocalColumn (column properties)
for lc in root.findall('.//a:LocalColumn', NS):
    seq_rep = lc.find('a:sequence_representation', NS).text
    gen_params = lc.find('a:generation_parameters', NS).text  # for implicit_linear
    ec_id = lc.find('a:ExternalComponentId', NS).text  # for external_component

# 5. ExternalComponent (binary data reference)
for ec in root.findall('.//a:ExternalComponent', NS):
    filename = ec.find('a:filename_url', NS).text
    start_offset = int(ec.find('a:start_offset', NS).text)
    component_length = int(ec.find('a:component_length', NS).text)
    value_type = ec.find('a:value_type', NS).text  # typically "ieeefloat4"
    block_size = int(ec.find('a:block_size', NS).text)

# 6. Unit definitions
for unit in root.findall('.//a:Unit', NS):
    name = unit.find('a:Name', NS).text  # e.g., "Pa", "Nm", "rpm", "km/h", "s"
```

### Step 3: Read BTF Binary Data

```python
import numpy as np

def read_btf_float32(btf_path, start_offset, num_values):
    """Read float32 data from BTF binary file."""
    with open(btf_path, 'rb') as f:
        f.seek(start_offset)
        data = f.read(num_values * 4)
    return np.frombuffer(data, dtype=np.float32)
```

**Important**: BTF file path is relative to the ATFX file's directory. Resolve with `os.path.join(atfx_dir, filename)`.

For `implicit_linear` time axes, generate values from `generation_parameters`:
```python
params = generation_parameters.split()  # "start step"
start, step = float(params[0]), float(params[1])
time_array = start + np.arange(num_rows) * step
```

### Step 4: Compute Statistics

For each data channel, compute:
- **Min, Max, Mean, Std, RMS** — use full data (before downsampling)
- **Peak-to-Peak** = |Max - Min|
- **Sampling rate** = 1 / step (from implicit_linear time axis)

### Step 5: Generate Visualizations

Use `matplotlib` with Agg backend. Required settings for Chinese text:
```python
matplotlib.use('Agg')
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'Noto Sans CJK SC']
plt.rcParams['axes.unicode_minus'] = False
```

**Standard chart set (adapt channel names dynamically from parsed data):**

1. **Time-domain waveform per file** — each submatrix's Y-axis channels plotted against time, with downsampling for high-frequency data (sample 2000 points via `np.linspace`)
2. **CAN signal time curves** — low-frequency channels (typically < 10000 samples) at full resolution
3. **Multi-file statistical comparison** — bar charts comparing Std/RMS/Peak-Peak across files (use log scale if ranges differ significantly)
4. **Probability density distribution** — histogram overlay comparing same channels across different files/conditions
5. **Combined multi-axis plot** — plot related CAN signals (speed, torque, vehicle speed) on shared time axis with twin Y-axes

Convert figures to base64 for embedding:
```python
import base64
from io import BytesIO

def fig_to_base64(fig, dpi=150):
    buf = BytesIO()
    fig.savefig(buf, format='png', dpi=dpi, bbox_inches='tight', facecolor='white')
    buf.seek(0)
    b64 = base64.b64encode(buf.read()).decode('utf-8')
    plt.close(fig)
    return f'data:image/png;base64,{b64}'
```

### Step 6: Generate HTML Report

Create a self-contained HTML file with:
- **Header** — file version, base model, application type, generation date
- **KPI cards** — file count, channel count, total sample count, condition labels
- **File overview table** — filename, condition, BTF file, sample counts, timestamps
- **Channel overview table** — channel name, type (vibration/CAN), physical quantity, unit, submatrix, sampling rate
- **Per-file statistics table** — min, max, mean, std, RMS for every channel
- **Cross-file comparison table** — std ratio, peak-peak values highlighting differences
- **Embedded charts** — all matplotlib figures as base64 `<img>` tags
- **Analysis insights** — text boxes summarizing key findings (use CSS `border-left` colored boxes)
- **ATFX structure explanation** — document the file hierarchy and data storage mechanism

**CSS styling**: Use a professional card-based layout with CSS variables, responsive design, table hover effects, colored badges for channel types.

## Handling Variations

### Different value_type in ExternalComponent
- `ieeefloat4` → `np.float32` (most common)
- `ieeefloat8` / `ieeefloat8` → `np.float64`
- `long` / `DT_LONG` → `np.int32`
- Adapt `block_size` (bytes per value) accordingly: float32=4, float64=8, int32=4

### Multiple Measurements per ATFX
Some ATFX files contain multiple `<Measurement>` elements. Iterate over all of them and analyze each independently.

### Missing BTF files
If the referenced BTF file doesn't exist at the expected path, report an error to the user and show only the metadata that can be extracted from the ATFX XML.

### Large files
For high-frequency data (>100k samples), always downsample for plotting (2000 points is sufficient for visual inspection). Compute statistics on FULL data.

## Output

- **Primary deliverable**: Self-contained HTML report saved to the user's workspace folder
- Use the `html-report` skill's styling patterns for professional appearance
- All text in the report must match the user's language
- Chart labels must use the actual channel names from the ATFX file (not hardcoded)
- Include the ATFX structure explanation section to educate the user about the format