# DJ MCP Server for Spotify

AI エージェントから Spotify を操作するための個人用 MCP サーバー

## 概要

DJ MCP Server for Spotify は、個人用 Spotify MCP（Model Context Protocol）サーバーです。AI アシスタントから Spotify の機能を操作するためのインターフェースを提供します。

このアプリケーションは Spotify の公式製品ではなく、Spotify API を利用した個人用のサードパーティアプリケーションです。Spotify および Spotify ロゴは Spotify AB の登録商標です。

## 機能

- プレイリスト管理：閲覧、作成、編集
- 楽曲検索：曲名、アーティスト名による検索
- 再生コントロール：再生、一時停止、スキップ
- レコメンデーション機能：気分や状況に基づいた曲の提案

## セットアップ方法

1. リポジトリをクローン

   ```bash
   git clone https://github.com/ユーザー名/dj-mcp-server-for-spotify.git
   cd dj-mcp-server-for-spotify
   ```

2. 環境変数ファイルの設定
   `.env.example`ファイルをコピーして`.env`ファイルを作成し、必要な情報を入力してください：

   ```bash
   cp .env.example .env
   # その後、エディタで.envファイルを開いて編集してください
   ```

   または以下の内容で`.env`ファイルをプロジェクトルートに手動で作成してください：

   ```
   # Spotify API認証情報
   SPOTIFY_CLIENT_ID=your_client_id_here
   SPOTIFY_CLIENT_SECRET=your_client_secret_here
   SPOTIFY_REDIRECT_URI=http://127.0.0.1:8000/callback

   # サーバー設定
   HOST=0.0.0.0
   PORT=8000

   # 開発環境設定
   DEBUG=True

   # トークン保存先
   TOKEN_PATH=./tokens
   ```

3. Spotify Developer Dashboard で取得した Client ID と Client Secret を設定してください。

## .env.example ファイルについて

このプロジェクトには`.env.example`ファイルが含まれています。これは環境変数のテンプレートで、実際の認証情報は含まれていません。新規ユーザーはこのファイルをコピーして`.env`として使用し、自身の認証情報を設定してください。

`.env.example`の内容：

```
# Spotify API認証情報
SPOTIFY_CLIENT_ID=your_client_id_here
SPOTIFY_CLIENT_SECRET=your_client_secret_here
SPOTIFY_REDIRECT_URI=http://127.0.0.1:8000/callback

# サーバー設定
HOST=0.0.0.0
PORT=8000

# 開発環境設定
DEBUG=True

# トークン保存先
TOKEN_PATH=./tokens
```

## データの取り扱いについて

このアプリケーションは、Spotify API から取得した以下のデータを変更せずにそのまま提供します：

- トラック、アーティスト、プレイリスト、アルバムのメタデータ
- アルバムアートワーク
- 再生状態と制御情報

Spotify のコンテンツを表示する際は、常に Spotify の帰属表示（ロゴまたはアイコン）を含め、提供元が Spotify であることを明示します。

## 免責事項

このアプリケーションは Spotify の公式アプリケーションではありません。Spotify API の利用に関しては、Spotify Developer Terms of Service に従います。
