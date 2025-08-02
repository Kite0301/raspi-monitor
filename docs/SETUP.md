# Raspberry Pi Monitor v1 セットアップガイド

このドキュメントでは、Raspberry Pi Monitor v1をRaspberry Piで動作させるための手順を説明します。

## 必要なハードウェア

- Raspberry Pi 3 B+ 以上
- USBウェブカメラ（マイク内蔵推奨）
  - 動作確認済み: Logitech Brio 100
- microSDカード（16GB以上推奨）
- 電源アダプター

## 前提条件

- Raspberry Pi OS (Bookworm) がインストール済み
- SSHが有効化されている
- インターネット接続が利用可能

## セットアップ手順

### 1. システムの更新

```bash
sudo apt update
sudo apt upgrade -y
```

### 2. 必要なシステムパッケージのインストール

```bash
# Python開発環境
sudo apt install -y python3-pip python3-venv

# OpenCV依存関係
sudo apt install -y libgstreamer1.0-dev libgstreamer-plugins-base1.0-dev

# 音声ライブラリ依存関係
sudo apt install -y portaudio19-dev python3-pyaudio

# V4L2ツール（カメラ確認用）
sudo apt install -y v4l2ctl
```

### 3. ユーザー権限の設定

```bash
# piユーザーをvideoグループに追加（カメラアクセス用）
sudo usermod -a -G video pi

# 再ログインまたは再起動が必要
sudo reboot
```

### 4. Motionサービスの無効化（競合回避）

```bash
# Motionがインストールされている場合は停止・無効化
sudo systemctl stop motion
sudo systemctl disable motion
```

### 5. プロジェクトのセットアップ

```bash
# ホームディレクトリに移動
cd /home/pi

# プロジェクトをクローン（またはファイルをコピー）
git clone https://github.com/[your-username]/raspi-monitor.git
cd raspi-monitor

# Python仮想環境の作成
python3 -m venv venv

# 仮想環境をアクティベート
source venv/bin/activate

# Pythonパッケージのインストール
pip install -r requirements.txt
```

### 6. カメラの確認

```bash
# 接続されているビデオデバイスを確認
ls /dev/video*

# カメラの詳細情報を確認
v4l2-ctl --list-devices

# 音声デバイスを確認
arecord -l
```

### 7. アプリケーションの起動

```bash
# 仮想環境をアクティベート（まだの場合）
source venv/bin/activate

# アプリケーションを起動
python audio_video_app.py
```

アプリケーションが起動すると、以下のURLでアクセスできます：
- `http://[Raspberry PiのIPアドレス]:5000/`

### 8. 自動起動の設定（オプション）

プロジェクトに含まれているsystemdサービスファイルを使用して自動起動を設定できます。

```bash
# サービスファイルをシステムにコピー
sudo cp /home/pi/raspi-monitor/raspi-monitor.service /etc/systemd/system/

# サービスを有効化
sudo systemctl daemon-reload
sudo systemctl enable raspi-monitor.service
sudo systemctl start raspi-monitor.service

# ステータス確認
sudo systemctl status raspi-monitor.service
```

#### サービスの管理コマンド

```bash
# サービスの停止
sudo systemctl stop raspi-monitor.service

# サービスの再起動
sudo systemctl restart raspi-monitor.service

# ログの確認
sudo journalctl -u raspi-monitor.service -f

# 自動起動の無効化
sudo systemctl disable raspi-monitor.service
```

**注意**: サービスファイルは仮想環境のパスが `/home/pi/raspi-monitor/venv` であることを前提としています。異なるパスを使用している場合は、サービスファイルを編集してください。

## 再起動後の手順

### 手動起動の場合

Raspberry Piを再起動した後、以下の手順でアプリケーションを起動します：

```bash
# SSHでRaspberry Piに接続
ssh raspi

# プロジェクトディレクトリに移動
cd /home/pi/raspi-monitor

# 仮想環境をアクティベート
source venv/bin/activate

# アプリケーションを起動
python audio_video_app.py
```

### 自動起動を設定している場合

自動起動サービスが設定されている場合は、再起動後に自動的にアプリケーションが起動します。

```bash
# サービスの状態確認
sudo systemctl status raspi-monitor.service

# ログの確認
sudo journalctl -u raspi-monitor.service -f
```

ブラウザで `http://[Raspberry PiのIPアドレス]:5000/` にアクセスして動作を確認してください。

## トラブルシューティング

### カメラが認識されない場合

1. USBケーブルの接続を確認
2. 別のUSBポートを試す
3. `dmesg | tail` でエラーメッセージを確認

### 音声が聞こえない場合

1. カメラにマイクが内蔵されているか確認
2. `arecord -l` で音声デバイスが認識されているか確認
3. ブラウザで「Enable Audio」ボタンをクリックしているか確認

### アプリケーションが起動しない場合

1. ポート5000が他のアプリケーションで使用されていないか確認
2. `sudo lsof -i :5000` でポートの使用状況を確認
3. ファイアウォールの設定を確認

## パフォーマンスの調整

`audio_video_app.py`内の以下のパラメータで調整可能：

- `VIDEO_WIDTH`, `VIDEO_HEIGHT`: 映像解像度
- `VIDEO_FPS`: フレームレート
- `RATE`: 音声サンプリングレート
- `CHUNK`: 音声バッファサイズ