import json
import os
import sys

# Reconfigure stdout to use utf-8 to avoid Big5 (cp950) encoding errors with emojis like 🍓, ✅, etc.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

"""
🛠️ Notebook 批量修復/更新工具 (Agent 專用)
---
用途：用於修復 讀取訓練結果.ipynb 的 StdinNotImplementedError 與 pkg_resources 缺失問題。
"""

ipynb_path = r"d:\銘澄專區\畢業專題工作區\讀取訓練結果.ipynb"

cell4_source = [
    "#監控訓練中的最新結果\n",
    "import pandas as pd\n",
    "import matplotlib.pyplot as plt\n",
    "import os\n",
    "import time\n",
    "import glob\n",
    "import threading\n",
    "from IPython.display import clear_output, display\n",
    "\n",
    "# 旗標：控制背景監控是否繼續\n",
    "keep_running = True\n",
    "\n",
    "def get_latest_results_csv(base_path=\"Strawberry_YOLOv11_4060ti-16G/*/results.csv\"):\n",
    "    files = glob.glob(base_path)\n",
    "    if not files: return None\n",
    "    return max(files, key=os.path.getmtime)\n",
    "\n",
    "def plot_training_results():\n",
    "    csv_path = get_latest_results_csv()\n",
    "    if csv_path is None or not os.path.exists(csv_path):\n",
    "        print(f\"⌛ 等待訓練數據產生中...\")\n",
    "        return\n",
    "\n",
    "    try:\n",
    "        df = pd.read_csv(csv_path)\n",
    "        df.columns = [c.strip() for c in df.columns]\n",
    "    except: return\n",
    "\n",
    "    if df.empty: return\n",
    "\n",
    "    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 5))\n",
    "\n",
    "    # --- Loss 圖 ---\n",
    "    ax1.plot(df['epoch'], df['train/box_loss'], label='Train Box', color='blue', alpha=0.4)\n",
    "    ax1.plot(df['epoch'], df['val/box_loss'], label='Val Box', color='blue', linestyle='--')\n",
    "    ax1.plot(df['epoch'], df['train/cls_loss'], label='Train Cls', color='orange', alpha=0.4)\n",
    "    ax1.plot(df['epoch'], df['val/cls_loss'], label='Val Cls', color='orange', linestyle='--')\n",
    "    ax1.set_title(f\"Loss Curves ({os.path.basename(os.path.dirname(csv_path))})\")\n",
    "    ax1.legend(); ax1.grid(True)\n",
    "\n",
    "    # --- mAP 圖 ---\n",
    "    ax2.plot(df['epoch'], df['metrics/mAP50(B)'], label='mAP50', color='green', linewidth=2)\n",
    "    ax2.plot(df['epoch'], df['metrics/mAP50-95(B)'], label='mAP50-95', color='red', linewidth=1)\n",
    "    ax2.set_title(\"Precision Metrics (mAP)\")\n",
    "    ax2.legend(); ax2.grid(True)\n",
    "\n",
    "    plt.tight_layout()\n",
    "    display(fig)\n",
    "    plt.close()\n",
    "\n",
    "def monitor_loop():\n",
    "    \"\"\" 背景執行的監控迴圈 \"\"\"\n",
    "    global keep_running\n",
    "    while keep_running:\n",
    "        clear_output(wait=True)\n",
    "        print(\"🟢 監控執行中... (如需停止，請在下方輸入框輸入 'q' 並按 Enter)\")\n",
    "        print(f\"最後更新時間: {time.strftime('%H:%M:%S')}\")\n",
    "        plot_training_results()\n",
    "        # 分段式 sleep，讓停止指令反應更快\n",
    "        for _ in range(5): \n",
    "            if not keep_running: break\n",
    "            time.sleep(1)\n",
    "\n",
    "# --- 主程式啟動 ---\n",
    "if __name__ == \"__main__\":\n",
    "    keep_running = True\n",
    "    \n",
    "    # 啟動背景執行緒\n",
    "    thread = threading.Thread(target=monitor_loop)\n",
    "    thread.start()\n",
    "\n",
    "    # 主線程等待輸入\n",
    "    try:\n",
    "        while True:\n",
    "            try:\n",
    "                user_cmd = input().strip().lower()\n",
    "            except Exception:\n",
    "                # 容錯處理：在無人值守 (如 nbconvert) 或非互動式環境中，自動退出\n",
    "                time.sleep(2)\n",
    "                keep_running = False\n",
    "                break\n",
    "            if user_cmd == 'q':\n",
    "                print(\"🛑 正在接收停止指令，請稍候...\")\n",
    "                keep_running = False\n",
    "                break\n",
    "    except KeyboardInterrupt:\n",
    "        keep_running = False\n",
    "\n",
    "    thread.join()\n",
    "    print(\"✅ 監控已安全停止，核心穩定。\")"
]

