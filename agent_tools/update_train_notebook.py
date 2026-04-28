import json
import os

# 設定檔案路徑
train_ipynb_path = r"c:\Users\0419mch\Desktop\project_0414\yolo訓練程式碼.ipynb"

# 1. 讀取 Notebook
with open(train_ipynb_path, 'r', encoding='utf-8') as f:
    nb = json.load(f)

# 2. 定義新原始碼 (Stage 2 強制重置日誌)
new_stage2_source = [
    "#🎯 二階段微調 (Fine-tuning)\n",
    "import os, glob, torch, gc, sys, logging, warnings\n",
    "from ultralytics import YOLO\n",
    "from agent_tools import error_logger, yolo_utils\n",
    "\n",
    "# --- 🌟 初始化：註冊自定義模組 ---\n",
    "yolo_utils.register_yolo_modules()\n",
    "warnings.filterwarnings(\"ignore\", message=\".*deterministic.*\")\n",
    "warnings.filterwarnings(\"ignore\", category=UserWarning)\n",
    "\n",
    "# --- 🛡️ 強制恢復日誌顯示 ---\n",
    "logging.getLogger(\"ultralytics\").setLevel(logging.INFO) \n",
    "os.environ[\"YOLO_VERBOSE\"] = \"True\"                  \n",
    "\n",
    "# --- 🛡️ 環境隔離 ---\n",
    "sys.argv = [sys.argv[0]] \n",
    "\n",
    "if __name__ == '__main__':\n",
    "    # 1. 自動尋找最新的一階段權重\n",
    "    train_dirs = glob.glob(os.path.join(\"runs\", \"detect\", \"train*\"))\n",
    "    primary_train_dirs = [d for d in train_dirs if \"_2\" not in d]\n",
    "    \n",
    "    if not primary_train_dirs:\n",
    "        print(\"❌ 找不到一階段訓練資料夾。\")\n",
    "    else:\n",
    "        latest_primary_dir = max(primary_train_dirs, key=os.path.getmtime)\n",
    "        base_name = os.path.basename(latest_primary_dir)\n",
    "        stage2_name = f\"{base_name}_2\"\n",
    "        best_weights = os.path.join(latest_primary_dir, \"weights\", \"best.pt\")\n",
    "\n",
    "        if not os.path.exists(best_weights):\n",
    "            print(f\"⚠️ 找不到權重檔：{best_weights}\")\n",
    "        else:\n",
    "            print(f\"🚀 啟動二階段微調：{base_name} -> {stage2_name}\")\n",
    "            \n",
    "            # 2. 顯存清理\n",
    "            if 'model_stage2' in globals(): del model_stage2\n",
    "            gc.collect()\n",
    "            if torch.cuda.is_available(): torch.cuda.empty_cache()\n",
    "            \n",
    "            try:\n",
    "                # 3. 載入模型\n",
    "                model_stage2 = YOLO(best_weights)\n",
    "                DEVICE_ID = 0 if torch.cuda.is_available() else 'cpu'\n",
    "                DATA_YAML_PATH = \"roboflow_1000_側拍_split/data.yaml\"\n",
    "\n",
    "                # 4. 執行低學習率微調\n",
    "                model_stage2.train(\n",
    "                    data=DATA_YAML_PATH,\n",
    "                    epochs=50,\n",
    "                    batch=4,\n",
    "                    imgsz=640,\n",
    "                    device=DEVICE_ID,\n",
    "                    name=stage2_name,\n",
    "                    optimizer='AdamW',\n",
    "                    lr0=0.0001,           # 學習率降低 10 倍\n",
    "                    freeze=10,            # 鎖定部分層\n",
    "                    multi_scale=False,\n",
    "                    plots=True,           \n",
    "                    verbose=True,         \n",
    "                    # 高強度數據增強\n",
    "                    degrees=15.0,\n",
    "                    translate=0.2,\n",
    "                    perspective=0.001,\n",
    "                    shear=2.0,\n",
    "                    mosaic=1.0,\n",
    "                    mixup=0.15,\n",
    "                    copy_paste=0.1,\n",
    "                    close_mosaic=10\n",
    "                )\n",
    "                print(f\"\\n✨ 二階段微調圓滿完成！權重已存入 runs/detect/{stage2_name}\")\n",
    "            except Exception as e:\n",
    "                error_logger.log_error(e, context=\"YOLO 二階段微調\")\n",
    "                raise"
]

# 3. 替換 Cell
modified = False
for cell in nb['cells']:
    if cell['cell_type'] == 'code' and 'model_stage2' in "".join(cell['source']):
        cell['source'] = new_stage2_source
        cell['outputs'] = []
        modified = True
        break

# 4. 存檔
with open(train_ipynb_path, 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=1, ensure_ascii=False)

if modified:
    print("Success: Forced log level to INFO for Stage 2!")
else:
    print("Error: Target Stage 2 cell not found.")
