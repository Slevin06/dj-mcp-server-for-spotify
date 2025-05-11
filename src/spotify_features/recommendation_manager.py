"""
レコメンデーションマネージャーモジュール

気分やシードに基づいてレコメンデーションを生成し、プレイリストを作成する機能などを担当するクラスを提供します。
"""

import random
import logging
from typing import List, Dict, Any, Optional
from spotipy import Spotify, SpotifyException
from fastapi import HTTPException
from ..models import Track, RecommendationSeed, RecommendationTrack, RecommendationsResponse

# ロガーの設定
logger = logging.getLogger(__name__)


class RecommendationManager:
    """レコメンデーション関連の操作を担当するクラス"""

    # 気分に基づくSpotify APIパラメータのマッピング
    MOOD_PARAMS = {
        "happy": {"target_valence": 0.8, "target_energy": 0.7, "min_danceability": 0.5},
        "sad": {"target_valence": 0.2, "max_energy": 0.5, "max_danceability": 0.5},
        "energetic": {"min_energy": 0.7, "target_tempo": 120, "target_valence": 0.7},
        "calm": {"target_energy": 0.3, "target_acousticness": 0.7, "max_tempo": 100},
        "focus": {"target_instrumentalness": 0.7, "max_speechiness": 0.3, "min_acousticness": 0.5, "target_energy": 0.3},
        "party": {"target_danceability": 0.9, "target_energy": 0.9, "min_popularity": 50},
        "relax": {"max_energy": 0.4, "target_acousticness": 0.6, "target_valence": 0.5},
        "sleep": {"max_energy": 0.2, "max_loudness": -20, "target_instrumentalness": 0.8, "target_acousticness": 0.8},
        "workout": {"min_energy": 0.7, "min_tempo": 130, "target_danceability": 0.6},
        "romantic": {"target_valence": 0.6, "target_acousticness": 0.5, "max_tempo": 120, "min_speechiness": 0.1, "max_speechiness": 0.4},
        "studying": {"target_instrumentalness": 0.6, "max_energy": 0.4, "max_valence": 0.5, "min_acousticness": 0.4},
        "upbeat": {"target_energy": 0.8, "min_tempo": 120, "target_danceability": 0.7},
        "mellow": {"target_energy": 0.4, "target_valence": 0.4, "target_acousticness": 0.6},
    }

    def __init__(self, cache_handler: Any, playlist_manager: Any, rate_limit_handler: Optional[Any] = None):
        """RecommendationManagerの初期化

        Args:
            cache_handler (CacheHandler): キャッシュハンドラーインスタンス
            playlist_manager (PlaylistManager): プレイリストマネージャーインスタンス
            rate_limit_handler (Optional[RateLimitHandler], optional): レート制限ハンドラーインスタンス。デフォルトはNone。
        """
        self.cache = cache_handler
        self.playlist_mgr = playlist_manager
        self.rate_limiter = rate_limit_handler

    def _call_spotipy_with_rate_limit(self, spotipy_method, *args, **kwargs) -> Any:
        """RateLimitHandler経由でspotipyメソッドを呼び出す共通関数

        Args:
            spotipy_method (Callable): 呼び出すspotipyのメソッド
            *args: メソッドに渡す位置引数
            **kwargs: メソッドに渡すキーワード引数

        Returns:
            Any: メソッドの実行結果

        Raises:
            HTTPException: API呼び出しに失敗した場合
        """
        if self.rate_limiter:
            return self.rate_limiter.execute_with_rate_limit(spotipy_method, *args, **kwargs)
        else:
            # レート制限ハンドラーがない場合は直接呼び出し
            try:
                return spotipy_method(*args, **kwargs)
            except SpotifyException as e:
                detail = f"Spotify API Error: {e.reason or e.msg or str(e)}"
                logger.error(f"Spotify API呼び出しエラー: {detail}")
                raise HTTPException(status_code=e.http_status or 500, detail=detail)
            except Exception as e:
                logger.error(f"予期せぬエラー: {e}")
                raise HTTPException(status_code=500, detail=f"予期せぬエラー: {str(e)}")

    def get_available_genres(self, sp: Spotify) -> List[str]:
        """利用可能なジャンル（カテゴリ）の一覧を取得

        Args:
            sp (Spotify): 認証済みのSpotifyクライアント

        Returns:
            List[str]: 利用可能なジャンルのリスト

        Raises:
            HTTPException: API呼び出しに失敗した場合
        """
        cache_key = "available_genres"
        cached_data = self.cache.get_from_cache(cache_key, max_age=86400)  # 24時間キャッシュ
        
        if cached_data:
            logger.debug("キャッシュから利用可能なジャンル一覧を取得しました")
            return cached_data
        
        try:
            genres = self._call_spotipy_with_rate_limit(sp.recommendation_genre_seeds)
            
            if not genres or not genres.get("genres"):
                logger.warning("利用可能なジャンルがありません")
                return []
            
            self.cache.save_to_cache(cache_key, genres["genres"])
            logger.debug(f"{len(genres['genres'])}件のジャンルを取得しました")
            
            return genres["genres"]
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"ジャンル取得中の予期せぬエラー: {e}")
            raise HTTPException(status_code=500, detail=f"利用可能なジャンル一覧の取得に失敗しました: {str(e)}")

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

        Raises:
            HTTPException: API呼び出しに失敗した場合
        """
        # シードが1つもない場合はエラー
        if not seed_artists and not seed_genres and not seed_tracks:
            raise HTTPException(status_code=400, detail="少なくとも1つのシード（アーティスト、ジャンル、トラック）が必要です")
        
        # シードの合計数は5つまで
        seed_count = len(seed_artists or []) + len(seed_genres or []) + len(seed_tracks or [])
        if seed_count > 5:
            raise HTTPException(status_code=400, detail="シードの合計数は5つまでです")
        
        # キャッシュキーの作成（パラメータを含めて一意になるようにする）
        cache_key_parts = [
            f"recommendations_limit_{limit}",
            f"artists_{'_'.join(sorted(seed_artists or []))}",
            f"genres_{'_'.join(sorted(seed_genres or []))}",
            f"tracks_{'_'.join(sorted(seed_tracks or []))}",
            f"market_{market or 'none'}"
        ]
        
        # 追加パラメータも含める
        for key, value in sorted(kwargs.items()):
            cache_key_parts.append(f"{key}_{value}")
        
        cache_key = "_".join(cache_key_parts)
        cached_data = self.cache.get_from_cache(cache_key, max_age=3600)  # 1時間キャッシュ
        
        if cached_data:
            logger.debug("キャッシュからレコメンデーションを取得しました")
            return [Track(**item) for item in cached_data]
        
        try:
            # レコメンデーションパラメータの準備
            recommend_kwargs = {
                "limit": limit,
                "seed_artists": seed_artists or [],
                "seed_genres": seed_genres or [],
                "seed_tracks": seed_tracks or [],
            }
            
            if market:
                recommend_kwargs["country"] = market
            
            # その他のパラメータを追加
            recommend_kwargs.update(kwargs)
            
            # レコメンデーション取得
            recommendations = self._call_spotipy_with_rate_limit(
                sp.recommendations, **recommend_kwargs
            )
            
            tracks_data = []
            
            for track in recommendations['tracks']:
                tracks_data.append(Track(
                    id=track['id'],
                    name=track['name'],
                    artist=track['artists'][0]['name'] if track['artists'] else "不明なアーティスト",
                    album=track['album']['name'] if track.get('album') else None
                ))
            
            # キャッシュに保存
            self.cache.save_to_cache(cache_key, [t.dict() for t in tracks_data])
            logger.debug(f"{len(tracks_data)}件のレコメンデーショントラックを取得しました")
            
            return tracks_data
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"レコメンデーション取得中の予期せぬエラー: {e}")
            raise HTTPException(status_code=500, detail=f"レコメンデーションの取得に失敗しました: {str(e)}")

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

        Raises:
            HTTPException: API呼び出しに失敗した場合
        """
        # 気分パラメータが存在するか確認
        if mood not in self.MOOD_PARAMS:
            available_moods = ", ".join(sorted(self.MOOD_PARAMS.keys()))
            raise HTTPException(status_code=400, detail=f"無効な気分: {mood}。有効な気分: {available_moods}")
        
        # 気分に対応するパラメータを取得し、ユーザー指定のパラメータで上書き
        mood_params = self.MOOD_PARAMS[mood].copy()
        mood_params.update(kwargs)
        
        # シードがない場合は、デフォルトでジャンルをランダムに選択
        if not seed_artists and not seed_genres and not seed_tracks:
            try:
                available_genres = self.get_available_genres(sp)
                if available_genres:
                    # 気分に合ったジャンルを設定（ここでは簡易的にランダム）
                    seed_genres = random.sample(available_genres, min(3, len(available_genres)))
            except Exception as e:
                logger.warning(f"ジャンル取得エラー（無視して続行）: {e}")
        
        # 通常のレコメンデーション取得関数を呼び出す
        return self.get_recommendations(
            sp=sp, limit=limit,
            seed_artists=seed_artists, seed_genres=seed_genres, seed_tracks=seed_tracks,
            market=market, **mood_params
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

        Raises:
            HTTPException: API呼び出しに失敗した場合
        """
        try:
            # レコメンデーションの取得
            if mood:
                tracks = self.get_recommendations_by_mood(
                    sp=sp, mood=mood, limit=limit,
                    seed_artists=seed_artists, seed_genres=seed_genres, seed_tracks=seed_tracks,
                    market=market, **kwargs
                )
            else:
                tracks = self.get_recommendations(
                    sp=sp, limit=limit,
                    seed_artists=seed_artists, seed_genres=seed_genres, seed_tracks=seed_tracks,
                    market=market, **kwargs
                )
            
            if not tracks:
                raise HTTPException(status_code=404, detail="レコメンデーションが見つかりませんでした")
            
            # プレイリストの作成
            playlist = self.playlist_mgr.create_playlist(
                sp=sp, user_id=user_id, name=name,
                description=description, public=public
            )
            
            # トラックを追加
            track_ids = [track.id for track in tracks]
            self.playlist_mgr.add_tracks_to_playlist(sp=sp, playlist_id=playlist.id, track_ids=track_ids)
            
            logger.info(f"レコメンデーションから新しいプレイリスト「{name}」を作成しました (ID: {playlist.id})")
            
            return {
                "playlist": playlist.dict(),
                "tracks": [t.dict() for t in tracks]
            }
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"レコメンデーションプレイリスト作成中の予期せぬエラー: {e}")
            raise HTTPException(status_code=500, detail=f"レコメンデーションからのプレイリスト作成に失敗しました: {str(e)}") 