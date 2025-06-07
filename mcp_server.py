#!/usr/bin/env python3
"""
DJ Spotify MCP Server エントリーポイント (LEGACY版)

⚠️ 注意: この版は基本機能のみ実装されています。
現在のメインサーバーは src/main.py (FastApiMCP版) です。

Cursor や他の MCP クライアントから呼び出されるサーバー起動スクリプト
"""

import asyncio
import sys
import os
from dotenv import load_dotenv

# プロジェクトルートをPATHに追加
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# 環境変数を読み込み
load_dotenv()

def main():
    """MCP サーバーを起動"""
    try:
        # FastMCPを使ったMCPサーバーの起動
        from mcp.server import FastMCP
        
        # FastMCPサーバーを作成（専用のSpotifyツールを登録）
        server = FastMCP(name="DJ Spotify MCP Server")
        
        # Spotifyツールを登録する
        from src.auth.spotify_auth import spotify_auth
        from src.spotify_tools import SpotifyTools
        from src.dependencies import get_spotify_tools_instance
        
        spotify_tools = get_spotify_tools_instance()
        
        # 認証状態確認ツール
        @server.tool(name="get_auth_status", description="Spotify認証状態を確認")
        def get_auth_status():
            """Spotify認証状態を確認"""
            return {
                "authenticated": spotify_auth.is_authenticated(),
                "message": "認証済み" if spotify_auth.is_authenticated() else "認証が必要です"
            }
        
        # 簡単なヘルスチェックツール
        @server.tool(name="health_check", description="サーバーの動作確認")
        def health_check():
            """サーバーの動作確認"""
            return {"status": "ok", "message": "DJ Spotify MCP Server is running"}
        
        # MCPサーバーをstdio経由で実行
        server.run(transport="stdio")
        
    except ImportError as e:
        print(f"インポートエラー: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"起動エラー: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main() 