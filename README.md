# Camera Importer

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
* `tqdm` 进度条显示

---

## 工作流程

```text
相机存储卡
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

修改脚本顶部的路径：

```python
SRC = Path(r"")
DST = Path(r"")
```

示例：

```python
SRC = Path(r"E:\DCIM\DJI_001")
DST = Path(r"D:\camera output\unprocessed")
```

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

防止多个实例同时运行。

---

### 临时文件标记

复制开始时创建：

```text
DJI_0001.MP4.tmp
```

程序异常退出时，下一次启动会自动检测并清理未完成文件。

---

### 哈希校验

源文件与目标文件分别计算 BLAKE3 哈希。

只有完全一致时才会删除源文件。

---

## License

MIT License
# Camera Importer

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
* `tqdm` 进度条显示

---

## 工作流程

```text
相机存储卡
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

修改脚本顶部的路径：

```python
SRC = Path(r"")
DST = Path(r"")
```

示例：

```python
SRC = Path(r"E:\DCIM\DJI_001")
DST = Path(r"D:\camera output\unprocessed")
```

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

防止多个实例同时运行。

---

### 临时文件标记

复制开始时创建：

```text
DJI_0001.MP4.tmp
```

程序异常退出时，下一次启动会自动检测并清理未完成文件。

---

### 哈希校验

源文件与目标文件分别计算 BLAKE3 哈希。

只有完全一致时才会删除源文件。

---

## License

MIT License




# Camera Importer

A simple Python tool for safely importing camera footage.

Originally created for a DJI Action 4 POV workflow, but it can be used with any directory containing video files.

---

## Features

* Single-instance lock protection
* Automatic removal of DJI `.LRF` files
* BLAKE3 hash verification
* Temporary file (`.tmp`) protection
* Automatic cleanup of unfinished transfers
* Automatic duplicate filename handling
* Source file deletion only after successful verification
* Progress bars using `tqdm`

---

## Workflow

```text
Camera Storage
      ↓
Copy File
      ↓
BLAKE3 Verification
      ↓
Verification Success
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

After losing a POV recording due to an interrupted transfer, I decided to redesign the workflow with verification and recovery mechanisms.

The following protections were added:

* Hash verification
* Temporary file markers
* Automatic recovery
* Single-instance lock

The design goal is simple:

> Never delete the original file unless the copied file has been verified.

---

## Configuration

Edit the paths at the top of the script:

```python
SRC = Path(r"")
DST = Path(r"")
```

Example:

```python
SRC = Path(r"E:\DCIM\DJI_001")
DST = Path(r"D:\camera output\unprocessed")
```

---

## Requirements

```bash
pip install tqdm blake3
```

---

## Usage

```bash
python CameraImporter.py
```

Or simply double-click the script if Python is associated with `.py` files.

---

## Safety Features

### Lock File

Prevents multiple instances from running simultaneously.

---

### Temporary Marker

Created when a transfer starts:

```text
DJI_0001.MP4.tmp
```

If the program exits unexpectedly, unfinished files will be detected and cleaned up during the next run.

---

### Hash Verification

Both source and destination files are verified using BLAKE3 hashes.

The source file is deleted only when the hashes match.

---

## License

MIT License
# Camera Importer

A simple Python tool for safely importing camera footage.

Originally created for a DJI Action 4 POV workflow, but it can be used with any directory containing video files.

---

## Features

* Single-instance lock protection
* Automatic removal of DJI `.LRF` files
* BLAKE3 hash verification
* Temporary file (`.tmp`) protection
* Automatic cleanup of unfinished transfers
* Automatic duplicate filename handling
* Source file deletion only after successful verification
* Progress bars using `tqdm`

---

## Workflow

```text
Camera Storage
      ↓
Copy File
      ↓
BLAKE3 Verification
      ↓
Verification Success
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

After losing a POV recording due to an interrupted transfer, I decided to redesign the workflow with verification and recovery mechanisms.

The following protections were added:

* Hash verification
* Temporary file markers
* Automatic recovery
* Single-instance lock

The design goal is simple:

> Never delete the original file unless the copied file has been verified.

---

## Configuration

Edit the paths at the top of the script:

```python
SRC = Path(r"")
DST = Path(r"")
```

Example:

```python
SRC = Path(r"E:\DCIM\DJI_001")
DST = Path(r"D:\camera output\unprocessed")
```

---

## Requirements

```bash
pip install tqdm blake3
```

---

## Usage

```bash
python CameraImporter.py
```

Or simply double-click the script if Python is associated with `.py` files.

---

## Safety Features

### Lock File

Prevents multiple instances from running simultaneously.

---

### Temporary Marker

Created when a transfer starts:

```text
DJI_0001.MP4.tmp
```

If the program exits unexpectedly, unfinished files will be detected and cleaned up during the next run.

---

### Hash Verification

Both source and destination files are verified using BLAKE3 hashes.

The source file is deleted only when the hashes match.

---

## License

MIT License
