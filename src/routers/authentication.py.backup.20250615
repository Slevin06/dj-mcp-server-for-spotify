from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse, HTMLResponse
from ..auth.spotify_auth import spotify_auth # spotify_auth は SpotifyAuth のインスタンス
from datetime import datetime

router = APIRouter()

@router.get("/login", operation_id="start_spotify_authentication")
async def login(request: Request, auto_redirect: bool = True):
    """Spotify認証を開始"""
    auth_url = spotify_auth.get_auth_url()
    if not auth_url:
        raise HTTPException(status_code=500, detail="認証情報が設定されていません。環境変数SPOTIFY_CLIENT_IDとSPOTIFY_CLIENT_SECRETを設定してください。")
    
    # User-Agentをチェックしてブラウザからのアクセスかを判定
    user_agent = request.headers.get("user-agent", "").lower()
    is_browser = any(browser in user_agent for browser in ["mozilla", "chrome", "safari", "firefox", "edge"])
    
    # auto_redirect=Trueかつブラウザからのアクセスの場合は自動リダイレクト
    if auto_redirect and is_browser:
        return RedirectResponse(url=auth_url, status_code=302)
    
    # auto_redirect=Falseまたは非ブラウザの場合はHTMLページを表示
    html_content = f"""
    <!DOCTYPE html>
    <html lang="ja">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Spotify 認証 - DJ MCP Server</title>
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                margin: 0;
                padding: 0;
                background: linear-gradient(135deg, #1db954, #191414);
                color: white;
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
            }}
            .container {{
                background: rgba(25, 20, 20, 0.9);
                padding: 2rem;
                border-radius: 12px;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
                text-align: center;
                max-width: 500px;
                margin: 1rem;
            }}
            .logo {{
                font-size: 2.5rem;
                margin-bottom: 1rem;
                color: #1db954;
            }}
            h1 {{
                margin-bottom: 1rem;
                font-size: 1.8rem;
            }}
            .subtitle {{
                margin-bottom: 2rem;
                opacity: 0.8;
                font-size: 1.1rem;
            }}
            .auth-button {{
                display: inline-block;
                background: #1db954;
                color: white;
                padding: 16px 32px;
                text-decoration: none;
                border-radius: 50px;
                font-weight: bold;
                font-size: 1.1rem;
                transition: all 0.3s ease;
                margin: 1rem 0;
                border: none;
                cursor: pointer;
                min-width: 200px;
            }}
            .auth-button:hover {{
                background: #1ed760;
                transform: translateY(-2px);
                box-shadow: 0 6px 20px rgba(29, 185, 84, 0.4);
            }}
            .manual-section {{
                margin-top: 2rem;
                padding-top: 2rem;
                border-top: 1px solid rgba(255, 255, 255, 0.1);
            }}
            .url-box {{
                background: rgba(0, 0, 0, 0.3);
                padding: 1rem;
                border-radius: 8px;
                margin: 1rem 0;
                word-break: break-all;
                font-family: monospace;
                font-size: 0.9rem;
                border: 1px solid rgba(255, 255, 255, 0.1);
            }}
            .copy-button {{
                background: #333;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                cursor: pointer;
                margin-top: 0.5rem;
                font-size: 0.9rem;
            }}
            .copy-button:hover {{
                background: #555;
            }}
            .instructions {{
                text-align: left;
                margin-top: 1rem;
                padding: 1rem;
                background: rgba(0, 0, 0, 0.2);
                border-radius: 8px;
                font-size: 0.95rem;
                line-height: 1.5;
            }}
            .step {{
                margin-bottom: 0.5rem;
            }}
            .notice {{
                background: rgba(255, 193, 7, 0.1);
                border: 1px solid rgba(255, 193, 7, 0.3);
                padding: 1rem;
                border-radius: 8px;
                margin: 1rem 0;
                font-size: 0.9rem;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="logo">🎵</div>
            <h1>Spotify 認証</h1>
            <p class="subtitle">DJ MCP Server for Spotify</p>
            
            <div class="notice">
                <strong>💡 認証手順:</strong><br>
                以下のボタンをクリックしてSpotifyにログインし、アプリの利用を許可してください。
            </div>
            
            <!-- メインの認証ボタン -->
            <a href="{auth_url}" class="auth-button" target="_blank" onclick="handleAuthClick()">
                🔐 Spotify でログイン
            </a>
            
            <!-- 手動コピー用セクション -->
            <div class="manual-section">
                <h3>🔧 手動で認証する場合</h3>
                <p>上のボタンが動作しない場合は、以下のURLをコピーしてブラウザで開いてください：</p>
                <div class="url-box" id="authUrl">{auth_url}</div>
                <button class="copy-button" onclick="copyToClipboard()">📋 URLをコピー</button>
                
                <div class="instructions">
                    <div class="step"><strong>ステップ1:</strong> 上記URLにアクセス</div>
                    <div class="step"><strong>ステップ2:</strong> Spotifyアカウントでログイン</div>
                    <div class="step"><strong>ステップ3:</strong> アプリのアクセスを許可</div>
                    <div class="step"><strong>ステップ4:</strong> 自動的にコールバックページに移動</div>
                </div>
            </div>
        </div>
        
        <script>
            function handleAuthClick() {{
                // 3秒後に状態確認を促すメッセージを表示
                setTimeout(() => {{
                    if (confirm('認証が完了しましたか？\\n\\n「OK」を押すと認証状態を確認します。\\n「キャンセル」を押すと後で確認できます。')) {{
                        window.location.href = '/auth/status';
                    }}
                }}, 3000);
            }}
            
            function copyToClipboard() {{
                const urlElement = document.getElementById('authUrl');
                const textArea = document.createElement('textarea');
                textArea.value = urlElement.textContent;
                document.body.appendChild(textArea);
                textArea.select();
                document.execCommand('copy');
                document.body.removeChild(textArea);
                
                const button = event.target;
                const originalText = button.textContent;
                button.textContent = '✅ コピーしました！';
                button.style.background = '#1db954';
                
                setTimeout(() => {{
                    button.textContent = originalText;
                    button.style.background = '#333';
                }}, 2000);
            }}
            
            // ページ読み込み時にauto_redirect=falseのURLに変更
            history.replaceState(null, '', '/auth/login?auto_redirect=false');
        </script>
    </body>
    </html>
    """
    
    return HTMLResponse(content=html_content)

