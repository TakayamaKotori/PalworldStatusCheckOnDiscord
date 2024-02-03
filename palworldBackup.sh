#!/bin/bash

# 停止メッセージを送信
python3.12 palworldServerBackup.py

# サービスの停止コマンド
sudo systemctl stop palworld-dedicated.service

# バックアップ実行
python3.12 palworldServerBackup.py

# サービスの再起動コマンド
sudo systemctl stop palworld-dedicated.service