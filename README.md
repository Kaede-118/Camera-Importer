# Camera Importer

一个用于安全转存相机视频的 Python 工具。

最初为 DJI Action 4 手元视频工作流编写，但同样适用于其他相机或存储设备的视频转存场景。

---

## 功能

* 单实例运行锁（残留锁支持强制接管）
* 自动删除 DJI `.LRF` 低清代理文件
* BLAKE3 哈希校验（复制时边写边算源文件哈希，复制后独立重读目标文件校验）
* `.tmp` 临时标记保护，校验成功后才删除源文件
* 启动时自动清理上次异常残留的 `.tmp` 与未完成文件
* 自动处理重名文件（追加 ` (2)`、` (3)` …）
* 双进度条：单文件复制进度 + 总进度（按块实时刷新）
* 动态 ETA 预估（EMA 平滑速度，显示预计剩余时间与实时速度）
* 完成/失败时弹出 Windows 桌面通知（winotify）并播放系统提示音
* 日志带时间戳，全程可追溯

---

## 工作流程

```text
相机存储卡
    ↓
复制文件（边复制边计算 BLAKE3）
    ↓
独立重读目标文件计算 BLAKE3
    ↓
校验成功？
    ├─ 是 → 先删 .tmp 标记，再删源文件
    └─ 否 → 保留源文件 + .tmp 标记，记录失败
```

失败的文件不会中断整体流程，全部处理完后统一报告。

---

## 为什么要写这个？

一次视频转存过程中，由于脚本设计问题导致源文件被提前删除，最终丢失了一份手元录像。

在那之后，重写了整个转存流程，并加入了：

* 哈希校验
* 临时文件标记
* 自动恢复机制
* 单实例保护

这个工具的核心原则非常简单：

> 永远不要在确认复制成功之前删除原文件。

---

## 配置

脚本从同目录的 `config.txt` 读取配置（`KEY=VALUE` 格式，`#` 开头为注释）。
首次运行时若不存在 `config.txt`，会自动生成模板并退出，填写后重新运行即可。

```text
# 相机源目录
SRC=E:\DCIM\DJI_001

# 转存目标目录
DST=D:\camera output\unprocessed
```

PyInstaller 打包的 exe 同样从 exe 所在目录读取 `config.txt`。

---

## 依赖

```bash
pip install tqdm blake3 winotify
```

---

## 使用方法

```bash
python Camera-Importer.py
```

或者双击 `run_Camera-Importer.bat` 启动。

处理完成后按回车退出；被批处理管道调用（stdin 不可交互）时自动跳过，不打断链式流程。

---

## 安全机制

### 运行锁

`DST/running.lock` 防止多个实例同时写入。

检测到锁文件时（另一实例运行中，或上次异常残留），输入 `1` 确认强制接管，其他输入则退出。

### 临时文件标记

复制开始时创建：

```text
DJI_0001.MP4.tmp
```

程序异常退出时，下一次启动会自动检测并清理未完成文件（先删 `.tmp` 和未完成的目标文件）。

### 哈希校验

源文件与目标文件分别计算 BLAKE3 哈希。

只有完全一致时才会删除源文件；校验失败时源文件与 `.tmp` 标记都会保留，方便下次重试。

---

## License

MIT License

---

# Camera Importer

A Python tool for safely importing camera footage.

Originally created for a DJI Action 4 POV workflow, but it can be used with any camera or storage device.

---

## Features

* Single-instance lock protection (with forced takeover for stale locks)
* Automatic removal of DJI `.LRF` proxy files
* BLAKE3 hash verification (source hash computed while copying, destination verified by re-reading)
* `.tmp` marker protection — source file is deleted only after successful verification
* Startup cleanup of leftover `.tmp` markers and incomplete files from a crashed run
* Automatic duplicate filename handling (` (2)`, ` (3)` …)
* Dual progress bars: per-file copy progress + overall progress (updated in real time)
* Dynamic ETA with EMA-smoothed speed estimate
* Windows desktop notification (winotify) and system beep on completion/failure
* Timestamped logs for full traceability

---

## Workflow

```text
Camera Storage
      ↓
Copy File (computing BLAKE3 on the fly)
      ↓
Re-read destination file and compute BLAKE3
      ↓
Hashes match?
      ├─ yes → delete `.tmp` marker first, then delete source
      └─ no  → keep source + `.tmp` marker, record the failure
```

Failed files do not abort the run — all remaining files are processed and failures are reported in a summary at the end.

---

## Why?

After losing a POV recording due to a script bug that deleted the source file too early, I redesigned the whole transfer flow with verification and recovery mechanisms.

The design goal is simple:

> Never delete the original file unless the copied file has been verified.

---

## Configuration

Config is read from `config.txt` next to the script (`KEY=VALUE` lines, `#` for comments).
On first run the script writes a template and exits; fill it in and run again.

```text
# Source directory
SRC=E:\DCIM\DJI_001

# Destination directory
DST=D:\camera output\unprocessed
```

The PyInstaller exe reads `config.txt` from its own directory.

---

## Requirements

```bash
pip install tqdm blake3 winotify
```

---

## Usage

```bash
python Camera-Importer.py
```

Or double-click `run_Camera-Importer.bat`.

Press Enter to exit when done; when stdin is not interactive (e.g. chained from a batch script) it exits automatically.

---

## Safety Features

### Lock File

`DST/running.lock` prevents multiple instances from running simultaneously.

When a lock file is detected (another instance or a stale lock), type `1` to force takeover, or any other key to exit.

### Temporary Marker

Created when a transfer starts:

```text
DJI_0001.MP4.tmp
```

If the program exits unexpectedly, leftover markers and incomplete files are detected and cleaned up on the next run.

### Hash Verification

Both source and destination files are verified using BLAKE3 hashes.

The source file is deleted only when the hashes match; on mismatch both the source and the `.tmp` marker are kept for retry.

---

## License

MIT License
