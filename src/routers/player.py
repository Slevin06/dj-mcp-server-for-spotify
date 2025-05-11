# src/routers/player.py
from fastapi import APIRouter, Depends, HTTPException, Body
from typing import List, Optional, Dict, Any
from spotipy import Spotify
from pydantic import BaseModel

from ..auth.spotify_auth import get_spotify_client
from ..main import spotify_tools_instance
from ..models import PlaybackState, Device # Pydanticモデルをインポート

router = APIRouter()

@router.get("/state", response_model=Optional[PlaybackState], operation_id="get_playback_state")
async def get_playback_state_endpoint(sp: Spotify = Depends(get_spotify_client)):
    """現在の再生状態（再生中か、シャッフルか、リピートか、音量、デバイス情報など）を取得"""
    return spotify_tools_instance.get_playback_state(sp)

@router.get("/now-playing", response_model=Optional[PlaybackState], operation_id="get_now_playing")
async def get_now_playing_endpoint(sp: Spotify = Depends(get_spotify_client)):
    """現在再生中の曲情報を取得"""
    return spotify_tools_instance.get_currently_playing_track(sp)

class PlayMusicRequest(BaseModel):
    device_id: Optional[str] = None
    context_uri: Optional[str] = None
    uris: Optional[List[str]] = None
    offset: Optional[Dict[str, Any]] = None # 例: {"position": 5} や {"uri": "spotify:track:123"}
    position_ms: Optional[int] = None

@router.put("/play", operation_id="play_music") # 03_main_application.md では spotify_tools_instance.start_resume_playback だったが、 SpotifyTools に合わせる
async def play_music_endpoint(
    request_body: PlayMusicRequest = Body(None), # リクエストボディを任意にする
    sp: Spotify = Depends(get_spotify_client)
):
    """指定されたコンテキストまたはトラックリストの再生を開始/再開"""
    # request_bodyがNoneの場合、空のdictとして扱うことで、引数なしでの再生（現在の再生を再開）に対応
    params = request_body.dict() if request_body else {}
    return spotify_tools_instance.play(sp, **params)

class PauseMusicRequest(BaseModel):
    device_id: Optional[str] = None

@router.put("/pause", operation_id="pause_music")
async def pause_music_endpoint(request_body: PauseMusicRequest = Body(None), sp: Spotify = Depends(get_spotify_client)):
    """再生を一時停止"""
    params = request_body.dict() if request_body else {}
    return spotify_tools_instance.pause(sp, **params)

class SkipToNextRequest(BaseModel):
    device_id: Optional[str] = None

@router.post("/next", operation_id="skip_to_next")
async def skip_to_next_endpoint(request_body: SkipToNextRequest = Body(None), sp: Spotify = Depends(get_spotify_client)):
    """次の曲へスキップ"""
    params = request_body.dict() if request_body else {}
    return spotify_tools_instance.next_track(sp, **params)

class SkipToPreviousRequest(BaseModel):
    device_id: Optional[str] = None

@router.post("/previous", operation_id="skip_to_previous")
async def skip_to_previous_endpoint(request_body: SkipToPreviousRequest = Body(None), sp: Spotify = Depends(get_spotify_client)):
    """前の曲へスキップ"""
    params = request_body.dict() if request_body else {}
    return spotify_tools_instance.previous_track(sp, **params)

@router.get("/devices", response_model=List[Device], operation_id="get_available_devices")
async def get_available_devices_endpoint(sp: Spotify = Depends(get_spotify_client)):
    """利用可能な再生デバイス一覧を取得"""
    return spotify_tools_instance.get_available_devices(sp)

class TransferPlaybackRequest(BaseModel):
    device_id: str
    play: Optional[bool] = False # 転送後に再生を開始するかどうか

@router.put("/transfer", operation_id="transfer_playback")
async def transfer_playback_endpoint(request_body: TransferPlaybackRequest, sp: Spotify = Depends(get_spotify_client)):
    """再生デバイスを切り替える"""
    # SpotifyToolsにtransfer_playbackメソッドがないため、spotipyのメソッドを直接呼び出すか、SpotifyToolsに実装する
    # ここでは直接呼び出す例（SpotifyToolsに実装推奨）
    try:
        sp.transfer_playback(device_id=request_body.device_id, force_play=request_body.play)
        return {"message": f"Playback transferred to device {request_body.device_id}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to transfer playback: {str(e)}")

class AddToQueueRequest(BaseModel):
    uri: str # spotify:track:TRACK_ID の形式
    device_id: Optional[str] = None

@router.post("/queue", operation_id="add_to_queue")
async def add_to_queue_endpoint(request_body: AddToQueueRequest, sp: Spotify = Depends(get_spotify_client)):
    """指定された曲を再生キューに追加する"""
    # SpotifyToolsにadd_to_queueメソッドがないため、spotipyのメソッドを直接呼び出すか、SpotifyToolsに実装する
    try:
        sp.add_to_queue(uri=request_body.uri, device_id=request_body.device_id)
        return {"message": f"Track {request_body.uri} added to queue"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add to queue: {str(e)}")

class SeekToPositionRequest(BaseModel):
    position_ms: int
    device_id: Optional[str] = None

@router.put("/seek", operation_id="seek_to_position")
async def seek_to_position_endpoint(request_body: SeekToPositionRequest, sp: Spotify = Depends(get_spotify_client)):
    """現在の曲の再生位置を変更する"""
    return spotify_tools_instance.player_manager.seek_track(sp, position_ms=request_body.position_ms, device_id=request_body.device_id)

class SetRepeatModeRequest(BaseModel):
    state: str # "track", "context", or "off"
    device_id: Optional[str] = None

@router.put("/repeat", operation_id="set_repeat_mode")
async def set_repeat_mode_endpoint(request_body: SetRepeatModeRequest, sp: Spotify = Depends(get_spotify_client)):
    """リピートモードを設定する"""
    return spotify_tools_instance.player_manager.set_repeat_mode(sp, state=request_body.state, device_id=request_body.device_id)

class SetShuffleModeRequest(BaseModel):
    state: bool
    device_id: Optional[str] = None

@router.put("/shuffle", operation_id="set_shuffle_mode")
async def set_shuffle_mode_endpoint(request_body: SetShuffleModeRequest, sp: Spotify = Depends(get_spotify_client)):
    """シャッフルモードを設定する"""
    return spotify_tools_instance.player_manager.set_shuffle(sp, state=request_body.state, device_id=request_body.device_id)

class SetVolumeRequest(BaseModel):
    volume_percent: int
    device_id: Optional[str] = None

@router.put("/volume", operation_id="set_volume")
async def set_volume_endpoint(request_body: SetVolumeRequest, sp: Spotify = Depends(get_spotify_client)):
    """音量を設定する"""
    return spotify_tools_instance.set_volume(sp, volume_percent=request_body.volume_percent, device_id=request_body.device_id) 