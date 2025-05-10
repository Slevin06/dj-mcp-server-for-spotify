# Dockerfile

# ベースとなる公式Pythonイメージを選択
FROM python:3.11-slim

# 環境変数を設定
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# コンテナ内の作業ディレクトリを作成・設定
WORKDIR /app

# 依存関係ファイルをコンテナにコピー
COPY requirements.txt .

# pipをアップグレードし、依存関係をインストール
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# srcディレクトリをコンテナの/app/srcにコピー
COPY src/ /app/src

# プロジェクトのルートにある他の設定ファイル等も必要に応じてコピー
# (例: .env を読み込むスクリプトがルートにある場合など)
# COPY .env .env
# COPY run_scripts/ /app/run_scripts/ # もし実行スクリプトをコンテナに入れる場合

# FastAPIサーバーがリッスンするポートを外部に公開
EXPOSE 8000

# コンテナ起動時に実行されるコマンド (src.main を指定)
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"] 