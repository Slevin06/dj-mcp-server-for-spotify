# 非エンジニア向け Spotify MCP サーバー 簡単セットアップガイド

このガイドでは、プログラミングの専門知識がない方でも、ご自身のコンピュータで Spotify MCP サーバーを簡単にセットアップして実行するための手順を説明します。

## 1. はじめに

このサーバーをセットアップすると、AI アシスタント (例: Cursor, ChatGPT カスタム GPTs など) からあなたの Spotify を操作できるようになります。例えば、「リラックスできる音楽をかけて」とお願いするだけで、AI が自動で音楽を選んで再生してくれます。

## 2. 必要なもの

- インターネット接続
- Windows, macOS, または Linux が動作するコンピュータ
- Spotify アカウント (無料版でも利用可能ですが、一部機能に制限がある場合があります)

## 3. 事前準備：基本ツールのインストール

サーバーを動かすためには、いくつかの基本的なツールをコンピュータにインストールする必要があります。

### 3.1. Git のインストール

Git は、プロジェクトのファイルをダウンロードするために使います。

- **Windows**: [gitforwindows.org](https://gitforwindows.org/) からインストーラーをダウンロードし、画面の指示に従ってインストールしてください。特に設定を変更する必要はありません、デフォルトのままで大丈夫です。
- **macOS**: ターミナルを開き、`git --version` と入力してください。コマンドが見つからない旨のメッセージが表示されたら、開発者ツールのインストールを促すダイアログが表示されるので、「インストール」をクリックしてください。もしくは、[brew.sh](https://brew.sh/) (Homebrew) をインストール後、ターミナルで `brew install git` を実行してください。
- **Linux**: ターミナルを開き、お使いのディストリビューションのパッケージマネージャでインストールします。例:
  - Debian/Ubuntu: `sudo apt update && sudo apt install git`
  - Fedora: `sudo dnf install git`

### 3.2. Python のインストール

Python は、サーバープログラムを実行するためのプログラミング言語です。

- **Windows**: [python.org のダウンロードページ](https://www.python.org/downloads/windows/) から最新版の Python インストーラーをダウンロードします。インストーラーを実行する際、**必ず「Add Python X.X to PATH」というチェックボックスにチェックを入れてください。** これを忘れると、後で問題が発生する可能性があります。
- **macOS**: [python.org のダウンロードページ](https://www.python.org/downloads/macos/) から macOS 用のインストーラーをダウンロードし、実行してください。通常、macOS には古いバージョンの Python がプリインストールされていますが、最新版をインストールすることを推奨します。
- **Linux**: 多くの Linux ディストリビューションには Python 3 がプリインストールされています。ターミナルで `python3 --version` を実行して確認してください。もしインストールされていなければ、パッケージマネージャでインストールします。例:
  - Debian/Ubuntu: `sudo apt update && sudo apt install python3 python3-pip python3-venv`
  - Fedora: `sudo dnf install python3 python3-pip`

### 3.3. `uv` のインストール (スクリプト内で自動試行されます)

`uv` は Python のパッケージ管理を高速に行うツールです。これは後の手順で実行するスクリプトが自動でインストールを試みますが、もしうまくいかない場合は手動でインストールできます。

- ターミナル (Windows ではコマンドプロンプトまたは PowerShell) を開き、以下のコマンドを実行します:
  ```bash
  pip install uv
  ```
  または macOS/Linux の場合:
  ```bash
  curl -LsSf https://astral.sh/uv/install.sh | sh
  ```

## 4. サーバープロジェクトのダウンロード

1. ターミナル (Windows では Git Bash またはコマンドプロンプト) を開きます。
2. プロジェクトを保存したいディレクトリに移動します。例えば、デスクトップに `SpotifyServer` というフォルダを作ってそこに保存する場合:
   - macOS/Linux: `mkdir ~/Desktop/SpotifyServer && cd ~/Desktop/SpotifyServer`
   - Windows: `mkdir %USERPROFILE%\Desktop\SpotifyServer && cd %USERPROFILE%\Desktop\SpotifyServer`
3. 次のコマンドを実行して、プロジェクトファイルをダウンロードします:
   ```bash
   git clone https://github.com/USERNAME/dj-mcp-server-for-spotify.git
   ```
   **(注意: `USERNAME/dj-mcp-server-for-spotify.git` の部分は実際のリポジトリの URL に置き換えてください。このガイドでは仮の URL です。)**
4. ダウンロードが完了したら、プロジェクトフォルダに移動します:
   ```bash
   cd dj-mcp-server-for-spotify
   ```

## 5. `.env` 環境設定ファイルの準備

サーバーが Spotify API に接続するためには、API キーなどの情報が必要です。これを `.env` というファイルに保存します。

1. プロジェクトフォルダ内に `.env.example` というファイルがあります。これをコピーして `.env` という名前に変更します。
   - エクスプローラーや Finder でファイルをコピー＆ペーストして名前を変更するか、ターミナルで以下のコマンドを実行します:
     - macOS/Linux: `cp .env.example .env`
     - Windows: `copy .env.example .env`
2. `.env` ファイルをテキストエディタ (メモ帳、VSCode、Sublime Text など) で開きます。
3. 以下の項目を設定します:

   - `SPOTIFY_CLIENT_ID`: あなたの Spotify Client ID に書き換えます。
   - `SPOTIFY_CLIENT_SECRET`: あなたの Spotify Client Secret に書き換えます。
   - `SPOTIFY_REDIRECT_URI`: 通常は `http://127.0.0.1:8000/callback` のままで大丈夫です。

   これらの情報は、[Spotify Developer Dashboard](https://developer.spotify.com/dashboard/) から取得できます。
   a. Dashboard にログインし、「Create App」または既存のアプリを選択します。
   b. Client ID と Client Secret が表示されますので、これをコピーして `.env` ファイルに貼り付けます。
   c. アプリの設定画面で、「Edit Settings」をクリックし、「Redirect URIs」に `http://127.0.0.1:8000/callback` を追加して保存します。

**重要:** `.env` ファイルは秘密の情報を含みますので、他人に見せたり、インターネット上にアップロードしたりしないでください。

## 6. サーバーのセットアップと実行

プロジェクトフォルダ内で、お使いの OS に合わせたスクリプトを実行します。

- **Windows の場合:**

  1. `run.bat` ファイルをダブルクリックして実行します。
  2. セキュリティの警告が表示された場合は、実行を許可してください。

- **macOS / Linux の場合:**
  1. ターミナルを開き、プロジェクトフォルダにいることを確認します。
  2. まず、スクリプトに実行権限を与えます (初回のみ):
     ```bash
     chmod +x run.sh
     ```
  3. 次に、スクリプトを実行します:
     ```bash
     ./run.sh
     ```

スクリプトが実行されると、必要なライブラリのインストールなどが自動で行われます。最後に「Starting the Spotify MCP Server...」のようなメッセージが表示されれば成功です。

## 7. Spotify 認証 (初回のみ)

サーバーを初めて起動した後、一度だけ Spotify アカウントとの連携認証を行う必要があります。

1. ウェブブラウザ (Chrome, Firefox, Safari など) を開きます。
2. アドレスバーに `http://127.0.0.1:8000/auth/login` と入力し、エンターキーを押します。
3. Spotify のログイン画面が表示されるので、あなたの Spotify アカウントでログインします。
4. アクセス許可を求める画面が表示されたら、内容を確認して「同意する」または「許可する」をクリックします。
5. 「認証成功！」のようなメッセージが表示されれば完了です。ブラウザのタブは閉じて構いません。

これで、サーバーがあなたの Spotify アカウントと連携されました。この認証情報はコンピュータに保存されるため、次回からはこの手順は不要です。

## 8. サーバーの停止

サーバーを停止するには、スクリプトを実行しているターミナルまたはコマンドプロンプトのウィンドウで、以下のキーを同時に押します:

- `Ctrl` + `C`

## 9. AI アシスタントからの利用

サーバーが起動していれば、AI アシスタントの設定で MCP サーバーとして `http://127.0.0.1:8000/mcp` を登録することで、Spotify の操作を依頼できるようになります。

## 10. トラブルシューティング

- **「Python が見つかりません」「pip が見つかりません」などのエラーが出る場合:**

  - Python のインストール時に「Add Python to PATH」にチェックを入れ忘れた可能性があります。Python を再インストールし、必ずチェックを入れてください。
  - または、環境変数の設定がうまくいっていない可能性があります。

- **スクリプト実行中に赤い文字でエラーがたくさん表示される場合:**

  - 依存関係のインストールに失敗している可能性があります。インターネット接続を確認してください。
  - `.env` ファイルの設定が間違っているか、API キーが無効な可能性があります。

- **認証後も AI アシスタントから操作できない場合:**
  - サーバーが正しく起動しているか確認してください。
  - AI アシスタントに設定した MCP サーバーの URL (`http://127.0.0.1:8000/mcp`) が正しいか確認してください。
  - ファイアウォールが通信をブロックしていないか確認してください。

問題が解決しない場合は、エラーメッセージをコピーして開発者に問い合わせてください。
