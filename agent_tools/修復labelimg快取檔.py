import os
from pathlib import Path

def reset_labelimg_settings():
    # 取得使用者家目錄，例如 C:\Users\0419mch
    home_dir = Path.home()
    settings_file = home_dir / ".labelImgSettings.pkl"

    if settings_file.exists():
        try:
            os.remove(settings_file)
            print(f"✅ 成功刪除設定檔: {settings_file}")
            print("現在你可以重新啟動 labelImg 試試看了。")
        except Exception as e:
            print(f"❌ 刪除失敗: {e}")
    else:
        print(f"🔍 找不到設定檔: {settings_file}")
        print("可能檔案已經被刪除，或存放在不同位置。")

if __name__ == "__main__":
    reset_labelimg_settings()