from datetime import datetime
import shutil
import sys
import atexit
import time
from pathlib import Path

from tqdm import tqdm
from blake3 import blake3
from winotify import Notification
import winsound


# =========================
# 配置
# =========================


if getattr(sys, "frozen", False):
    # PyInstaller exe
    BASE_DIR = Path(sys.executable).parent
else:
    # Python源码运行
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
        print(f"位置: {CONFIG_FILE}")
        print("请填写 SRC 和 DST 后重新运行")

        input("\n按回车退出...")
        sys.exit(0)


    config = {}

    with open(CONFIG_FILE, "r", encoding="utf-8") as f:

        for line in f:

            line = line.strip()

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



# Source Path
SRC = Path(config["SRC"])

# Destination Path
DST = Path(config["DST"])


BUF_SIZE = 8 * 1024 * 1024

# 动态速度估算 — EMA 平滑系数（0.3：较快适应真实速度，同时过滤单文件波动）
EMA_ALPHA = 0.3
INIT_SPEED = 36 * 1024 * 1024  # 36 MB/s，冷启动种子（USB 2.0 典型满速）


# =========================
# 完成通知
# =========================


def notify_done(ok_count, fail_count, failed_files=None):

    if fail_count == 0:
        title = "转存完成 ✓"
        msg = f"全部 {ok_count} 个文件校验通过"
        duration = "short"
    else:
        title = f"转存完成（{fail_count} 个失败）"
        msg = f"成功 {ok_count} / 失败 {fail_count}"
        if failed_files:
            msg += "\n" + "\n".join(name for name, _ in failed_files[:3])
            if len(failed_files) > 3:
                msg += f"\n…还有 {len(failed_files) - 3} 个"
        duration = "long"

    try:
        toast = Notification(
            app_id="Camera Importer",
            title=title,
            msg=msg,
            duration=duration,
        )
        toast.show()
    except Exception:
        pass

    try:
        if fail_count == 0:
            winsound.MessageBeep(winsound.MB_OK)
        else:
            winsound.MessageBeep(winsound.MB_ICONWARNING)
    except Exception:
        pass



# =========================
# 单实例锁定义
# =========================

LOCKFILE = DST / "running.lock"

LOCK_CREATED = False



def release_lock():

    global LOCK_CREATED

    try:

        if LOCK_CREATED and LOCKFILE.exists():

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


