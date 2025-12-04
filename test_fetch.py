import re
import requests
from io import BytesIO

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

def fetch_image(url):
    """
    サーバー側で画像をダウンロードして返す
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
        print(f"画像の読み込みに失敗しました: {e}")
        return None

# Test
test_url = "https://drive.google.com/open?id=1l3eAEAhRQjCjM40HS9IPi-fzxGxKnbhh"
print(f"Testing URL: {test_url}")
print(f"Converted URL: {convert_google_drive_url(test_url)}")

image_data = fetch_image(test_url)
if image_data:
    print(f"Success! Downloaded {len(image_data.getvalue())} bytes")
else:
    print("Failed to download image")
