import os
import sys
import argparse
import time
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle

# Reconfigure stdout to use UTF-8 to prevent encoding issues on Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

"""
🎥 草莓監測機器人：YouTube API 自動化影片上傳工具
---
本腳本用於自動將「偵測結果影片」中的 .mp4 檔案自動上傳至 YouTube 作為成果展示與備份。

依賴安裝：
    C:\ProgramData\anaconda3\envs\pytorch\python.exe -m pip install google-api-python-client google-auth-oauthlib google-auth-httplib2

使用前置作業：
    1. 前往 Google Cloud Console (https://console.cloud.google.com/) 建立專案。
    2. 啟用 "YouTube Data API v3"。
    3. 建立 "OAuth 2.0 用戶端 ID" 憑證（應用程式類型選擇「電腦版」）。
    4. 下載 credentials.json，並將其放置於 agent_tools/ 目錄下。
    5. 首次執行本程式時，會彈出瀏覽器視窗請求 YouTube 權限，授權後會自動在本地生成 token.pickle，此後執行即可免登入自動化上傳。
"""

# 設定作用域：允許管理您的 YouTube 影片
SCOPES = ['https://www.googleapis.com/auth/youtube.upload']

def get_authenticated_service(credentials_path='agent_tools/credentials.json', token_path='agent_tools/token.pickle'):
    creds = None
    # 讀取已快取的 token
    if os.path.exists(token_path):
        with open(token_path, 'rb') as token:
            creds = pickle.load(token)
            
    # 如果沒有 token 或已失效，則重新進行 OAuth2 授權流程
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("🔄 正在透過 Refresh Token 刷新憑證...")
            creds.refresh(Request())
        else:
            if not os.path.exists(credentials_path):
                raise FileNotFoundError(
                    f"❌ 找不到 OAuth 2.0 憑證檔案: {credentials_path}\n"
                    "請先前往 Google Cloud Console 下載憑證並命名為 credentials.json 放入 agent_tools/ 中。"
                )
            print("🔑 正在啟動瀏覽器進行 OAuth 2.0 授權登入...")
            flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
            creds = flow.run_local_server(port=0)
            
        # 儲存 token 供下次使用
        with open(token_path, 'wb') as token:
            pickle.dump(creds, token)
            
    return build('youtube', 'v3', credentials=creds)

def upload_video(youtube, video_path, title, description, category_id="28", privacy_status="unlisted"):
    """
    自動上傳影片到 YouTube
    ---
    參數:
        category_id: "28" 代表 "Science & Technology" (科學與技術)
        privacy_status: "public" (公開), "private" (私人), "unlisted" (不公開 - 推薦專題展示用)
    """
    if not os.path.exists(video_path):
        print(f"❌ 找不到影片檔案: {video_path}")
        return None

    print(f"🎬 準備上傳影片: {os.path.basename(video_path)}")
    print(f"   - 標題: {title}")
    print(f"   - 狀態: {privacy_status}")

    body = {
        'snippet': {
            'title': title,
            'description': description,
            'categoryId': category_id,
            'tags': ['草莓監測', 'YOLOv11', 'CCPP路徑規劃', '畢業專題']
        },
        'status': {
            'privacyStatus': privacy_status,
            'selfDeclaredMadeForKids': False
        }
    }

    # 建立分塊上傳要求 (Resumable Upload)
    media = MediaFileUpload(video_path, chunksize=1024*1024, resumable=True)
    request = youtube.videos().insert(
        part=','.join(body.keys()),
        body=body,
        media_body=media
    )

    response = None
    print("🚀 開始上傳至 YouTube...")
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"   - 上傳進度: {int(status.progress() * 100)}% ...")
            
    video_id = response.get('id')
    video_url = f"https://www.youtube.com/watch?v={video_id}"
    print("\n✅ 影片上傳成功！")
    print(f"🔗 YouTube 連結: {video_url}")
    return video_url

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="YouTube API 自動影片上傳工具")
    parser.add_argument('--video', type=str, required=True, help="影片檔案路徑")
    parser.add_argument('--title', type=str, default="草莓成熟度監測機器人 - 成果展示", help="影片標題")
    parser.add_argument('--desc', type=str, default="畢業專案：結合 YOLOv11 與雙側相機 CCPP 之草莓成熟度監測系統實車成果。", help="影片說明描述")
    parser.add_argument('--privacy', type=str, default="unlisted", choices=['public', 'private', 'unlisted'], help="隱私狀態")
    
    args = parser.parse_args()
    
    try:
        youtube_service = get_authenticated_service()
        upload_video(
            youtube=youtube_service,
            video_path=args.video,
            title=args.title,
            description=args.desc,
            privacy_status=args.privacy
        )
    except Exception as e:
        print(f"❌ 發生錯誤: {e}")
