import json
import os

# 設定檔案路徑
train_ipynb_path = r"c:\Users\0419mch\Desktop\project_0414\yolo訓練程式碼.ipynb"

# 1. 讀取 Notebook
with open(train_ipynb_path, 'r', encoding='utf-8') as f:
    nb = json.load(f)

# 2. 定義新原始碼 (強制重置日誌等級)
new_stage1_source = [
    "#yolo訓練程式碼 (Stage 1)\n",
    "import os, torch, gc, sys, logging, warnings\n",
    "from ultralytics import YOLO\n",
    "from agent_tools import error_logger, yolo_utils\n",
    "\n",
    "# --- 🌟 初始化：環境優化與自定義模組 ---\n",
    "yolo_utils.register_yolo_modules()\n",
    "warnings.filterwarnings(\"ignore\", message=\".*deterministic.*\")\n",
    "warnings.filterwarnings(\"ignore\", category=UserWarning)\n",
    "try:\n",
    "    torch.use_deterministic_algorithms(False)\n",
    "except Exception: pass\n",
    "\n",
    "# --- 🛡️ 強制恢復日誌顯示 ---\n",
    "logging.getLogger(\"ultralytics\").setLevel(logging.INFO) # 🚀 強制重置為 INFO\n",
    "os.environ[\"YOLO_VERBOSE\"] = \"True\"                  # 🚀 強制環境變數為 True\n",
    "\n",
    "# --- 🛡️ 環境隔離 ---\n",
    "sys.argv = [sys.argv[0]]\n",
    "\n",
    "if __name__ == '__main__':\n",
    "    # 1. 顯存與變數清理\n",
    "    if 'model' in globals(): del model\n",
    "    gc.collect()\n",
    "    if torch.cuda.is_available():\n",
    "        torch.cuda.empty_cache()\n",
    "        DEVICE_ID = 0\n",
    "        print(f\"🔥 使用 GPU: {torch.cuda.get_device_name(0)}\")\n",
    "    else:\n",
    "        DEVICE_ID = 'cpu'\n",
    "\n",
    "    # 2. 參數設定\n",
    "    MODEL_CFG = \"yolo11-strawberry-p2-cbam-s.yaml\" \n",
    "    PRETRAINED_WEIGHTS = \"yolo11s.pt\"\n",
    "    DATA_YAML_PATH = \"roboflow_1000_側拍_split/data.yaml\"\n",
    "\n",
    "    try:\n",
    "        # 3. 建立模型\n",
    "        model = YOLO(MODEL_CFG).load(PRETRAINED_WEIGHTS)\n",
    "        print(f\"\\n🚀 啟動一階段訓練：{MODEL_CFG}\\n\")\n",
    "\n",
    "        # 4. 啟動訓練\n",
    "        model.train(\n",
    "            data=DATA_YAML_PATH,\n",
    "            epochs=300,\n",
    "            batch=32,\n",
    "            imgsz=640,\n",
    "            device=DEVICE_ID,\n",
    "            workers=4,\n",
    "            optimizer='AdamW',\n",
    "            lr0=0.001,\n",
    "            weight_decay=0.001,\n",
    "            cos_lr=True,\n",
    "            patience=30,\n",
    "            box=15.0,\n",
    "            cls=0.8,\n",
    "            multi_scale=False, \n",
    "            plots=True,       \n",
    "            verbose=True,     \n",
    "            # === 數據增強 ===\n",
    "            mosaic=1.0,\n",
    "            mixup=0.2,\n",
    "            copy_paste=0.02,\n",
    "            scale=0.5,\n",
    "            degrees=10.0,\n",
    "            fliplr=0.5,\n",
    "            hsv_h=0.015,\n",
    "            hsv_s=0.7,\n",
    "            hsv_v=0.4,\n",
    "            warmup_epochs=3.0,\n",
    "            close_mosaic=30\n",
    "        )\n",
    "        print(\"\\n✨ 一階段基礎訓練順利結束！\")\n",
    "    except Exception as e:\n",
    "        error_logger.log_error(e, context=\"YOLO 一階段基礎訓練\")\n",
    "        raise"
]

# 3. 替換 Cell
modified = False
for cell in nb['cells']:
    if cell['cell_type'] == 'code' and ('#yolo訓練程式碼' in "".join(cell['source']) or 'yolo11-strawberry-p2-cbam' in "".join(cell['source'])):
        cell['source'] = new_stage1_source
        cell['outputs'] = []
        modified = True
        break

# 4. 存檔
with open(train_ipynb_path, 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=1, ensure_ascii=False)

if modified:
    print("Success: Forced log level to INFO for Stage 1!")
else:
    print("Error: Target Stage 1 cell not found.")
