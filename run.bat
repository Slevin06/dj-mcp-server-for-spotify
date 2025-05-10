@echo off
setlocal

REM Pythonの確認
echo Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo Python is not installed or not in PATH. Please install Python and try again.
    echo You can download it from https://www.python.org/downloads/
    pause
    exit /b 1
)
python --version

REM uvの確認とインストール
echo.
echo Checking uv installation...
uv --version >nul 2>&1
if errorlevel 1 (
    echo uv is not installed. Attempting to install uv...
    python -m pip install uv
    if errorlevel 1 (
        echo Failed to install uv via pip.
        echo Please try installing it manually: https://astral.sh/uv#installation
        pause
        exit /b 1
    )
    echo uv installed successfully via pip.
) else (
    echo uv is already installed.
)
uv --version

REM 依存関係のインストール
echo.
echo Installing dependencies using uv...
uv pip install -r requirements.txt
if errorlevel 1 (
    echo Failed to install dependencies.
    pause
    exit /b 1
)
echo Dependencies installed successfully.

REM .env ファイルの準備
echo.
echo Checking .env file...
if not exist .env (
    if exist .env.example (
        echo .env file not found. Copying .env.example to .env...
        copy .env.example .env >nul
        echo .env file created from .env.example.
        echo Please edit the .env file to set your Spotify API credentials.
    ) else (
        echo .env file not found and .env.example is also missing.
        echo Please create an .env file with your Spotify API credentials.
        pause
        exit /b 1
    )
)

REM .env ファイルの必須項目確認 (簡易的なチェック)
REM findstr は空行や不完全な行もヒットする可能性があるため、より堅牢なチェックは複雑になります。
REM ここではユーザーに確認を促す程度とします。
findstr /C:"SPOTIFY_CLIENT_ID=your_client_id_here" .env >nul
if not errorlevel 1 (
    echo.
    echo WARNING: SPOTIFY_CLIENT_ID might not be set in .env file (found default value).
    echo Please open the .env file and set your Spotify API credentials.
    echo You can get them from your Spotify Developer Dashboard: https://developer.spotify.com/dashboard/
    pause
    exit /b 1
)
findstr /C:"SPOTIFY_CLIENT_SECRET=your_client_secret_here" .env >nul
if not errorlevel 1 (
    echo.
    echo WARNING: SPOTIFY_CLIENT_SECRET might not be set in .env file (found default value).
    echo Please open the .env file and set your Spotify API credentials.
    echo You can get them from your Spotify Developer Dashboard: https://developer.spotify.com/dashboard/
    pause
    exit /b 1
)
echo .env file seems configured.

REM アプリケーションの起動
echo.
echo Starting the Spotify MCP Server...
echo You can access the server at http://127.0.0.1:8000
echo To authenticate, open your browser and go to: http://127.0.0.1:8000/auth/login
echo Press Ctrl+C in this window to stop the server.

uv uvicorn main:app --host 0.0.0.0 --port 8000
if errorlevel 1 (
    echo.
    echo Failed to start the server with uv uvicorn.
    echo Trying with python -m uvicorn...
    python -m uvicorn main:app --host 0.0.0.0 --port 8000
    if errorlevel 1 (
        echo.
        echo Failed to start the server with python -m uvicorn as well.
        echo Please check your main.py and uvicorn installation.
        pause
        exit /b 1
    )
)

endlocal 