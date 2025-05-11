"""
プレイヤーマネージャーモジュール

再生コントロール関連の操作（再生状態取得、再生/一時停止、デバイス切り替えなど）を担当するクラスを提供します。
"""

import time
import logging
from typing import List, Dict, Any, Optional
from spotipy import Spotify, SpotifyException
from fastapi import HTTPException
from ..models import Device, PlaybackState

# ロガーの設定
logger = logging.getLogger(__name__)


class PlayerManager:
    """再生コントロール関連の操作を担当するクラス"""

    def __init__(self, cache_handler: Any, rate_limit_handler: Optional[Any] = None):
        """PlayerManagerの初期化

        Args:
            cache_handler (CacheHandler): キャッシュハンドラーインスタンス
            rate_limit_handler (Optional[RateLimitHandler], optional): レート制限ハンドラーインスタンス。デフォルトはNone。
        """
        self.cache = cache_handler
        self.rate_limiter = rate_limit_handler

    def _call_spotipy(self, spotipy_method, *args, **kwargs) -> Any:
        """spotipyのメソッドを呼び出し、エラーハンドリングを行う共通関数

        Args:
            spotipy_method (Callable): 呼び出すspotipyのメソッド
            *args: メソッドに渡す位置引数
            **kwargs: メソッドに渡すキーワード引数

        Returns:
            Any: メソッドの実行結果

        Raises:
            HTTPException: API呼び出しに失敗した場合
        """
        try:
            # レート制限ハンドラーがあれば、それを使って呼び出す
            if self.rate_limiter:
                return self.rate_limiter.execute_with_rate_limit(spotipy_method, *args, **kwargs)
            else:
                # なければ直接呼び出す
                return spotipy_method(*args, **kwargs)
        except SpotifyException as e:
            # エラーメッセージを整形
            detail = f"Spotify API Error: {e.reason or e.msg or str(e)} (HTTP {e.http_status})"
            
            # 特定のHTTPステータスコードに対してより詳細なエラーメッセージを提供
            if e.http_status == 401:  # Unauthorized
                detail = "認証エラー: アクセストークンが期限切れか無効です。再認証してください。"
            elif e.http_status == 403:  # Forbidden
                detail = "権限エラー: この操作を実行する権限がありません。"
            elif e.http_status == 404:  # Not Found
                detail = "Not Found: 要求されたリソース（デバイス、トラックなど）が見つかりません。"
            elif e.http_status == 429:  # Too Many Requests
                detail = "レート制限: リクエストが多すぎます。しばらく待ってから再試行してください。"
            
            logger.error(f"Spotify API呼び出しエラー: {detail}")
            raise HTTPException(status_code=e.http_status or 500, detail=detail)
        except Exception as e:
            # 予期せぬエラー
            logger.error(f"予期せぬエラー: {e}")
            raise HTTPException(status_code=500, detail=f"予期せぬエラー: {str(e)}")

    # --- 再生状態取得系 ---
    def get_playback_state(self, sp: Spotify) -> Optional[PlaybackState]:
        """現在の包括的な再生状態を取得

        Args:
            sp (Spotify): 認証済みのSpotifyクライアント

        Returns:
            Optional[PlaybackState]: 再生状態。アクティブなデバイスがない場合はNone。

        Raises:
            HTTPException: API呼び出しに失敗した場合
        """
        # 再生状態は頻繁に変わるため、キャッシュは使用しない
        try:
            current_playback = self._call_spotipy(sp.current_playback)
            
            if not current_playback:
                logger.debug("アクティブな再生状態がありません")
                return None
            
            logger.debug(f"現在の再生状態を取得しました: {current_playback.get('item', {}).get('name', 'Unknown')}")
            return PlaybackState(**current_playback)
        except HTTPException:
            # _call_spotipy内で既にHTTPExceptionに変換されている
            raise
        except Exception as e:
            logger.error(f"再生状態取得中の予期せぬエラー: {e}")
            raise HTTPException(status_code=500, detail=f"再生状態の取得に失敗しました: {str(e)}")

    def get_currently_playing_track(self, sp: Spotify) -> Optional[PlaybackState]:
        """現在再生中の曲情報を取得

        Args:
            sp (Spotify): 認証済みのSpotifyクライアント

        Returns:
            Optional[PlaybackState]: 現在再生中の曲情報を含む再生状態。何も再生していない場合はNone。

        Raises:
            HTTPException: API呼び出しに失敗した場合
        """
        # 現在の曲も頻繁に変わるため、キャッシュは使用しない
        try:
            current_track_info = self._call_spotipy(sp.current_user_playing_track)
            
            if not current_track_info:
                logger.debug("現在再生中の曲はありません")
                return None
            
            track_name = current_track_info.get('item', {}).get('name', 'Unknown')
            logger.debug(f"現在再生中の曲を取得しました: {track_name}")
            return PlaybackState(**current_track_info)
        except HTTPException:
            # _call_spotipy内で既にHTTPExceptionに変換されている
            raise
        except Exception as e:
            logger.error(f"現在再生中の曲取得中の予期せぬエラー: {e}")
            raise HTTPException(status_code=500, detail=f"現在再生中の曲の取得に失敗しました: {str(e)}")

    def get_available_devices(self, sp: Spotify) -> List[Device]:
        """利用可能なデバイス一覧を取得

        Args:
            sp (Spotify): 認証済みのSpotifyクライアント

        Returns:
            List[Device]: 利用可能なデバイスのリスト

        Raises:
            HTTPException: API呼び出しに失敗した場合
        """
        # デバイスリストは短時間でも変わる可能性があるため、短めのキャッシュ
        cache_key = f"devices_{int(time.time() // 30)}"  # 30秒キャッシュ
        cached_data = self.cache.get_from_cache(cache_key, max_age=30)
        
        if cached_data:
            logger.debug("キャッシュからデバイス一覧を取得しました")
            return [Device(**item) for item in cached_data]
        
        try:
            devices_info = self._call_spotipy(sp.devices)
            devices = []
            
            if devices_info and 'devices' in devices_info:
                for device in devices_info['devices']:
                    devices.append(Device(
                        id=device.get('id'),
                        name=device.get('name', 'Unknown Device'),
                        type=device.get('type', 'Unknown'),
                        is_active=device.get('is_active', False),
                        is_private_session=device.get('is_private_session', False),
                        is_restricted=device.get('is_restricted', False),
                        volume_percent=device.get('volume_percent')
                    ))
            
            # キャッシュに保存
            self.cache.save_to_cache(cache_key, [d.dict() for d in devices])
            logger.debug(f"{len(devices)}件のデバイスを取得しました")
            
            return devices
        except HTTPException:
            # _call_spotipy内で既にHTTPExceptionに変換されている
            raise
        except Exception as e:
            logger.error(f"デバイス一覧取得中の予期せぬエラー: {e}")
            raise HTTPException(status_code=500, detail=f"デバイス一覧の取得に失敗しました: {str(e)}")

    # --- 再生コントロール系 ---
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

        Raises:
            HTTPException: API呼び出しに失敗した場合
        """
        try:
            # キャッシュから現在の再生状態をクリア
            self.cache.clear_cache_by_key(f"devices_{int(time.time() // 30)}")
            
            # 再生パラメータの準備
            play_kwargs = {}
            if device_id:
                play_kwargs['device_id'] = device_id
            if context_uri:
                play_kwargs['context_uri'] = context_uri
            if uris:
                play_kwargs['uris'] = uris
            if offset:
                play_kwargs['offset'] = offset
            if position_ms:
                play_kwargs['position_ms'] = position_ms
            
            # 再生開始
            self._call_spotipy(sp.start_playback, **play_kwargs)
            
            logger.info("再生を開始しました")
            return {"success": True}
        except HTTPException as e:
            if e.status_code == 404:
                # デバイスが見つからない場合は、より具体的なメッセージに
                logger.error("再生開始エラー: アクティブなデバイスが見つかりません")
                raise HTTPException(status_code=404, detail="アクティブなデバイスが見つかりません。Spotify Appを開いてデバイスをアクティブにしてください。")
            raise
        except Exception as e:
            logger.error(f"再生開始中の予期せぬエラー: {e}")
            raise HTTPException(status_code=500, detail=f"再生の開始に失敗しました: {str(e)}")

    def pause(self, sp: Spotify, device_id: Optional[str] = None) -> Dict[str, Any]:
        """再生を一時停止

        Args:
            sp (Spotify): 認証済みのSpotifyクライアント
            device_id (Optional[str], optional): デバイスID。デフォルトはNone（アクティブデバイス）。

        Returns:
            Dict[str, Any]: {"success": bool}

        Raises:
            HTTPException: API呼び出しに失敗した場合
        """
        try:
            # キャッシュから現在の再生状態をクリア
            self.cache.clear_cache_by_key(f"devices_{int(time.time() // 30)}")
            
            # 一時停止パラメータの準備
            pause_kwargs = {}
            if device_id:
                pause_kwargs['device_id'] = device_id
            
            # 一時停止
            self._call_spotipy(sp.pause_playback, **pause_kwargs)
            
            logger.info("再生を一時停止しました")
            return {"success": True}
        except HTTPException as e:
            if e.status_code == 404:
                logger.error("一時停止エラー: アクティブなデバイスが見つかりません")
                raise HTTPException(status_code=404, detail="アクティブなデバイスが見つかりません。")
            raise
        except Exception as e:
            logger.error(f"一時停止中の予期せぬエラー: {e}")
            raise HTTPException(status_code=500, detail=f"一時停止に失敗しました: {str(e)}")

    def next_track(self, sp: Spotify, device_id: Optional[str] = None) -> Dict[str, Any]:
        """次の曲へ

        Args:
            sp (Spotify): 認証済みのSpotifyクライアント
            device_id (Optional[str], optional): デバイスID。デフォルトはNone（アクティブデバイス）。

        Returns:
            Dict[str, Any]: {"success": bool}

        Raises:
            HTTPException: API呼び出しに失敗した場合
        """
        try:
            # キャッシュから現在の再生状態をクリア
            self.cache.clear_cache_by_key(f"devices_{int(time.time() // 30)}")
            
            # 次の曲パラメータの準備
            next_kwargs = {}
            if device_id:
                next_kwargs['device_id'] = device_id
            
            # 次の曲へ
            self._call_spotipy(sp.next_track, **next_kwargs)
            
            logger.info("次の曲に移動しました")
            return {"success": True}
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"次の曲への移動中の予期せぬエラー: {e}")
            raise HTTPException(status_code=500, detail=f"次の曲への移動に失敗しました: {str(e)}")

    def previous_track(self, sp: Spotify, device_id: Optional[str] = None) -> Dict[str, Any]:
        """前の曲へ

        Args:
            sp (Spotify): 認証済みのSpotifyクライアント
            device_id (Optional[str], optional): デバイスID。デフォルトはNone（アクティブデバイス）。

        Returns:
            Dict[str, Any]: {"success": bool}

        Raises:
            HTTPException: API呼び出しに失敗した場合
        """
        try:
            # キャッシュから現在の再生状態をクリア
            self.cache.clear_cache_by_key(f"devices_{int(time.time() // 30)}")
            
            # 前の曲パラメータの準備
            previous_kwargs = {}
            if device_id:
                previous_kwargs['device_id'] = device_id
            
            # 前の曲へ
            self._call_spotipy(sp.previous_track, **previous_kwargs)
            
            logger.info("前の曲に移動しました")
            return {"success": True}
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"前の曲への移動中の予期せぬエラー: {e}")
            raise HTTPException(status_code=500, detail=f"前の曲への移動に失敗しました: {str(e)}")

    def set_volume(self, sp: Spotify, volume_percent: int, device_id: Optional[str] = None) -> Dict[str, Any]:
        """音量を設定

        Args:
            sp (Spotify): 認証済みのSpotifyクライアント
            volume_percent (int): 音量（0～100）
            device_id (Optional[str], optional): デバイスID。デフォルトはNone（アクティブデバイス）。

        Returns:
            Dict[str, Any]: {"success": bool, "volume_percent": int}

        Raises:
            HTTPException: API呼び出しに失敗した場合
        """
        # 音量の範囲を確認
        if volume_percent < 0 or volume_percent > 100:
            raise HTTPException(status_code=400, detail="音量は0から100の間で指定してください")
        
        try:
            # キャッシュから現在の再生状態をクリア
            self.cache.clear_cache_by_key(f"devices_{int(time.time() // 30)}")
            
            # 音量設定パラメータの準備
            volume_kwargs = {"volume_percent": volume_percent}
            if device_id:
                volume_kwargs['device_id'] = device_id
            
            # 音量設定
            self._call_spotipy(sp.volume, **volume_kwargs)
            
            logger.info(f"音量を{volume_percent}%に設定しました")
            return {"success": True, "volume_percent": volume_percent}
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"音量設定中の予期せぬエラー: {e}")
            raise HTTPException(status_code=500, detail=f"音量の設定に失敗しました: {str(e)}")

    def seek_track(self, sp: Spotify, position_ms: int, device_id: Optional[str] = None) -> Dict[str, Any]:
        """曲の再生位置を変更

        Args:
            sp (Spotify): 認証済みのSpotifyクライアント
            position_ms (int): 曲内の位置（ミリ秒）
            device_id (Optional[str], optional): デバイスID。デフォルトはNone（アクティブデバイス）。

        Returns:
            Dict[str, Any]: {"success": bool, "position_ms": int}

        Raises:
            HTTPException: API呼び出しに失敗した場合
        """
        if position_ms < 0:
            raise HTTPException(status_code=400, detail="再生位置は0以上の値を指定してください")
        
        try:
            # シーク パラメータの準備
            seek_kwargs = {"position_ms": position_ms}
            if device_id:
                seek_kwargs['device_id'] = device_id
            
            # 再生位置変更
            self._call_spotipy(sp.seek_track, **seek_kwargs)
            
            logger.info(f"再生位置を{position_ms}msに設定しました")
            return {"success": True, "position_ms": position_ms}
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"再生位置設定中の予期せぬエラー: {e}")
            raise HTTPException(status_code=500, detail=f"再生位置の設定に失敗しました: {str(e)}")

    def set_repeat_mode(self, sp: Spotify, state: str, device_id: Optional[str] = None) -> Dict[str, Any]:
        """リピートモードを設定

        Args:
            sp (Spotify): 認証済みのSpotifyクライアント
            state (str): リピートモード（'track', 'context', 'off'）
            device_id (Optional[str], optional): デバイスID。デフォルトはNone（アクティブデバイス）。

        Returns:
            Dict[str, Any]: {"success": bool, "repeat_state": str}

        Raises:
            HTTPException: API呼び出しに失敗した場合
        """
        valid_states = ['track', 'context', 'off']
        if state not in valid_states:
            raise HTTPException(status_code=400, detail=f"リピートモードは{', '.join(valid_states)}のいずれかを指定してください")
        
        try:
            # リピートモード パラメータの準備
            repeat_kwargs = {"state": state}
            if device_id:
                repeat_kwargs['device_id'] = device_id
            
            # リピートモード設定
            self._call_spotipy(sp.repeat, **repeat_kwargs)
            
            logger.info(f"リピートモードを{state}に設定しました")
            return {"success": True, "repeat_state": state}
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"リピートモード設定中の予期せぬエラー: {e}")
            raise HTTPException(status_code=500, detail=f"リピートモードの設定に失敗しました: {str(e)}")

    def set_shuffle(self, sp: Spotify, state: bool, device_id: Optional[str] = None) -> Dict[str, Any]:
        """シャッフルモードを設定

        Args:
            sp (Spotify): 認証済みのSpotifyクライアント
            state (bool): シャッフルモードの有効/無効
            device_id (Optional[str], optional): デバイスID。デフォルトはNone（アクティブデバイス）。

        Returns:
            Dict[str, Any]: {"success": bool, "shuffle_state": bool}

        Raises:
            HTTPException: API呼び出しに失敗した場合
        """
        try:
            # シャッフルモード パラメータの準備
            shuffle_kwargs = {"state": state}
            if device_id:
                shuffle_kwargs['device_id'] = device_id
            
            # シャッフルモード設定
            self._call_spotipy(sp.shuffle, **shuffle_kwargs)
            
            logger.info(f"シャッフルモードを{'有効' if state else '無効'}に設定しました")
            return {"success": True, "shuffle_state": state}
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"シャッフルモード設定中の予期せぬエラー: {e}")
            raise HTTPException(status_code=500, detail=f"シャッフルモードの設定に失敗しました: {str(e)}") 