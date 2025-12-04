import pandas as pd
import re
import urllib.request
import urllib.error

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

def check_images():
    try:
        df = pd.read_csv("data.csv")
    except FileNotFoundError:
        print("data.csv not found")
        return

    print(f"Checking {len(df)} images...")
    
    for index, row in df.iterrows():
        original_url = row["顔写真"]
        converted_url = convert_google_drive_url(original_url)
        
        print(f"\nRow {index+1}: {row['名前']}")
        print(f"Original: {original_url}")
        print(f"Converted: {converted_url}")
        
        try:
            # Check if URL is accessible
            req = urllib.request.Request(converted_url, method='HEAD')
            # Google Drive sometimes blocks HEAD requests or requires cookies.
            # Let's try GET with a small range or just open it.
            # Actually, let's just try to open it and read headers.
            
            # Using a User-Agent is sometimes helpful
            req.add_header('User-Agent', 'Mozilla/5.0')
            
            # Disable SSL verification for debugging purposes
            import ssl
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            
            with urllib.request.urlopen(req, timeout=10, context=ctx) as response:
                status_code = response.getcode()
                content_type = response.headers.get('Content-Type')
                
                print(f"Status Code: {status_code}")
                print(f"Content-Type: {content_type}")
                
                if status_code == 200 and 'image' in content_type:
                    print("Result: OK (Image accessible)")
                elif 'text/html' in content_type:
                    print("Result: WARNING (Returned HTML instead of image - likely Google Drive viewer or virus scan warning)")
                else:
                    print("Result: ERROR (Not an image)")
                
        except urllib.error.HTTPError as e:
            print(f"Result: ERROR (HTTP {e.code}: {e.reason})")
        except Exception as e:
            print(f"Result: ERROR (Exception: {e})")

if __name__ == "__main__":
    check_images()
