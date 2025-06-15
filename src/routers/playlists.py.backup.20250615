from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Any, Optional
from spotipy import Spotify
from pydantic import BaseModel

from ..auth.spotify_auth import get_spotify_client
from ..dependencies import get_spotify_tools_instance
from ..models import Playlist, Track

router = APIRouter()

# === 基本モデル定義 ===
class CreatePlaylistRequest(BaseModel):
    name: str
    description: Optional[str] = ""
    public: Optional[bool] = False

class AddTracksRequest(BaseModel):
    track_ids: List[str]

class AddTracksResponse(BaseModel):
    success: bool
    playlist: Playlist
    snapshot_id: str

class ReorderTrackRequest(BaseModel):
    range_start: int
    insert_before: int
    range_length: Optional[int] = 1

class ReorderTrackResponse(BaseModel):
    success: bool
    snapshot_id: str

class PlaylistTracksResponse(BaseModel):
    tracks: List[Track]
    total: int
    limit: int
    offset: int

# === プレビュー用のモデル ===
class PlaylistPreview(BaseModel):
    name: str
    description: str
    public: bool
    total_tracks: int = 0
    preview_message: str

class TracksAdditionPreview(BaseModel):
    playlist_name: str
    playlist_id: str
    tracks_to_add: List[Track]
    total_tracks_count: int
    preview_message: str

# === プレビュー用エンドポイント ===
@router.post("/preview-creation", response_model=PlaylistPreview, operation_id="preview_playlist_creation")
async def preview_playlist_creation(
    request_body: CreatePlaylistRequest,
    sp: Spotify = Depends(get_spotify_client)
):
    """
    プレイリスト作成のプレビューを表示する
    
    ⚠️ 重要: このツールは実際には作成を行いません。
    プレビュー結果を確認してユーザーが承認した場合のみ、
    create_playlist ツールを使用して実際に作成してください。
    """
    try:
        # 基本的な検証
        if not request_body.name.strip():
            raise HTTPException(status_code=400, detail="プレイリスト名は必須です")
        
        preview_message = f"""
📋 プレイリスト作成プレビュー

【作成予定の内容】
• プレイリスト名: "{request_body.name}"
• 説明: "{request_body.description or '(説明なし)'}"
• 公開設定: {"公開" if request_body.public else "非公開（自分のみ）"}
• 初期楽曲数: 0曲（空のプレイリストを作成）

❓ この内容でプレイリストを作成してよろしいですか？
承認いただける場合は「はい、作成してください」とお答えください。
"""
        
        return PlaylistPreview(
            name=request_body.name,
            description=request_body.description or "",
            public=request_body.public,
            total_tracks=0,
            preview_message=preview_message
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"プレビュー生成エラー: {str(e)}")

@router.post("/{playlist_id}/preview-tracks-addition", response_model=TracksAdditionPreview, operation_id="preview_tracks_addition")
async def preview_tracks_addition(
    playlist_id: str,
    request_body: AddTracksRequest,
    sp: Spotify = Depends(get_spotify_client)
):
    """
    プレイリストへの楽曲追加のプレビューを表示する
    
    ⚠️ 重要: このツールは実際には追加を行いません。
    プレビュー結果を確認してユーザーが承認した場合のみ、
    add_tracks_to_playlist ツールを使用して実際に追加してください。
    """
    try:
        # プレイリスト情報を取得
        playlist_info = sp.playlist(playlist_id, fields="name,tracks(total)")
        
        # 追加予定の楽曲情報を取得
        if not request_body.track_ids:
            raise HTTPException(status_code=400, detail="追加する楽曲が指定されていません")
        
        tracks_info = sp.tracks(request_body.track_ids[:50])  # 最大50曲まで
        
        tracks_to_add = []
        for track in tracks_info['tracks']:
            if track:  # Noneでない場合のみ追加
                tracks_to_add.append(Track(
                    id=track['id'],
                    name=track['name'],
                    artist=track['artists'][0]['name'] if track['artists'] else "不明なアーティスト",
                    album=track['album']['name'] if track.get('album') else None
                ))
        
        preview_message = f"""
🎵 楽曲追加プレビュー

【対象プレイリスト】
• プレイリスト名: "{playlist_info['name']}"
• 現在の楽曲数: {playlist_info['tracks']['total']}曲

【追加予定の楽曲】 ({len(tracks_to_add)}曲)
"""
        
        for i, track in enumerate(tracks_to_add[:10], 1):  # 最初の10曲まで表示
            preview_message += f"{i}. {track.name} - {track.artist}\n"
        
        if len(tracks_to_add) > 10:
            preview_message += f"...他{len(tracks_to_add) - 10}曲\n"
        
        preview_message += f"""
【追加後の楽曲数】
• 追加後の総楽曲数: {playlist_info['tracks']['total'] + len(tracks_to_add)}曲

❓ これらの楽曲をプレイリストに追加してよろしいですか？
承認いただける場合は「はい、追加してください」とお答えください。
"""
        
        return TracksAdditionPreview(
            playlist_name=playlist_info['name'],
            playlist_id=playlist_id,
            tracks_to_add=tracks_to_add,
            total_tracks_count=playlist_info['tracks']['total'] + len(tracks_to_add),
            preview_message=preview_message
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"プレビュー生成エラー: {str(e)}")

