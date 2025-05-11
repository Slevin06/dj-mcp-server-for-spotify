"""
Spotify API機能を提供する各マネージャークラス群のパッケージ

このパッケージには、以下のマネージャークラスが含まれています：
- CacheHandler: APIレスポンスのキャッシングを担当
- RateLimitHandler: APIリクエストの頻度制限対策
- PlaylistManager: プレイリスト関連の操作
- SearchManager: 検索関連の操作
- ArtistManager: アーティスト関連の操作
- PlayerManager: 再生コントロール関連の操作
- RecommendationManager: レコメンデーション関連の操作
"""

__all__ = [
    "CacheHandler",
    "RateLimitHandler",
    "PlaylistManager",
    "SearchManager",
    "ArtistManager",
    "PlayerManager",
    "RecommendationManager",
] 