---
name: scipy-signal-processing
description: "Scientific signal processing with scipy.signal — peak detection, filtering, and spectral analysis for periodic/quasi-periodic data. Covers find_peaks tuning, amplitude/baseline compensation, and filter design."
version: 1.2.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [signal, scipy, find_peaks, peak-detection, filtering, dsp, data-science, engine]
    category: data-science
---

# scipy.signal Processing

Guides for working with periodic/quasi-periodic signals using `scipy.signal`.
Covers peak detection, filtering, and common failure-mode remediation.

## When to Load This Skill

- User asks about **peak detection** with `find_peaks` / `scipy.signal`
- User reports **inconsistent peak detection** (missed peaks, false peaks)
- Signal has **amplitude variation**, **baseline drift**, or **noise**
- User provides **frequency + sampling rate** and wants filtering or feature extraction
- Task involves **periodic waveform analysis** (vibration, audio, sensor data)
- **Engine/motor signal analysis** — especially when the user gives RPM, not Hz

## Core Parameters (Get These First)

Always ask or calculate before touching `find_peaks`:

| Parameter | How to get it |
|-----------|--------------|
| `fs` — sampling rate (Hz) | Usually known from acquisition hardware |
| `f_signal` — signal frequency (Hz) | From FFT, spec sheet, or `np.argmax(np.abs(np.fft.rfft(signal)))` |
| `period` — samples per cycle | `int(fs / f_signal)` |
| `min_distance` — min peak spacing | `int(period * 0.6)` — allows slight period variation |

## Peak Detection: The Main Workflow

### Step 1 — Baseline attempt

```python
from scipy.signal import find_peaks

period = int(fs / f_signal)
peaks, props = find_peaks(signal, distance=int(period * 0.6))
```

### Step 2 — FFT diagnostic (recommended before tuning)

Run FFT to check what frequencies are present. Competing frequencies (e.g. 65Hz mechanical vs 32.5Hz combustion) are the #1 reason find_peaks fails on engine signals. See `references/peak-detection-strategies.md` → FFT Diagnostic Workflow.

### Step 3 — Check for problems

Count peaks and compare with expected: `expected = int(duration * f_signal)`.

**Common failure modes:**

| Symptom | Likely cause |
|---------|-------------|
| Missing peaks in **late portion** of signal | **Amplitude decay** — fixed `height` / `prominence` too high for weak later peaks |
| Peaks shifted or inconsistent spacing | **Baseline drift** — slow DC offset confuses local maxima |
| Extra false peaks near true peaks | **Noise** — signal-to-noise ratio too low |
| Systematic miss of every Nth peak | **Picket-fence effect** — `distance` too restrictive or signal has harmonic content |
| Detected count is ~half of expected | You divided frequency by 2 by mistake (e.g. 3900Hz ↔ 3900RPM confusion) |

### Step 4 — Remediate

**For amplitude decay** → use adaptive height or envelope normalization
**For baseline drift** → detrend + high-pass filter
**For noise** → bandpass filter + increase prominence

**For competing mechanical frequencies** (e.g. 65Hz rotation vs 32.5Hz combustion on real data):
1. Run FFT diagnostic first to identify all strong frequencies
2. Even when the mechanical frequency amplitude EXCEEDS the target frequency, a correctly-tuned `distance` parameter alone can still work perfectly
3. Set `distance = int(period * 0.7)` — generous enough to allow slight period variation but tight enough to skip the mechanical sub-peaks between true combustion events

### Step 5 — Verify

Print the inter-peak intervals and their std — a good detection has low std
and mean close to `period`. Plot the first and last 10 detected peaks
on the signal to confirm visually.

## Plot Presentation (User Preference)

When generating matplotlib plots for this user, always enable Chinese font rendering:

```python
import matplotlib.pyplot as plt
plt.rcParams['font.sans-serif'] = ['WenQuanYi Zen Hei']  # Linux
plt.rcParams['axes.unicode_minus'] = False
```

This avoids "Glyph missing from font" warnings and renders titles/labels/legends correctly.

## Key References

- `references/peak-detection-strategies.md` — detailed strategies with full code for adaptive_h, envelope, detrend, combined, and cyclical approaches; FFT diagnostic workflow
- `references/parameter-cheatsheet.md` — find_peaks parameter reference and tuning guide
- `references/engine-combustion-peaks.md` — engine combustion signal peak detection (RPM→Hz conversion, cylinder math, adaptive tuning)
- `scripts/read_engine_bin.py` — read NI-DAQ dual-channel .bin files with diagnostic info
- `scripts/diagnose_engine_bin.py` — full diagnostic: FFT + top frequencies + peak detection + validation; run `python diagnose_engine_bin.py file.bin`
- `scripts/validate_peaks.py` — complete verification protocol: count vs expected, interval statistics, front/back balance, FFT cross-check, quality flags. Run standalone: `python validate_peaks.py signal.npy peaks.npy --fs 51200 --period 1575 --expected 104`. Can also be imported as `from validate_peaks import validate_peaks, pretty_print`.

## Pitfalls

- **Don't use fixed `height` when amplitude varies** — always adapt locally or via envelope normalization
- **Don't set `distance` larger than `period * 0.8`** — you'll miss peaks when frequency fluctuates slightly
- **Don't skip filtering when there's baseline drift** — `detrend(signal, type='linear')` is fast and almost always helpful before peak detection
- **Don't use `sosfilt` where you meant `filtfilt`** — SOS-form filters use `sosfilt` (one pass, causal) or `sosfiltfilt` (zero-phase). `filtfilt` takes `b, a`, not SOS.
- **Don't ignore edge effects** — filter transients at signal start/end can create false peaks. Pad or trim first ~100 samples from analysis.
- **Don't use `prominence=None` on noisy signals** — it defaults to 0, which will find every local fluctuation as a peak
- **Don't guess the signal frequency from a noisy FFT** — use `scipy.signal.find_peaks` on the spectrum itself, or `np.argmax` after smoothing the spectrum
- **Don't assume '3900' or similar number is in Hz** — when the user gives a frequency-like number for engine/motor/machinery signals, ALWAYS verify: is it Hz, RPM, or BPM? Ask. A 3900RPM engine produces a 65Hz fundamental (3900/60). A 4-cylinder 4-stroke at 3900RPM fires at 130Hz (3900/60*2). A single-cylinder 4-stroke at 3900RPM fires at 32.5Hz (3900/60/2). Getting this wrong changes the period by orders of magnitude and makes all peak detection fail.
- **Don't use `sosfilt` when you need zero-phase filtering** — `sosfilt` introduces a phase shift. Use `sosfiltfilt` for zero-phase (forward-backward) filtering. `filtfilt(b, a, x)` takes numerator/denominator coefficients, not SOS. For SOS-form: `sosfiltfilt(sos, x)`.
