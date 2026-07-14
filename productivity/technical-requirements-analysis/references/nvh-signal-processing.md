# NVH 信号处理算法速查

汽车 NVH (Noise, Vibration, Harshness) 分析涉及的核心算法实现参考。

## 格式支持

| 格式 | 解析方式 | 备注 |
|------|---------|------|
| ATFX | 正则块解析 (见 atfx-analyzer 技能) | ASAM ODS 标准 |
| WAV/FLAC | soundfile.read() | 标准音频格式 |
| CSV | numpy.loadtxt() / pandas.read_csv() | 文本数值数据 |
| MAT | scipy.io.loadmat() | MATLAB 格式 |
| UFF | pyuff 库 | 通用文件格式 |
| JSON | json.load() | 测试配置和标签 |

## 信号前处理

- **滤波器**: scipy.signal.butter() + filtfilt (零相位)
- **陷波**: scipy.signal.iirnotch(w0, Q)
- **重采样**: scipy.signal.resample() / librosa.resample()
- **A/C/Z 计权**: 按 IEC 61672 标准滤波器系数
- **去直流/归一化/异常脉冲剔除**: numpy/scipy 基础运算

## 频率分析

- **FFT/PSD**: np.fft.rfft() / scipy.signal.welch()
- **互功率谱**: scipy.signal.csd()
- **倍频程**: 按 ANSI S1.11 标准 (1/1, 1/3, 1/6, 1/12, 1/24)
- **包络谱**: Hilbert 变换 → abs → FFT
- **倒频谱**: irfft(log(abs(fft)))
- **峰值追踪**: scipy.signal.find_peaks() + 谐波匹配

## 阶次分析

转速信号插值 → 角域重采样 → FFT 获取阶次谱。核心工具:
- scipy.interpolate.interp1d (时域→角域插值)
- Vold-Kalman 阶次跟踪
- 瀑布图: 分段 FFT 堆叠为 [时间 × 频率 × 幅值] 矩阵

## 时频分析

- **STFT**: scipy.signal.stft()
- **CWT**: scipy.signal.cwt()
- **语谱图**: matplotlib.specgram() / librosa.display.specshow()

## 声品质 (Zwicker 模型)

| 指标 | 标准 | 开源实现 |
|------|------|---------|
| 响度 | ISO 532B | mosqito / pySDM |
| 尖锐度 | DIN 45692 | mosqito |
| 粗糙度/抖动度 | ECMA-74 | mosqito |

## dB 转换

- **振幅量**: 20 * log10(magnitude / ref)
- **功率量**: 10 * log10(power / ref)
- 参考值: 声压 2e-5 Pa, 加速度 1e-6 m/s²
- **安全地板值**: np.maximum(data, 1e-20) + np.isfinite 守卫

## 声音回放 ±2.0dB 平坦度

硬件: ASIO 专业声卡 (Focusrite/RME) + 参考级耳机 (Beyerdynamic/Sennheiser)
软件: FIR 频响补偿 + sounddevice/PyAudio 引擎

## 典型 NVH 故障特征

| 故障 | 频率特征 | 典型工况 |
|------|---------|---------|
| 稳态噪声 | 宽带平稳 | 恒定转速 |
| 瞬态异响 | 冲击、短时非平稳 | 加减速 |
| 阶次啸叫 | 与转速成比例窄带 | 特定转速区间 |
| 共振轰鸣 | 特定频率大幅值 | 特定挡位 |
| 敲击 | 周期性瞬态 | 怠速/低负荷