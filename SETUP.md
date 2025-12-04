# セットアップガイド

このアプリケーションは、Google Sheets APIを使用してスプレッドシートからデータを読み込みます。以下の手順に従ってセットアップしてください。

## 前提条件

- Googleアカウント
- Google Sheetsにデータが格納されたスプレッドシート

## 1. Google Cloud Platformでのセットアップ

### 1.1 プロジェクトの作成

1. [Google Cloud Console](https://console.cloud.google.com/)にアクセス
2. 新しいプロジェクトを作成（例: `employee-directory`）

### 1.2 Google Sheets APIの有効化

1. 左側のメニューから「APIとサービス」→「ライブラリ」を選択
2. 「Google Sheets API」を検索
3. 「有効にする」をクリック

### 1.3 サービスアカウントの作成

1. 左側のメニューから「APIとサービス」→「認証情報」を選択
2. 「認証情報を作成」→「サービスアカウント」を選択
3. サービスアカウント名を入力（例: `sheets-reader`）
4. 「作成して続行」をクリック
5. ロールは設定不要（スキップ）
6. 「完了」をクリック

### 1.4 サービスアカウントキーの作成

1. 作成したサービスアカウントをクリック
2. 「キー」タブを選択
3. 「鍵を追加」→「新しい鍵を作成」を選択
4. 「JSON」を選択して「作成」をクリック
5. JSONファイルがダウンロードされます（**このファイルは安全に保管してください**）

## 2. Google Sheetsの設定

### 2.1 スプレッドシートの共有

1. データが格納されたGoogle Sheetsを開く
2. 右上の「共有」ボタンをクリック
3. サービスアカウントのメールアドレス（`xxx@xxx.iam.gserviceaccount.com`）を追加
4. 権限を「閲覧者」に設定
5. 「送信」をクリック

### 2.2 スプレッドシートIDの取得

スプレッドシートのURLから、IDをコピーします:
```
https://docs.google.com/spreadsheets/d/SPREADSHEET_ID/edit
                                       ^^^^^^^^^^^^^^^^
                                       この部分がID
```

### 2.3 データ形式

スプレッドシートの1行目はヘッダー行として扱われます。以下の列が必要です:

| 名前 | 顔写真 | 質問1 | 質問2 |
|------|--------|-------|-------|
| 山田 太郎 | https://drive.google.com/... | 営業部 | Python |

## 3. ローカル環境のセットアップ

### 3.1 依存関係のインストール

```bash
pip install -r requirements.txt
```

### 3.2 認証情報の設定

1. `.streamlit/secrets.toml.example`を`.streamlit/secrets.toml`にコピー

```bash
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
```

2. `.streamlit/secrets.toml`を編集して、ダウンロードしたJSONファイルの内容を設定

```toml
[gcp_service_account]
type = "service_account"
project_id = "your-project-id"
private_key_id = "your-private-key-id"
private_key = "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
client_email = "your-service-account@your-project.iam.gserviceaccount.com"
client_id = "123456789"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "https://www.googleapis.com/robot/v1/metadata/x509/..."

spreadsheet_key = "YOUR_SPREADSHEET_ID_HERE"
```

**重要**: `private_key`の値は、改行を`\n`に置き換える必要があります。

### 3.3 アプリケーションの起動

```bash
streamlit run app.py
```

ブラウザで `http://localhost:8501` が自動的に開きます。

## 4. Streamlit Cloudへのデプロイ

### 4.1 GitHubリポジトリの準備

1. GitHubに新しいリポジトリを作成
2. コードをプッシュ（`.streamlit/secrets.toml`は`.gitignore`で除外されます）

```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git push -u origin main
```

### 4.2 Streamlit Cloudでのデプロイ

1. [Streamlit Cloud](https://share.streamlit.io/)にアクセス
2. GitHubアカウントでログイン
3. 「New app」をクリック
4. リポジトリ、ブランチ、メインファイル（`app.py`）を選択
5. 「Deploy」をクリック

### 4.3 Secretsの設定

1. デプロイ後、アプリの設定画面を開く
2. 「Settings」→「Secrets」を選択
3. `.streamlit/secrets.toml`の内容をそのままコピー&ペースト
4. 「Save」をクリック

アプリが自動的に再起動し、Google Sheetsからデータを読み込むようになります。

## トラブルシューティング

### エラー: "Google Sheets APIの初期化に失敗しました"

- `secrets.toml`の形式が正しいか確認
- サービスアカウントのJSONキーが正しくコピーされているか確認
- `private_key`の改行が`\n`に置き換えられているか確認

### エラー: "データの読み込みに失敗しました"

- スプレッドシートIDが正しいか確認
- スプレッドシートがサービスアカウントと共有されているか確認
- Google Sheets APIが有効化されているか確認

### 画像が表示されない

- Google Driveの画像URLが正しいか確認
- 画像がサービスアカウントと共有されているか確認（または「リンクを知っている全員」に公開）
