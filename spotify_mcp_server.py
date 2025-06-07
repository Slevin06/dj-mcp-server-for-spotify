#!/usr/bin/env python3
"""
Spotify MCP Server using FastMCP
"""

from fastmcp import FastMCP
from dotenv import load_dotenv
import os
from typing import Optional, List, Dict, Any

# 環境変数読み込み
load_dotenv()

# FastMCP サーバーインスタンス作成
mcp = FastMCP("Spotify DJ Assistant")

# Spotify関連のインポート
try:
    from src.auth.spotify_auth import spotify_auth
    from src.dependencies import init_spotify_tools_instance
    spotify_tools_instance = init_spotify_tools_instance()
except ImportError as e:
    print(f"Spotifyモジュールのインポートエラー: {e}")
    spotify_tools_instance = None

def get_spotify_client():
    """Spotify認証済みクライアントを取得"""
    if not spotify_tools_instance:
        return None
    return spotify_auth.get_client()

# 🎵 Spotify MCP ツール定義

@mcp.tool()
def search_tracks(query: str, limit: int = 10) -> Dict[str, Any]:
    """Spotifyで楽曲を検索します
    
    Args:
        query: 検索クエリ（アーティスト名、楽曲名など）
        limit: 取得する最大件数（デフォルト: 10）
    
    Returns:
        検索結果のトラックリスト
    """
    try:
        sp = get_spotify_client()
        if not sp:
            return {"error": "Spotify認証が必要です"}
        
        tracks = spotify_tools_instance.search_tracks(sp, query, limit)
        return {
            "success": True,
            "tracks": [
                {
                    "id": track.id,
                    "name": track.name,
                    "artist": track.artist,
                    "album": track.album,
                    "uri": track.uri,
                    "preview_url": track.preview_url
                }
                for track in tracks
            ]
        }
    except Exception as e:
        return {"error": f"検索中にエラーが発生しました: {str(e)}"}

@mcp.tool()
def play_track(track_id: str, device_id: Optional[str] = None) -> Dict[str, Any]:
    """指定したトラックを再生します
    
    Args:
        track_id: 再生するトラックのSpotify ID
        device_id: 再生デバイスID（省略可）
    
    Returns:
        再生開始の結果
    """
    try:
        sp = get_spotify_client()
        if not sp:
            return {"error": "Spotify認証が必要です"}
        
        track_uri = f"spotify:track:{track_id}"
        result = spotify_tools_instance.play(sp, uris=[track_uri], device_id=device_id)
        return {"success": True, "message": "再生を開始しました", "result": result}
    except Exception as e:
        return {"error": f"再生中にエラーが発生しました: {str(e)}"}

@mcp.tool()
def get_current_playing() -> Dict[str, Any]:
    """現在再生中の楽曲情報を取得します
    
    Returns:
        現在再生中の楽曲情報またはnull
    """
    try:
        sp = get_spotify_client()
        if not sp:
            return {"error": "Spotify認証が必要です"}
        
        playback_state = spotify_tools_instance.get_currently_playing_track(sp)
        if playback_state:
            return {
                "success": True,
                "is_playing": playback_state.is_playing,
                "track": {
                    "id": playback_state.track.id if playback_state.track else None,
                    "name": playback_state.track.name if playback_state.track else None,
                    "artist": playback_state.track.artist if playback_state.track else None,
                    "album": playback_state.track.album if playback_state.track else None
                },
                "device": {
                    "id": playback_state.device.id if playback_state.device else None,
                    "name": playback_state.device.name if playback_state.device else None
                } if playback_state.device else None
            }
        return {"success": True, "is_playing": False, "track": None}
    except Exception as e:
        return {"error": f"再生状態の取得中にエラーが発生しました: {str(e)}"}

@mcp.tool()
def pause_playback(device_id: Optional[str] = None) -> Dict[str, Any]:
    """再生を一時停止します
    
    Args:
        device_id: 対象デバイスID（省略可）
    
    Returns:
        一時停止の結果
    """
    try:
        sp = get_spotify_client()
        if not sp:
            return {"error": "Spotify認証が必要です"}
        
        result = spotify_tools_instance.pause(sp, device_id=device_id)
        return {"success": True, "message": "再生を一時停止しました", "result": result}
    except Exception as e:
        return {"error": f"一時停止中にエラーが発生しました: {str(e)}"}

@mcp.tool()
def next_track(device_id: Optional[str] = None) -> Dict[str, Any]:
    """次の楽曲にスキップします
    
    Args:
        device_id: 対象デバイスID（省略可）
    
    Returns:
        スキップの結果
    """
    try:
        sp = get_spotify_client()
        if not sp:
            return {"error": "Spotify認証が必要です"}
        
        result = spotify_tools_instance.next_track(sp, device_id=device_id)
        return {"success": True, "message": "次の楽曲にスキップしました", "result": result}
    except Exception as e:
        return {"error": f"次の楽曲へのスキップ中にエラーが発生しました: {str(e)}"}

