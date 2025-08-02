# Raspberry Pi Monitor v1

リアルタイムで映像と音声をストリーミングできるRaspberry Pi用の監視システムです。

## 概要

このプロジェクトは、USBウェブカメラを使用してRaspberry Piから映像と音声をブラウザにストリーミングするシンプルなWebアプリケーションです。ベビーモニターやペット監視、簡易的な監視カメラとして使用できます。

## 主な機能

- **リアルタイム映像ストリーミング**: 640x480 @ 15FPS
- **リアルタイム音声ストリーミング**: 16kHz モノラル
- **ブラウザベースのインターフェース**: 特別なアプリ不要
- **音声のオン/オフ切り替え**: 必要に応じて音声を有効化

## 技術仕様

- **バックエンド**: Flask + Flask-SocketIO
- **映像処理**: OpenCV
- **音声処理**: PyAudio
- **通信方式**: 
  - 映像: HTTP Multipart streaming
  - 音声: WebSocket (Socket.IO)

## 必要環境

- Raspberry Pi 3 B+ 以上
- Raspberry Pi OS (Bookworm)
- Python 3.11+
- USBウェブカメラ（マイク内蔵推奨）

## クイックスタート

1. リポジトリをクローン
```bash
git clone https://github.com/[your-username]/raspi-monitor.git
cd raspi-monitor
```

2. 仮想環境を作成してパッケージをインストール
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

3. アプリケーションを起動
```bash
python audio_video_app.py
```

4. ブラウザでアクセス
```
http://[Raspberry PiのIPアドレス]:5000/
```

詳細なセットアップ手順は [docs/SETUP.md](docs/SETUP.md) を参照してください。

## プロジェクト構造

```
raspi-monitor/
├── audio_video_app.py    # メインアプリケーション
├── requirements.txt      # Pythonパッケージ一覧
├── README.md            # このファイル
├── docs/
│   ├── SETUP.md         # 詳細なセットアップガイド
│   └── requirements.md  # プロジェクト要件
└── CLAUDE.md           # AI開発支援用の説明
```

## 使い方

1. ブラウザでアプリケーションにアクセス
2. 映像が自動的に表示されます
3. 音声を聞く場合は「Enable Audio」ボタンをクリック
4. 音声を停止する場合は「Disable Audio」ボタンをクリック

## 既知の問題

- 初回の音声有効化時に若干の遅延が発生する場合があります
- ネットワーク帯域によっては映像/音声が途切れる場合があります

## ライセンス

MIT License

## 作者

[Your Name]

## 謝辞

このプロジェクトは、オープンソースコミュニティの多くの優れたライブラリを使用しています。