"""
プレイリストマネージャーモジュール

プレイリスト関連の操作（取得・作成・編集など）を担当するクラスを提供します。
"""

import logging
from typing import List, Dict, Any, Optional
from spotipy import Spotify, SpotifyException
from fastapi import HTTPException
from ..models import Playlist, Track, PlaylistTrackInfo, ExternalUrls, ImageObject

# ロガーの設定
logger = logging.getLogger(__name__)


class PlaylistManager:
    """プレイリスト関連の操作を担当するクラス"""

    def __init__(self, cache_handler: Any):
        """PlaylistManagerの初期化

        Args:
            cache_handler (CacheHandler): キャッシュハンドラーインスタンス
        """
        self.cache = cache_handler

    def get_playlists(self, sp: Spotify) -> List[Playlist]:
        """ユーザーのプレイリスト一覧を取得

        Args:
            sp (Spotify): 認証済みのSpotifyクライアント

        Returns:
            List[Playlist]: プレイリストのリスト

        Raises:
            HTTPException: API呼び出しに失敗した場合
        """
        cache_key = "user_playlists"
        cached_data = self.cache.get_from_cache(cache_key, max_age=3600)  # 1時間キャッシュ
        
        if cached_data:
            logger.debug("キャッシュからプレイリスト一覧を取得しました")
            return [Playlist(**item) for item in cached_data]
        
        try:
            results = sp.current_user_playlists()
            playlists_data = []
            
            for item in results['items']:
                playlists_data.append(Playlist(
                    id=item['id'],
                    name=item['name'],
                    description=item.get('description', ''),
                    tracks=PlaylistTrackInfo(total=item['tracks']['total']),
                    external_urls=ExternalUrls(**item.get('external_urls', {})),
                    images=[ImageObject(**img) for img in item.get('images', [])] if item.get('images') else None,
                    owner=item.get('owner'),
                    public=item.get('public')
                ))
            
            # キャッシュに保存
            self.cache.save_to_cache(cache_key, [p.dict() for p in playlists_data])
            logger.debug(f"{len(playlists_data)}件のプレイリスト一覧を取得しました")
            
            return playlists_data
        except SpotifyException as e:
            logger.error(f"プレイリスト一覧取得エラー: {e}")
            raise HTTPException(status_code=e.http_status or 500, detail=f"Spotifyエラー: {str(e)}")
        except Exception as e:
            logger.error(f"予期せぬエラー: {e}")
            raise HTTPException(status_code=500, detail=f"予期せぬエラー: {str(e)}")

    def get_playlist_tracks(self, sp: Spotify, playlist_id: str, limit: int = 50, offset: int = 0) -> Dict[str, Any]:
        """プレイリスト内のトラック一覧を取得

        Args:
            sp (Spotify): 認証済みのSpotifyクライアント
            playlist_id (str): プレイリストID
            limit (int, optional): 取得する曲数の上限。デフォルト50曲。
            offset (int, optional): 取得開始位置。デフォルト0（先頭から）。

        Returns:
            Dict[str, Any]: {"tracks": List[Track], "total": int, "limit": int, "offset": int}

        Raises:
            HTTPException: API呼び出しに失敗した場合
        """
        cache_key = f"playlist_{playlist_id}_tracks_{offset}_{limit}"
        cached_data = self.cache.get_from_cache(cache_key, max_age=3600)  # 1時間キャッシュ
        
        if cached_data:
            logger.debug(f"キャッシュからプレイリスト({playlist_id})のトラック一覧を取得しました")
            cached_data["tracks"] = [Track(**t) for t in cached_data["tracks"]]
            return cached_data
        
        try:
            results = sp.playlist_items(
                playlist_id=playlist_id, limit=limit, offset=offset,
                fields="items(track(id,name,artists,album(name))),total"
            )
            
            tracks_data = []
            for item in results['items']:
                track = item.get('track')
                if track:
                    tracks_data.append(Track(
                        id=track['id'],
                        name=track['name'],
                        artist=track['artists'][0]['name'] if track['artists'] else "不明なアーティスト",
                        album=track['album']['name'] if track.get('album') else None
                    ))
            
            response_data = {
                "tracks": tracks_data,
                "total": results['total'],
                "limit": limit,
                "offset": offset
            }
            
            # キャッシュ保存用にTrackをdictに変換
            cache_save_data = response_data.copy()
            cache_save_data["tracks"] = [t.dict() for t in tracks_data]
            self.cache.save_to_cache(cache_key, cache_save_data)
            
            logger.debug(f"プレイリスト({playlist_id})から{len(tracks_data)}件のトラックを取得しました")
            return response_data
        except SpotifyException as e:
            logger.error(f"プレイリストトラック取得エラー ({playlist_id}): {e}")
            detail = f"プレイリスト取得エラー: {str(e)}"
            if e.http_status == 404:
                detail = "プレイリストが見つかりません"
            raise HTTPException(status_code=e.http_status or 500, detail=detail)
        except Exception as e:
            logger.error(f"予期せぬエラー: {e}")
            raise HTTPException(status_code=500, detail=f"予期せぬエラー: {str(e)}")

    def create_playlist(self, sp: Spotify, user_id: str, name: str, description: str = "", public: bool = False) -> Playlist:
        """プレイリストを作成

        Args:
            sp (Spotify): 認証済みのSpotifyクライアント
            user_id (str): ユーザーID
            name (str): プレイリスト名
            description (str, optional): プレイリストの説明。デフォルトは空文字。
            public (bool, optional): 公開プレイリストかどうか。デフォルトはFalse（非公開）。

        Returns:
            Playlist: 作成されたプレイリスト

        Raises:
            HTTPException: API呼び出しに失敗した場合
        """
        try:
            result = sp.user_playlist_create(
                user=user_id,
                name=name,
                public=public,
                description=description
            )
            
            # 作成後、関連キャッシュをクリア
            self.cache.clear_cache_by_key("user_playlists")
            
            logger.info(f"プレイリスト「{name}」を作成しました (ID: {result['id']})")
            
            return Playlist(
                id=result['id'],
                name=result['name'],
                description=result.get('description', ''),
                tracks=PlaylistTrackInfo(total=result.get('tracks', {}).get('total', 0)),
                external_urls=ExternalUrls(**result.get('external_urls', {})),
                images=[ImageObject(**img) for img in result.get('images', [])] if result.get('images') else None,
                owner=result.get('owner'),
                public=result.get('public')
            )
        except SpotifyException as e:
            logger.error(f"プレイリスト作成エラー: {e}")
            detail = f"プレイリスト作成エラー: {str(e)}"
            if e.http_status == 403:
                detail = "プレイリスト作成の権限がありません。"
            raise HTTPException(status_code=e.http_status or 500, detail=detail)
        except Exception as e:
            logger.error(f"予期せぬエラー: {e}")
            raise HTTPException(status_code=500, detail=f"予期せぬエラー: {str(e)}")

    def add_tracks_to_playlist(self, sp: Spotify, playlist_id: str, track_ids: List[str]) -> Dict[str, Any]:
        """プレイリストにトラックを追加

        Args:
            sp (Spotify): 認証済みのSpotifyクライアント
            playlist_id (str): プレイリストID
            track_ids (List[str]): 追加するトラックIDのリスト

        Returns:
            Dict[str, Any]: {"success": bool, "playlist": Playlist, "snapshot_id": str}

        Raises:
            HTTPException: API呼び出しに失敗した場合
        """
        try:
            # Spotify URI形式に変換
            track_uris = [f"spotify:track:{track_id}" for track_id in track_ids]
            
            # トラックを追加
            result = sp.playlist_add_items(playlist_id, track_uris)
            
            # 更新後のプレイリスト情報を取得
            playlist = sp.playlist(playlist_id)
            
            # 関連キャッシュをクリア
            self.cache.clear_cache_by_key(f"playlist_{playlist_id}_tracks_0_50")  # 基本的なキャッシュをクリア
            self.cache.clear_cache_by_key("user_playlists")  # プレイリスト一覧も更新されるため
            
            logger.info(f"プレイリスト({playlist_id})に{len(track_ids)}曲を追加しました")
            
            return {
                "success": True,
                "playlist": Playlist(
                    id=playlist['id'],
                    name=playlist['name'],
                    description=playlist.get('description', ''),
                    tracks=PlaylistTrackInfo(total=playlist['tracks']['total'] if playlist.get('tracks') else 0),
                    external_urls=ExternalUrls(**playlist.get('external_urls', {})),
                    images=[ImageObject(**img) for img in playlist.get('images', [])] if playlist.get('images') else None,
                    owner=playlist.get('owner'),
                    public=playlist.get('public')
                ).dict(),
                "snapshot_id": result['snapshot_id']
            }
        except SpotifyException as e:
            logger.error(f"プレイリストへのトラック追加エラー ({playlist_id}): {e}")
            detail = f"プレイリストへの曲追加エラー: {str(e)}"
            if e.http_status == 404:
                detail = "プレイリストまたは曲が見つかりません"
            elif e.http_status == 403:
                detail = "プレイリスト編集の権限がありません"
            raise HTTPException(status_code=e.http_status or 500, detail=detail)
        except Exception as e:
            logger.error(f"予期せぬエラー: {e}")
            raise HTTPException(status_code=500, detail=f"予期せぬエラー: {str(e)}")

    def reorder_track(self, sp: Spotify, playlist_id: str, range_start: int, insert_before: int, range_length: int = 1) -> Dict[str, Any]:
        """プレイリスト内のトラック順序を変更

        Args:
            sp (Spotify): 認証済みのSpotifyクライアント
            playlist_id (str): プレイリストID
            range_start (int): 移動する範囲の開始インデックス
            insert_before (int): この位置の前に挿入
            range_length (int, optional): 移動する範囲の長さ。デフォルトは1。

        Returns:
            Dict[str, Any]: {"success": bool, "snapshot_id": str}

        Raises:
            HTTPException: API呼び出しに失敗した場合
        """
        try:
            result = sp.playlist_reorder_items(
                playlist_id=playlist_id,
                range_start=range_start,
                insert_before=insert_before,
                range_length=range_length
            )
            
            # 関連キャッシュをクリア
            cache_key_pattern = f"playlist_{playlist_id}_tracks_"
            # 正確にはすべてのoffsetとlimitの組み合わせをクリアすべきだが、
            # パターンマッチング機能がないため簡易的に対応
            for i in range(0, 1000, 50):  # 一般的な範囲をカバー
                self.cache.clear_cache_by_key(f"{cache_key_pattern}{i}_50")
            
            logger.info(f"プレイリスト({playlist_id})のトラック順序を変更しました")
            
            return {
                "success": True,
                "snapshot_id": result["snapshot_id"]
            }
        except SpotifyException as e:
            logger.error(f"プレイリストの曲順変更エラー ({playlist_id}): {e}")
            detail = f"曲順変更エラー: {str(e)}"
            if e.http_status == 404:
                detail = "プレイリストが見つかりません"
            elif e.http_status == 403:
                detail = "プレイリスト編集の権限がありません"
            raise HTTPException(status_code=e.http_status or 500, detail=detail)
        except Exception as e:
            logger.error(f"予期せぬエラー: {e}")
            raise HTTPException(status_code=500, detail=f"予期せぬエラー: {str(e)}") 