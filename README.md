# 個人専用 DJ Spotify MCP Server（Docker 対応・拡張機能版）

Spotify API を MCP（Model Context Protocol）サーバーとして公開し、AI アシスタント（Claude、Cursor など）から操作できるようにするプロジェクトです。このバージョンには、再生コントロール、アーティスト検索、気分に基づくプレイリスト生成など多くの拡張機能が含まれています。Docker Compose を利用して環境構築の再現性を高めています。

## セットアップ手順

**非エンジニアの方や、より詳細なステップバイステップのセットアップ手順が必要な方は、こちらの[簡単セットアップガイド (SETUP_GUIDE.md)](SETUP_GUIDE.md)をご覧ください。** このガイドでは、スクリプト (`run.sh` / `run.bat`) を使用した簡単なセットアップ方法を解説しています。

### Docker を使用する場合（推奨）

Docker を使用すると、環境構築が簡単になり、再現性も高まります。

1.  Docker と Docker Compose をインストールしてください。
2.  このリポジトリをクローンします:
    ```bash
    git clone https://github.com/Slevin06/dj-mcp-server-for-spotify.git
    cd dj-mcp-server-for-spotify
    ```
3.  プロジェクトルートに `.env.example` を参考に `.env` ファイルを作成し、Spotify API のキー情報を設定します。詳細は [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/) を確認してください。
    - `SPOTIFY_CLIENT_ID`: あなたの Client ID
    - `SPOTIFY_CLIENT_SECRET`: あなたの Client Secret
    - `SPOTIFY_REDIRECT_URI`: `http://127.0.0.1:8000/callback` (Spotify Developer Dashboard にもこの URI を登録)
4.  Docker Compose でサーバーを起動します:
    ```bash
    docker-compose up --build
    ```
5.  初回のみ、ウェブブラウザで `http://127.0.0.1:8000/auth/login` にアクセスして Spotify 認証を行います。
6.  AI アシスタントで MCP サーバーとして `http://127.0.0.1:8000/mcp` を設定します。

> **注意:** Spotify はリダイレクト URI に `localhost` ではなく `127.0.0.1` の使用を推奨しています。

### Docker を使用しない場合

Docker を使用しないセットアップ方法については、[簡単セットアップガイド (SETUP_GUIDE.md)](SETUP_GUIDE.md) を参照してください。このガイドでは、必要なツールのインストールからサーバーの起動までを詳しく説明しています。

## 主な機能

### プレイリスト管理

- プレイリスト一覧取得 `/playlists/me`
- プレイリスト内の曲一覧取得 `/playlists/{playlist_id}/tracks`
- プレイリスト作成 `/playlists`
- プレイリストへの曲追加 `/playlists/{playlist_id}/tracks`
- プレイリスト内の曲順変更 `/playlists/{playlist_id}/tracks/reorder`

### 検索機能

- 曲検索 `/search/tracks`
- アーティスト検索 `/search/artists`
- アーティスト情報取得 `/search/artists/{artist_id}`
- アーティストの人気曲取得 `/search/artists/{artist_id}/top-tracks`
- 複数の曲情報を一度に取得 `/search/tracks/get-multiple`

### 再生コントロール

- 現在再生中の曲情報取得 `/player/now-playing`
- 再生開始/再開 `/player/play`
- 一時停止 `/player/pause`
- 次の曲へスキップ `/player/next`
- 前の曲へ戻る `/player/previous`
- シャッフルモード切替 `/player/shuffle`
- リピートモード設定 `/player/repeat`
- 音量設定 `/player/volume`
- 利用可能デバイス一覧取得 `/player/devices`
- 再生デバイス切り替え `/player/transfer`
- 再生キューに追加 `/player/queue`
- 再生位置を移動 `/player/seek`

### レコメンデーション

- 利用可能なジャンル（カテゴリ）一覧取得 `/recommendations/genres`
- 気分に基づくレコメンド取得 `/recommendations/by-mood`
  - 対応する気分: happy, sad, energetic, calm, focus, party, relax, sleep, workout, romantic, studying, upbeat, mellow
- カテゴリ（ジャンル）に基づくレコメンド取得 `/recommendations/by-category`
- アーティストに基づくレコメンド取得 `/recommendations/by-artist`
- レコメンドからプレイリスト作成 `/recommendations/generate-playlist`
- レコメンドして即時再生 `/recommendations/play-recommendations`

### 複合機能

- 気分に基づく曲の検索・視聴・プレイリスト作成（`/recommendations/by-mood` + プレイリスト作成オプション + 再生機能）
- カテゴリ指定による視聴・プレイリスト作成（`/recommendations/by-category` + プレイリスト作成オプション + 再生機能）
- アーティスト指定による視聴・プレイリスト作成（`/recommendations/by-artist` + プレイリスト作成オプション + 再生機能）

## 注意点

- このサーバーは個人利用に最適化されています。
- Spotify への認証は一度だけ行えば、トークンが自動的に更新されます。
- サーバーを再起動しても認証状態は保持されます（Docker 環境ではボリュームマウントにより永続化されます。スクリプト実行の場合もローカルにトークンファイルが保存されます）。
- 再生コントロール機能を使うには、アクティブな Spotify クライアントが必要です。