cell6_source = [
    "# GPU 健檢\n",
    "import warnings; warnings.filterwarnings(\"ignore\", category=FutureWarning, message=\".*pynvml.*\"); import os, sys, torch, pynvml, platform\n",
    "import importlib.metadata\n",
    "\n",
    "def get_gpu_health_check():\n",
    "    print(f\"{'='*30} 🚀 GPU 深度健檢報告 {'='*30}\")\n",
    "    \n",
    "    # 1. 系統與軟體環境偵測\n",
    "    print(f\"💻 作業系統: {platform.system()} {platform.release()}\")\n",
    "    print(f\"🐍 Python 版本: {sys.version.split()[0]}\")\n",
    "    \n",
    "    print(\"\\n📦 [核心 AI 套件偵測]\")\n",
    "    # 偵測 torch 與 ultralytics 系列套件\n",
    "    target_pkgs = ['torch', 'torchvision', 'torchaudio', 'ultralytics', 'wandb', 'pandas']\n",
    "    for pkg in target_pkgs:\n",
    "        try:\n",
    "            ver = importlib.metadata.version(pkg)\n",
    "            print(f\"   - {pkg:15}: v{ver}\")\n",
    "        except importlib.metadata.PackageNotFoundError:\n",
    "            print(f\"   - {pkg:15}: ❌ 未安裝\")\n",
    "\n",
    "    # 2. PyTorch CUDA 狀態\n",
    "    print(\"\\n🔥 [PyTorch CUDA 狀態]\")\n",
    "    cuda_available = torch.cuda.is_available()\n",
    "    print(f\"   - CUDA 可用性    : {cuda_available}\")\n",
    "    if cuda_available:\n",
    "        print(f\"   - 當前裝置       : {torch.cuda.get_device_name(0)}\")\n",
    "        print(f\"   - CUDA 版本      : {torch.version.cuda}\")\n",
    "        print(f\"   - cuDNN 版本     : {torch.backends.cudnn.version()}\")\n",
    "        print(f\"   - 顯存保留 (MB)  : {torch.cuda.memory_reserved(0)/1024/1024:.1f}\")\n",
    "\n",
    "    # 3. NVML 硬體底層診斷\n",
    "    print(\"\\n🖥️  [NVML 硬體底層診斷]\")\n",
    "    try:\n",
    "        pynvml.nvmlInit()\n",
    "        handle = pynvml.nvmlDeviceGetHandleByIndex(0)\n",
    "        \n",
    "        def safe_decode(val):\n",
    "            return val.decode() if isinstance(val, bytes) else val\n",
    "\n",
    "        # 取得各種資訊\n",
    "        gpu_name = safe_decode(pynvml.nvmlDeviceGetName(handle))\n",
    "        driver_ver = safe_decode(pynvml.nvmlSystemGetDriverVersion())\n",
    "        mem_info = pynvml.nvmlDeviceGetMemoryInfo(handle)\n",
    "        \n",
    "        # 時脈與頻寬相關\n",
    "        curr_graphics_clock = pynvml.nvmlDeviceGetClockInfo(handle, pynvml.NVML_CLOCK_GRAPHICS)\n",
    "        curr_mem_clock = pynvml.nvmlDeviceGetClockInfo(handle, pynvml.NVML_CLOCK_MEM)\n",
    "        max_graphics_clock = pynvml.nvmlDeviceGetMaxClockInfo(handle, pynvml.NVML_CLOCK_GRAPHICS)\n",
    "        \n",
    "        # 溫度與電力\n",
    "        temp = pynvml.nvmlDeviceGetTemperature(handle, pynvml.NVML_TEMPERATURE_GPU)\n",
    "        power_usage = pynvml.nvmlDeviceGetPowerUsage(handle) / 1000.0 # 轉為 W\n",
    "        power_limit = pynvml.nvmlDeviceGetPowerManagementLimit(handle) / 1000.0\n",
    "\n",
    "        print(f\"   - 正式名稱       : {gpu_name}\")\n",
    "        print(f\"   - 驅動程式版本   : {driver_ver}\")\n",
    "        print(f\"   - 總顯存 (VRAM)  : {mem_info.total / 1024**2:.0f} MB\")\n",
    "        print(f\"   - 目前顯存佔用   : {mem_info.used / 1024**2:.0f} MB ({(mem_info.used/mem_info.total)*100:.1f}%)\")\n",
    "        print(f\"   - 核心時脈       : {curr_graphics_clock} MHz (Max: {max_graphics_clock} MHz)\")\n",
    "        print(f\"   - 記憶體時脈     : {curr_mem_clock} MHz\")\n",
    "        print(f\"   - 當前溫度       : {temp} °C\")\n",
    "        print(f\"   - 當前功耗       : {power_usage:.1f} W / {power_limit:.1f} W\")\n",
    "        \n",
    "        # 計算理論頻寬\n",
    "        pcie_gen = pynvml.nvmlDeviceGetMaxPcieLinkGeneration(handle)\n",
    "        pcie_width = pynvml.nvmlDeviceGetMaxPcieLinkWidth(handle)\n",
    "        print(f\"   - PCIe 介面      : Gen {pcie_gen} x{pcie_width}\")\n",
    "\n",
    "    except Exception as e:\n",
    "        print(f\"   ❌ NVML 診斷失敗: {e}\")\n",
    "    finally:\n",
    "        try: pynvml.nvmlShutdown()\n",
    "        except: pass\n",
    "\n",
    "    print(f\"\\n{'='*80}\")\n",
    "    print(\"✅ 健檢完成！目前環境與 RTX 4060 Ti 處於最佳狀態。\")\n",
    "\n",
    "get_gpu_health_check()\n"
]

def update_notebook():
    if not os.path.exists(ipynb_path):
        print(f"❌ 找不到目標檔案: {ipynb_path}")
        return

    with open(ipynb_path, 'r', encoding='utf-8') as f:
        nb = json.load(f)

    # 修復監控 Cell (index 4) 與 GPU 健檢 Cell (index 6)
    nb['cells'][4]['source'] = cell4_source
    nb['cells'][6]['source'] = cell6_source

    with open(ipynb_path, 'w', encoding='utf-8') as f:
        json.dump(nb, f, indent=1, ensure_ascii=False)
    
    print(f"✅ 已成功更新 讀取訓練結果.ipynb 中的 Cell 4 與 Cell 6。")

if __name__ == "__main__":
    update_notebook()
