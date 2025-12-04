import streamlit as st
import pandas as pd

# ページ設定
st.set_page_config(page_title="社員名鑑", layout="wide")

import re
import requests
from io import BytesIO
import gspread
from google.oauth2.service_account import Credentials

def convert_google_drive_url(url):
    """
    Googleドライブの共有URLを直接表示可能なURLに変換する
    対応フォーマット:
    - https://drive.google.com/open?id=FILE_ID
    - https://drive.google.com/file/d/FILE_ID/view
    - https://drive.google.com/uc?id=FILE_ID
    """
    if not isinstance(url, str):
        return ""
    
    # 正規表現でファイルIDを抽出
    # パターン1: id=パラメータ (open?id=..., uc?id=...)
    match_id = re.search(r'[?&]id=([^&]+)', url)
    if match_id:
        return f"https://drive.google.com/thumbnail?id={match_id.group(1)}&sz=w1000"
    
    # パターン2: パス内のID (file/d/...)
    match_path = re.search(r'/file/d/([^/]+)', url)
    if match_path:
        return f"https://drive.google.com/thumbnail?id={match_path.group(1)}&sz=w1000"

    return url

@st.cache_data(show_spinner=False)
def fetch_image(url):
    """
    サーバー側で画像をダウンロードして返す
    キャッシュを使用してパフォーマンスを向上
    """
    if not url:
        return None
    
    try:
        # URLを変換
        converted_url = convert_google_drive_url(url)
        
        # 画像をダウンロード
        response = requests.get(converted_url, timeout=10)
        response.raise_for_status()
        
        # 画像のバイトデータを返す
        return BytesIO(response.content)
    except Exception as e:
        st.error(f"画像の読み込みに失敗しました: {e}")
        return None

@st.cache_resource
def get_google_sheets_client():
    """
    Google Sheets APIクライアントを初期化
    st.secretsから認証情報を取得
    """
    try:
        # 認証情報をst.secretsから取得
        credentials_dict = dict(st.secrets["gcp_service_account"])
        
        # 認証情報を作成
        credentials = Credentials.from_service_account_info(
            credentials_dict,
            scopes=[
                "https://www.googleapis.com/auth/spreadsheets.readonly",
                "https://www.googleapis.com/auth/drive.readonly"
            ]
        )
        
        # Google Sheetsクライアントを返す
        return gspread.authorize(credentials)
    except Exception as e:
        st.error(f"Google Sheets APIの初期化に失敗しました: {e}")
        st.info("認証情報が正しく設定されているか確認してください。")
        return None

@st.cache_data(ttl=600)  # 10分間キャッシュ
def load_data_from_sheets():
    """
    Google Sheetsからデータを読み込む
    """
    try:
        # Google Sheetsクライアントを取得
        client = get_google_sheets_client()
        if client is None:
            return None
        
        # スプレッドシートIDを取得
        spreadsheet_key = st.secrets["spreadsheet_key"]
        
        # スプレッドシートを開く
        sheet = client.open_by_key(spreadsheet_key)
        
        # 最初のワークシートを取得
        worksheet = sheet.get_worksheet(0)
        
        # データを取得してDataFrameに変換
        data = worksheet.get_all_records()
        df = pd.DataFrame(data)
        
        return df
    except Exception as e:
        st.error(f"データの読み込みに失敗しました: {e}")
        return None

def main():
    st.title("社員名鑑")

    # デバッグ用
    # st.write("Available secrets:", list(st.secrets.keys()))
    
    # データの読み込み
    df = load_data_from_sheets()
    
    if df is None:
        st.error("データの読み込みに失敗しました。")
        st.info("Google Sheetsの設定を確認してください。")
        return
    
    if df.empty:
        st.warning("データが空です。")
        return

    # サイドバーの設定
    st.sidebar.header("検索フィルター")

    # 質問1（所属部署など）のフィルター
    # ユニークな値を抽出して選択肢にする
    options_q1 = df["質問1"].unique().tolist()
    selected_q1 = st.sidebar.multiselect("所属部署 (質問1)", options_q1, default=options_q1)

    # 質問2（スキルなど）のフィルター
    options_q2 = df["質問2"].unique().tolist()
    selected_q2 = st.sidebar.multiselect("スキル (質問2)", options_q2, default=options_q2)

    # フィルタリング実行
    # 選択された条件のいずれかに合致するものではなく、
    # ユーザーの要件「すべての条件（AND条件）」は、
    # 「部署が選択されたものの中にあり」かつ「スキルが選択されたものの中にある」という意味で解釈するのが一般的。
    # つまり、レコードの部署がselected_q1に含まれ、かつレコードのスキルがselected_q2に含まれるものを表示。
    
    filtered_df = df[
        (df["質問1"].isin(selected_q1)) &
        (df["質問2"].isin(selected_q2))
    ]

    st.write(f"該当件数: {len(filtered_df)} 件")

    # グリッド表示
    # 3列のカラムを作成
    cols_per_row = 3
    
    # 行ごとにループ
    for i in range(0, len(filtered_df), cols_per_row):
        cols = st.columns(cols_per_row)
        # 列ごとにループ
        for j in range(cols_per_row):
            if i + j < len(filtered_df):
                row = filtered_df.iloc[i + j]
                with cols[j]:
                    # カード風の表示
                    with st.container(border=True):
                        # サーバー側で画像を取得
                        image_data = fetch_image(row["顔写真"])
                        
                        # 画像表示
                        if image_data:
                            st.image(image_data, use_container_width=True)
                        else:
                            st.write("画像を読み込めませんでした")
                        
                        st.subheader(row["名前"])
                        st.write(f"**部署:** {row['質問1']}")
                        st.write(f"**スキル:** {row['質問2']}")

if __name__ == "__main__":
    main()