@mcp.tool()
def previous_track(device_id: Optional[str] = None) -> Dict[str, Any]:
    """前の楽曲に戻ります
    
    Args:
        device_id: 対象デバイスID（省略可）
    
    Returns:
        戻りの結果
    """
    try:
        sp = get_spotify_client()
        if not sp:
            return {"error": "Spotify認証が必要です"}
        
        result = spotify_tools_instance.previous_track(sp, device_id=device_id)
        return {"success": True, "message": "前の楽曲に戻りました", "result": result}
    except Exception as e:
        return {"error": f"前の楽曲への戻り中にエラーが発生しました: {str(e)}"}

@mcp.tool()
def search_artists(query: str, limit: int = 10) -> Dict[str, Any]:
    """Spotifyでアーティストを検索します
    
    Args:
        query: 検索クエリ（アーティスト名）
        limit: 取得する最大件数（デフォルト: 10）
    
    Returns:
        検索結果のアーティストリスト
    """
    try:
        sp = get_spotify_client()
        if not sp:
            return {"error": "Spotify認証が必要です"}
        
        artists = spotify_tools_instance.search_artists(sp, query, limit)
        return {
            "success": True,
            "artists": [
                {
                    "id": artist.id,
                    "name": artist.name,
                    "genres": artist.genres,
                    "popularity": artist.popularity,
                    "uri": artist.uri,
                    "followers": artist.followers
                }
                for artist in artists
            ]
        }
    except Exception as e:
        return {"error": f"アーティスト検索中にエラーが発生しました: {str(e)}"}

@mcp.tool()
def get_user_playlists() -> Dict[str, Any]:
    """ユーザーのプレイリスト一覧を取得します
    
    Returns:
        プレイリストのリスト
    """
    try:
        sp = get_spotify_client()
        if not sp:
            return {"error": "Spotify認証が必要です"}
        
        playlists = spotify_tools_instance.get_playlists(sp)
        return {
            "success": True,
            "playlists": [
                {
                    "id": playlist.id,
                    "name": playlist.name,
                    "description": playlist.description,
                    "public": playlist.public,
                    "tracks_total": playlist.tracks_total,
                    "uri": playlist.uri
                }
                for playlist in playlists
            ]
        }
    except Exception as e:
        return {"error": f"プレイリスト取得中にエラーが発生しました: {str(e)}"}

@mcp.tool()
def get_available_devices() -> Dict[str, Any]:
    """利用可能な再生デバイス一覧を取得します
    
    Returns:
        デバイスのリスト
    """
    try:
        sp = get_spotify_client()
        if not sp:
            return {"error": "Spotify認証が必要です"}
        
        devices = spotify_tools_instance.get_available_devices(sp)
        return {
            "success": True,
            "devices": [
                {
                    "id": device.id,
                    "name": device.name,
                    "type": device.type,
                    "is_active": device.is_active,
                    "is_private_session": device.is_private_session,
                    "is_restricted": device.is_restricted,
                    "volume_percent": device.volume_percent
                }
                for device in devices
            ]
        }
    except Exception as e:
        return {"error": f"デバイス一覧の取得中にエラーが発生しました: {str(e)}"}

@mcp.tool()
def set_volume(volume_percent: int, device_id: Optional[str] = None) -> Dict[str, Any]:
    """音量を設定します
    
    Args:
        volume_percent: 音量の百分率（0-100）
        device_id: 対象デバイスID（省略可）
    
    Returns:
        音量設定の結果
    """
    try:
        sp = get_spotify_client()
        if not sp:
            return {"error": "Spotify認証が必要です"}
        
        # 音量の範囲チェック
        if not 0 <= volume_percent <= 100:
            return {"error": "音量は0-100の範囲で指定してください"}
        
        result = spotify_tools_instance.set_volume(sp, volume_percent, device_id=device_id)
        return {"success": True, "message": f"音量を{volume_percent}%に設定しました", "result": result}
    except Exception as e:
        return {"error": f"音量設定中にエラーが発生しました: {str(e)}"}

if __name__ == "__main__":
    # サーバーを起動
    print("🎵 Spotify MCP Server starting...")
    print("利用可能なツール:")
    print("- search_tracks: 楽曲検索")
    print("- play_track: 楽曲再生")
    print("- get_current_playing: 現在再生中の楽曲情報")
    print("- pause_playback: 再生一時停止")
    print("- next_track: 次の楽曲")
    print("- previous_track: 前の楽曲")
    print("- search_artists: アーティスト検索")
    print("- get_user_playlists: プレイリスト一覧")
    print("- get_available_devices: デバイス一覧")
    print("- set_volume: 音量設定")
    
    mcp.run() 