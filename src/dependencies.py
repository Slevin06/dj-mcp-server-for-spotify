"""
共有依存関係を管理するモジュール

循環インポートを避けるために、グローバルインスタンスをここで管理します。
"""

from .spotify_tools import SpotifyTools

# グローバルインスタンス
_spotify_tools_instance = None

def get_spotify_tools_instance() -> SpotifyTools:
    """SpotifyToolsのグローバルインスタンスを取得"""
    global _spotify_tools_instance
    if _spotify_tools_instance is None:
        _spotify_tools_instance = SpotifyTools()
    return _spotify_tools_instance

def init_spotify_tools_instance():
    """SpotifyToolsのグローバルインスタンスを初期化"""
    global _spotify_tools_instance
    _spotify_tools_instance = SpotifyTools()
    return _spotify_tools_instance 