# === 既存のエンドポイント（説明文を更新） ===

@router.get("/me", response_model=List[Playlist], operation_id="get_my_playlists")
async def get_my_playlists(sp: Spotify = Depends(get_spotify_client)):
    """ユーザーのプレイリスト一覧を取得"""
    return get_spotify_tools_instance().get_playlists(sp)

@router.get("/{playlist_id}/tracks", response_model=PlaylistTracksResponse, operation_id="get_playlist_tracks")
async def get_playlist_tracks(playlist_id: str, limit: int = 50, offset: int = 0, sp: Spotify = Depends(get_spotify_client)):
    """指定されたプレイリスト内のトラック一覧を取得する"""
    return get_spotify_tools_instance().get_playlist_tracks(sp, playlist_id, limit, offset)

@router.post("", response_model=Playlist, operation_id="create_playlist")
async def create_playlist_endpoint(
    request_body: CreatePlaylistRequest,
    sp: Spotify = Depends(get_spotify_client)
):
    """
    プレイリストを新規作成
    
    ⚠️ 重要: 必ず事前に preview_playlist_creation ツールを使用して
    ユーザーに内容を確認・承認してもらってから実行してください。
    """
    try:
        user_profile = sp.me()
        if not user_profile or not user_profile.get('id'):
            raise HTTPException(status_code=500, detail="ユーザーIDの取得に失敗しました")
        user_id = user_profile['id']
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"ユーザープロファイル取得エラー: {str(e)}")

    return get_spotify_tools_instance().create_playlist(
        sp, 
        user_id=user_id, 
        name=request_body.name, 
        description=request_body.description, 
        public=request_body.public
    )

@router.post("/{playlist_id}/tracks", response_model=AddTracksResponse, operation_id="add_tracks_to_playlist")
async def add_tracks_to_playlist_endpoint(
    playlist_id: str, 
    request_body: AddTracksRequest, 
    sp: Spotify = Depends(get_spotify_client)
):
    """
    プレイリストに複数の曲を追加する
    
    ⚠️ 重要: 必ず事前に preview_tracks_addition ツールを使用して
    ユーザーに内容を確認・承認してもらってから実行してください。
    """
    return get_spotify_tools_instance().add_tracks_to_playlist(sp, playlist_id, request_body.track_ids)

@router.put("/{playlist_id}/tracks/reorder", response_model=ReorderTrackResponse, operation_id="reorder_playlist_track")
async def reorder_playlist_track_endpoint(
    playlist_id: str, 
    request_body: ReorderTrackRequest, 
    sp: Spotify = Depends(get_spotify_client)
):
    """プレイリスト内の曲順を変更する"""
    return get_spotify_tools_instance().reorder_track(
        sp, 
        playlist_id, 
        request_body.range_start, 
        request_body.insert_before, 
        request_body.range_length
    ) 