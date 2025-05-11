from fastapi import APIRouter, Depends, HTTPException, Body
from typing import List, Optional, Dict, Any
from spotipy import Spotify
from pydantic import BaseModel

from ..auth.spotify_auth import get_spotify_client
from ..main import spotify_tools_instance
from ..models import Track, Playlist, RecommendationsResponse # Pydanticモデルをインポート

router = APIRouter()

@router.get("/genres", response_model=List[str], operation_id="get_available_genres")
async def get_available_genres_endpoint(sp: Spotify = Depends(get_spotify_client)):
    """利用可能なレコメンデーションジャンルシードを取得する"""
    return spotify_tools_instance.get_available_genres(sp)

class RecommendationRequestBase(BaseModel):
    limit: Optional[int] = 20
    market: Optional[str] = None
    # target_*, min_*, max_* params for recommendations
    target_acousticness: Optional[float] = None
    target_danceability: Optional[float] = None
    target_duration_ms: Optional[int] = None
    target_energy: Optional[float] = None
    target_instrumentalness: Optional[float] = None
    target_key: Optional[int] = None
    target_liveness: Optional[float] = None
    target_loudness: Optional[float] = None
    target_mode: Optional[int] = None
    target_popularity: Optional[int] = None
    target_speechiness: Optional[float] = None
    target_tempo: Optional[float] = None
    target_time_signature: Optional[int] = None
    target_valence: Optional[float] = None
    min_acousticness: Optional[float] = None
    # ... Add all other min/max params as needed
    max_valence: Optional[float] = None

class GetRecommendationsBySeedRequest(RecommendationRequestBase):
    seed_artists: Optional[List[str]] = None
    seed_genres: Optional[List[str]] = None
    seed_tracks: Optional[List[str]] = None

@router.post("/by-seed", response_model=List[Track], operation_id="get_recommendations_by_seed")
async def get_recommendations_by_seed_endpoint(
    request_body: GetRecommendationsBySeedRequest, 
    sp: Spotify = Depends(get_spotify_client)
):
    """シード（アーティスト、ジャンル、トラック）に基づいてレコメンデーションを取得"""
    if not request_body.seed_artists and not request_body.seed_genres and not request_body.seed_tracks:
        raise HTTPException(status_code=400, detail="At least one seed (artists, genres, or tracks) must be provided.")
    
    return spotify_tools_instance.get_recommendations(
        sp,
        limit=request_body.limit,
        market=request_body.market,
        seed_artists=request_body.seed_artists,
        seed_genres=request_body.seed_genres,
        seed_tracks=request_body.seed_tracks,
        # **request_body.dict(exclude_none=True, exclude={'seed_artists', 'seed_genres', 'seed_tracks', 'limit', 'market'})
        # Pydantic v2では excludeの代わりに exclude_unset=True または exclude_defaults=True を使う
        **request_body.model_dump(exclude_none=True, exclude={'seed_artists', 'seed_genres', 'seed_tracks', 'limit', 'market'})
    )

class GetRecommendationsByMoodRequest(RecommendationRequestBase):
    mood: str
    seed_artists: Optional[List[str]] = None
    seed_genres: Optional[List[str]] = None
    seed_tracks: Optional[List[str]] = None

@router.post("/by-mood", response_model=List[Track], operation_id="get_recommendations_by_mood")
async def get_recommendations_by_mood_endpoint(request_body: GetRecommendationsByMoodRequest, sp: Spotify = Depends(get_spotify_client)):
    """気分に基づいてレコメンデーションを取得"""
    return spotify_tools_instance.get_recommendations_by_mood(
        sp,
        mood=request_body.mood,
        limit=request_body.limit,
        market=request_body.market,
        seed_artists=request_body.seed_artists,
        seed_genres=request_body.seed_genres,
        seed_tracks=request_body.seed_tracks,
        **request_body.model_dump(exclude_none=True, exclude={'mood', 'seed_artists', 'seed_genres', 'seed_tracks', 'limit', 'market'})
    )

class GetRecommendationsByCategoryRequest(RecommendationRequestBase):
    category_id: str # Spotify APIのジャンルシードは実際には文字列ID
    # seed_artists と seed_tracks もオプションで追加可能
    seed_artists: Optional[List[str]] = None
    seed_tracks: Optional[List[str]] = None

@router.post("/by-category", response_model=List[Track], operation_id="get_recommendations_by_category")
async def get_recommendations_by_category_endpoint(request_body: GetRecommendationsByCategoryRequest, sp: Spotify = Depends(get_spotify_client)):
    """カテゴリ（ジャンル）に基づいてレコメンデーションを取得"""
    # RecommendationManager に by_category がないので、get_recommendations を seed_genres を使って呼び出す
    return spotify_tools_instance.get_recommendations(
        sp,
        seed_genres=[request_body.category_id], # category_idをseed_genresとして渡す
        limit=request_body.limit,
        market=request_body.market,
        seed_artists=request_body.seed_artists,
        seed_tracks=request_body.seed_tracks,
        **request_body.model_dump(exclude_none=True, exclude={'category_id', 'seed_artists', 'seed_genres', 'seed_tracks', 'limit', 'market'})
    )

