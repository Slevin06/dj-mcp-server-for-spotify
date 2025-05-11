"""
アーティストマネージャーモジュール

アーティスト情報の検索・取得を担当するクラスを提供します。
"""

import logging
from typing import List, Dict, Any, Optional
from spotipy import Spotify, SpotifyException
from fastapi import HTTPException
from ..models import Artist, Track

# ロガーの設定
logger = logging.getLogger(__name__)


class ArtistManager:
    """アーティスト関連の操作を担当するクラス"""

    def __init__(self, cache_handler: Any):
        """ArtistManagerの初期化

        Args:
            cache_handler (CacheHandler): キャッシュハンドラーインスタンス
        """
        self.cache = cache_handler

    def search_artists(self, sp: Spotify, query: str, limit: int = 10) -> List[Artist]:
        """アーティストを検索

        Args:
            sp (Spotify): 認証済みのSpotifyクライアント
            query (str): 検索クエリ
            limit (int, optional): 取得する最大件数。デフォルトは10件。

        Returns:
            List[Artist]: 検索結果のアーティストリスト

        Raises:
            HTTPException: API呼び出しに失敗した場合
        """
        cache_key = f"search_artists_{query}_{limit}"
        cached_data = self.cache.get_from_cache(cache_key, max_age=300)  # 5分キャッシュ
        
        if cached_data:
            logger.debug(f"キャッシュからアーティスト検索結果を取得しました: {query}")
            return [Artist(**item) for item in cached_data]
        
        try:
            results = sp.search(q=query, limit=limit, type='artist')
            artists_data = []
            
            for item in results['artists']['items']:
                image_url = item['images'][0]['url'] if item['images'] else None
                artists_data.append(Artist(
                    id=item['id'],
                    name=item['name'],
                    popularity=item['popularity'],
                    genres=item['genres'],
                    image_url=image_url
                ))
            
            # キャッシュに保存
            self.cache.save_to_cache(cache_key, [a.dict() for a in artists_data])
            logger.debug(f"「{query}」の検索で{len(artists_data)}件のアーティストを取得しました")
            
            return artists_data
        except SpotifyException as e:
            logger.error(f"アーティスト検索エラー ({query}): {e}")
            raise HTTPException(status_code=e.http_status or 500, detail=f"アーティスト検索エラー: {str(e)}")
        except Exception as e:
            logger.error(f"予期せぬエラー: {e}")
            raise HTTPException(status_code=500, detail=f"予期せぬエラー: {str(e)}")

    def get_artist_info(self, sp: Spotify, artist_id: str) -> Artist:
        """アーティスト情報を取得

        Args:
            sp (Spotify): 認証済みのSpotifyクライアント
            artist_id (str): アーティストID

        Returns:
            Artist: アーティスト情報

        Raises:
            HTTPException: API呼び出しに失敗した場合
        """
        cache_key = f"artist_info_{artist_id}"
        cached_data = self.cache.get_from_cache(cache_key, max_age=86400)  # 24時間キャッシュ
        
        if cached_data:
            logger.debug(f"キャッシュからアーティスト情報を取得しました: {artist_id}")
            return Artist(**cached_data)
        
        try:
            artist = sp.artist(artist_id)
            image_url = artist['images'][0]['url'] if artist['images'] else None
            
            artist_obj = Artist(
                id=artist['id'],
                name=artist['name'],
                popularity=artist['popularity'],
                genres=artist['genres'],
                image_url=image_url
            )
            
            # キャッシュに保存
            self.cache.save_to_cache(cache_key, artist_obj.dict())
            logger.debug(f"アーティスト「{artist['name']}」の情報を取得しました")
            
            return artist_obj
        except SpotifyException as e:
            logger.error(f"アーティスト情報取得エラー ({artist_id}): {e}")
            detail = f"アーティスト情報取得エラー: {str(e)}"
            if e.http_status == 404:
                detail = "アーティストが見つかりません"
            raise HTTPException(status_code=e.http_status or 500, detail=detail)
        except Exception as e:
            logger.error(f"予期せぬエラー: {e}")
            raise HTTPException(status_code=500, detail=f"予期せぬエラー: {str(e)}")

    def get_artist_top_tracks(self, sp: Spotify, artist_id: str, country: str = "JP") -> List[Track]:
        """アーティストの人気曲を取得

        Args:
            sp (Spotify): 認証済みのSpotifyクライアント
            artist_id (str): アーティストID
            country (str, optional): 国コード（ISO 3166-1アルファ2コード）。デフォルトは"JP"。

        Returns:
            List[Track]: 人気曲のリスト

        Raises:
            HTTPException: API呼び出しに失敗した場合
        """
        cache_key = f"artist_top_tracks_{artist_id}_{country}"
        cached_data = self.cache.get_from_cache(cache_key, max_age=43200)  # 12時間キャッシュ
        
        if cached_data:
            logger.debug(f"キャッシュからアーティストの人気曲を取得しました: {artist_id}")
            return [Track(**item) for item in cached_data]
        
        try:
            results = sp.artist_top_tracks(artist_id, country=country)
            tracks_data = []
            
            for track in results['tracks']:
                tracks_data.append(Track(
                    id=track['id'],
                    name=track['name'],
                    artist=track['artists'][0]['name'] if track['artists'] else "不明なアーティスト",
                    album=track['album']['name'] if track.get('album') else None
                ))
            
            # キャッシュに保存
            self.cache.save_to_cache(cache_key, [t.dict() for t in tracks_data])
            logger.debug(f"アーティスト({artist_id})の人気曲{len(tracks_data)}件を取得しました")
            
            return tracks_data
        except SpotifyException as e:
            logger.error(f"アーティスト人気曲取得エラー ({artist_id}): {e}")
            detail = f"アーティスト人気曲取得エラー: {str(e)}"
            if e.http_status == 404:
                detail = "アーティストが見つかりません"
            raise HTTPException(status_code=e.http_status or 500, detail=detail)
        except Exception as e:
            logger.error(f"予期せぬエラー: {e}")
            raise HTTPException(status_code=500, detail=f"予期せぬエラー: {str(e)}")

    def get_related_artists(self, sp: Spotify, artist_id: str) -> List[Artist]:
        """関連アーティストを取得

        Args:
            sp (Spotify): 認証済みのSpotifyクライアント
            artist_id (str): アーティストID

        Returns:
            List[Artist]: 関連アーティストのリスト

        Raises:
            HTTPException: API呼び出しに失敗した場合
        """
        cache_key = f"related_artists_{artist_id}"
        cached_data = self.cache.get_from_cache(cache_key, max_age=86400)  # 24時間キャッシュ
        
        if cached_data:
            logger.debug(f"キャッシュから関連アーティストを取得しました: {artist_id}")
            return [Artist(**item) for item in cached_data]
        
        try:
            results = sp.artist_related_artists(artist_id)
            artists_data = []
            
            for artist in results['artists']:
                image_url = artist['images'][0]['url'] if artist['images'] else None
                artists_data.append(Artist(
                    id=artist['id'],
                    name=artist['name'],
                    popularity=artist['popularity'],
                    genres=artist['genres'],
                    image_url=image_url
                ))
            
            # キャッシュに保存
            self.cache.save_to_cache(cache_key, [a.dict() for a in artists_data])
            logger.debug(f"アーティスト({artist_id})の関連アーティスト{len(artists_data)}件を取得しました")
            
            return artists_data
        except SpotifyException as e:
            logger.error(f"関連アーティスト取得エラー ({artist_id}): {e}")
            detail = f"関連アーティスト取得エラー: {str(e)}"
            if e.http_status == 404:
                detail = "アーティストが見つかりません"
            raise HTTPException(status_code=e.http_status or 500, detail=detail)
        except Exception as e:
            logger.error(f"予期せぬエラー: {e}")
            raise HTTPException(status_code=500, detail=f"予期せぬエラー: {str(e)}") 