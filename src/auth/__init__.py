"""
認証関連モジュール

このパッケージには、Spotify認証処理に関連するクラスとユーティリティが含まれています。
- SpotifyAuth: 認証フローの中核となるクラス
- TokenManager: トークンの保存・読み込み・削除を管理するクラス
- CacheManager: 認証関連キャッシュを管理するクラス
"""

import os
import logging

# ロガーの設定
logger = logging.getLogger(__name__)

# 定数
DEFAULT_TOKEN_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "tokens")
DEFAULT_CACHE_EXPIRY = 3600  # キャッシュのデフォルト有効期限（秒）

# ヘルパー関数
def ensure_directory_exists(directory_path):
    """指定されたディレクトリが存在しない場合は作成する

    Args:
        directory_path (str): 作成するディレクトリのパス
    """
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)
        logger.info(f"ディレクトリを作成しました: {directory_path}")

# クラスのインポート（循環インポートを避けるためにファイルの最後に配置）
from .token_manager import TokenManager
from .cache_manager import CacheManager
from .spotify_auth import SpotifyAuth

__all__ = ["TokenManager", "CacheManager", "SpotifyAuth"] 