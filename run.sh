#!/bin/bash

# 色付け用
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Pythonの確認
echo -e "${GREEN}Checking Python installation...${NC}"
if ! command -v python3 &> /dev/null
then
    echo -e "${RED}Python 3 is not installed. Please install Python 3 and try again.${NC}"
    echo "You can download it from https://www.python.org/downloads/"
    exit 1
fi
python3 --version

# uvの確認とインストール
echo -e "\n${GREEN}Checking uv installation...${NC}"
if ! command -v uv &> /dev/null
then
    echo -e "${YELLOW}uv is not installed. Attempting to install uv...${NC}"
    # uvのインストール (pipを使用)
    if python3 -m pip install uv; then
        echo -e "${GREEN}uv installed successfully via pip.${NC}"
    else
        echo -e "${RED}Failed to install uv via pip.${NC}"
        echo "Please try installing it manually: https://astral.sh/uv#installation" 
        echo "Alternatively, you can try: curl -LsSf https://astral.sh/uv/install.sh | sh" 
        exit 1
    fi
else
    echo -e "${GREEN}uv is already installed.${NC}"
fi
uv --version

# 依存関係のインストール
echo -e "\n${GREEN}Installing dependencies using uv...${NC}"
if uv pip install -r requirements.txt; then
    echo -e "${GREEN}Dependencies installed successfully.${NC}"
elif uv pip install --system -r requirements.txt; then #フォールバックとしてシステムPythonの利用を試みる
    echo -e "${GREEN}Dependencies installed successfully using system Python.${NC}"
else
    echo -e "${RED}Failed to install dependencies.${NC}"
    exit 1
fi

# .env ファイルの準備
echo -e "\n${GREEN}Checking .env file...${NC}"
if [ ! -f .env ] && [ -f .env.example ]; then
    echo -e "${YELLOW}.env file not found. Copying .env.example to .env...${NC}"
    cp .env.example .env
    echo -e "${GREEN}.env file created from .env.example.${NC}"
    echo -e "${YELLOW}Please edit the .env file to set your Spotify API credentials.${NC}"
elif [ ! -f .env ]; then
    echo -e "${RED}.env file not found and .env.example is also missing.${NC}"
    echo "Please create an .env file with your Spotify API credentials."
    exit 1
fi

# .env ファイルの必須項目確認
CLIENT_ID=$(grep SPOTIFY_CLIENT_ID .env | cut -d '=' -f2)
CLIENT_SECRET=$(grep SPOTIFY_CLIENT_SECRET .env | cut -d '=' -f2)

if [ -z "$CLIENT_ID" ] || [ "$CLIENT_ID" == "your_client_id_here" ] || [ -z "$CLIENT_SECRET" ] || [ "$CLIENT_SECRET" == "your_client_secret_here" ]; then
    echo -e "\n${RED}SPOTIFY_CLIENT_ID or SPOTIFY_CLIENT_SECRET is not set in .env file.${NC}"
    echo "Please open the .env file and set these values."
    echo "You can get them from your Spotify Developer Dashboard: https://developer.spotify.com/dashboard/"
    # エディタで.envファイルを開く選択肢 (オプション)
    # read -p "Do you want to open .env in nano to edit? (y/N): " choice
    # if [[ "$choice" =~ ^[Yy]$ ]]; then
    # nano .env
    # fi
    exit 1
else
    echo -e "${GREEN}.env file seems configured.${NC}"
fi

# アプリケーションの起動
echo -e "\n${GREEN}Starting the Spotify MCP Server...${NC}"
echo "You can access the server at http://127.0.0.1:8000"
echo "To authenticate, open your browser and go to: http://127.0.0.1:8000/auth/login"
echo "Press Ctrl+C to stop the server."

if ! uv uvicorn main:app --host 0.0.0.0 --port 8000; then
    echo -e "\n${RED}Failed to start the server with uv uvicorn.${NC}"
    echo "Trying with python -m uvicorn..."
    if ! python3 -m uvicorn main:app --host 0.0.0.0 --port 8000; then
        echo -e "\n${RED}Failed to start the server with python -m uvicorn as well.${NC}"
        echo "Please check your main.py and uvicorn installation."
        exit 1
    fi
fi 