from common import common
import logging
from logging.handlers import TimedRotatingFileHandler
import datetime
import os


def getLogger(name, logFilePath):
    logger = logging.getLogger(name)
    formatter = logging.Formatter("%(asctime)s - %(levelname)s:%(name)s - %(message)s")

    config_ini = common.getConfigFile()
    logLevelSetting = config_ini["DEFAULT"]["LOGLEVEL"]
    directory_name = os.path.dirname(logFilePath)
    # ディレクトリが存在しない場合は作成
    if not os.path.exists(directory_name):
        os.makedirs(directory_name)

    # ファイルハンドラでtest.logにログを出力するように設定
    file_handler = TimedRotatingFileHandler(
        logFilePath,
        when="D",
        interval=1,
        backupCount=7,
        atTime=datetime.time(0, 0, 0),
    )

    # test.logに出力するログレベルを個別でERRORに設定
    logLevel = logging.INFO
    if logLevelSetting == "debug":
        logLevel = logging.DEBUG

    # ロガーのレベルを設定
    logger.setLevel(logLevel)

    file_handler.setLevel(logLevel)
    file_handler.setFormatter(formatter)

    # コンソールに出力するためのStreamHandlerを設定
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    # loggerにそれぞれのハンドラーを追加
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)

    return logger
