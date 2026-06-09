import os, torch, gc, shutil, sys, logging, warnings, time
from datetime import datetime
from ultralytics import YOLO
import pandas as pd
from agent_tools import yolo_utils

# ── 1. 全域常數設定 ──
RUNS_DIR = "runs/detect"
BEST_WEIGHTS_DIR = "best_weights"
LOG_DIR = "logs"
PROJECT_NAME = "Strawberry_YOLOv11_4060ti"

# WandB 設定
os.environ["WANDB_PROJECT"] = PROJECT_NAME

# 相對路徑設定
DATA_YAML = "strawberry-maturity-yolo-graduate-1/data.yaml"
CUSTOM_M_YAML = "yolo11-strawberry-p2-cbam-m.yaml"
CUSTOM_S_YAML = "yolo11-strawberry-p2-cbam-s.yaml"

# ── 2. 基礎訓練參數 (針對 4060 Ti 16G 穩定性優化) ──
BASE_TRAIN_KWARGS = dict(
    data        = DATA_YAML,
    epochs      = 300,
    patience    = 100,
    batch       = 16,
    imgsz       = 640,
    device      = 0,
    workers     = 0,      # Windows 環境設為 0 最穩定，避開無限迴圈
    cache       = 'RAM',  # 啟用 RAM 快取提升速度
    save        = True,
    exist_ok    = True,   # 確保資料夾名稱固定，方便搬移
    pretrained  = True,
    verbose     = False,
    plots       = False,
    optimizer   = 'AdamW',
    seed        = 42,
    hsv_h=0.015, hsv_s=0.7, hsv_v=0.4,
    degrees=15.0, translate=0.1, scale=0.5,
    fliplr=0.5, flipud=0.1,
    mosaic=1.0, mixup=0.1, copy_paste=0.1,
    erasing=0.4,
)

# ── 3. 核心訓練函式 (全域) ──
def train_model(model_path: str, run_name: str, extra_kwargs: dict = None):
    # 確保自定義模組已註冊 (移入內部以提升 Windows 穩定性)
    yolo_utils.register_yolo_modules()
    
    run_dir = os.path.join(RUNS_DIR, run_name)
    result_csv = os.path.join(run_dir, "results.csv")
    completed_marker = os.path.join(run_dir, ".completed")
    
    if os.path.exists(completed_marker):
        print(f"✅ 找到已完成標記，跳過訓練：{run_name}")
        return None
        
    if run_name in ["exp1a_yolo11s_baseline", "exp1b_yolo11m_baseline"] and os.path.exists(result_csv):
        print(f"✅ 找到已手動保留的訓練結果，跳過訓練：{run_name}")
        return None
    
    if os.path.exists(run_dir):
        print(f"⚠️ 偵測到未完成的殘留實驗資料夾，正在清理以重新訓練：{run_name}")
        shutil.rmtree(run_dir, ignore_errors=True)
    
    gc.collect()
    torch.cuda.empty_cache()
    print(f"\n{'='*60}\n🚀 開始訓練：{run_name}\n   模型：{model_path}\n{'='*60}\n")
    
    kwargs = {**BASE_TRAIN_KWARGS}
    if extra_kwargs:
        kwargs.update(extra_kwargs)
    
    # 臨時產出目錄
    temp_project = PROJECT_NAME
    model = YOLO(model_path)
    results = model.train(name=run_name, project=temp_project, **kwargs)
    
    # 搬移邏輯
    possible_srcs = [
        os.path.join(temp_project, run_name),
        os.path.join(RUNS_DIR, temp_project, run_name)
    ]
    src_dir = next((p for p in possible_srcs if os.path.exists(p)), None)
    
    if src_dir:
        # 🌟 核心改良：增加緩衝時間，讓 WandB 背景程序有時間關閉檔案鎖 (Windows 特有問題)
        print(f"⏳ 訓練結束，等待系統釋放檔案鎖 (10秒)...")
        time.sleep(10)
        
        try:
            os.makedirs(os.path.dirname(run_dir), exist_ok=True)
            if os.path.exists(run_dir):
                shutil.rmtree(run_dir, ignore_errors=True)
            
            shutil.move(src_dir, run_dir)
            print(f"✅ 結果已成功搬移至 {run_dir}")
        except Exception as e:
            print(f"⚠️ 搬移失敗，檔案可能仍被佔用: {e}")
            print(f"💡 請手動將 {src_dir} 搬移至 {run_dir}")
            
        try:
            parent_temp = os.path.dirname(src_dir)
            if os.path.exists(parent_temp) and not os.listdir(parent_temp):
                os.rmdir(parent_temp)
        except: pass
    else:
        print(f"⚠️ 警告：找不到產出目錄 {possible_srcs}")

    # 指標顯示
    best_map50 = results.results_dict.get("metrics/mAP50(B)", "N/A")
    print(f"\n📊 [{run_name}] 訓練完成 | mAP50 = {best_map50}")
    
    os.makedirs(os.path.dirname(completed_marker), exist_ok=True)
    with open(completed_marker, "w") as f:
        f.write(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    return results

# ── 4. 主自動化流程 ──
def main():
    try:
        os.makedirs(BEST_WEIGHTS_DIR, exist_ok=True)
        os.makedirs(LOG_DIR, exist_ok=True)

        # Phase 1: 基本架構比對
        print("\n🧪 開始 Phase 1：架構比對")
        train_model("yolo11s.pt", "exp1a_yolo11s_baseline", dict(batch=32))
        train_model("yolo11m.pt", "exp1b_yolo11m_baseline", dict(batch=16))
        train_model(CUSTOM_S_YAML, "exp1c_yolo11s_p2cbam", dict(batch=16))
        train_model(CUSTOM_M_YAML, "exp1d_yolo11m_p2cbam", dict(batch=12))

        print("\n✅ Phase 1 流程檢查完畢。")

    except Exception as e:
        print(f"❌ 發生錯誤: {e}")

if __name__ == "__main__":
    main()
