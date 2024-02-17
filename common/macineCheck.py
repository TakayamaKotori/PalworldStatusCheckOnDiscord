import psutil
import asyncio
import matplotlib.pyplot as plt
import time
import os
import pandas as pd
import re
from common import discordTextMessage


async def memoryUsageToCsv(filePath):
    df = await getMameryUsageDf()
    dfToDateCsv(df, filePath)


async def getMameryUsageDf():

    times = []
    cpu_usages = []
    memory_usages = []
    swap_usages = []

    t, c, u, s = await getMacineUsage_async()

    # メモリ使用状況を記録 [時刻,CPU使用率,メモリ使用率,スワップメモリ使用率]
    times.append(t)
    cpu_usages.append(c)
    memory_usages.append(u)
    swap_usages.append(s)

    data = {
        "Time": times,
        "CpuUsage": cpu_usages,
        "MemoryUsage": memory_usages,
        "SwapMemoryUsage": swap_usages,
    }
    df = pd.DataFrame(data)

    return df


def getMacineUsage():
    # CPU使用状況を取得
    cpu_usage = psutil.cpu_percent(interval=60)
    # メモリ使用状況を取得
    memory_usage = psutil.virtual_memory().percent
    # スワップメモリ使用状況を取得
    swap_usage = psutil.swap_memory().percent
    # 現在の時刻を記録
    current_time = time.strftime("%H:%M", time.localtime())
    return current_time, cpu_usage, memory_usage, swap_usage


async def getMacineUsage_async():
    loop = asyncio.get_running_loop()
    # 非同期で実行される関数を実行するためのexecutorを設定
    # CPU使用状況を取得
    cpu_usage = await loop.run_in_executor(
        None, lambda: psutil.cpu_percent(interval=60)
    )
    # メモリ使用状況を取得
    memory_usage = await loop.run_in_executor(
        None, lambda: psutil.virtual_memory().percent
    )
    # スワップメモリ使用状況を取得
    swap_usage = await loop.run_in_executor(None, lambda: psutil.swap_memory().percent)
    # 現在の時刻を記録
    current_time = time.strftime("%H:%M", time.localtime())
    return current_time, cpu_usage, memory_usage, swap_usage


data_csv_dir = "memory_logs"
csv_prefix = "memory_log"
csv_ext = "csv"

plt_png_dir = "memory_plt"


def getExistFilePath(fileName):

    csv_path = os.path.join(data_csv_dir, f"{fileName}")
    return csv_path


def getOutPltFilePath(fileName):

    pltFileName = (
        fileName.replace(data_csv_dir + "/", plt_png_dir + "/")
        .replace(data_csv_dir + "\\", plt_png_dir + "\\")
        .replace(".csv", ".png")
    )
    return pltFileName


def getOutCsvFilePath():

    csv_path = os.path.join(
        data_csv_dir, f"{csv_prefix}_{time.strftime('%Y%m%d')}.{csv_ext}"
    )
    return csv_path


def csvToDf(filePath):
    df = pd.read_csv(filePath, index_col=0)
    return df


def dfToDateCsv(df, filePath):

    if isFilePathExist(filePath):
        df.to_csv(filePath, mode="a", header=False, index=False)
    else:
        df.to_csv(filePath, mode="w", index=False)


def isFilePathExist(filePath):
    is_file = os.path.isfile(filePath)
    return is_file


def getLatestFile(directory_path, file_prefix="memory_log", file_extension=".csv"):
    pattern = re.compile(rf"{file_prefix}_(\d{{8}}){file_extension}")

    files = [f for f in os.listdir(directory_path) if pattern.match(f)]

    if not files:
        return None

    latest_file = max(files, key=lambda f: int(pattern.match(f).group(1)))
    return latest_file


def getLastFilePath():

    latest_file_name = getLatestFile(data_csv_dir)
    if latest_file_name is None:
        return None
    latestFilePath = getExistFilePath(latest_file_name)
    return latestFilePath


def cleanup_old_files(
    directory_path, file_prefix="memory_log", file_extension=".csv", max_files=7
):

    pattern = re.compile(rf"{file_prefix}_(\d{{8}}){file_extension}")

    files = [f for f in os.listdir(directory_path) if pattern.match(f)]
    files.sort()  # ファイルを日付順にソート

    if len(files) > max_files:
        files_to_delete = files[:-max_files]  # 古いファイルから max_files 以降を取得

        for file_to_delete in files_to_delete:
            file_path = os.path.join(directory_path, file_to_delete)
            os.remove(file_path)
            print(f"Deleted file: {file_path}")


def fileRotation():
    cleanup_old_files(data_csv_dir, file_extension=".csv")

    cleanup_old_files(plt_png_dir, file_extension=".png")


async def run(logger, client=None, channelId=None):

    # ディレクトリが存在しない場合は作成
    if not os.path.exists(data_csv_dir):
        os.makedirs(data_csv_dir)
    if not os.path.exists(plt_png_dir):
        os.makedirs(plt_png_dir)

    logger.info("ファイルチェック")
    latestFilePath = getLastFilePath()

    saveCsvFilePath = getOutCsvFilePath()

    # 1件もない場合はスキップ
    # これから処理するファイルが新規作成の場合は直前のデータは前日分
    # 最後のファイルをグラフに変換して出力
    if latestFilePath is not None and saveCsvFilePath != latestFilePath:
        logger.info("グラフ出力")
        # 新規に作成する場合はファイル出力
        df = csvToDf(latestFilePath)
        plt.figure()
        df.plot()
        pltFilePath = getOutPltFilePath(latestFilePath)
        plt.savefig(pltFilePath)
        plt.close("all")
        if client is not None and channelId is not None:
            file_name = os.path.basename(pltFilePath)
            await discordTextMessage.sendFileAndMessage(
                client, channelId, file_name, pltFilePath, file_name
            )

    logger.info("計測開始")
    await memoryUsageToCsv(saveCsvFilePath)
    logger.info("計測終了")

    fileRotation()

    return saveCsvFilePath
