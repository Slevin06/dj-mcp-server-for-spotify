"""
キャッシュハンドラーモジュール

API レスポンスなどをキャッシュするための汎用ハンドラークラスを提供します。
"""

import os
import json
import time
import logging
from typing import Any, Optional

# ロガーの設定
logger = logging.getLogger(__name__)

# キャッシュ関連の定数
CACHE_BASE_PATH = os.getenv("CACHE_PATH", "./cache")  # .envでの設定を想定
CACHE_DIR_NAME = "spotify_api_cache"  # Spotify APIレスポンス専用のキャッシュディレクトリ名
CACHE_DIR = os.path.join(CACHE_BASE_PATH, CACHE_DIR_NAME)


class CacheHandler:
    """APIレスポンスのキャッシングを担当するクラス"""

    def __init__(self, cache_dir: str = CACHE_DIR):
        """CacheHandlerの初期化

        Args:
            cache_dir (str, optional): キャッシュディレクトリのパス。デフォルトはCACHE_DIR。
        """
        self.cache_dir = cache_dir
        self._ensure_cache_directory()

    def _ensure_cache_directory(self) -> None:
        """キャッシュディレクトリが存在することを確認し、なければ作成"""
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir, exist_ok=True)
            logger.info(f"キャッシュディレクトリを作成しました: {self.cache_dir}")

    def _get_cache_path(self, cache_key: str) -> str:
        """キャッシュキーからキャッシュファイルのパスを生成

        Args:
            cache_key (str): キャッシュキー

        Returns:
            str: キャッシュファイルのパス
        """
        # キャッシュキーに使用できない文字を置換してファイル名に適した形式にする
        safe_key = "".join([c if c.isalnum() else "_" for c in cache_key])
        return os.path.join(self.cache_dir, f"{safe_key}.json")

    def get_from_cache(self, cache_key: str, max_age: int = 3600) -> Optional[Any]:
        """キャッシュからデータを取得

        Args:
            cache_key (str): キャッシュキー
            max_age (int, optional): キャッシュの最大有効期間（秒）。デフォルトは3600秒（1時間）。

        Returns:
            Optional[Any]: キャッシュされたデータ。キャッシュが存在しないか期限切れの場合はNone。
        """
        cache_path = self._get_cache_path(cache_key)
        
        # キャッシュファイルが存在しない場合
        if not os.path.exists(cache_path):
            logger.debug(f"キャッシュが存在しません: {cache_key}")
            return None
        
        # キャッシュの有効期限をチェック
        file_time = os.path.getmtime(cache_path)
        if (time.time() - file_time) > max_age:
            logger.debug(f"キャッシュの期限が切れています: {cache_key}")
            # 期限切れのキャッシュは削除も可能
            try:
                os.remove(cache_path)
            except Exception as e:
                logger.error(f"期限切れキャッシュの削除に失敗しました ({cache_key}): {e}")
            return None
        
        # キャッシュからデータを読み込み
        try:
            with open(cache_path, 'r') as f:
                data = json.load(f)
            logger.debug(f"キャッシュからデータを読み込みました: {cache_key}")
            return data
        except Exception as e:
            logger.error(f"キャッシュの読み込みに失敗しました ({cache_key}): {e}")
            return None

    def save_to_cache(self, cache_key: str, data: Any) -> None:
        """データをキャッシュに保存

        Args:
            cache_key (str): キャッシュキー
            data (Any): 保存するデータ（JSONシリアライズ可能なもの）
        """
        self._ensure_cache_directory()
        cache_path = self._get_cache_path(cache_key)
        
        try:
            with open(cache_path, 'w') as f:
                json.dump(data, f)
            logger.debug(f"データをキャッシュに保存しました: {cache_key}")
        except Exception as e:
            logger.error(f"キャッシュの保存に失敗しました ({cache_key}): {e}")

    def clear_cache_by_key(self, cache_key: str) -> bool:
        """指定したキーのキャッシュを削除

        Args:
            cache_key (str): 削除するキャッシュのキー

        Returns:
            bool: 削除成功時はTrue、失敗時はFalse
        """
        cache_path = self._get_cache_path(cache_key)
        
        if os.path.exists(cache_path):
            try:
                os.remove(cache_path)
                logger.debug(f"キャッシュを削除しました: {cache_key}")
                return True
            except Exception as e:
                logger.error(f"キャッシュの削除に失敗しました ({cache_key}): {e}")
                return False
        
        logger.debug(f"削除対象のキャッシュが存在しません: {cache_key}")
        return False

    def clear_all_cache(self) -> None:
        """すべてのキャッシュを削除"""
        self._ensure_cache_directory()
        
        try:
            # キャッシュディレクトリ内のJSONファイルのみを削除（安全のため）
            count = 0
            for item in os.listdir(self.cache_dir):
                if item.endswith(".json"):
                    try:
                        os.remove(os.path.join(self.cache_dir, item))
                        count += 1
                    except Exception as e:
                        logger.error(f"キャッシュファイルの削除に失敗しました ({item}): {e}")
            
            logger.info(f"{count}個のキャッシュファイルを削除しました")
        except Exception as e:
            logger.error(f"全キャッシュ削除中にエラーが発生しました: {e}")

    def get_cache_size(self) -> int:
        """キャッシュディレクトリのサイズを取得

        Returns:
            int: キャッシュディレクトリの合計サイズ（バイト）
        """
        self._ensure_cache_directory()
        
        total_size = 0
        try:
            for item in os.listdir(self.cache_dir):
                if item.endswith(".json"):
                    item_path = os.path.join(self.cache_dir, item)
                    if os.path.isfile(item_path):
                        total_size += os.path.getsize(item_path)
        except Exception as e:
            logger.error(f"キャッシュサイズの計算中にエラーが発生しました: {e}")
        
        return total_size

    def cleanup_expired_cache(self, max_age: int = 3600) -> None:
        """期限切れのキャッシュファイルを削除

        Args:
            max_age (int, optional): キャッシュの最大有効期間（秒）。デフォルトは3600秒（1時間）。
        """
        self._ensure_cache_directory()
        
        try:
            now = time.time()
            count = 0
            
            for item in os.listdir(self.cache_dir):
                if item.endswith(".json"):
                    item_path = os.path.join(self.cache_dir, item)
                    if os.path.isfile(item_path):
                        file_time = os.path.getmtime(item_path)
                        if (now - file_time) > max_age:
                            try:
                                os.remove(item_path)
                                count += 1
                            except Exception as e:
                                logger.error(f"期限切れキャッシュの削除に失敗しました ({item}): {e}")
            
            if count > 0:
                logger.info(f"{count}個の期限切れキャッシュファイルを削除しました")
        except Exception as e:
            logger.error(f"期限切れキャッシュのクリーンアップ中にエラーが発生しました: {e}") 