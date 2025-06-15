# src/routers/utility.py
from fastapi import APIRouter, Depends, HTTPException, Body
from typing import List, Dict, Any, Optional
from spotipy import Spotify
from pydantic import BaseModel, Field

from ..auth.spotify_auth import get_spotify_client
from ..dependencies import get_spotify_tools_instance # mainからインポート
from .. import __version__ # ルートの __init__.py からバージョン情報をインポート
from ..models import Track, Artist # Pydanticモデルをインポート

router = APIRouter()

@router.get("/health", operation_id="health_check")
async def health_check():
    """サーバーのヘルスチェック用エンドポイント"""
    return {"status": "ok", "version": __version__}

@router.get("/version", operation_id="get_server_version")
async def get_server_version():
    """サーバーのバージョン情報を取得"""
    return {"version": __version__}

# Spotify APIの sp.me() のレスポンス型を定義 (必要なものだけ)
class UserProfile(BaseModel):
    display_name: Optional[str] = None
    id: str
    email: Optional[str] = None # スコープによる
    external_urls: Dict[str, str]
    followers: Optional[Dict[str, Any]] = None # followersオブジェクトの具体的な型は省略
    href: str
    images: Optional[List[Dict[str, Any]]] = None # ImageObjectモデルを使うのが望ましい
    type: str
    uri: str
    country: Optional[str] = None # スコープによる

@router.get("/me", response_model=Optional[UserProfile], operation_id="get_user_profile")
async def get_user_profile_endpoint(sp: Spotify = Depends(get_spotify_client)):
    """現在認証しているユーザーのプロファイル情報を取得"""
    try:
        profile = sp.me()
        return UserProfile(**profile) if profile else None
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"ユーザープロファイルの取得に失敗: {str(e)}")

# RecentlyPlayedItemモデル (spotipyのレスポンスを参考に)
class RecentlyPlayedItem(BaseModel):
    track: Track
    played_at: str # ISOフォーマットのタイムスタンプ
    context: Optional[Dict[str, Any]] = None # contextオブジェクトの具体的な型は省略

class RecentlyPlayedResponse(BaseModel):
    items: List[RecentlyPlayedItem]
    # next: Optional[str] = None # カーソルベースのページネーション情報も追加可能
    # cursors: Optional[Dict[str, str]] = None
    # limit: Optional[int] = None

@router.get("/me/player/recently-played", response_model=RecentlyPlayedResponse, operation_id="get_recently_played_tracks")
async def get_recently_played_tracks_endpoint(limit: int = 20, after: Optional[int] = None, before: Optional[int] = None, sp: Spotify = Depends(get_spotify_client)):
    """ユーザーが最近再生した曲のリストを取得"""
    # SpotifyTools にメソッドがないため、直接 spotipy を使用
    try:
        results = sp.current_user_recently_played(limit=limit, after=after, before=before)
        # Trackモデルに変換
        items = []
        for item_data in results.get('items', []):
            track_data = item_data.get('track')
            if track_data:
                track = Track(
                    id=track_data['id'], 
                    name=track_data['name'], 
                    artist=track_data['artists'][0]['name'] if track_data.get('artists') else "Unknown Artist",
                    album=track_data.get('album', {}).get('name')
                )
                items.append(RecentlyPlayedItem(track=track, played_at=item_data['played_at'], context=item_data.get('context')))
        return RecentlyPlayedResponse(items=items)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"最近再生した曲の取得に失敗: {str(e)}")

class TopItemsResponse(BaseModel):
    items: List[Dict[str, Any]] # TrackまたはArtistモデルのリストになるが、ここでは汎用的にDict

@router.get("/me/top/{type}", response_model=TopItemsResponse, operation_id="get_user_top_items")
async def get_user_top_items_endpoint(type: str, limit: int = 20, offset: int = 0, time_range: str = "medium_term", sp: Spotify = Depends(get_spotify_client)):
    """ユーザーのトップアイテム（曲またはアーティスト）を取得 (type: 'artists' or 'tracks')"""
    if type not in ["artists", "tracks"]:
        raise HTTPException(status_code=400, detail="Type must be 'artists' or 'tracks'")
    # SpotifyTools にメソッドがないため、直接 spotipy を使用
    try:
        results = sp.current_user_top_artists(limit=limit, offset=offset, time_range=time_range) if type == "artists" else sp.current_user_top_tracks(limit=limit, offset=offset, time_range=time_range)
        # モデルへの変換は省略（必要なら行う）
        return TopItemsResponse(items=results.get('items', []))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"トップ{type}の取得に失敗: {str(e)}")

@router.get("/markets", response_model=List[str], operation_id="get_available_markets")
async def get_available_markets_endpoint(sp: Spotify = Depends(get_spotify_client)):
    """Spotifyが利用可能なマーケット（国コード）のリストを取得"""
    # SpotifyTools にメソッドがないため、直接 spotipy を使用
    try:
        markets = sp.available_markets()
        return markets.get('markets', [])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"利用可能マーケットの取得に失敗: {str(e)}")

class FollowedArtistsResponse(BaseModel):
    artists: Dict[str, Any] # spotipyのレスポンス形式に合わせる

@router.get("/me/following", response_model=FollowedArtistsResponse, operation_id="get_followed_artists")
async def get_followed_artists_endpoint(type: str = "artist", limit: int = 20, after: Optional[str] = None, sp: Spotify = Depends(get_spotify_client)):
    """現在認証しているユーザーがフォローしているアーティストを取得"""
    if type != "artist": # 現在はアーティストのみサポート
        raise HTTPException(status_code=400, detail="Currently only type 'artist' is supported.")
    # SpotifyTools にメソッドがないため、直接 spotipy を使用
    try:
        results = sp.current_user_followed_artists(limit=limit, after=after)
        return FollowedArtistsResponse(artists=results.get('artists', {}))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"フォロー中アーティストの取得に失敗: {str(e)}")

class FollowRequest(BaseModel):
    ids: List[str]
    type: str = Field("artist", description="'artist' or 'user'") # 現状はartistのみ

@router.put("/me/following", status_code=204, operation_id="follow_artists_or_users")
async def follow_artists_or_users_endpoint(request_body: FollowRequest, sp: Spotify = Depends(get_spotify_client)):
    """指定されたアーティストまたはユーザーをフォローする"""
    if request_body.type != "artist":
        raise HTTPException(status_code=400, detail="Currently only following artists is supported.")
    # SpotifyTools にメソッドがないため、直接 spotipy を使用
    try:
        sp.user_follow_artists(request_body.ids)
        return # No content
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"フォローに失敗: {str(e)}")

@router.delete("/me/following", status_code=204, operation_id="unfollow_artists_or_users")
async def unfollow_artists_or_users_endpoint(ids: List[str] = Body(...), type: str = Body("artist"), sp: Spotify = Depends(get_spotify_client)):
    """指定されたアーティストまたはユーザーのフォローを解除する"""
    if type != "artist":
        raise HTTPException(status_code=400, detail="Currently only unfollowing artists is supported.")
    # SpotifyTools にメソッドがないため、直接 spotipy を使用
    try:
        sp.user_unfollow_artists(ids)
        return # No content
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"フォロー解除に失敗: {str(e)}") 