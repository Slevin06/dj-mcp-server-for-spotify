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
spotify_tools_instance = SpotifyTools() 

# MCPサーバーの設定
mcp = FastApiMCP(
    app,
    name="Spotify Assistant for DJ MCP Server", # MCPサーバー名を修正
    description="Spotifyの各種機能をMCP経由で操作します。", # MCPサーバーの説明を追加
    prefix="/mcp", # MCPサーバーのエンドポイントプレフィックス
    include_model_validation_error_detail=True, # バリデーションエラー詳細を含める
    # describe_full_response_schema=True # デフォルトTrueなので明示不要の場合も
)

# 各ルーターをアプリケーションに登録
# プレフィックスとタグを指定してグループ化
app.include_router(authentication.router, prefix="/auth", tags=["Authentication"])
app.include_router(playlists.router, prefix="/playlists", tags=["Playlists"])
app.include_router(search.router, prefix="/search", tags=["Search"])
app.include_router(player.router, prefix="/player", tags=["Player Control"])
app.include_router(recommendations.router, prefix="/recommendations", tags=["Recommendations"])
app.include_router(utility.router, prefix="/utility", tags=["Utility"]) # プレフィックスを /utility に変更

# MCPサーバーをマウント
mcp.mount()

# 開発用にルートパスにリダイレクトを追加（任意）
from fastapi.responses import RedirectResponse
@app.get("/", include_in_schema=False)
async def root_redirect():
    return RedirectResponse(url="/docs")


if __name__ == "__main__":
    import uvicorn
    # SSL証明書とキーのパス (自己署名証明書の場合)
    # ssl_keyfile = "./certs/key.pem"
    # ssl_certfile = "./certs/cert.pem"

    # uvicorn.run(
    # app,
    # host="0.0.0.0",
    # port=8000,
    # ssl_keyfile=ssl_keyfile if os.path.exists(ssl_keyfile) else None,
    # ssl_certfile=ssl_certfile if os.path.exists(ssl_certfile) else None
    # )
    uvicorn.run(app, host="0.0.0.0", port=8000) 