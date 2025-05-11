from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Any, Optional
from spotipy import Spotify
from pydantic import BaseModel

from ..auth.spotify_auth import get_spotify_client
from ..main import spotify_tools_instance
from ..models import Playlist, Track

router = APIRouter()

@router.get("/me", response_model=List[Playlist], operation_id="get_my_playlists")
async def get_my_playlists(sp: Spotify = Depends(get_spotify_client)):
    """ユーザーのプレイリスト一覧を取得"""
    return spotify_tools_instance.get_playlists(sp)

class PlaylistTracksResponse(BaseModel):
    tracks: List[Track]
    total: int
    limit: int
    offset: int

@router.get("/{playlist_id}/tracks", response_model=PlaylistTracksResponse, operation_id="get_playlist_tracks")
async def get_playlist_tracks(playlist_id: str, limit: int = 50, offset: int = 0, sp: Spotify = Depends(get_spotify_client)):
    """指定されたプレイリスト内のトラック一覧を取得する"""
    return spotify_tools_instance.get_playlist_tracks(sp, playlist_id, limit, offset)

class CreatePlaylistRequest(BaseModel):
    name: str
    description: Optional[str] = ""
    public: Optional[bool] = False

@router.post("", response_model=Playlist, operation_id="create_playlist")
async def create_playlist_endpoint(
    request_body: CreatePlaylistRequest,
    sp: Spotify = Depends(get_spotify_client)
):
    """プレイリストを新規作成"""
    try:
        user_profile = sp.me()
        if not user_profile or not user_profile.get('id'):
            raise HTTPException(status_code=500, detail="ユーザーIDの取得に失敗しました")
        user_id = user_profile['id']
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"ユーザープロファイル取得エラー: {str(e)}")

    return spotify_tools_instance.create_playlist(
        sp, 
        user_id=user_id, 
        name=request_body.name, 
        description=request_body.description, 
        public=request_body.public
    )

class AddTracksRequest(BaseModel):
    track_ids: List[str]

class AddTracksResponse(BaseModel):
    success: bool
    playlist: Playlist
    snapshot_id: str

@router.post("/{playlist_id}/tracks", response_model=AddTracksResponse, operation_id="add_tracks_to_playlist")
async def add_tracks_to_playlist_endpoint(
    playlist_id: str, 
    request_body: AddTracksRequest, 
    sp: Spotify = Depends(get_spotify_client)
):
    """プレイリストに複数の曲を追加する"""
    return spotify_tools_instance.add_tracks_to_playlist(sp, playlist_id, request_body.track_ids)

class ReorderTrackRequest(BaseModel):
    range_start: int
    insert_before: int
    range_length: Optional[int] = 1

class ReorderTrackResponse(BaseModel):
    success: bool
    snapshot_id: str

@router.put("/{playlist_id}/tracks/reorder", response_model=ReorderTrackResponse, operation_id="reorder_playlist_track")
async def reorder_playlist_track_endpoint(
    playlist_id: str, 
    request_body: ReorderTrackRequest, 
    sp: Spotify = Depends(get_spotify_client)
):
    """プレイリスト内の曲順を変更する"""
    return spotify_tools_instance.reorder_track(
        sp, 
        playlist_id, 
        request_body.range_start, 
        request_body.insert_before, 
        request_body.range_length
    ) 