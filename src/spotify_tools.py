"""
Spotify API ファサードモジュール

Spotify API へのアクセスを提供する各フィーチャーマネージャーを呼び出すファサードとしての役割を持つクラスを提供します。
"""

from typing import List, Dict, Any, Optional

from spotipy import Spotify
from .models import (
    Playlist, Track, Artist, Device, PlaybackState,
    RecommendationTrack, RecommendationSeed, RecommendationsResponse
)

from .spotify_features.cache_handler import CacheHandler
from .spotify_features.rate_limit_handler import RateLimitHandler
from .spotify_features.playlist_manager import PlaylistManager
from .spotify_features.search_manager import SearchManager
from .spotify_features.artist_manager import ArtistManager
from .spotify_features.player_manager import PlayerManager
from .spotify_features.recommendation_manager import RecommendationManager


class SpotifyTools:
    """Spotify API へのアクセスを提供するファサードクラス"""

    def __init__(self):
        """SpotifyToolsの初期化"""
        # 共通コンポーネントをインスタンス化
        self.cache_handler = CacheHandler()
        self.rate_limit_handler = RateLimitHandler()

        # 各フィーチャーマネージャーをインスタンス化
        self.playlist_manager = PlaylistManager(cache_handler=self.cache_handler)
        self.search_manager = SearchManager(cache_handler=self.cache_handler)
        self.artist_manager = ArtistManager(cache_handler=self.cache_handler)
        self.player_manager = PlayerManager(
            cache_handler=self.cache_handler,
            rate_limit_handler=self.rate_limit_handler
        )
        # RecommendationManagerはPlaylistManagerに依存
        self.recommendation_manager = RecommendationManager(
            cache_handler=self.cache_handler,
            playlist_manager=self.playlist_manager,
            rate_limit_handler=self.rate_limit_handler
        )

    # --- プレイリスト関連メソッド（PlaylistManagerへの委譲） ---
    def get_playlists(self, sp: Spotify) -> List[Playlist]:
        """ユーザーのプレイリスト一覧を取得

        Args:
            sp (Spotify): 認証済みのSpotifyクライアント

        Returns:
            List[Playlist]: プレイリストのリスト
        """
        return self.playlist_manager.get_playlists(sp)

    def get_playlist_tracks(self, sp: Spotify, playlist_id: str, limit: int = 50, offset: int = 0) -> Dict[str, Any]:
        """プレイリスト内のトラック一覧を取得

        Args:
            sp (Spotify): 認証済みのSpotifyクライアント
            playlist_id (str): プレイリストID
            limit (int, optional): 取得する曲数の上限。デフォルト50曲。
            offset (int, optional): 取得開始位置。デフォルト0（先頭から）。

        Returns:
            Dict[str, Any]: {"tracks": List[Track], "total": int, "limit": int, "offset": int}
        """
        return self.playlist_manager.get_playlist_tracks(sp, playlist_id, limit, offset)

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
        """
        return self.playlist_manager.create_playlist(sp, user_id, name, description, public)

    def add_tracks_to_playlist(self, sp: Spotify, playlist_id: str, track_ids: List[str]) -> Dict[str, Any]:
        """プレイリストにトラックを追加

        Args:
            sp (Spotify): 認証済みのSpotifyクライアント
            playlist_id (str): プレイリストID
            track_ids (List[str]): 追加するトラックIDのリスト

        Returns:
            Dict[str, Any]: {"success": bool, "playlist": Playlist, "snapshot_id": str}
        """
        return self.playlist_manager.add_tracks_to_playlist(sp, playlist_id, track_ids)

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
        """
        return self.playlist_manager.reorder_track(sp, playlist_id, range_start, insert_before, range_length)

    # --- 検索関連メソッド（SearchManagerへの委譲） ---
    def search_tracks(self, sp: Spotify, query: str, limit: int = 10) -> List[Track]:
        """トラックを検索

        Args:
            sp (Spotify): 認証済みのSpotifyクライアント
            query (str): 検索クエリ
            limit (int, optional): 取得する最大件数。デフォルトは10件。

        Returns:
            List[Track]: 検索結果のトラックリスト
        """
        return self.search_manager.search_tracks(sp, query, limit)

    def get_tracks_by_ids(self, sp: Spotify, track_ids: List[str]) -> List[Track]:
        """複数のトラックIDからトラック情報を一括取得

        Args:
            sp (Spotify): 認証済みのSpotifyクライアント
            track_ids (List[str]): トラックIDのリスト

        Returns:
            List[Track]: トラック情報のリスト
        """
        return self.search_manager.get_tracks_by_ids(sp, track_ids)

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
        """
        return self.search_manager.search_with_filters(
            sp, track=track, artist=artist, album=album, year=year, genre=genre, limit=limit
        )

    # --- アーティスト関連メソッド（ArtistManagerへの委譲） ---
    def search_artists(self, sp: Spotify, query: str, limit: int = 10) -> List[Artist]:
        """アーティストを検索

        Args:
            sp (Spotify): 認証済みのSpotifyクライアント
            query (str): 検索クエリ
            limit (int, optional): 取得する最大件数。デフォルトは10件。

        Returns:
            List[Artist]: 検索結果のアーティストリスト
        """
        return self.artist_manager.search_artists(sp, query, limit)

    def get_artist_info(self, sp: Spotify, artist_id: str) -> Artist:
        """アーティスト情報を取得

        Args:
            sp (Spotify): 認証済みのSpotifyクライアント
            artist_id (str): アーティストID

        Returns:
            Artist: アーティスト情報
        """
        return self.artist_manager.get_artist_info(sp, artist_id)

    def get_artist_top_tracks(self, sp: Spotify, artist_id: str, country: str = "JP") -> List[Track]:
        """アーティストの人気曲を取得

        Args:
            sp (Spotify): 認証済みのSpotifyクライアント
            artist_id (str): アーティストID
            country (str, optional): 国コード（ISO 3166-1アルファ2コード）。デフォルトは"JP"。

        Returns:
            List[Track]: 人気曲のリスト
        """
        return self.artist_manager.get_artist_top_tracks(sp, artist_id, country)

    def get_related_artists(self, sp: Spotify, artist_id: str) -> List[Artist]:
        """関連アーティストを取得

        Args:
            sp (Spotify): 認証済みのSpotifyクライアント
            artist_id (str): アーティストID

        Returns:
            List[Artist]: 関連アーティストのリスト
        """
        return self.artist_manager.get_related_artists(sp, artist_id)

    # --- 再生コントロール関連メソッド（PlayerManagerへの委譲） ---
    def get_playback_state(self, sp: Spotify) -> Optional[PlaybackState]:
        """現在の包括的な再生状態を取得

        Args:
            sp (Spotify): 認証済みのSpotifyクライアント

        Returns:
            Optional[PlaybackState]: 再生状態。アクティブなデバイスがない場合はNone。
        """
        return self.player_manager.get_playback_state(sp)

    def get_currently_playing_track(self, sp: Spotify) -> Optional[PlaybackState]:
        """現在再生中の曲情報を取得

        Args:
            sp (Spotify): 認証済みのSpotifyクライアント

        Returns:
            Optional[PlaybackState]: 現在再生中の曲情報を含む再生状態。何も再生していない場合はNone。
        """
        return self.player_manager.get_currently_playing_track(sp)

    def get_available_devices(self, sp: Spotify) -> List[Device]:
        """利用可能なデバイス一覧を取得

        Args:
            sp (Spotify): 認証済みのSpotifyクライアント

        Returns:
            List[Device]: 利用可能なデバイスのリスト
        """
        return self.player_manager.get_available_devices(sp)

    def play(self, sp: Spotify, device_id: Optional[str] = None, 
             context_uri: Optional[str] = None, uris: Optional[List[str]] = None, 
             offset: Optional[Dict[str, Any]] = None, position_ms: Optional[int] = None) -> Dict[str, Any]:
        """再生を開始

        Args:
            sp (Spotify): 認証済みのSpotifyクライアント
            device_id (Optional[str], optional): デバイスID。デフォルトはNone（アクティブデバイス）。
            context_uri (Optional[str], optional): 再生するコンテキストのURI。デフォルトはNone。
            uris (Optional[List[str]], optional): 再生するトラックURIのリスト。デフォルトはNone。
            offset (Optional[Dict[str, Any]], optional): 開始位置。デフォルトはNone。
            position_ms (Optional[int], optional): 曲内の開始位置（ミリ秒）。デフォルトはNone。

        Returns:
            Dict[str, Any]: {"success": bool}
        """
        return self.player_manager.play(
            sp, device_id=device_id, context_uri=context_uri, 
            uris=uris, offset=offset, position_ms=position_ms
        )

    def pause(self, sp: Spotify, device_id: Optional[str] = None) -> Dict[str, Any]:
        """再生を一時停止

        Args:
            sp (Spotify): 認証済みのSpotifyクライアント
            device_id (Optional[str], optional): デバイスID。デフォルトはNone（アクティブデバイス）。

        Returns:
            Dict[str, Any]: {"success": bool}
        """
        return self.player_manager.pause(sp, device_id=device_id)

    def next_track(self, sp: Spotify, device_id: Optional[str] = None) -> Dict[str, Any]:
        """次の曲へ

        Args:
            sp (Spotify): 認証済みのSpotifyクライアント
            device_id (Optional[str], optional): デバイスID。デフォルトはNone（アクティブデバイス）。

        Returns:
            Dict[str, Any]: {"success": bool}
        """
        return self.player_manager.next_track(sp, device_id=device_id)

    def previous_track(self, sp: Spotify, device_id: Optional[str] = None) -> Dict[str, Any]:
        """前の曲へ

        Args:
            sp (Spotify): 認証済みのSpotifyクライアント
            device_id (Optional[str], optional): デバイスID。デフォルトはNone（アクティブデバイス）。

        Returns:
            Dict[str, Any]: {"success": bool}
        """
        return self.player_manager.previous_track(sp, device_id=device_id)

    def set_volume(self, sp: Spotify, volume_percent: int, device_id: Optional[str] = None) -> Dict[str, Any]:
        """音量を設定

        Args:
            sp (Spotify): 認証済みのSpotifyクライアント
            volume_percent (int): 音量（0～100）
            device_id (Optional[str], optional): デバイスID。デフォルトはNone（アクティブデバイス）。

        Returns:
            Dict[str, Any]: {"success": bool, "volume_percent": int}
        """
        return self.player_manager.set_volume(sp, volume_percent=volume_percent, device_id=device_id)

    # --- レコメンデーション関連メソッド（RecommendationManagerへの委譲） ---
    def get_available_genres(self, sp: Spotify) -> List[str]:
        """利用可能なジャンル（カテゴリ）の一覧を取得

        Args:
            sp (Spotify): 認証済みのSpotifyクライアント

        Returns:
            List[str]: 利用可能なジャンルのリスト
        """
        return self.recommendation_manager.get_available_genres(sp)

    def get_recommendations(self, sp: Spotify, limit: int = 20,
                          seed_artists: Optional[List[str]] = None,
                          seed_genres: Optional[List[str]] = None,
                          seed_tracks: Optional[List[str]] = None,
                          market: Optional[str] = None,
                          **kwargs: Any) -> List[Track]:
        """トラックのレコメンデーションを取得

        Args:
            sp (Spotify): 認証済みのSpotifyクライアント
            limit (int, optional): 取得する最大件数。デフォルトは20件。
            seed_artists (Optional[List[str]], optional): シードアーティストIDのリスト。デフォルトはNone。
            seed_genres (Optional[List[str]], optional): シードジャンルのリスト。デフォルトはNone。
            seed_tracks (Optional[List[str]], optional): シードトラックIDのリスト。デフォルトはNone。
            market (Optional[str], optional): マーケット（国コード）。デフォルトはNone。
            **kwargs: その他のレコメンデーションパラメータ（target_*, min_*, max_*）

        Returns:
            List[Track]: レコメンデーショントラックのリスト
        """
        return self.recommendation_manager.get_recommendations(
            sp, limit=limit, seed_artists=seed_artists, seed_genres=seed_genres,
            seed_tracks=seed_tracks, market=market, **kwargs
        )

    def get_recommendations_by_mood(self, sp: Spotify, mood: str, limit: int = 20,
                                  seed_artists: Optional[List[str]] = None,
                                  seed_genres: Optional[List[str]] = None,
                                  seed_tracks: Optional[List[str]] = None,
                                  market: Optional[str] = None,
                                  **kwargs: Any) -> List[Track]:
        """気分に基づいたレコメンデーションを取得

        Args:
            sp (Spotify): 認証済みのSpotifyクライアント
            mood (str): 気分（"happy", "sad", "energetic"など）
            limit (int, optional): 取得する最大件数。デフォルトは20件。
            seed_artists (Optional[List[str]], optional): シードアーティストIDのリスト。デフォルトはNone。
            seed_genres (Optional[List[str]], optional): シードジャンルのリスト。デフォルトはNone。
            seed_tracks (Optional[List[str]], optional): シードトラックIDのリスト。デフォルトはNone。
            market (Optional[str], optional): マーケット（国コード）。デフォルトはNone。
            **kwargs: その他のレコメンデーションパラメータ（target_*, min_*, max_*）

        Returns:
            List[Track]: レコメンデーショントラックのリスト
        """
        return self.recommendation_manager.get_recommendations_by_mood(
            sp, mood=mood, limit=limit, seed_artists=seed_artists, 
            seed_genres=seed_genres, seed_tracks=seed_tracks, market=market, **kwargs
        )

    def create_playlist_from_recommendations(self, sp: Spotify, user_id: str, name: str,
                                           description: str = "",
                                           public: bool = False,
                                           mood: Optional[str] = None,
                                           seed_artists: Optional[List[str]] = None,
                                           seed_genres: Optional[List[str]] = None,
                                           seed_tracks: Optional[List[str]] = None,
                                           limit: int = 20,
                                           market: Optional[str] = None,
                                           **kwargs: Any) -> Dict[str, Any]:
        """レコメンデーションからプレイリストを作成

        Args:
            sp (Spotify): 認証済みのSpotifyクライアント
            user_id (str): ユーザーID
            name (str): プレイリスト名
            description (str, optional): プレイリストの説明。デフォルトは空文字。
            public (bool, optional): 公開プレイリストかどうか。デフォルトはFalse（非公開）。
            mood (Optional[str], optional): 気分。デフォルトはNone。
            seed_artists (Optional[List[str]], optional): シードアーティストIDのリスト。デフォルトはNone。
            seed_genres (Optional[List[str]], optional): シードジャンルのリスト。デフォルトはNone。
            seed_tracks (Optional[List[str]], optional): シードトラックIDのリスト。デフォルトはNone。
            limit (int, optional): レコメンデーションの最大件数。デフォルトは20件。
            market (Optional[str], optional): マーケット（国コード）。デフォルトはNone。
            **kwargs: その他のレコメンデーションパラメータ（target_*, min_*, max_*）

        Returns:
            Dict[str, Any]: {"playlist": Playlist, "tracks": List[Track]}
        """
        return self.recommendation_manager.create_playlist_from_recommendations(
            sp, user_id=user_id, name=name, description=description, public=public,
            mood=mood, seed_artists=seed_artists, seed_genres=seed_genres,
            seed_tracks=seed_tracks, limit=limit, market=market, **kwargs
        )


# SpotifyTools のシングルトンインスタンス
spotify_tools = SpotifyTools() 