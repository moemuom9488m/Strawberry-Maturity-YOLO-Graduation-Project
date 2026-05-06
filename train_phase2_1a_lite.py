# train_phase2_1a_lite.py (針對一般訓練機)
import os, sys
# 確保能引用到同目錄下的 train_all.py
sys.path.append(os.getcwd())
from train_all import train_model

# 指定 Phase 1 的 S-Baseline 權重路徑
BEST_1A_WEIGHTS = "runs/detect/exp1a_yolo11s_baseline/weights/best.pt"

if __name__ == "__main__":
    if not os.path.exists(BEST_1A_WEIGHTS):
        print(f"❌ 錯誤：找不到基礎權重 {BEST_1A_WEIGHTS}")
    else:
        print("🚀 啟動 Phase 2 分支：[1a] S-Baseline 深度探討")
        # 解析度測試：640, 800, 1024
        train_model(BEST_1A_WEIGHTS, "exp2a_1a_img640",  dict(imgsz=640,  epochs=150, batch=96, freeze=10, lr0=0.005))
        train_model(BEST_1A_WEIGHTS, "exp2b_1a_img800",  dict(imgsz=800,  epochs=150, batch=72, freeze=10, lr0=0.005))
        train_model(BEST_1A_WEIGHTS, "exp2c_1a_img1024", dict(imgsz=1024, epochs=150, batch=32, freeze=10, lr0=0.005))