@router.get("/login/direct", operation_id="direct_spotify_authentication") 
async def login_direct():
    """Spotify認証を開始（直接リダイレクト）"""
    auth_url = spotify_auth.get_auth_url()
    if not auth_url:
        raise HTTPException(status_code=500, detail="認証情報が設定されていません。環境変数SPOTIFY_CLIENT_IDとSPOTIFY_CLIENT_SECRETを設定してください。")
    
    return RedirectResponse(url=auth_url, status_code=302)

@router.get("/login/json", operation_id="json_spotify_authentication")
async def login_json():
    """Spotify認証URLをJSON形式で取得（API用）"""
    auth_url = spotify_auth.get_auth_url()
    if not auth_url:
        raise HTTPException(status_code=500, detail="認証情報が設定されていません。環境変数SPOTIFY_CLIENT_IDとSPOTIFY_CLIENT_SECRETを設定してください。")
    
    return {"auth_url": auth_url}

@router.get("/callback", operation_id="handle_spotify_callback")
async def callback(code: str, state: str = None):
    """認証コールバック処理"""
    # stateの検証処理が必要な場合がある
    try:
        success = spotify_auth.handle_callback(code)
        if success:
            # 成功時は美しいHTMLページを表示
            html_content = """
            <!DOCTYPE html>
            <html lang="ja">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>認証成功 - DJ MCP Server</title>
                <style>
                    body {
                        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                        margin: 0;
                        padding: 0;
                        background: linear-gradient(135deg, #1db954, #191414);
                        color: white;
                        min-height: 100vh;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                    }
                    .container {
                        background: rgba(25, 20, 20, 0.9);
                        padding: 2rem;
                        border-radius: 12px;
                        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
                        text-align: center;
                        max-width: 500px;
                        margin: 1rem;
                    }
                    .success-icon {
                        font-size: 4rem;
                        margin-bottom: 1rem;
                        color: #1db954;
                    }
                    h1 {
                        margin-bottom: 1rem;
                        color: #1db954;
                    }
                    .message {
                        margin-bottom: 2rem;
                        font-size: 1.1rem;
                        opacity: 0.9;
                    }
                    .next-steps {
                        background: rgba(0, 0, 0, 0.2);
                        padding: 1.5rem;
                        border-radius: 8px;
                        margin: 1rem 0;
                        text-align: left;
                    }
                    .action-button {
                        display: inline-block;
                        background: #1db954;
                        color: white;
                        padding: 12px 24px;
                        text-decoration: none;
                        border-radius: 25px;
                        font-weight: bold;
                        margin: 0.5rem;
                        transition: all 0.3s ease;
                    }
                    .action-button:hover {
                        background: #1ed760;
                        transform: translateY(-2px);
                    }
                    .secondary-button {
                        background: #333;
                    }
                    .secondary-button:hover {
                        background: #555;
                    }
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="success-icon">✅</div>
                    <h1>認証成功！</h1>
                    <p class="message">
                        Spotify アカウントとの連携が完了しました。<br>
                        これで AI アシスタントから Spotify を操作できます。
                    </p>
                    
                    <div class="next-steps">
                        <h3>🚀 次のステップ:</h3>
                        <ul>
                            <li>AI アシスタント（Claude、Cursor など）に戻る</li>
                            <li>「今の音楽の気分は？」「プレイリストを作って」などの指示を試す</li>
                            <li>認証状態は自動的に保持されます</li>
                        </ul>
                    </div>
                    
                    <a href="/auth/status" class="action-button">認証状態を確認</a>
                    <a href="/docs" class="action-button secondary-button">API ドキュメント</a>
                </div>
                
                <script>
                    // 5秒後に自動的にタブを閉じるかを確認
                    setTimeout(() => {
                        if (confirm('認証が完了しました。\\n\\nこのタブを閉じて AI アシスタントに戻りますか？')) {
                            window.close();
                        }
                    }, 5000);
                </script>
            </body>
            </html>
            """
            return HTMLResponse(content=html_content)
        else:
            raise HTTPException(status_code=400, detail="認証に失敗しました。")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"コールバック処理エラー: {str(e)}")

@router.get("/status", operation_id="get_spotify_auth_status")
async def auth_status():
    """認証状態を確認"""
    is_authenticated = spotify_auth.is_authenticated()
    token_info = spotify_auth._token_info # トークン情報を直接取得
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
    cleared = spotify_auth.clear_cache() # SpotifyAuth側に実装した想定
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
    return spotify_auth._token_info 