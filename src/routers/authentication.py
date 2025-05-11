from fastapi import APIRouter, Depends, HTTPException
from ..auth import spotify_auth # spotify_auth は SpotifyAuth のインスタンス
from datetime import datetime

router = APIRouter()

@router.get("/login")
async def login():
    """Spotify認証を開始"""
    auth_url, state = spotify_auth.get_auth_url()
    # stateをセッションやクッキーに保存する処理が必要な場合があるが、
    # MCPサーバーのコンテキストではシンプルにURLを返す
    return {"auth_url": auth_url}

@router.get("/callback")
async def callback(code: str, state: str = None):
    """認証コールバック処理"""
    # stateの検証処理が必要な場合がある
    try:
        await spotify_auth.process_callback(code)
        return {"message": "認証に成功しました。"}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"コールバック処理エラー: {str(e)}")

@router.get("/status")
async def auth_status():
    """認証状態を確認"""
    is_authenticated = spotify_auth.is_authenticated()
    token_info = spotify_auth.get_token_info() # トークン情報も返すように変更
    user_profile = None
    if is_authenticated:
        try:
            # 簡単なユーザー情報を取得して表示（オプション）
            sp = spotify_auth.get_spotify_client()
            if sp:
                user_profile = sp.me()
        except Exception as e:
            # ユーザー情報取得に失敗しても認証状態は返す
            pass 

    return {
        "authenticated": is_authenticated,
        "message": "認証済みです" if is_authenticated else "まだ認証されていません。/auth/loginにアクセスして認証を行ってください。",
        "user_profile": user_profile if user_profile else None,
        "token_expires_at": datetime.fromtimestamp(token_info["expires_at"]).isoformat() if token_info and "expires_at" in token_info else None
    }

@router.post("/disconnect", operation_id="disconnect_spotify_account")
async def disconnect_spotify():
    """Spotifyアカウント接続を解除する（トークンを削除）"""
    disconnected = spotify_auth.disconnect()
    if disconnected:
        return {"message": "Spotifyアカウントの接続を解除しました。"}
    else:
        # disconnectがFalseを返す具体的なケースは現実装ではないが念のため
        raise HTTPException(status_code=500, detail="アカウント接続の解除に失敗しました。")


@router.post("/cache/clear", operation_id="clear_auth_cache")
async def clear_cache():
    """認証関連のキャッシュデータを削除する"""
    # SpotifyAuthクラスにキャッシュクリア機能がないため、TokenManagerの機能を使う
    # 必要であればSpotifyAuthクラスに CacheManager を使ったメソッドを追加する
    cleared = spotify_auth.clear_auth_cache() # SpotifyAuth側に実装した想定
    if cleared:
        return {"message": "認証キャッシュをクリアしました。"}
    else:
        raise HTTPException(status_code=500, detail="認証キャッシュのクリアに失敗しました。")

# 開発用：現在のトークン情報を表示するエンドポイント (本番では削除または保護)
@router.get("/token", include_in_schema=False) # MCPツールとしては公開しない
async def get_current_token_info():
    """現在のアクセストークン情報を取得（開発用）"""
    if not spotify_auth.is_authenticated():
        raise HTTPException(status_code=401, detail="認証されていません。")
    return spotify_auth.get_token_info() 