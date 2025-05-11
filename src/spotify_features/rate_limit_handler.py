"""
レート制限ハンドラーモジュール

Spotify API へのリクエスト頻度を制御し、レート制限エラー (429) を回避・処理するためのハンドラーを提供します。
"""

import time
import logging
from typing import Callable, Any, Dict
from spotipy import SpotifyException
from fastapi import HTTPException

# ロガーの設定
logger = logging.getLogger(__name__)


class RateLimitHandler:
    """APIリクエストの頻度制限対策を行うクラス"""

    def __init__(self, max_retries: int = 3, initial_backoff: float = 1.0, max_backoff: float = 60.0):
        """RateLimitHandlerの初期化

        Args:
            max_retries (int, optional): 最大リトライ回数。デフォルトは3回。
            initial_backoff (float, optional): 初期バックオフ時間（秒）。デフォルトは1.0秒。
            max_backoff (float, optional): 最大バックオフ時間（秒）。デフォルトは60.0秒。
        """
        self.max_retries = max_retries
        self.initial_backoff = initial_backoff
        self.max_backoff = max_backoff
        # 将来的にはエンドポイントごとのリクエスト制限カウンターの実装も可能

    def execute_with_rate_limit(self, func: Callable, *args: Any, **kwargs: Any) -> Any:
        """レート制限を考慮してAPI関数を実行

        Args:
            func (Callable): 実行する関数（通常はspotipyのメソッド）
            *args: 関数に渡す位置引数
            **kwargs: 関数に渡すキーワード引数

        Returns:
            Any: 関数の実行結果

        Raises:
            HTTPException: APIリクエストに失敗した場合、またはリトライ回数を超えた場合
        """
        retries = 0
        current_backoff = self.initial_backoff
        
        while retries < self.max_retries:
            try:
                return func(*args, **kwargs)
            except SpotifyException as e:
                # レート制限エラー（HTTP 429）の場合はリトライ
                if hasattr(e, 'http_status') and e.http_status == 429:
                    # Retry-Afterヘッダーがあればその値を使用
                    retry_after_header = getattr(e, 'headers', {}).get('Retry-After')
                    wait_time = current_backoff
                    
                    if retry_after_header:
                        try:
                            wait_time = float(retry_after_header)
                        except (ValueError, TypeError):
                            # ヘッダーが予期せぬ形式の場合、計算されたバックオフを使用
                            pass

                    # 実際の待機時間は最大バックオフ時間を超えないようにする
                    actual_wait_time = min(wait_time, self.max_backoff)
                    logger.warning(f"レート制限: {actual_wait_time:.2f}秒待機して再試行します ({retries + 1}/{self.max_retries})")
                    time.sleep(actual_wait_time)
                    retries += 1
                    
                    # バックオフ時間を指数関数的に増やす（ただし上限あり）
                    current_backoff = min(current_backoff * 2, self.max_backoff)
                else:
                    # 429以外のSpotifyExceptionはそのまま上位に投げる
                    self._handle_spotify_exception(e)
            except Exception as e:
                # その他の予期せぬエラー
                logger.error(f"API呼び出し中の予期せぬエラー: {e}")
                raise HTTPException(status_code=500, detail=f"API呼び出し中の予期せぬエラー: {str(e)}")

        # 最大リトライ回数を超えた場合
        logger.error("Spotify APIのレート制限が継続しています。最大リトライ回数を超えました。")
        raise HTTPException(
            status_code=429,
            detail="Spotify APIのレート制限が継続しています。しばらくしてから再試行してください。"
        )

    def _handle_spotify_exception(self, e: SpotifyException) -> None:
        """SpotifyExceptionをHTTPExceptionに変換して投げる

        Args:
            e (SpotifyException): 変換するSpotifyException

        Raises:
            HTTPException: 変換されたHTTPException
        """
        http_status = getattr(e, 'http_status', 500)
        reason = getattr(e, 'reason', '')
        msg = getattr(e, 'msg', str(e))
        
        detail = f"Spotify API Error: {reason or msg}"
        
        # 特定のエラーコードに対するカスタムメッセージ
        if http_status == 401:
            detail = "認証に失敗しました。アクセストークンが無効または期限切れです。"
        elif http_status == 403:
            detail = "この操作を実行する権限がありません。"
        elif http_status == 404:
            detail = "リクエストされたリソース（デバイス、トラックなど）が見つかりません。"
        
        raise HTTPException(status_code=http_status, detail=detail) 