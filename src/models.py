"""
Pydanticモデル定義

SpotifyAPIから取得するデータ構造を表現するモデルを定義します。
"""

from typing import Dict, List, Optional, Any
from pydantic import BaseModel


class ExternalUrls(BaseModel):
    """外部URLのモデル"""
    spotify: Optional[str] = None


class ImageObject(BaseModel):
    """画像オブジェクトのモデル"""
    url: str
    height: Optional[int] = None
    width: Optional[int] = None


class PlaylistTrackInfo(BaseModel):
    """プレイリストのトラック情報モデル"""
    total: int


class Playlist(BaseModel):
    """プレイリストのモデル"""
    id: str
    name: str
    description: Optional[str] = None
    tracks: Optional[PlaylistTrackInfo] = None
    external_urls: Optional[ExternalUrls] = None
    images: Optional[List[ImageObject]] = None
    owner: Optional[Dict[str, Any]] = None
    public: Optional[bool] = None


class Track(BaseModel):
    """トラックのモデル"""
    id: str
    name: str
    artist: str
    album: Optional[str] = None


class Artist(BaseModel):
    """アーティストのモデル"""
    id: str
    name: str
    popularity: int
    genres: List[str] = []
    image_url: Optional[str] = None


class Device(BaseModel):
    """デバイスのモデル"""
    id: Optional[str] = None
    is_active: bool = False
    is_private_session: bool = False
    is_restricted: bool = False
    name: str = "Unknown Device"
    type: str = "Unknown"
    volume_percent: Optional[int] = None


class PlaybackContext(BaseModel):
    """再生コンテキストのモデル"""
    type: Optional[str] = None
    href: Optional[str] = None
    external_urls: Optional[Dict[str, str]] = None
    uri: Optional[str] = None


class PlaybackItem(BaseModel):
    """再生アイテムのモデル"""
    id: Optional[str] = None
    name: Optional[str] = None
    type: Optional[str] = None
    uri: Optional[str] = None
    duration_ms: Optional[int] = None
    artists: Optional[List[Dict[str, Any]]] = None
    album: Optional[Dict[str, Any]] = None


class PlaybackState(BaseModel):
    """再生状態のモデル"""
    device: Optional[Device] = None
    shuffle_state: Optional[bool] = None
    repeat_state: Optional[str] = None
    timestamp: Optional[int] = None
    context: Optional[PlaybackContext] = None
    progress_ms: Optional[int] = None
    item: Optional[PlaybackItem] = None
    currently_playing_type: Optional[str] = None
    actions: Optional[Dict[str, Any]] = None
    is_playing: bool = False


class RecommendationExternalUrls(BaseModel):
    """レコメンデーション用外部URLのモデル"""
    spotify: Optional[str] = None


class RecommendationArtistSimple(BaseModel):
    """レコメンデーション用簡易アーティストモデル"""
    external_urls: Optional[RecommendationExternalUrls] = None
    href: Optional[str] = None
    id: str
    name: str
    type: str
    uri: Optional[str] = None


class RecommendationAlbumSimple(BaseModel):
    """レコメンデーション用簡易アルバムモデル"""
    album_type: str
    total_tracks: int
    available_markets: Optional[List[str]] = None
    external_urls: Optional[RecommendationExternalUrls] = None
    href: Optional[str] = None
    id: str
    images: Optional[List[Dict[str, Any]]] = None
    name: str
    release_date: Optional[str] = None
    release_date_precision: Optional[str] = None
    type: str
    uri: Optional[str] = None
    artists: Optional[List[RecommendationArtistSimple]] = None


class RecommendationTrack(BaseModel):
    """レコメンデーショントラックのモデル"""
    artists: Optional[List[RecommendationArtistSimple]] = None
    available_markets: Optional[List[str]] = None
    disc_number: Optional[int] = None
    duration_ms: Optional[int] = None
    explicit: Optional[bool] = None
    external_urls: Optional[RecommendationExternalUrls] = None
    href: Optional[str] = None
    id: str
    is_playable: Optional[bool] = None
    name: str
    preview_url: Optional[str] = None
    track_number: Optional[int] = None
    type: str
    uri: Optional[str] = None
    is_local: Optional[bool] = None
    album: Optional[RecommendationAlbumSimple] = None
    popularity: Optional[int] = None


class RecommendationSeed(BaseModel):
    """レコメンデーションシードのモデル"""
    afterFilteringSize: int
    afterRelinkingSize: int
    href: Optional[str] = None
    id: str
    initialPoolSize: int
    type: str


class RecommendationsResponse(BaseModel):
    """レコメンデーションレスポンスのモデル"""
    seeds: List[RecommendationSeed]
    tracks: List[RecommendationTrack] 