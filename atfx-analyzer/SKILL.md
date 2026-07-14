---
name: "atfx-analyzer"
description: "Parses ASAM ODS ATFX files and associated BTF binary data, generates statistical tables and visualization charts. Invoke when user wants to analyze, visualize, or compare ATFX format files."
version: 1.4.0
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

### Flat ID Cross-Reference Structure

**IMPORTANT**: ATFX instance data (exported by Simcenter TestLab) uses a **flat structure** — all elements are top-level siblings, NOT nested. Elements reference each other via `<Id>` fields. Do NOT use `xml.etree.ElementTree` XPath queries — use regex-based block parsing instead.

### Key XML Elements

| Element | Purpose |
|---------|---------|
| `Measurement` | Measurement group with timestamp, references Submatrices |
| `Submatrix` | Data block with `number_of_rows`, contains LocalColumns |
| `MeasurementQuantity` | Channel definition with name, data type, min/max, unit reference |
| `LocalColumn` | Column in submatrix: axis type, sequence representation |
| `ExternalComponent` | Binary data reference: BTF filename, byte offset, length, data type |
| `Dimension` / `Unit` | Physical dimension and unit definitions |

## Workflow

### Step 1: Discover ATFX Files

Scan the user-specified directory for `*.atfx` files. Check for associated BTF files (referenced in the XML or co-located).

### Step 2: Parse ATFX XML Metadata

**Use regex-based block parsing** — NOT ElementTree XPath. Strip namespaces first, then parse each entity type independently with `re.finditer(r'<Tag>(.*?)</Tag>', content, re.DOTALL)`. Build lookup dicts by `<Id>` to resolve cross-references.

### Step 3: Read BTF Binary Data

Use `numpy.frombuffer` for float32 data. For `implicit_linear` time axes, generate from `generation_parameters` (start + step).

### Handling Complex Spectrum Data

When `value_type = 'DT_COMPLEX'` or (`value_type = 'ieeefloat4'` AND `component_length = 2 × number_of_rows`): data is interleaved real/imag float32 pairs. De-interleave and compute `np.abs()` for magnitude.

### Handling AutoPower Spectrum Data

When `value_type = 'ieeefloat4'` AND `component_length == number_of_rows`: real-valued spectral power. Reshape as `[n_rpm × n_freq]`. Convert to dB using `10*log10` with `1e-20` floor (not `1e-300` — float32 underflow).

### Step 4: Compute Statistics

Min, Max, Mean, Std, RMS, Peak-to-Peak, sampling rate. dB conversion: `20*log10` for amplitude, `10*log10` for power. Always use `1e-20` floor, guard with `np.isfinite()`.

### Step 5: Generate Visualizations

Matplotlib Agg backend. Charts: time-domain waveforms, CAN signals, multi-file comparison, probability density, multi-axis plots, 1/1 octave band analysis, PSD density.

### Step 6: Generate HTML Report

Self-contained HTML: KPI cards, file/channel overview tables, statistics tables, embedded base64 chart images, analysis insights, ATFX structure explanation.

## Pitfalls

### ❌ ATFX Flat Structure
ElementTree XPath fails on flat-exported ATFX. Use regex block matching: `re.finditer(r'<Tag>(.*?)</Tag>', content, re.DOTALL)`.

### ❌ Windows GBK Encoding
Unicode superscripts (`g²/Hz`) crash on GBK console. Set `PYTHONIOENCODING=utf-8` or use ASCII replacements.

### ❌ dB Floor Value
Float32 cannot represent `1e-300` (underflows to 0). Always use `1e-20` as floor for dB conversion.

## Output

- Self-contained HTML report in user's workspace
- All text matches user's language
- Chart labels use actual ATFX channel names
- Includes ATFX structure explanation section