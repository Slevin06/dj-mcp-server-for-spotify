"""
検索マネージャーモジュール

Spotify API を使った楽曲やアーティストなどの検索処理を担当するクラスを提供します。
"""

import logging
from typing import List, Dict, Any, Optional
from spotipy import Spotify, SpotifyException
from fastapi import HTTPException
from ..models import Track

# ロガーの設定
logger = logging.getLogger(__name__)


class SearchManager:
    """検索関連の操作を担当するクラス"""

    def __init__(self, cache_handler: Any):
        """SearchManagerの初期化

        Args:
            cache_handler (CacheHandler): キャッシュハンドラーインスタンス
        """
        self.cache = cache_handler

    def search_tracks(self, sp: Spotify, query: str, limit: int = 10) -> List[Track]:
        """トラックを検索

        Args:
            sp (Spotify): 認証済みのSpotifyクライアント
            query (str): 検索クエリ
            limit (int, optional): 取得する最大件数。デフォルトは10件。

        Returns:
            List[Track]: 検索結果のトラックリスト

        Raises:
            HTTPException: API呼び出しに失敗した場合
        """
        cache_key = f"search_tracks_{query}_{limit}"
        cached_data = self.cache.get_from_cache(cache_key, max_age=300)  # 5分キャッシュ
        
        if cached_data:
            logger.debug(f"キャッシュから検索結果を取得しました: {query}")
            return [Track(**item) for item in cached_data]
        
        try:
            results = sp.search(q=query, limit=limit, type='track')
            tracks_data = []
            
            for item in results['tracks']['items']:
                tracks_data.append(Track(
                    id=item['id'],
                    name=item['name'],
                    artist=item['artists'][0]['name'] if item['artists'] else "不明なアーティスト",
                    album=item['album']['name'] if item.get('album') else None
                ))
            
            # キャッシュに保存
            self.cache.save_to_cache(cache_key, [t.dict() for t in tracks_data])
            logger.debug(f"「{query}」の検索で{len(tracks_data)}件のトラックを取得しました")
            
            return tracks_data
        except SpotifyException as e:
            logger.error(f"トラック検索エラー ({query}): {e}")
            raise HTTPException(status_code=e.http_status or 500, detail=f"検索エラー: {str(e)}")
        except Exception as e:
            logger.error(f"予期せぬエラー: {e}")
            raise HTTPException(status_code=500, detail=f"予期せぬエラー: {str(e)}")

    def get_tracks_by_ids(self, sp: Spotify, track_ids: List[str]) -> List[Track]:
        """複数のトラックIDからトラック情報を一括取得

        Args:
            sp (Spotify): 認証済みのSpotifyクライアント
            track_ids (List[str]): トラックIDのリスト

        Returns:
            List[Track]: トラック情報のリスト

        Raises:
            HTTPException: API呼び出しに失敗した場合
        """
        if not track_ids:
            return []
        
        # IDのリストをソートしてキャッシュキーを作成（順序に依存しないように）
        sorted_ids = sorted(track_ids)
        cache_key = f"tracks_by_ids_{'_'.join(sorted_ids)}"
        cached_data = self.cache.get_from_cache(cache_key, max_age=3600)  # 1時間キャッシュ
        
        if cached_data:
            logger.debug(f"キャッシュから{len(cached_data)}件のトラック情報を取得しました")
            return [Track(**item) for item in cached_data]
        
        try:
            # SpotifyはAPIで一度に最大50個までのIDs取得をサポート
            MAX_TRACKS_PER_REQUEST = 50
            all_tracks = []
            
            # トラックIDを最大50個ずつの小さなバッチに分割
            for i in range(0, len(track_ids), MAX_TRACKS_PER_REQUEST):
                batch_ids = track_ids[i:i+MAX_TRACKS_PER_REQUEST]
                batch_results = sp.tracks(batch_ids)
                
                for track in batch_results['tracks']:
                    if track is not None:  # 無効なIDの場合はNoneが返される
                        all_tracks.append(Track(
                            id=track['id'],
                            name=track['name'],
                            artist=track['artists'][0]['name'] if track['artists'] else "不明なアーティスト",
                            album=track['album']['name'] if track.get('album') else None
                        ))
            
            # キャッシュに保存
            self.cache.save_to_cache(cache_key, [t.dict() for t in all_tracks])
            logger.debug(f"{len(all_tracks)}件のトラック情報を取得しました")
            
            return all_tracks
        except SpotifyException as e:
            logger.error(f"複数トラック取得エラー: {e}")
            raise HTTPException(status_code=e.http_status or 500, detail=f"トラック情報取得エラー: {str(e)}")
        except Exception as e:
            logger.error(f"予期せぬエラー: {e}")
            raise HTTPException(status_code=500, detail=f"予期せぬエラー: {str(e)}")
            
    def search_with_filters(self, sp: Spotify, track: Optional[str] = None, artist: Optional[str] = None, 
                           album: Optional[str] = None, year: Optional[str] = None, 
                           genre: Optional[str] = None, limit: int = 10) -> List[Track]:
        """フィルター付きで検索

        Args:
            sp (Spotify): 認証済みのSpotifyクライアント
            track (Optional[str], optional): トラック名。デフォルトはNone。
            artist (Optional[str], optional): アーティスト名。デフォルトはNone。
            album (Optional[str], optional): アルバム名。デフォルトはNone。
            year (Optional[str], optional): 年（例: "2021"）。デフォルトはNone。
            genre (Optional[str], optional): ジャンル。デフォルトはNone。
            limit (int, optional): 取得する最大件数。デフォルトは10件。

        Returns:
            List[Track]: 検索結果のトラックリスト

        Raises:
            HTTPException: API呼び出しに失敗した場合
        """
        # Spotifyの高度な検索構文を使用してクエリを構築
        query_parts = []
        
        if track:
            query_parts.append(f'track:"{track}"')
        if artist:
            query_parts.append(f'artist:"{artist}"')
        if album:
            query_parts.append(f'album:"{album}"')
        if year:
            query_parts.append(f'year:{year}')
        if genre:
            query_parts.append(f'genre:"{genre}"')
        
        # クエリパーツが空の場合、空のリストを返す
        if not query_parts:
            return []
        
        # 完全なクエリ文字列を構築
        query = ' '.join(query_parts)
        
        # 標準の検索関数を使用
        return self.search_tracks(sp, query, limit) 