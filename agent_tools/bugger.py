#pip install icrawler bing-image-downloader
from bing_image_downloader import downloader
import os
import shutil
from icrawler.builtin import GoogleImageCrawler, BaiduImageCrawler 

# --- 設定 ---
IMAGE_LIMIT = 20  # 每個類別的目標圖片數量
TIMEOUT = 20      # 下載超時
BASE_SOURCE_DIR = "negative_dataset_v2"  # 存放所有圖片的根資料夾
DOWNLOAD_SOURCE = 1  # 1: Bing, 2: Google, 3: Baidu
LANG = "en"  # ✅ 切換語言： "zh" 中文 ｜ "en" 英文

# --- 類別列表 ---
english_CLASSES = [
    "RedBerryStickeronBox",
    "RedCrateFieldView",
    "RedDeliveryBoxonGround",
    
    "StrawberryEatingSelfie",
    "StrawberryHarvestPersonPicking",
    "handholdingstrawberrycloseup",
]

chinese_CLASSES = []

# 根據語言切換
if LANG == "en":
    target_CLASSES = english_CLASSES
    print("目前語言：英文模式 (English mode)")
else:
    target_CLASSES = chinese_CLASSES
    print("目前語言：中文模式 (Chinese mode)")

# -------------------------------------------------------------
# --- 輔助函數 ---
def get_file_count(directory):
    """計算資料夾中檔案數量"""
    if not os.path.isdir(directory):
        return 0
    return sum(os.path.isfile(os.path.join(directory, f)) for f in os.listdir(directory))

# --- 下載函數 ---
def download_bing_images(query, limit, output_dir):
    print(f"-> 使用 Bing 下載: {query} ...")

    # Bing 預設會建立 output_dir/query，所以這裡先記錄下來
    pre_existing = set(os.listdir(output_dir))

    downloader.download(
        query,
        limit=limit,
        output_dir=output_dir,
        adult_filter_off=True,
        force_replace=False,
        timeout=TIMEOUT,
        verbose=True
    )

    # 🔧 Bing 多產生一層資料夾時直接搬上來
    created_folders = [f for f in os.listdir(output_dir)
                       if os.path.isdir(os.path.join(output_dir, f)) and f not in pre_existing]
    for folder in created_folders:
        inner = os.path.join(output_dir, folder)
        for file in os.listdir(inner):
            shutil.move(os.path.join(inner, file), os.path.join(output_dir, file))
        shutil.rmtree(inner)

def download_google_images(query, limit, output_dir):
    print(f"-> 使用 Google 下載: {query} ...")
    crawler = GoogleImageCrawler(
        storage={"root_dir": output_dir},
        downloader_threads=4,
        feeder_threads=1,
        parser_threads=1
        # ❌ 移除 downloader_kwargs，icrawler 新版本不支援
    )
    crawler.crawl(keyword=query, max_num=limit, min_size=(224, 224))


def download_baidu_images(query, limit, output_dir):
    crawler = BaiduImageCrawler(
        storage={"root_dir": output_dir},
        downloader_threads=4
    )
    print(f"-> 使用 Baidu 下載: {query} ...")
    crawler.crawl(keyword=query, max_num=limit, min_size=(224, 224))

# -------------------------------------------------------------
# --- 主程式 ---
if not os.path.exists(BASE_SOURCE_DIR):
    os.makedirs(BASE_SOURCE_DIR)

print("--- 開始下載圖片 ---")

for class_name in target_CLASSES:
    final_target_folder = os.path.join(BASE_SOURCE_DIR, class_name)
    os.makedirs(final_target_folder, exist_ok=True)

    current_count = get_file_count(final_target_folder)
    needed_count = IMAGE_LIMIT - current_count

    if needed_count <= 0:
        print(f"'{class_name}' 已有 {current_count} 張圖片，跳過。")
        continue

    print(f"'{class_name}' 目前有 {current_count} 張，還需要下載 {needed_count} 張...")

    if DOWNLOAD_SOURCE == 1:
        download_bing_images(class_name, needed_count, final_target_folder)
    elif DOWNLOAD_SOURCE == 2:
        download_google_images(class_name, needed_count, final_target_folder)
    elif DOWNLOAD_SOURCE == 3:
        download_baidu_images(class_name, needed_count, final_target_folder)
    else:
        print("ERROR: DOWNLOAD_SOURCE 設定錯誤，請設定為 1 (Bing), 2 (Google), 3 (Baidu)")

print("--- 全部下載完成 ---")
print(f"✅ 請到 '{BASE_SOURCE_DIR}' 資料夾查看圖片")
