"""
キャッシュ管理モジュール

認証関連のキャッシュを管理します。期限切れのキャッシュを削除し、キャッシュディレクトリを管理します。
"""

import os
import json
import time
import logging
import glob
from . import ensure_directory_exists, DEFAULT_CACHE_EXPIRY

logger = logging.getLogger(__name__)

class CacheManager:
    """認証関連のキャッシュを管理するクラス"""

    def __init__(self, cache_path=None, expiry=None):
        """CacheManagerの初期化

        Args:
            cache_path (str, optional): キャッシュを保存するディレクトリパス。
                                       指定がない場合はデフォルトパスを使用。
            expiry (int, optional): キャッシュの有効期限（秒）。
                                   指定がない場合はデフォルト値を使用。
        """
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        self.cache_path = cache_path or os.path.join(base_dir, "cache", "auth")
        self.expiry = expiry or DEFAULT_CACHE_EXPIRY
        self._ensure_cache_directory()

    def _ensure_cache_directory(self):
        """キャッシュディレクトリが存在することを確認し、なければ作成"""
        ensure_directory_exists(self.cache_path)

    def save_cache(self, key, data):
        """データをキャッシュとして保存

        Args:
            key (str): キャッシュのキー
            data: 保存するデータ（JSONシリアライズ可能なもの）
        """
        self._ensure_cache_directory()
        cache_file = os.path.join(self.cache_path, f"{key}.json")
        
        cache_data = {
            "data": data,
            "timestamp": time.time(),
            "expiry": self.expiry
        }
        
        try:
            with open(cache_file, 'w') as f:
                json.dump(cache_data, f)
            logger.debug(f"キャッシュを保存しました: {key}")
        except Exception as e:
            logger.error(f"キャッシュの保存に失敗しました ({key}): {e}")

    def get_cache(self, key):
        """キャッシュからデータを取得

        Args:
            key (str): キャッシュのキー

        Returns:
            any or None: キャッシュされたデータ。キャッシュが存在しないか期限切れの場合はNone
        """
        cache_file = os.path.join(self.cache_path, f"{key}.json")
        
        if not os.path.exists(cache_file):
            return None
        
        try:
            with open(cache_file, 'r') as f:
                cache_data = json.load(f)
            
            # 期限切れチェック
            timestamp = cache_data.get("timestamp", 0)
            expiry = cache_data.get("expiry", self.expiry)
            
            if time.time() - timestamp > expiry:
                logger.debug(f"キャッシュの期限が切れています: {key}")
                try:
                    os.remove(cache_file)
                except Exception as e:
                    logger.error(f"期限切れキャッシュの削除に失敗しました ({key}): {e}")
                return None
            
            return cache_data.get("data")
        except Exception as e:
            logger.error(f"キャッシュの読み込みに失敗しました ({key}): {e}")
            return None

    def delete_cache(self, key):
        """指定されたキーのキャッシュを削除

        Args:
            key (str): 削除するキャッシュのキー
        """
        cache_file = os.path.join(self.cache_path, f"{key}.json")
        
        if not os.path.exists(cache_file):
            return
        
        try:
            os.remove(cache_file)
            logger.debug(f"キャッシュを削除しました: {key}")
        except Exception as e:
            logger.error(f"キャッシュの削除に失敗しました ({key}): {e}")

    def clear_all_cache(self):
        """すべてのキャッシュを削除"""
        self._ensure_cache_directory()
        
        try:
            cache_files = glob.glob(os.path.join(self.cache_path, "*.json"))
            for cache_file in cache_files:
                try:
                    os.remove(cache_file)
                except Exception as e:
                    logger.error(f"キャッシュファイルの削除に失敗しました ({os.path.basename(cache_file)}): {e}")
            
            logger.info(f"{len(cache_files)}個のキャッシュファイルを削除しました")
        except Exception as e:
            logger.error(f"キャッシュクリア中にエラーが発生しました: {e}")

    def cleanup_expired_cache(self):
        """期限切れのキャッシュファイルをすべて削除"""
        self._ensure_cache_directory()
        
        try:
            cache_files = glob.glob(os.path.join(self.cache_path, "*.json"))
            expired_count = 0
            
            for cache_file in cache_files:
                try:
                    with open(cache_file, 'r') as f:
                        cache_data = json.load(f)
                    
                    timestamp = cache_data.get("timestamp", 0)
                    expiry = cache_data.get("expiry", self.expiry)
                    
                    if time.time() - timestamp > expiry:
                        os.remove(cache_file)
                        expired_count += 1
                except Exception as e:
                    logger.error(f"キャッシュファイルの処理中にエラーが発生しました ({os.path.basename(cache_file)}): {e}")
            
            if expired_count > 0:
                logger.info(f"{expired_count}個の期限切れキャッシュファイルを削除しました")
        except Exception as e:
            logger.error(f"期限切れキャッシュのクリーンアップ中にエラーが発生しました: {e}")

    def get_cache_size(self):
        """キャッシュディレクトリのサイズを取得

        Returns:
            int: キャッシュディレクトリの合計サイズ（バイト）
        """
        total_size = 0
        
        try:
            cache_files = glob.glob(os.path.join(self.cache_path, "*.json"))
            for cache_file in cache_files:
                total_size += os.path.getsize(cache_file)
        except Exception as e:
            logger.error(f"キャッシュサイズの計算中にエラーが発生しました: {e}")
        
        return total_size 