from fastapi import APIRouter, Depends
from typing import List, Optional
from spotipy import Spotify
from pydantic import BaseModel

from ..auth.spotify_auth import get_spotify_client
from ..dependencies import get_spotify_tools_instance
from ..models import Track, Artist

router = APIRouter()

@router.get("/tracks", response_model=List[Track], operation_id="search_tracks")
async def search_tracks_endpoint(query: str, limit: int = 10, sp: Spotify = Depends(get_spotify_client)):
    """曲を検索"""
    # limitを確実にintに変換
    limit_int = int(limit) if limit is not None else 10
    return get_spotify_tools_instance().search_tracks(sp, query, limit_int)

@router.get("/artists", response_model=List[Artist], operation_id="search_artists")
async def search_artists_endpoint(query: str, limit: int = 10, sp: Spotify = Depends(get_spotify_client)):
    """アーティストを検索する"""
    return get_spotify_tools_instance().search_artists(sp, query, limit)

@router.get("/artists/{artist_id}", response_model=Artist, operation_id="get_artist_info")
async def get_artist_info_endpoint(artist_id: str, sp: Spotify = Depends(get_spotify_client)):
    """指定されたアーティストの詳細情報を取得する"""
    return get_spotify_tools_instance().get_artist_info(sp, artist_id)

@router.get("/artists/{artist_id}/top-tracks", response_model=List[Track], operation_id="get_artist_top_tracks")
async def get_artist_top_tracks_endpoint(artist_id: str, country: Optional[str] = "JP", sp: Spotify = Depends(get_spotify_client)):
    """アーティストの人気曲を取得する"""
    return get_spotify_tools_instance().get_artist_top_tracks(sp, artist_id, country=country)

class GetMultipleTracksRequest(BaseModel):
    track_ids: List[str]

@router.post("/tracks/get-multiple", response_model=List[Track], operation_id="get_multiple_tracks")
async def get_multiple_tracks_endpoint(request_body: GetMultipleTracksRequest, sp: Spotify = Depends(get_spotify_client)):
    """複数の曲情報を一度に取得（バルク処理）"""
    return get_spotify_tools_instance().get_tracks_by_ids(sp, request_body.track_ids)



@router.get("/tracks/filter", response_model=List[Track], operation_id="search_tracks_with_filters")
async def search_tracks_with_filters_endpoint(
    track: Optional[str] = None,
    artist: Optional[str] = None,
    album: Optional[str] = None,
    year: Optional[str] = None,
    genre: Optional[str] = None,
    sp: Spotify = Depends(get_spotify_client)
):
    """フィルターを使って楽曲を検索（固定で10件取得）"""
    return get_spotify_tools_instance().search_with_filters(
        sp,
        track=track,
        artist=artist,
        album=album,
        year=year,
        genre=genre,
        limit=10  # 固定値として設定
    ) 