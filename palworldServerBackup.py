import os
import tarfile
from datetime import datetime
from pathlib import Path
import configparser
from common import rcon, loggerUtil


config_ini = configparser.ConfigParser()
config_ini.read("setting.ini", encoding="utf-8")


PalWorldServerIP = config_ini["DEFAULT"]["PalWorldServerIP"]
PalWorldAdminPassword = config_ini["DEFAULT"]["PalWorldAdminPassword"]
PalworldPortRconPort = int(config_ini["DEFAULT"]["PalworldPortRconPort"])


logFilePath = config_ini["DEFAULT"]["BackupLogFilePath"]
logger = loggerUtil.getLogger(__name__, logFilePath)


def sendServerMessage(MessageText):
    logger.debug("getServerVersion")
    try:
        rcon.callPalworldRcon(f"/Broadcast {MessageText}")
    except Exception as e:
        logger.error("サーバーへメッセージ送信失敗")
        logger.error(e)


# 世代数（保持するファイルの数）
BackupGenerations = int(config_ini["DEFAULT"]["BackupGenerations"])


# バックアップ元ディレクトリ
SaveDir = config_ini["DEFAULT"]["SaveDir"]


# バックアップ先ディレクトリ
backup_dir = "./backup"

# ディレクトリが存在しない場合は作成
if not os.path.exists(backup_dir):
    os.makedirs(backup_dir)

# tar.gzファイルの作成
logger.info("バックアップ作成")
backup_filename = f"palworld_backup_{datetime.now().strftime('%Y%m%d%H%M%S')}.tar.gz"
with tarfile.open(os.path.join(backup_dir, backup_filename), "w:gz") as tar:
    tar.add(SaveDir, arcname=os.path.basename(SaveDir))

# 世代数を超えた古いバックアップファイルを削除

logger.info("古いバックアップ削除")
l = os.listdir(backup_dir)
logger.info(type(l[0]))
paths = list(Path(backup_dir).glob(r"*.tar.gz"))
paths.sort(key=os.path.getmtime, reverse=True)
for old_backup in paths[BackupGenerations:]:
    logger.info(old_backup)
    os.remove(old_backup)
