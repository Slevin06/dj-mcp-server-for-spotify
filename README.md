# 🎵 DJ Spotify MCP Server

**FastMCP（HTTP）方式で構築された Spotify Web API の MCP（Model Context Protocol）サーバー**

AI アシスタント（Claude、Cursor など）から自然言語で Spotify を操作できる個人開発プロジェクトです。FastMCP フレームワークを使用して HTTP 経由で MCP プロトコルを提供し、すべての Spotify 機能が AI から利用可能になります。

[![GitHub](https://img.shields.io/badge/GitHub-Repository-blue)](https://github.com/Slevin06/dj-mcp-server-for-spotify)
[![Python](https://img.shields.io/badge/Python-3.11+-blue)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-Latest-green)](https://fastapi.tiangolo.com)
[![MCP](https://img.shields.io/badge/MCP-Protocol-purple)](https://modelcontextprotocol.io)

## ✨ 特徴

- 🚀 **FastMCP（HTTP）方式**: 安定した HTTP 通信による MCP プロトコル提供
- 🎵 **包括的な Spotify 機能**: 検索、再生、プレイリスト管理、レコメンデーションなど
- 🤖 **AI アシスタント対応**: Claude、Cursor などから自然言語で操作
- 🔐 **OAuth2.0 認証**: Spotify 公式 API による安全な認証
- 📋 **自動ツール生成**: FastAPI エンドポイントが自動的に MCP ツール化
- 📖 **開発者フレンドリー**: Swagger UI、ReDoc による API ドキュメント自動生成

## 🚀 クイックスタート

### 1. プロジェクトの準備

```bash
# リポジトリをクローン
git clone https://github.com/Slevin06/dj-mcp-server-for-spotify.git
cd dj-mcp-server-for-spotify

# 仮想環境を作成・アクティベート
python -m venv .venv
source .venv/bin/activate  # macOS/Linux
# または .venv\Scripts\activate  # Windows

# 依存関係をインストール
pip install -r requirements.txt
```

### 2. Spotify API 設定

1. [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/) でアプリを作成
2. リダイレクト URI に `http://127.0.0.1:8000/auth/callback` を追加
3. `.env.example` を `.env` にコピーして API 情報を設定：

```bash
cp .env.example .env
```

`.env` ファイルを編集：

```env
SPOTIFY_CLIENT_ID=your_client_id_here
SPOTIFY_CLIENT_SECRET=your_client_secret_here
SPOTIFY_REDIRECT_URI=http://127.0.0.1:8000/auth/callback
```

### 3. サーバー起動

```bash
# FastMCP サーバーを起動
./run_fastapi_mcp.sh
```

起動後、以下が利用可能になります：

- **MCP エンドポイント**: `http://localhost:8000/mcp`
- **API ドキュメント**: `http://localhost:8000/docs`
- **Swagger UI**: `http://localhost:8000/redoc`

### 4. AI アシスタントの設定

**~/.cursor/mcp.json** に以下を追加：

```json
{
  "mcpServers": {
    "dj-spotify-mcp-server": {
      "url": "http://localhost:8000/mcp"
    }
  }
}
```

### 5. Spotify 認証

1. ブラウザで `http://localhost:8000/auth/login` にアクセス
2. Spotify アカウントでログイン・許可
3. 認証完了後、AI アシスタントから利用可能

## 🎯 主な機能

### 🔐 認証機能 ✅ **全てフリープランで利用可能**

- `start_spotify_authentication` - Spotify OAuth2.0 認証開始
- `handle_spotify_callback` - OAuth 認証コールバック処理
- `get_spotify_auth_status` - 認証状態確認・トークン管理
- `disconnect_spotify_account` - アカウント接続解除
- `clear_auth_cache` - 認証キャッシュクリア

### 🎵 プレイリスト管理 ✅ **全てフリープランで利用可能**

#### 参照機能

- `get_my_playlists` - プレイリスト一覧取得
- `get_playlist_tracks` - プレイリスト内楽曲詳細表示

#### 編集機能（2 段階確認付き）

- `preview_playlist_creation` - プレイリスト作成プレビュー **[新機能]**
- `create_playlist` - 新規プレイリスト作成（要事前承認）
- `preview_tracks_addition` - 楽曲追加プレビュー **[新機能]**
- `add_tracks_to_playlist` - プレイリストへの楽曲追加（要事前承認）
- `reorder_playlist_track` - プレイリスト内楽曲の順序変更

**💡 ユーザー体験の向上**: プレイリスト作成・楽曲追加は事前にプレビューで内容を確認してから実行できるため、安心して利用できます。

### 🔍 検索機能 ✅ **全てフリープランで利用可能**

- `search_tracks` - 楽曲検索
- `search_artists` - アーティスト検索
- `get_artist_info` - アーティスト詳細情報取得
- `get_artist_top_tracks` - アーティストの人気曲取得
- `get_multiple_tracks` - 複数楽曲情報の一括取得
- `search_tracks_with_filters` - フィルター付き楽曲検索

### 🎚️ 再生コントロール ⚠️ **プレミアムプラン専用**

#### 再生状態取得 ✅ **フリープランで利用可能**

- `get_playback_state` - 現在の包括的な再生状態取得
- `get_now_playing` - 現在再生中の楽曲情報取得
- `get_available_devices` - 利用可能デバイス一覧取得

#### 再生操作 🔒 **プレミアムプラン専用**

- `play_music` - 楽曲の再生開始
- `pause_music` - 再生の一時停止
- `skip_to_next` - 次の楽曲へスキップ
- `skip_to_previous` - 前の楽曲へ戻る
- `seek_to_position` - 楽曲内の再生位置移動

#### プレイヤー設定 🔒 **プレミアムプラン専用**

- `set_volume` - 音量調整
- `set_shuffle_mode` - シャッフルモードの設定
- `set_repeat_mode` - リピートモードの設定
- `transfer_playback` - 再生デバイスの切り替え

#### キュー操作 🔒 **プレミアムプラン専用**

- `add_to_queue` - 再生キューへの楽曲追加

### 🎯 レコメンデーション ✅ **全てフリープランで利用可能**

- `get_available_genres` - 利用可能ジャンル取得
- `get_recommendations` - 楽曲推薦取得
- `get_recommendations_by_mood` - 気分・カテゴリ基準の楽曲推薦
- `create_playlist_from_recommendations` - 推薦楽曲からの自動プレイリスト作成

### 👤 ユーザー情報・履歴 ✅ **全てフリープランで利用可能**

- `get_user_profile` - ユーザープロファイル取得
- `get_recently_played_tracks` - 最近再生した楽曲履歴
- `get_user_top_items` - ユーザーのトップアイテム（楽曲・アーティスト）
- `get_followed_artists` - フォロー中アーティスト取得
- `follow_artists_or_users` - アーティスト・ユーザーのフォロー
- `unfollow_artists_or_users` - フォロー解除

### 🛠️ ユーティリティ ✅ **全てフリープランで利用可能**

- `health_check` - サーバーヘルスチェック
- `get_server_version` - サーバーバージョン情報取得
- `get_available_markets` - 利用可能地域（国コード）取得

## ⚠️ Spotify プレミアムプラン要件

### 🔒 プレミアム専用機能について

フリープランユーザーがプレミアム専用機能を使用した場合、以下のエラーが発生します：

#### 一般的な権限エラー（HTTP 403）

```json
{
  "detail": "予期せぬエラー: 403: この操作を実行する権限がありません。"
}
```

**対象機能**: `play_music`, `pause_music`, `skip_to_next`, `skip_to_previous`, `set_volume`, `set_shuffle_mode`, `set_repeat_mode`, `seek_to_position`, `transfer_playback`

#### 明示的なプレミアム要求エラー

```json
{
  "detail": "Failed to add to queue: http status: 403, code: -1 - https://api.spotify.com/v1/me/player/queue?uri=spotify:track:xxxxx:\n Player command failed: Premium required, reason: PREMIUM_REQUIRED"
}
```

**対象機能**: `add_to_queue`

### ✅ フリープランでも十分活用可能

DJ MCP Server は**フリープランでも以下の用途で十分活用できます**：

- 🔍 **音楽発見・検索**: アーティスト・楽曲の詳細検索
- 📋 **プレイリスト管理**: 作成・編集・楽曲追加・順序変更
- 🎯 **レコメンデーション**: 気分や好みに基づく楽曲推薦
- 📊 **リスニング分析**: 再生履歴・トップアイテム・フォロー管理
- 🎵 **音楽ライブラリ整理**: 効率的なプレイリスト作成・管理

**プレミアムプランが必要なのは**、実際の楽曲再生やプレイヤーコントロール機能のみです。

## 💡 使用例

AI アシスタントから以下のように操作できます：

```
# プレイリスト作成
「リラックスできる音楽のプレイリストを作成して」

# 楽曲検索・再生
「藤井風の人気曲を検索して再生して」

# 状態確認
「今再生中の曲は何ですか？」

# レコメンデーション
「jazz っぽい音楽を推薦してください」
```

## 📋 AI インタラクションルールの活用

DJ MCP Server では、AI アシスタントとの安全で快適な対話を実現するために、専用のインタラクションルールを提供しています。

### 🔗 インタラクションルールファイル

**`docs/ai_interaction_rules.mdc`** には以下のルールが定義されています：

- **プレイリスト操作の 2 段階確認プロセス**
- **プレビュー機能の活用方法**
- **ユーザー承認フローのベストプラクティス**
- **プレイリストディスクリプションの標準化ルール**

### 🤖 AI アシスタント（Cursor）での活用手順

#### 1. ルールファイルをコンテキストに追加

AI アシスタントとの対話において、以下のようにルールファイルを参照してください：

```
@docs/ai_interaction_rules.mdc プレイリストを作成したいです
```

#### 2. 自動適用される安全機能

ルールファイルを参照することで、以下が自動的に適用されます：

- ✅ **プレビュー表示**: 作成・追加前の内容確認
- ✅ **承認待ち**: ユーザーの明示的な承認まで実行待機
- ✅ **標準化されたディスクリプション**: 統一されたプレイリスト説明
- ✅ **エラー防止**: 意図しない操作の防止

#### 3. 対話例

```bash
# ルールに従った安全な対話フロー

You: @docs/ai_interaction_rules.mdc
     チルアウトプレイリストを作成してください

AI: プレイリストを作成します。まず内容を確認いたします。
    📋 作成予定のプレイリスト内容
    • 名前: "チルアウトミックス"
    • 説明: "リラックスタイムに最適な楽曲集。DJ MCP Server for Spotifyで作成。"
    • 公開設定: プライベート
    この内容でプレイリストを作成してよろしいですか？

You: はい、作成してください

AI: ✅ プレイリストを作成しました！
```

### 💡 活用のメリット

- **🛡️ 安全性**: 意図しない操作を防止
- **👀 透明性**: 実行前に内容を確認可能
- **📝 一貫性**: 統一されたプレイリスト管理
- **🤝 ユーザビリティ**: 直感的で分かりやすい対話

### 📖 詳細ルール

完全なルールの詳細については、**`docs/ai_interaction_rules.mdc`** を参照してください。

## 🏗️ プロジェクト構造

```
dj-mcp-server-for-spotify/
├── src/                          # メインソースコード
│   ├── main.py                  # FastMCP メインアプリケーション
│   ├── auth/                    # 認証関連
│   │   └── spotify_auth.py      # Spotify OAuth2 実装
│   ├── routers/                 # API エンドポイント群
│   │   ├── authentication.py   # 認証エンドポイント
│   │   ├── playlists.py        # プレイリスト操作
│   │   ├── search.py           # 検索機能
│   │   ├── player.py           # 再生コントロール
│   │   ├── recommendations.py  # レコメンデーション
│   │   └── utility.py          # ユーティリティ
│   ├── spotify_features/        # 機能実装
│   │   ├── playlists.py        # プレイリスト管理
│   │   ├── search.py           # 検索機能
│   │   ├── player.py           # 再生制御
│   │   └── recommendations.py  # レコメンデーション
│   ├── dependencies.py         # 依存性注入
│   ├── spotify_tools.py        # Spotify ツール統合
│   └── models.py               # Pydantic モデル
├── tokens/                      # 認証トークン保存
├── cache/                       # API キャッシュ
├── docs/                        # ドキュメント
├── .env                        # 環境変数（作成要）
├── requirements.txt            # Python 依存関係
├── run_fastapi_mcp.sh         # サーバー起動スクリプト
└── README.md                  # このファイル
```

## 🔧 技術スタック

- **Python 3.11+**: 基盤プログラミング言語
- **FastAPI**: 高性能 Web API フレームワーク
- **FastMCP**: MCP プロトコル実装
- **Spotipy**: Spotify Web API Python ライブラリ
- **Pydantic**: データバリデーション・設定管理
- **Uvicorn**: ASGI サーバー

## 🧪 開発・テスト

### 手動テスト

```bash
# サーバー起動テスト
./run_fastapi_mcp.sh

# API エンドポイント確認
curl http://localhost:8000/utility/health

# MCP エンドポイント確認
curl http://localhost:8000/mcp
```

### 開発ツール

- **API ドキュメント**: `http://localhost:8000/docs`
- **Swagger UI**: `http://localhost:8000/redoc`
- **OpenAPI JSON**: `http://localhost:8000/openapi.json`

## 🔒 セキュリティと制限

### 認証・プライバシー

- **個人利用専用**: 自分の Spotify アカウントのみ操作
- **OAuth2.0**: Spotify 公式認証フロー
- **トークン管理**: ローカル暗号化保存・自動更新

### API 制限

- **レート制限**: Spotify API の制限に準拠
- **スコープ制限**: 必要最小限の権限のみ要求
- **デバイス制限**: アクティブな Spotify アプリが必要（一部機能）

## 🛠️ トラブルシューティング

### よくある問題

**1. サーバーが起動しない**

```bash
# .env ファイルの確認
ls -la .env

# 仮想環境の確認
which python
```

**2. ポート 8000 が使用中の場合**

```bash
# ERROR: [Errno 48] address already in use が発生した場合

# ポート8000を使用しているプロセスを確認
lsof -i :8000

# 表示されたプロセスのPIDを確認してkill
# 例: PID が 12345 の場合
kill -9 12345

# 複数のプロセスが表示された場合は、すべてkill
# 一括でkillする場合（注意して実行）
lsof -ti :8000 | xargs kill -9

# サーバーを再起動
./run_fastapi_mcp.sh
```

**3. MCP ツールが認識されない**

```bash
# mcp.json の設定確認
cat ~/.cursor/mcp.json

# サーバー URL の確認
curl http://localhost:8000/mcp
```

**4. 認証エラー**

```bash
# Spotify API 設定確認
echo $SPOTIFY_CLIENT_ID

# 認証状態確認
curl http://localhost:8000/auth/status
```

**5. 再生コントロールが動作しない**

- Spotify アプリ（デスクトップ・モバイル・Web Player）を起動
- デバイス一覧を確認: `curl http://localhost:8000/player/devices`

## 📈 今後の予定

- [ ] Docker Compose 対応完全化
- [ ] レコメンデーション機能の拡張
- [ ] プレイリスト画像設定機能
- [ ] バッチ処理機能（大量楽曲操作）
- [ ] 詳細な使用統計・分析機能

## 🤝 コントリビューション

個人開発プロジェクトですが、フィードバックや提案を歓迎します！

1. Issue を作成して問題・提案を報告
2. Fork してプルリクエストを送信
3. ドキュメント改善の提案

## 📄 ライセンス

MIT License - 詳細は [LICENSE](LICENSE) ファイルを参照

## 🙏 謝辞

- [Spotify Web API](https://developer.spotify.com/documentation/web-api/) - 豊富な音楽データの提供
- [FastAPI](https://fastapi.tiangolo.com) - 高性能な Web API フレームワーク
- [MCP Protocol](https://modelcontextprotocol.io) - AI アシスタント連携の標準化
- [Spotipy](https://spotipy.readthedocs.io) - Spotify API の Python ラッパー

---

**🎵 音楽と AI の融合を楽しんでください！**
