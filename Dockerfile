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

# プロジェクトの残りのファイルを作業ディレクトリにコピー
COPY . .

# FastAPIサーバーがリッスンするポートを外部に公開
EXPOSE 8000

# コンテナ起動時に実行されるコマンド
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"] 