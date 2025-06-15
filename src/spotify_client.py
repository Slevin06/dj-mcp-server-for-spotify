"""
Spotify クライアントのシンプルなファクトリー

従来のdependencies.pyの代替として、よりシンプルなアプローチを提供します。
"""
from functools import lru_cache
from .spotify_tools import SpotifyTools

@lru_cache(maxsize=1)
def get_spotify_tools() -> SpotifyTools:
    """
    SpotifyToolsインスタンスを取得
    
    LRUキャッシュにより、同一インスタンスを再利用します。
    
    Returns:
        SpotifyTools: Spotify機能の統合インターフェース
    """
    return SpotifyTools()

# 既存コードとの互換性のための別名
get_spotify_tools_instance = get_spotify_tools

def clear_spotify_tools_cache():
    """
    キャッシュをクリアして新しいインスタンスを強制作成
    主にテスト用途で使用します。
    """
    get_spotify_tools.cache_clear()