import os
import gc
import torch
from ultralytics import YOLO
import wandb

# 1. 環境整理
gc.collect()
torch.cuda.empty_cache()

# 2. 設定 WandB 專案名稱
os.environ["WANDB_PROJECT"] = "Strawberry_YOLOv11"

def run_small_test():
    print("🚀 啟動 WandB 連線小測試...")
    
    # 3. 強制初始化 WandB (確保在 online 模式)
    run = wandb.init(project="Strawberry_YOLOv11", name="wandb_test_run", mode="online")
    
    # 載入極小模型以節省資源 (Nano)
    model = YOLO("yolo11n.pt") 
    
    # 執行 1 個 Epoch 的訓練
    results = model.train(
        data="strawberry-maturity-yolo-graduate-1/data.yaml",
        epochs=1,
        imgsz=640,
        batch=8,
        device="cuda:0",
        project="Strawberry_YOLOv11",
        name="wandb_test_run",
        verbose=True,
        plots=False,
        exist_ok=True
    )
    
    print("✅ 測試訓練完成，請檢查 WandB 儀表板。")
    run.finish()

if __name__ == "__main__":
    try:
        run_small_test()
    except Exception as e:
        print(f"❌ 測試失敗: {e}")
