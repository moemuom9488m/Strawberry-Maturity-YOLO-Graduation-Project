"""
error_logger.py
===============
全局錯誤日誌記錄工具，供整個專案（包含訓練、影片偵測等）使用。
每次呼叫 log_error() 時會：
  1. 將完整 traceback 寫入 training_logs/detection_errors.log
  2. 在 console 印出簡短提示
"""

import os
import traceback
import datetime

# 日誌存放資料夾（退回上一層專案根目錄，存入 training_logs）
LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "training_logs")
LOG_FILE = os.path.join(LOG_DIR, "detection_errors.log")


def _ensure_log_dir():
    os.makedirs(LOG_DIR, exist_ok=True)


def log_error(e: Exception, context: str = "影片偵測"):
    """
    記錄錯誤到日誌檔案。
    
    Parameters
    ----------
    e       : 捕捉到的 Exception 物件
    context : 發生錯誤的情境說明字串
    """
    _ensure_log_dir()

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    tb_str = traceback.format_exc()

    log_entry = (
        f"\n{'='*60}\n"
        f"[{timestamp}] ❌ 錯誤發生於：{context}\n"
        f"錯誤類型：{type(e).__name__}\n"
        f"錯誤訊息：{e}\n"
        f"完整 Traceback：\n{tb_str}"
        f"{'='*60}\n"
    )

    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(log_entry)

    print(f"\n❌ {context} 時發生錯誤: {e}")
    print(f"📝 完整錯誤日誌已記錄至: {LOG_FILE}")


def print_recent_errors(n: int = 5):
    """印出最近 n 筆錯誤記錄，方便在 Notebook 內快速查閱。"""
    if not os.path.exists(LOG_FILE):
        print("📋 目前尚無錯誤日誌。")
        return

    with open(LOG_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    entries = content.split("=" * 60)
    # 過濾空白項
    entries = [e.strip() for e in entries if e.strip()]
    recent = entries[-n:]
    
    print(f"\n📋 最近 {len(recent)} 筆錯誤記錄：\n")
    for entry in recent:
        print("=" * 60)
        print(entry)
    print("=" * 60)
