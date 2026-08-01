
from datetime import datetime
import shutil
import sys
import atexit
from pathlib import Path

from tqdm import tqdm
from blake3 import blake3

# =========================
# 配置
# =========================

# 当前脚本目录
BASE_DIR = Path(__file__).parent

CONFIG_FILE = BASE_DIR / "config.txt"


def load_config():

    # 不存在则创建模板
    if not CONFIG_FILE.exists():

        CONFIG_FILE.write_text(
            """# 相机源目录
SRC=

# 转存目标目录
DST=
""",
            encoding="utf-8"
        )

        print("首次运行，已创建 config.txt")
        print("请填写 SRC 和 DST 后重新运行")

        input("\n按回车退出...")
        sys.exit(0)


    config = {}

    with open(CONFIG_FILE, "r", encoding="utf-8") as f:

        for line in f:

            line = line.strip()

            # 跳过注释和空行
            if not line or line.startswith("#"):
                continue

            if "=" in line:

                key, value = line.split("=", 1)

                config[key.strip()] = value.strip()


    return config



config = load_config()


if not config.get("SRC") or not config.get("DST"):

    print("config.txt 配置不完整")
    print("请填写 SRC 和 DST")

    input("\n按回车退出...")
    sys.exit(1)



#Source Path 相机目录
SRC = Path(config["SRC"])

#Destination Path 转存目录
DST = Path(config["DST"])


BUF_SIZE = 8 * 1024 * 1024  # 8MB

# =========================
# 创建目标目录
# =========================

DST.mkdir(parents=True, exist_ok=True)

# =========================
# 单实例锁
# =========================

LOCKFILE = DST / "running.lock"

if LOCKFILE.exists():

    print("另一个实例正在运行，退出")
    input("\n按回车退出...")
    sys.exit(1)

LOCKFILE.touch()

# =========================
# 自动释放锁
# =========================

def release_lock():

    try:

        if LOCKFILE.exists():
            LOCKFILE.unlink()
            print("已释放运行锁")

    except Exception:
        pass

atexit.register(release_lock)

# =========================
# 计算 blake3
# =========================

def calc_blake3(file_path):

    h = blake3()

    with open(file_path, "rb") as f:

        while chunk := f.read(BUF_SIZE):
            h.update(chunk)

    return h.hexdigest()

# =========================
# 边复制边计算源文件 hash
# =========================

def copy_with_hash(src, dst):

    src_hash = blake3()

    total_size = src.stat().st_size

    with tqdm(
            total=total_size,
            unit="B",
            unit_scale=True,
            unit_divisor=1024,
            desc="复制进度",
            leave=True,
            dynamic_ncols=True
    ) as pbar:

        with open(src, "rb") as sf, open(dst, "wb") as df:

            while chunk := sf.read(BUF_SIZE):

                df.write(chunk)

                src_hash.update(chunk)

                pbar.update(len(chunk))

    shutil.copystat(src, dst)

    return src_hash.hexdigest()

# =========================
# 主逻辑
# =========================

try:

    # =========================
    # 检查源目录
    # =========================

    if not SRC.exists():

        print(f"源目录不存在: {SRC}")
        input("\n按回车退出...")
        sys.exit(1)

    # =========================
    # 删除 LRF
    # =========================

    print("\n=====================================")
    print("删除 .LRF 文件")
    print("=====================================")

    for lrf in SRC.glob("*.LRF"):

        try:

            lrf.unlink()
            print(f"已删除 LRF: {lrf.name}")

        except Exception as e:

            print(f"删除失败: {lrf.name}")
            print(e)
    print("\n=====================================")
    print("清理残留 tmp")
    print("=====================================")

    for tmp_file in DST.glob("*.tmp"):

        try:

            target_file = Path(
                str(tmp_file)[:-4]
            )

            if target_file.exists():
                print(
                    f"删除未完成文件: "
                    f"{target_file.name}"
                )

                target_file.unlink()

            print(
                f"删除残留 tmp: "
                f"{tmp_file.name}"
            )

            tmp_file.unlink()

        except Exception as e:

            print(
                f"清理失败: "
                f"{tmp_file.name}"
            )

            print(e)
    # =========================
    # 获取 MP4
    # =========================

    files_to_process = list(SRC.glob("*.MP4"))

    if not files_to_process:

        print("\n没有需要处理的 MP4 文件")
        release_lock()
        sys.exit(0)

    fail_count = 0
    failed_files = []
    print(f"处理开始时间: {datetime.now():%Y-%m-%d %H:%M:%S}")
    print("\n=====================================")
    print("开始处理 MP4 文件")
    print("=====================================")
    # =========================
    # 遍历文件
    # =========================

    for f in tqdm(
        files_to_process,
        desc="处理 MP4 文件",
        unit="file",
        leave=False
    ):

        dst_file = DST / f.name

        # =========================
        # 重名自动重命名
        # =========================

        if dst_file.exists():

            stem = dst_file.stem
            suffix = dst_file.suffix

            index = 2

            while True:

                candidate = (
                        DST /
                        f"{stem} ({index}){suffix}"
                )

                if not candidate.exists():
                    dst_file = candidate
                    break

                index += 1

            tqdm.write(
                f"检测到重名，重命名为: "
                f"{dst_file.name}"
            )
        # =========================
        # 开始复制
        # =========================
        tmp_file = Path(
            str(dst_file) + ".tmp"
        )

        tmp_file.touch(
            exist_ok=True
        )
        try:

            tqdm.write(f"复制文件: {f.name},{datetime.now():%Y-%m-%d %H:%M:%S}")

            # 边复制边计算源hash
            src_hash = copy_with_hash(f, dst_file)

            tqdm.write(f"复制完成，开始校验目标文件...{datetime.now():%Y-%m-%d %H:%M:%S}")

            # 只读取目标文件一次
            dst_hash = calc_blake3(dst_file)

            # =========================
            # 校验
            # =========================

            if src_hash == dst_hash:

                tqdm.write(
                    f"校验成功，删除源文件: {f.name}，{datetime.now():%Y-%m-%d %H:%M:%S}"
                )

                f.unlink()

                tmp_file.unlink(
                    missing_ok=True
                )

            else:

                tqdm.write(
                    f"校验失败，保留源文件和tmp: {f.name}，{datetime.now():%Y-%m-%d %H:%M:%S}"
                )

                fail_count += 1

                failed_files.append(
                    (
                        f.name,
                        "hash mismatch"
                    )
                )

                continue

        except Exception as e:

            tqdm.write(f"处理失败: {f.name}，{datetime.now():%Y-%m-%d %H:%M:%S}")
            tqdm.write(str(e))

            fail_count += 1

            failed_files.append(
                (
                    f.name,
                    str(e)
                )
            )

            continue

    # =========================
    # 完成
    # =========================

    print("\n=====================================")
    print(f"全部完成，{datetime.now():%Y-%m-%d %H:%M:%S}")
    print(f"失败数量: {fail_count}")

    if failed_files:

        print("\n失败文件列表:")

        for name, reason in failed_files:
            print(f"\n{name}")
            print(f"原因: {reason}")
    print("=====================================")

# =========================
# 全局异常
# =========================

except Exception as e:

    print(f"\n程序发生未处理异常,{datetime.now():%Y-%m-%d %H:%M:%S}")
    print(e)

# =========================
# 最终停留
# =========================

finally:

    release_lock()



