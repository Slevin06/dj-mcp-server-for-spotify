"""
トークン管理モジュール

Spotify認証トークンの読み込み、保存、削除を管理します。
"""

import os
import json
import logging
from . import ensure_directory_exists, DEFAULT_TOKEN_PATH

logger = logging.getLogger(__name__)

class TokenManager:
    """Spotify認証トークンの管理を行うクラス"""

    def __init__(self, token_path=None):
        """TokenManagerの初期化

        Args:
            token_path (str, optional): トークンを保存するディレクトリパス。
                                       指定がない場合はデフォルトパスを使用。
        """
        self.token_path = token_path or DEFAULT_TOKEN_PATH
        self.token_file = os.path.join(self.token_path, "spotify_token.json")
        self._ensure_token_directory()

    def _ensure_token_directory(self):
        """トークン保存用ディレクトリが存在することを確認し、なければ作成"""
        ensure_directory_exists(self.token_path)

    def save_token(self, token_info):
        """トークン情報をファイルに保存

        Args:
            token_info (dict): 保存するトークン情報
        """
        self._ensure_token_directory()
        
        try:
            with open(self.token_file, 'w') as f:
                json.dump(token_info, f)
            logger.info("トークンを保存しました")
        except Exception as e:
            logger.error(f"トークンの保存に失敗しました: {e}")
            raise

    def load_token(self):
        """保存されたトークン情報を読み込む

        Returns:
            dict or None: トークン情報。ファイルが存在しない場合はNone
        """
        if not os.path.exists(self.token_file):
            logger.info("トークンファイルが存在しません")
            return None
        
        # ディレクトリではなくファイルかチェック
        if os.path.isdir(self.token_file):
            logger.warning(f"トークンパスがディレクトリです: {self.token_file}")
            return None
        
        try:
            with open(self.token_file, 'r') as f:
                token_info = json.load(f)
            logger.info("トークンを読み込みました")
            return token_info
        except Exception as e:
            logger.error(f"トークンの読み込みに失敗しました: {e}")
            return None

    def delete_token(self):
        """トークンファイルを削除"""
        if not os.path.exists(self.token_file):
            logger.info("削除対象のトークンファイルが存在しません")
            return
        
        try:
            os.remove(self.token_file)
            logger.info("トークンファイルを削除しました")
        except Exception as e:
            logger.error(f"トークンファイルの削除に失敗しました: {e}")
            raise

    def token_exists(self):
        """トークンファイルが存在するか確認

        Returns:
            bool: トークンファイルが存在する場合はTrue
        """
        return os.path.exists(self.token_file) 