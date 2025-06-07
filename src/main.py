# src/main.py
from fastapi import FastAPI
from fastapi_mcp import FastApiMCP
from dotenv import load_dotenv
from datetime import datetime # authentication router で使用

# ルーターのインポート (src/routersディレクトリから)
from .routers import authentication, playlists, search, player, recommendations, utility
# 共通モジュールのインポート (同じsrcディレクトリ内)
from .spotify_tools import SpotifyTools
from .auth.spotify_auth import spotify_auth # グローバルなspotify_authインスタンスをインポート

# 環境変数を読み込む (プロジェクトルートの .env を想定)
load_dotenv()

# FastAPIアプリケーションの初期化
app = FastAPI(
    title="DJ MCP Server for Spotify",
    description="個人用 Spotify MCP サーバー。AI アシスタントから Spotify 機能を操作するためのインターフェース",
    version="1.0.0" # __init__.py と合わせる
)

# グローバルインスタンスの生成
from .dependencies import init_spotify_tools_instance
spotify_tools_instance = init_spotify_tools_instance() 

# 各ルーターをアプリケーションに登録
# プレフィックスとタグを指定してグループ化
app.include_router(authentication.router, prefix="/auth", tags=["Authentication"])
app.include_router(playlists.router, prefix="/playlists", tags=["Playlists"])
app.include_router(search.router, prefix="/search", tags=["Search"])
app.include_router(player.router, prefix="/player", tags=["Player Control"])
app.include_router(recommendations.router, prefix="/recommendations", tags=["Recommendations"])
app.include_router(utility.router, prefix="/utility", tags=["Utility"]) # プレフィックスを /utility に変更

# 🎵 MCPサーバーの設定とマウント
# FastApiMCPは既存のFastAPIエンドポイントを自動的にMCPツールとして公開します
mcp = FastApiMCP(
    app,
    name="Spotify Assistant for DJ MCP Server", # MCPサーバー名
    description="Spotifyの各種機能をMCP経由で操作します。楽曲検索、再生制御、プレイリスト管理などが可能です。", # MCPサーバーの説明
    # 特定のタグのエンドポイントのみをMCPツールとして公開
    include_tags=["Search", "Player Control", "Playlists", "Authentication", "Utility"],
    # レスポンススキーマを詳細に含める
    describe_all_responses=True,
    describe_full_response_schema=True
)

# MCPサーバーをマウント
mcp.mount()

# 開発用にルートパスにリダイレクトを追加（任意）
from fastapi.responses import RedirectResponse
@app.get("/", include_in_schema=False)
async def root_redirect():
    return RedirectResponse(url="/docs")


if __name__ == "__main__":
    import uvicorn
    # FastApiMCPはHTTPサーバーとして動作し、MCPプロトコルを/mcpエンドポイントで提供
    uvicorn.run(app, host="0.0.0.0", port=8000) 