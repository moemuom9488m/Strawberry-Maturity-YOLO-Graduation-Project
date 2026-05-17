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
    
    # 自動將連結寫入 偵測結果影片/README.md 紀錄檔中
    try:
        update_markdown_record(video_path, video_url, title, privacy_status)
    except Exception as e:
        print(f"⚠️ 無法更新 Markdown 紀錄檔: {e}")
        
    return video_url

def update_markdown_record(video_path, video_url, title, privacy_status):
    """
    自動將上傳成功的 YouTube 播放連結寫入 偵測結果影片/README.md。
    """
    markdown_path = '偵測結果影片/README.md'
    os.makedirs(os.path.dirname(markdown_path), exist_ok=True)
    
    headers = [
        "# 🎬 YouTube 成果影片上傳紀錄",
        "",
        "本目錄下的辨識成果影片已自動同步備份至 YouTube，點選下方連結即可直接在線上檢視影片：",
        "",
        "| 上傳時間 | 影片名稱 / 日期編號 | YouTube 播放連結 | 隱私狀態 |",
        "| :--- | :--- | :--- | :--- |"
    ]
    
    existing_lines = []
    if os.path.exists(markdown_path):
        with open(markdown_path, 'r', encoding='utf-8') as f:
            existing_lines = f.readlines()
            
    # 如果檔案不存在或格式不合，使用預設標頭
    if not existing_lines or not any("| YouTube 播放連結 |" in line for line in existing_lines):
        lines = [h + "\n" for h in headers]
    else:
        lines = [line for line in existing_lines if line.strip() or line == "\n"]
        
    # 取得台北時間
    upload_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    
    privacy_zh = {
        "public": "🟢 公開 (Public)",
        "unlisted": "🟡 不公開 (Unlisted)",
        "private": "🔴 私人 (Private)"
    }.get(privacy_status, privacy_status)
    
    # 新增一列紀錄
    new_row = f"| {upload_time} | **{title}** | [點此線上觀看 📺]({video_url}) | {privacy_zh} |\n"
    lines.append(new_row)
    
    with open(markdown_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)
        
    print(f"📝 已成功將 YouTube 播放連結記錄至 {markdown_path}！")

import re

def parse_title_from_filename(video_path):
    """
    依照檔名上面的日期及編號自動解析生成 YouTube 影片標題。
    例如：
      - best_20260505_模擬_2.mp4 ➡️ 20260505 模擬 2
      - 模擬_1_20260505_output.mp4 ➡️ 20260505 模擬 1
    """
    basename = os.path.basename(video_path)
    name_without_ext = os.path.splitext(basename)[0]
    
    # 尋找 8 位數日期 (如 20260505)
    date_match = re.search(r'\d{8}', name_without_ext)
    date_str = date_match.group(0) if date_match else ""
    
    # 尋找編號 (排除已找到的日期數字)
    temp_name = name_without_ext.replace(date_str, "") if date_str else name_without_ext
    num_match = re.search(r'\d+', temp_name)
    num_str = num_match.group(0) if num_match else ""
    
    if date_str and num_str:
        return f"{date_str} 模擬 {num_str}"
    elif date_str:
        return f"{date_str} 成果影片"
    return name_without_ext

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="YouTube API 自動影片上傳工具")
    parser.add_argument('--video', type=str, required=True, help="影片檔案路徑")
    parser.add_argument('--title', type=str, default=None, help="影片標題 (預設會自動從檔名解析日期與編號)")
    parser.add_argument('--desc', type=str, default="畢業專案：結合 YOLOv11 與雙側相機 CCPP 之草莓成熟度監測系統實車成果。", help="影片說明描述")
    parser.add_argument('--privacy', type=str, default="unlisted", choices=['public', 'private', 'unlisted'], help="隱私狀態")
    
    args = parser.parse_args()
    
    # 如果使用者沒有指定標題，自動從檔案名稱解析日期與編號
    final_title = args.title
    if final_title is None:
        final_title = parse_title_from_filename(args.video)
    
    try:
        youtube_service = get_authenticated_service()
        upload_video(
            youtube=youtube_service,
            video_path=args.video,
            title=final_title,
            description=args.desc,
            privacy_status=args.privacy
        )
    except Exception as e:
        print(f"❌ 發生錯誤: {e}")
