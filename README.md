# Camera-Importer

一个用于安全转存相机视频的 Python 工具。

最初为 DJI Action 4 手元视频工作流编写，但同样适用于其他相机或存储设备的视频转存场景。

---

## 功能

* 单实例运行锁
* 自动删除 DJI `.LRF` 文件
* BLAKE3 哈希校验
* `.tmp` 临时标记保护
* 自动清理未完成转存
* 自动处理重名文件
* 校验成功后才删除源文件
* 外部 `config.txt` 配置路径
* `tqdm` 进度条显示

---

## 工作流程

```text
相机存储卡
    ↓
读取配置文件
    ↓
复制文件
    ↓
计算并校验 BLAKE3
    ↓
校验成功
    ↓
删除源文件
```

如果校验失败：

```text
保留源文件
保留 tmp 标记
报告错误
```

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

程序首次运行时，会自动在脚本同目录创建：

```text
config.txt
```

默认内容：

```txt
# 相机源目录
SRC=

# 转存目标目录
DST=
```

填写对应路径：

示例：

```txt
# 相机源目录
SRC=E:\DCIM\DJI_001

# 转存目标目录
DST=D:\camera output\unprocessed
```

保存后重新运行即可。

---

## 依赖

```bash
pip install tqdm blake3
```

---

## 使用方法

```bash
python CameraImporter.py
```

或者直接双击运行。

---

## 安全机制

### 运行锁

程序启动时创建：

```text
running.lock
```

用于防止多个实例同时运行，避免重复转存导致数据冲突。

---

### 临时文件标记

复制开始时创建：

```text
DJI_0001.MP4.tmp
```

如果程序异常退出：

下一次启动时会自动检测并清理未完成文件。

---

### BLAKE3 哈希校验

源文件与目标文件分别计算 BLAKE3 哈希。

只有：

```text
源文件 Hash == 目标文件 Hash
```

时才会删除源文件。

---

### 重名处理

如果目标目录存在同名文件：

自动生成：

```text
DJI_0001 (2).MP4
```

避免覆盖已有文件。

---

## License

MIT License

# Camera-Importer

A Python tool for safely importing camera footage.

Originally created for a DJI Action 4 POV recording workflow, but it can also be used for safely transferring videos from other cameras or storage devices.

---

## Features

* Single-instance execution lock
* Automatic removal of DJI `.LRF` files
* BLAKE3 hash verification
* Temporary `.tmp` file protection
* Automatic cleanup of incomplete transfers
* Automatic duplicate filename handling
* Delete source files only after successful verification
* External path configuration through `config.txt`
* Progress display with `tqdm`

---

## Workflow

```text
Camera Storage
        ↓
Read Configuration
        ↓
Copy File
        ↓
Calculate & Verify BLAKE3 Hash
        ↓
Verification Successful
        ↓
Delete Source File
```

If verification fails:

```text
Keep Source File
Keep Temporary Marker
Report Error
```

---

## Why?

During a previous video transfer, a design flaw caused the original file to be deleted before the copy process was fully verified, resulting in the loss of a POV recording.

After that incident, the entire transfer workflow was redesigned with:

* Hash verification
* Temporary file markers
* Automatic recovery
* Single-instance protection

The core principle is simple:

> Never delete the original file before confirming that the copied file is valid.

---

## Configuration

On the first run, the program automatically creates:

```text
config.txt
```

in the same directory as the script.

Default content:

```txt
# Camera source directory
SRC=

# Transfer destination directory
DST=
```

Fill in your own paths:

Example:

```txt
# Camera source directory
SRC=E:\DCIM\DJI_001

# Transfer destination directory
DST=D:\camera output\unprocessed
```

Save the file and run the program again.

---

## Requirements

Install dependencies:

```bash
pip install tqdm blake3
```

---

## Usage

Run:

```bash
python CameraImporter.py
```

Or simply double-click the script if Python is associated with `.py` files.

---

## Safety Features

### Lock File

When the program starts, it creates:

```text
running.lock
```

This prevents multiple instances from running at the same time and avoids duplicate transfers.

---

### Temporary File Marker

When a transfer starts, a temporary marker is created:

```text
DJI_0001.MP4.tmp
```

If the program exits unexpectedly, unfinished transfers will be detected and cleaned up during the next run.

---

### BLAKE3 Hash Verification

Both source and destination files are calculated using BLAKE3.

The source file will only be deleted when:

```text
Source Hash == Destination Hash
```

This ensures that the transferred file is identical to the original.

---

### Duplicate Filename Handling

If a file with the same name already exists in the destination directory:

The program automatically creates a new filename:

```text
DJI_0001 (2).MP4
```

Existing files will never be overwritten.

---

## License

MIT License
