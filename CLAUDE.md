# CLAUDE.md

このファイルは、Claude Code (claude.ai/code) がこのリポジトリでコードを扱う際のガイダンスを提供します。

## 開発コマンド

### サーバー管理
- **FastMCPサーバー起動**: `./run_fastapi_mcp.sh`
- **代替起動方法**: `python -m src.main`
- **サーバーヘルスチェック**: `curl http://localhost:8000/utility/health`
- **APIドキュメント表示**: `http://localhost:8000/docs`

### 環境セットアップ
```bash
# 仮想環境を作成
python -m venv .venv
source .venv/bin/activate  # macOS/Linux

# 依存関係をインストール
pip install -r requirements.txt

# .envファイルに必要な環境変数:
SPOTIFY_CLIENT_ID=your_client_id_here
SPOTIFY_CLIENT_SECRET=your_client_secret_here  
SPOTIFY_REDIRECT_URI=http://127.0.0.1:8000/auth/callback
```

### テスト
- **手動APIテスト**: `curl http://localhost:8000/mcp`
- **ヘルスチェック**: `curl http://localhost:8000/utility/health`
- **認証テスト**: `curl http://localhost:8000/auth/status`
- **検索機能テスト**: `curl "http://localhost:8000/search/tracks?query=test"`

### 開発・デバッグ
- **ポート8000で実行中のプロセス確認**: `lsof -i :8000`
- **ポート8000使用プロセス強制終了**: `lsof -ti :8000 | xargs kill -9`
- **サーバーログ確認**: `./run_fastapi_mcp.sh`のターミナル出力を確認

## アーキテクチャ概要

### コアフレームワーク
- **FastAPI + FastMCP**: FastAPIエンドポイントを自動的にMCPツールに変換するHTTPベースのMCPプロトコルサーバー
- **Spotify Web API**: spotipyライブラリを使用したOAuth2.0認証
- **Pydanticモデル**: 全体を通じた型安全なデータ検証

### 主要コンポーネント

#### 1. アプリケーションエントリーポイント (`src/main.py`)
- FastMCPと統合したFastAPIアプリの初期化
- 組織化されたプレフィックス（`/auth`, `/playlists`, `/search`, `/player`, `/recommendations`, `/utility`）でのルーター登録
- `/mcp`エンドポイントでのMCPサーバーマウント
- グローバルSpotifyToolsインスタンス管理

#### 2. 依存性注入 (`src/dependencies.py`)
- 循環インポートを防ぐためのSpotifyToolsインスタンス用シングルトンパターン
- グローバル状態管理用の`get_spotify_tools_instance()`と`init_spotify_tools_instance()`

#### 3. ファサードパターン (`src/spotify_tools.py`)
- SpotifyToolsクラスがSpotify機能すべてに対する統一インターフェースとして機能
- `src/spotify_features/`内の専門化された機能マネージャーに委譲
- 共通のキャッシュとレート制限を一元管理

#### 4. 機能マネージャー (`src/spotify_features/`)
- **PlaylistManager**: 2段階確認付きCRUD操作（プレビュー → 実行）  
- **SearchManager**: キャッシュとフィルタリング機能付きトラック・アーティスト検索
- **PlayerManager**: 再生制御（ほとんどの操作でプレミアムプラン必須）
- **RecommendationManager**: AI対応音楽レコメンデーション
- **ArtistManager**: アーティスト情報と関連データ  
- **CacheHandler**: ファイルシステムベースのAPIレスポンスキャッシュ
- **RateLimitHandler**: Spotify APIレート制限管理

#### 5. ルーター構成 (`src/routers/`)
各ルーターは一貫したエラーハンドリングとPydantic検証を用いて特定のドメインロジックを処理します。

### 認証フロー
1. `/auth/login` → Spotify OAuth2.0リダイレクト
2. `/auth/callback` → トークン交換と`tokens/spotify_token.json`への保存
3. `src/auth/spotify_auth.py`が自動更新付きでトークンライフサイクルを管理

### AI安全機能
- **2段階確認**: すべての破壊的操作（プレイリスト作成、トラック追加）でプレビュー → 承認ワークフローが必要
- **プレイリスト説明の標準化**: 自動的に「DJ MCP Server for Spotifyで作成。」サフィックスを追加
- 完全なAIインタラクションガイドラインは`docs/ai_interaction_rules.mdc`を参照

### Spotifyプランの制限
- **フリープラン**: すべての読み取り操作、プレイリスト管理、検索、レコメンデーション
- **プレミアムプラン必須**: 実際の再生制御（再生/一時停止/スキップ/音量調整）

## 重要な開発ノート

### エラーハンドリング
- Spotify APIエラーは説明的なメッセージでラップされます
- HTTP 403エラーはプレミアムプラン要件を示します
- レート制限は指数バックオフで自動処理されます

### キャッシュ管理
- APIレスポンスは`cache/spotify_api_cache/`にキャッシュされます
- 効率的な検索のため、操作+パラメータベースのキャッシュキーを使用
- 認証トークンは`cache/auth/`に別途キャッシュされます

### ファイル構成パターン
- `src/`パッケージ内ではすべて相対インポートを使用
- ルーターメソッドは一貫した命名規則に従います: `{operation}_{resource}`
- 型安全性のためPydanticモデルを`src/models.py`に配置
- 機能マネージャーがビジネスロジックをカプセル化し、ルーターがHTTP関連事項を処理

### MCP統合
- FastMCPがFastAPIエンドポイントを自動的にMCPツールとして公開
- ツールの説明はFastAPIエンドポイントのdocstringから派生
- AIアシスタントのコンテキスト用にレスポンススキーマを含む

## Spotifyプランの要件と制限

### フリープランで利用可能な機能
- すべての検索操作（トラック、アーティスト、アルバム）
- プレイリスト管理（作成、表示、編集、並び替え）
- ユーザープロファイルと再生履歴
- レコメンデーションとジャンル情報
- アーティスト詳細とトップトラック
- 認証とトークン管理

### プレミアムプラン必須機能
- **再生制御**: 再生、一時停止、スキップ、シーク、音量制御
- **デバイス管理**: デバイス間での再生転送
- **キュー操作**: 再生キューへのトラック追加
- **シャッフル/リピート**: 再生モード制御

### 一般的なエラーパターン
- **フリープランでのHTTP 403**: `この操作を実行する権限がありません`
- **プレミアム必須エラー**: `Player command failed: Premium required, reason: PREMIUM_REQUIRED`

## よくある問題のトラブルシューティング

### ポート8000がすでに使用中
```bash
# ポート8000を使用しているプロセスを検索・強制終了
lsof -i :8000
lsof -ti :8000 | xargs kill -9
```

### 認証問題
- `.env`ファイルに有効なSpotify API認証情報が含まれているか確認
- リダイレクトURIがSpotifyアプリ設定と一致するか確認: `http://127.0.0.1:8000/auth/callback`
- 認証状態テスト: `curl http://localhost:8000/auth/status`
- 再認証: `http://localhost:8000/auth/login`にアクセス

### キャッシュ問題
- APIレスポンスは`cache/spotify_api_cache/`にキャッシュされます
- 認証トークンは`cache/auth/`にキャッシュされます
- 必要に応じてキャッシュディレクトリを削除してキャッシュをクリア