def copy_with_hash(src, dst, pbar_total=None):
    # src: 源文件路径；dst: 目标文件路径
    # pbar_total: 可选参数，传入总进度条后每复制一块同步累计，实现总进度实时刷新
    # 返回值: 源文件内容的 BLAKE3 哈希（十六进制字符串）

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

                # 同步累计总进度条，让总进度实时推进
                if pbar_total is not None:
                    pbar_total.update(len(chunk))


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
    # 创建目标目录
    # =========================


    DST.mkdir(
        parents=True,
        exist_ok=True
    )



    # =========================
    # 创建运行锁
    # =========================


    if LOCKFILE.exists():

        # 锁文件存在:可能是另一实例正在运行,也可能是上次异常退出残留
        # 输入 1 确认强制接管(继续使用旧锁),其他输入则退出
        print("检测到 running.lock(另一实例运行中或上次异常残留)")

        answer = input("输入 1 确认强制开始,其他任意键退出: ")

        if answer.strip() != "1":

            input("\n按回车退出...")

            sys.exit(1)


    LOCKFILE.touch()

    LOCK_CREATED = True



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



    # =========================
    # 清理残留 tmp
    # =========================


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
                    f"删除未完成文件: {target_file.name}"
                )

                target_file.unlink()



            print(
                f"删除残留 tmp: {tmp_file.name}"
            )


            tmp_file.unlink()



        except Exception as e:


            print(
                f"清理失败: {tmp_file.name}"
            )

            print(e)



    # =========================
    # 获取 MP4
    # =========================


    files_to_process = list(
        SRC.glob("*.MP4")
    )


    if not files_to_process:


        print("\n没有需要处理的 MP4 文件")

        sys.exit(0)



    fail_count = 0

    failed_files = []


    total_size = sum(f.stat().st_size for f in files_to_process)

    print(
        f"处理开始时间: {datetime.now():%Y-%m-%d %H:%M:%S}"
    )
    print(f"文件数量: {len(files_to_process)}")
    print(f"总大小:   {total_size / (1024**3):.2f} GB")


    print("\n=====================================")
    print("开始处理 MP4 文件")
    print("=====================================")



    # =========================
    # 遍历文件
    # =========================

    pbar = tqdm(
        total=total_size,
        unit="B",
        unit_scale=True,
        unit_divisor=1024,
        desc="总进度",
        leave=True,
    )

    ema_speed = None  # 动态速度，首个文件完成后初始化

    for f in files_to_process:

        file_size = f.stat().st_size
        dst_file = DST / f.name



        if dst_file.exists():


            stem = dst_file.stem

            suffix = dst_file.suffix

            index = 2


            while True:


                candidate = DST / f"{stem} ({index}){suffix}"


                if not candidate.exists():

                    dst_file = candidate

                    break


                index += 1



            tqdm.write(
                f"检测到重名，重命名为: {dst_file.name}"
            )



        tmp_file = Path(
            str(dst_file) + ".tmp"
        )


        tmp_file.touch(
            exist_ok=True
        )

        file_start = time.monotonic()

        try:


            tqdm.write(
                f"复制文件: {f.name},{datetime.now():%Y-%m-%d %H:%M:%S}"
            )


            src_hash = copy_with_hash(
                f,
                dst_file,
                pbar
            )


            tqdm.write(
                f"复制完成，开始校验目标文件...,{datetime.now():%Y-%m-%d %H:%M:%S}"
            )


            dst_hash = calc_blake3(
                dst_file
            )



            if src_hash == dst_hash:


                tqdm.write(
                    f"校验成功，删除源文件: {f.name},{datetime.now():%Y-%m-%d %H:%M:%S}"
                )


                tmp_file.unlink(
                    missing_ok=True
                )


                # 先删 tmp 再删源：避免中断时残留的 tmp 触发清理逻辑误删完整文件
                f.unlink()


            else:


                tqdm.write(
                    f"校验失败，保留源文件和tmp: {f.name},{datetime.now():%Y-%m-%d %H:%M:%S}"
                )


                fail_count += 1


                failed_files.append(
                    (
                        f.name,
                        "hash mismatch"
                    )
                )


        except Exception as e:


            tqdm.write(
                f"处理失败: {f.name},{datetime.now():%Y-%m-%d %H:%M:%S}"
            )

            tqdm.write(
                str(e)
            )


            fail_count += 1


            failed_files.append(
                (
                    f.name,
                    str(e)
                )
            )


        # 总进度已在 copy_with_hash 内按块实时累计，这里不再重复 update

        # 动态速度估算（EMA），按剩余字节 ÷ 当前速度计算 ETA
        elapsed = time.monotonic() - file_start
        if elapsed > 0:
            cur_speed = file_size / elapsed
        else:
            cur_speed = INIT_SPEED

        if ema_speed is None:
            ema_speed = cur_speed
        else:
            ema_speed = EMA_ALPHA * cur_speed + (1 - EMA_ALPHA) * ema_speed

        remaining = pbar.total - pbar.n
        eta_seconds = remaining / ema_speed if ema_speed > 0 else 0
        if eta_seconds < 3600:
            eta_str = f"{int(eta_seconds // 60)}分{int(eta_seconds % 60)}秒"
        else:
            eta_str = f"{eta_seconds / 3600:.1f}小时"
        pbar.set_postfix(预估剩余=eta_str, 速度=f"{ema_speed / 1024**2:.1f}MB/s")


    pbar.close()

    print("\n=====================================")

    print(
        f"全部完成，{datetime.now():%Y-%m-%d %H:%M:%S}"
    )

    print(
        f"失败数量: {fail_count}"
    )


    if failed_files:


        print("\n失败文件列表:")


        for name, reason in failed_files:

            print(name)

            print(reason)


    print("=====================================")

    ok_count = len(files_to_process) - fail_count
    notify_done(ok_count, fail_count, failed_files)

    try:
        input("\n按回车退出...")
    except EOFError:
        # stdin 不可交互（如被批处理管道调用）时自动退出，不打断链式流程
        pass



except Exception as e:


    print(
        f"\n程序发生未处理异常,{datetime.now():%Y-%m-%d %H:%M:%S}"
    )

    print(e)

    try:
        toast = Notification(
            app_id="Camera Importer",
            title="转存异常 ✗",
            msg=str(e)[:256],
            duration="long",
        )
        toast.show()
        winsound.MessageBeep(winsound.MB_ICONERROR)
    except Exception:
        pass



finally:


    release_lock()