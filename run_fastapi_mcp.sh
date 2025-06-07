#!/bin/bash

# FastApiMCP Spotify MCP Server 起動スクリプト

echo "🎵 FastApiMCP Spotify MCP Server を起動しています..."

# プロジェクトディレクトリに移動
cd "$(dirname "$0")"

# .envファイルから環境変数を読み込み
if [ -f .env ]; then
    echo "📋 環境変数を読み込み中..."
    export $(grep -v '^#' .env | xargs)
else
    echo "❌ .envファイルが見つかりません"
    exit 1
fi

# 仮想環境をアクティベート
if [ -f .venv/bin/activate ]; then
    echo "🐍 仮想環境をアクティベート中..."
    source .venv/bin/activate
else
    echo "❌ 仮想環境が見つかりません"
    exit 1
fi

# 必要な環境変数を設定
export PYTHONPATH="$(pwd)"
export FASTMCP_LOG_LEVEL="INFO"

echo "🚀 FastApiMCPサーバーを起動中..."
echo "📡 MCP Endpoint: http://localhost:8000/mcp"
echo "📖 API Docs: http://localhost:8000/docs"
echo "🔗 Swagger UI: http://localhost:8000/redoc"
echo ""

# FastApiMCPサーバーを起動
python -m src.main 