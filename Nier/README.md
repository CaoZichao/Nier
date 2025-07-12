# Nier Chat
OpenAI APIをベースにした仮想キャラクター対話システム。ゲーム『ブルーアーカイブ』のキャラクター『伊落マリー』を模倣し、永続化メモリ機能を統合。

## 概要
- “マリー”というキャラクターとの対話
- 会話履歴の永続化（SQLite）
- 外部情報の自動スクレイピング（Wiki、Pixiv など）
- Flask ベースの Web UI

## ディレクトリ構成
```
.
├── main.py         # メインロジック（メモリ管理・外部取得・対話生成）
├── gui.py          # Flask サーバー起動・フロントエンド
├── memory.db       # SQLite DB（自動生成、.gitignore 対象）
├── Avatar.jpg      # キャラクター画像
├── requirements.txt
├── README.md

```

## 動作環境
- Python
- Flask
- openai

## インストール手順
1. リポジトリをクローン  
   ```bash
   git clone <リポジトリURL>
   cd <プロジェクト名>
   ```
2. 仮想環境を作成・有効化  
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
3. 依存パッケージをインストール  
   ```bash
   pip install -r requirements.txt
   ```

## 設定
- 環境変数 `OPENAI_API_KEY` に OpenAI API キーを設定  
  ```bash
  export OPENAI_API_KEY="あなたのAPIキー"
  ```

## 使い方
1. サーバーを起動  
   ```bash
   python gui.py
   ```
2. ブラウザで `http://localhost:5000` にアクセス  
3. キャラクターとの対話を開始

git clone https://github.com/CaoZichao/nier.git