class GetRecommendationsByArtistRequest(RecommendationRequestBase):
    artist_id: str
    # seed_genres と seed_tracks もオプションで追加可能
    seed_genres: Optional[List[str]] = None
    seed_tracks: Optional[List[str]] = None

@router.post("/by-artist", response_model=List[Track], operation_id="get_recommendations_by_artist")
async def get_recommendations_by_artist_endpoint(request_body: GetRecommendationsByArtistRequest, sp: Spotify = Depends(get_spotify_client)):
    """アーティストに基づいてレコメンデーションを取得"""
    # RecommendationManager に by_artist がないので、get_recommendations を seed_artists を使って呼び出す
    return spotify_tools_instance.get_recommendations(
        sp,
        seed_artists=[request_body.artist_id], # artist_idをseed_artistsとして渡す
        limit=request_body.limit,
        market=request_body.market,
        seed_genres=request_body.seed_genres,
        seed_tracks=request_body.seed_tracks,
        **request_body.model_dump(exclude_none=True, exclude={'artist_id', 'seed_artists', 'seed_genres', 'seed_tracks', 'limit', 'market'})
    )

class CreatePlaylistFromRecommendationsRequest(RecommendationRequestBase):
    name: str
    description: Optional[str] = ""
    public: Optional[bool] = False
    mood: Optional[str] = None
    seed_artists: Optional[List[str]] = None
    seed_genres: Optional[List[str]] = None
    seed_tracks: Optional[List[str]] = None

class CreatePlaylistFromRecommendationsResponse(BaseModel):
    playlist: Playlist
    tracks: List[Track]

@router.post("/generate-playlist", response_model=CreatePlaylistFromRecommendationsResponse, operation_id="create_playlist_from_recommendations")
async def create_playlist_from_recommendations_endpoint(
    request_body: CreatePlaylistFromRecommendationsRequest, 
    sp: Spotify = Depends(get_spotify_client)
):
    """レコメンデーションから新しいプレイリストを作成する"""
    try:
        user_profile = sp.me()
        if not user_profile or not user_profile.get('id'):
            raise HTTPException(status_code=500, detail="ユーザーIDの取得に失敗しました")
        user_id = user_profile['id']
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"ユーザープロファイル取得エラー: {str(e)}")

    return spotify_tools_instance.create_playlist_from_recommendations(
        sp,
        user_id=user_id,
        name=request_body.name,
        description=request_body.description,
        public=request_body.public,
        mood=request_body.mood,
        seed_artists=request_body.seed_artists,
        seed_genres=request_body.seed_genres,
        seed_tracks=request_body.seed_tracks,
        limit=request_body.limit,
        market=request_body.market,
        **request_body.model_dump(exclude_none=True, exclude={
            'name', 'description', 'public', 'mood', 
            'seed_artists', 'seed_genres', 'seed_tracks', 'limit', 'market'
        })
    )

class PlayRecommendationsRequest(RecommendationRequestBase):
    # 再生に必要なシード情報
    mood: Optional[str] = None
    seed_artists: Optional[List[str]] = None
    seed_genres: Optional[List[str]] = None
    seed_tracks: Optional[List[str]] = None
    # 再生デバイスID
    device_id: Optional[str] = None

@router.post("/play", operation_id="play_recommendations")
async def play_recommendations_endpoint(request_body: PlayRecommendationsRequest, sp: Spotify = Depends(get_spotify_client)):
    """レコメンデーションされた曲を即時再生する"""
    tracks_to_play: List[Track] = []
    
    # RecommendationRequestBaseから共通パラメータを抽出
    common_params = request_body.model_dump(exclude_none=True, exclude={
        'mood', 'seed_artists', 'seed_genres', 'seed_tracks', 'device_id'
    })

    if request_body.mood:
        tracks_to_play = spotify_tools_instance.get_recommendations_by_mood(
            sp,
            mood=request_body.mood,
            seed_artists=request_body.seed_artists,
            seed_genres=request_body.seed_genres,
            seed_tracks=request_body.seed_tracks,
            **common_params
        )
    elif request_body.seed_artists or request_body.seed_genres or request_body.seed_tracks:
        tracks_to_play = spotify_tools_instance.get_recommendations(
            sp,
            seed_artists=request_body.seed_artists,
            seed_genres=request_body.seed_genres,
            seed_tracks=request_body.seed_tracks,
            **common_params
        )
    else:
        raise HTTPException(status_code=400, detail="再生のためのレコメンデーションシード（mood, artists, genres, or tracks）が必要です。")

    if not tracks_to_play:
        raise HTTPException(status_code=404, detail="レコメンデーションが見つからず、再生できませんでした。")

    track_uris = [f"spotify:track:{track.id}" for track in tracks_to_play]
    
    try:
        return spotify_tools_instance.player_manager.play(sp, uris=track_uris, device_id=request_body.device_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"レコメンデーションの再生に失敗しました: {str(e)}") 