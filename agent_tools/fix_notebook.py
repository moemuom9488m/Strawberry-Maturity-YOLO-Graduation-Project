# -*- coding: utf-8 -*-
import json
import os
import sys

# Reconfigure stdout to use utf-8 to avoid Big5 (cp950) encoding errors with emojis
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

"""
🛠️ Notebook 一次性修復/更新工具 (Agent 專用)
* 根據使用者指示，此腳本僅保留「最新一次」需要的修改內容，避免冗長與重複執行過時的覆寫邏輯。
"""

def fix_calculator_cell():
    video_ipynb_path = r"d:\銘澄專區\畢業專題工作區\影片偵測.ipynb"
    if not os.path.exists(video_ipynb_path):
        print(f"❌ 找不到目標檔案: {video_ipynb_path}")
        return

    with open(video_ipynb_path, 'r', encoding='utf-8') as f:
        nb = json.load(f)

    cell1_source = [
        "import math\n",
        "\n",
        "# ==========================================\n",
        "# 📐 鏡頭範圍與高度計算器 (專業彙報版)\n",
        "# ==========================================\n",
        "\n",
        "PRESET_OPTIONS = [\n",
        "    {\"name\": \"Logitech C920 (16:9)\", \"h_fov\": 70.4, \"v_fov\": 43.3},\n",
        "    {\"name\": \"DJI Mini 4 Pro (16:9)\", \"h_fov\": 75.0, \"v_fov\": 46.5},\n",
        "    {\"name\": \"DJI Mini 4 Pro (4:3)\", \"h_fov\": 71.2, \"v_fov\": 56.2},\n",
        "    {\"name\": \"iPhone 15 Main (16:9)\", \"h_fov\": 73.7, \"v_fov\": 45.4},\n",
        "    {\"name\": \"RPi Camera V3 (16:9)\", \"h_fov\": 66.0, \"v_fov\": 41.0},\n",
        "    {\"name\": \"Custom\", \"h_fov\": 84.0, \"v_fov\": 60.0}\n",
        "]\n",
        "\n",
        "print(\"--- 🛠️ 功能模式選擇 ---\")\n",
        "print(\"[1] 已知『所需區域大小』 -> 計算『支架高度』\")\n",
        "print(\"[2] 已知『支架高度』     -> 計算『實際畫面涵蓋範圍』\")\n",
        "\n",
        "try:\n",
        "    calc_mode = int(input(\"請選擇功能模式 (1-2, 預設 1): \") or 1)\n",
        "    mode_name = \"已知區域求高度\" if calc_mode == 1 else \"已知高度求範圍\"\n",
        "    \n",
        "    print(\"\\n--- 📱 拍攝方向選擇 ---\")\n",
        "    print(\"[1] 橫向拍攝 (Landscape)\")\n",
        "    print(\"[2] 直向拍攝 (Portrait)\")\n",
        "    orient = int(input(\"請選擇拍攝方向 (1-2, 預設 1): \") or 1)\n",
        "    orient_name = \"橫向拍攝 (Landscape)\" if orient == 1 else \"直向拍攝 (Portrait)\"\n",
        "\n",
        "    print(\"\\n--- 🎥 鏡頭參數設定 ---\")\n",
        "    for i, opt in enumerate(PRESET_OPTIONS):\n",
        "        print(f\"[{i+1}] {opt['name']}\")\n",
        "    \n",
        "    cam_choice = int(input(f\"請輸入鏡頭編號 (1-{len(PRESET_OPTIONS)}, 預設 3): \") or 3)\n",
        "    selected = PRESET_OPTIONS[cam_choice-1]\n",
        "    \n",
        "    if orient == 1:\n",
        "        use_h_fov, use_v_fov = selected['h_fov'], selected['v_fov']\n",
        "    else:\n",
        "        # 直拍：交換水平與垂直視角\n",
        "        use_h_fov, use_v_fov = selected['v_fov'], selected['h_fov']\n",
        "\n",
        "    print(f\"\\n--- 📐 拍攝環境設定 ({orient_name}) ---\")\n",
        "    angle = float(input(\"請輸入拍攝俯視角度 (度, 90為正俯拍, 預設 90): \") or 90)\n",
        "    obj_h = float(input(\"請輸入『目標物高度』 (m, 預設 0.5): \") or 0.5)\n",
        "    zoom  = float(input(\"請輸入縮放倍率 (預設 1.0): \") or 1.0)\n",
        "\n",
        "    eff_tan_h = math.tan(math.radians(use_h_fov / 2)) / zoom\n",
        "    eff_tan_v = math.tan(math.radians(use_v_fov / 2)) / zoom\n",
        "\n",
        "    if calc_mode == 1:\n",
        "        target_w = float(input(\"請輸入希望涵蓋的『橫向寬度』 (m, 左右寬度, 預設 23.0): \") or 23.0)\n",
        "        target_l = float(input(\"請輸入希望涵蓋的『縱向長度』 (m, 上下長度, 若無請填0, 預設 18.0): \") or 18.0)\n",
        "        \n",
        "        req_h_w = (target_w * math.sin(math.radians(angle)) / (2 * eff_tan_h)) + obj_h\n",
        "        if target_l > 0:\n",
        "            req_h_l = (target_l * math.sin(math.radians(angle)) / (2 * eff_tan_v)) + obj_h\n",
        "        else:\n",
        "            req_h_l = 0\n",
        "            \n",
        "        req_h = max(req_h_w, req_h_l)\n",
        "        slant_range = (req_h - obj_h) / math.sin(math.radians(angle))\n",
        "        bottleneck = \"橫向寬度限制\" if req_h_w >= req_h_l else \"縱向長度限制\"\n",
        "        \n",
        "        print(\"\\n==========================================\")\n",
        "        print(\"📋 輸入參數彙總：\")\n",
        "        print(f\"   - 計算模式: {mode_name}\")\n",
        "        print(f\"   - 拍攝方向: {orient_name}\")\n",
        "        print(f\"   - 使用鏡頭: {selected['name']}\")\n",
        "        print(f\"   - 俯視角度: {angle}°\")\n",
        "        print(f\"   - 目標橫向寬度: {target_w} m\")\n",
        "        if target_l > 0:\n",
        "            print(f\"   - 目標縱向長度: {target_l} m\")\n",
        "        print(\"------------------------------------------\")\n",
        "        print(f\"✅ 計算完畢 (高度受『{bottleneck}』影響)：\")\n",
        "        print(f\"   - 🚀 建議『支架垂直高度』 (H): {req_h:.2f} 公尺 (約 {req_h*100:.1f} 公分)\")\n",
        "        print(f\"   - 📏 鏡頭到目標中心直線距離: {slant_range:.2f} 公尺\")\n",
        "        \n",
        "        # 顯示在這個高度下，實際拍出來的畫面大小\n",
        "        actual_w = (req_h - obj_h) * 2 * eff_tan_h / math.sin(math.radians(angle))\n",
        "        actual_l = (req_h - obj_h) * 2 * eff_tan_v / math.sin(math.radians(angle))\n",
        "        print(\"------------------------------------------\")\n",
        "        print(f\"🖼️ 此高度下實際畫面涵蓋範圍：\")\n",
        "        print(f\"   - 實際橫向涵蓋寬度: {actual_w:.2f} 公尺\")\n",
        "        print(f\"   - 實際縱向涵蓋長度: {actual_l:.2f} 公尺\")\n",
        "        print(\"==========================================\")\n",
        "        \n",
        "    else:\n",
        "        input_h = float(input(\"請輸入目前的『支架垂直高度』 (m, 預設 17.5): \") or 17.5)\n",
        "        work_h = input_h - obj_h\n",
        "        \n",
        "        print(\"\\n==========================================\")\n",
        "        print(\"📋 輸入參數彙總：\")\n",
        "        print(f\"   - 計算模式: {mode_name}\")\n",
        "        print(f\"   - 拍攝方向: {orient_name}\")\n",
        "        print(f\"   - 使用鏡頭: {selected['name']}\")\n",
        "        print(f\"   - 俯視角度: {angle}°\")\n",
        "        print(f\"   - 支架高度: {input_h} m\")\n",
        "        print(\"------------------------------------------\")\n",
        "        \n",
        "        if work_h <= 0:\n",
        "            print(\"❌ 錯誤：支架高度必須大於目標物高度！\")\n",
        "        else:\n",
        "            fov_w = (2 * work_h * eff_tan_h) / math.sin(math.radians(angle))\n",
        "            fov_h = (2 * work_h * eff_tan_v) / math.sin(math.radians(angle))\n",
        "            \n",
        "            print(f\"✅ 計算完畢：\")\n",
        "            print(f\"   - 🖼️ 實際畫面涵蓋『寬度』: {fov_w:.2f} 公尺 (約 {fov_w*100:.1f} 公分)\")\n",
        "            print(f\"   - 🖼️ 實際畫面涵蓋『長度』: {fov_h:.2f} 公尺 (約 {fov_h*100:.1f} 公分)\")\n",
        "            print(f\"   - 💡 提示：若為傾斜拍攝，實際長度範圍可能會因透視形變而略有增減。\")\n",
        "        print(\"==========================================\")\n",
        "\n",
        "except Exception as e:\n",
        "    print(f\"\\n❌ 發生錯誤: {e}\\n\")\n"
    ]

    nb['cells'][1]['source'] = cell1_source
    with open(video_ipynb_path, 'w', encoding='utf-8') as f:
        json.dump(nb, f, indent=1, ensure_ascii=False)
    print("✅ 已成功將 影片偵測.ipynb 第1個 cell 更新為雙軸高度計算機！")

def fix_tradeoff_cell():
    notebook_path = r"d:\銘澄專區\畢業專題工作區\模型評估與特徵視覺化.ipynb"
    if not os.path.exists(notebook_path):
        print(f"❌ 找不到目標檔案: {notebook_path}")
        return

    with open(notebook_path, 'r', encoding='utf-8') as f:
        nb = json.load(f)

    # 目標 cell 索引為 11 (已在先前步驟確認)
    target_idx = 11
    
    # 為了安全起見，我們先驗證 cell 內容是否包含 Tradeoff 字眼
    cell = nb['cells'][target_idx]
    source_text = "".join(cell.get('source', []))
    if "Tradeoff" not in source_text:
        print("⚠️ 警告: 索引 11 的 cell 似乎不是 Tradeoff 分析的 cell。開始搜尋正確的 cell...")
        found_idx = -1
        for idx, c in enumerate(nb.get('cells', [])):
            if c.get('cell_type') == 'code':
                txt = "".join(c.get('source', []))
                if "Tradeoff" in txt or "模型抉擇" in txt or "YOLO11s Baseline" in txt:
                    found_idx = idx
                    break
        if found_idx != -1:
            target_idx = found_idx
            print(f"🎯 找到正確的 cell 索引為: {target_idx}")
        else:
            print("❌ 未在筆記本中找到符合特徵的 Cell")
            return

    new_source = [
        "# ==============================================================================\n",
        "# 📈 畢業專題：草莓成熟度偵測模型抉擇與 Tradeoff 分析 (簡報與論文專用圖表繪製)\n",
        "# 本 Cell 可單獨執行，用於生成高質量的雙 Y 軸折線與柱狀對照圖。\n",
        "# ==============================================================================\n",
        "import sys, os\n",
        "sys.argv = [sys.argv[0]]  # 隔離 Jupyter Kernel 的內部參數干擾\n",
        "\n",
        "# --- 環境與中文字型初始化 ---\n",
        "import matplotlib.pyplot as plt\n",
        "import seaborn as sns\n",
        "import numpy as np\n",
        "\n",
        "sns.set_theme(style='whitegrid')\n",
        "plt.rcParams['font.sans-serif'] = [\n",
        "    'Microsoft JhengHei',  # 微軟正黑體\n",
        "    'DFKai-SB',            # 標楷體\n",
        "    'PingFang TC',         # 蘋果繁中\n",
        "    'sans-serif'\n",
        "]\n",
        "plt.rcParams['axes.unicode_minus'] = False\n",
        "\n",
        "# 1. 準備數據 (改為四個 exp1 階段一實驗的比較)\n",
        "models = [\n",
        "    'YOLO11s Baseline\\n(640px)',\n",
        "    'YOLO11m Baseline\\n(640px)',\n",
        "    'YOLO11s P2-CBAM\\n(640px)',\n",
        "    'YOLO11m P2-CBAM\\n(640px)'\n",
        "]\n",
        "\n",
        "map50 = [0.8699, 0.8648, 0.8602, 0.8706]\n",
        "map50_95 = [0.6307, 0.4929, 0.6132, 0.6257]\n",
        "\n",
        "x = np.arange(len(models))\n",
        "width = 0.4  # 柱子寬度\n",
        "\n",
        "# 2. 創建畫布 (高解析度 1920*1080)\n",
        "fig, ax1 = plt.subplots(figsize=(9.6, 5.4), dpi=200)\n",
        "\n",
        "# 質感 HSL 漸層配色 (s_baseline, m_baseline, s_p2cbam, m_p2cbam)\n",
        "bar_colors = ['#4CC9F0', '#4361EE', '#FF9F1C', '#F72585']\n",
        "\n",
        "# 3. 繪製左軸：Best mAP@0.5 與 mAP@0.5:0.95 (重疊柱狀圖)\n",
        "# 3.1 繪製底層的 mAP@0.5 柱狀圖\n",
        "bars = ax1.bar(x, map50, width, color=bar_colors, alpha=0.85, edgecolor='black', linewidth=1.2, zorder=3, label='mAP@0.5')\n",
        "\n",
        "# 3.2 覆蓋上層的 mAP@0.5:0.95 虛線斜線柱狀圖 (採用半透明白色磨砂玻璃效果 + 斜線填充 Hatch)\n",
        "bars_95 = ax1.bar(x, map50_95, width, color='white', alpha=0.35, edgecolor='black', linestyle='--', linewidth=1.8, hatch='//', zorder=4, label='mAP@0.5:0.95')\n",
        "\n",
        "ax1.set_xlabel('評估實驗模型 (640px)', fontsize=14, labelpad=15, fontweight='bold')\n",
        "ax1.set_ylabel('Best mAP', fontsize=14, color='#4361EE', fontweight='bold', rotation=0, labelpad=35, va='center', ha='right')\n",
        "ax1.tick_params(axis='y', labelcolor='#4361EE', labelsize=12)\n",
        "ax1.set_ylim(0.35, 0.95)  # 擴大範圍以完整容納兩種指標\n",
        "ax1.set_xticks(x)\n",
        "ax1.set_xticklabels(models, fontsize=12, fontweight='bold')\n",
        "\n",
        "# 在 mAP50 柱狀圖上方標註數值\n",
        "for bar in bars:\n",
        "    height = bar.get_height()\n",
        "    ax1.annotate(f'{height:.4f}',\n",
        "                xy=(bar.get_x() + bar.get_width() / 2, height),\n",
        "                xytext=(0, 5),  # 向上偏移 5 點\n",
        "                textcoords='offset points',\n",
        "                ha='center', va='bottom', fontsize=11, fontweight='bold', color='black')\n",
        "\n",
        "# 在 mAP50-95 柱狀圖內部頂端標註數值\n",
        "for bar in bars_95:\n",
        "    height = bar.get_height()\n",
        "    ax1.annotate(f'{height:.4f}',\n",
        "                xy=(bar.get_x() + bar.get_width() / 2, height),\n",
        "                xytext=(0, -15),  # 往下偏移 15 點\n",
        "                textcoords='offset points',\n",
        "                ha='center', va='top', fontsize=10, fontweight='bold', color='black')\n",
        "    \n",
        "# 5. 圖表美化設計 (無邊框、精緻格線)\n",
        "ax1.grid(True, linestyle=':', alpha=0.6, zorder=0)\n",
        "\n",
        "# 6. 建立統一圖例，並放置於圖表左下角外面 (在 Best mAP 標籤下方)\n",
        "import matplotlib.patches as mpatches\n",
        "map50_patch = mpatches.Patch(facecolor='#808080', alpha=0.85, edgecolor='black', label='mAP@0.5 (底層彩色柱狀)')\n",
        "map95_patch = mpatches.Patch(facecolor='white', alpha=0.35, edgecolor='black', linestyle='--', linewidth=1.5, hatch='//', label='mAP@0.5:0.95 (上層虛線)')\n",
        "ax1.legend(handles=[map50_patch, map95_patch], loc='upper left', bbox_to_anchor=(-0.35, -0.15), fontsize=10, frameon=True, facecolor='#F8F9FA')\n",
        "\n",
        "# 7. 儲存圖片 (精準 1920*1080 像素，無裁切，確保外置圖例不被切掉)\n",
        "output_dir = 'evaluation_results'\n",
        "os.makedirs(output_dir, exist_ok=True)\n",
        "img_path = os.path.join(output_dir, 'ppt_model_selection_comparison.png')\n",
        "plt.tight_layout()\n",
        "plt.savefig(img_path, dpi=200, bbox_inches='tight')\n",
        "plt.show()\n",
        "print(f'🎉 [SUCCESS] 簡報專用決策圖已成功生成與儲存: {img_path}')\n"
    ]
    
    nb['cells'][target_idx]['source'] = new_source
    with open(notebook_path, 'w', encoding='utf-8') as f:
        json.dump(nb, f, indent=1, ensure_ascii=False)
    print(f"✅ 已成功將 模型評估與特徵視覺化.ipynb 索引 {target_idx} 的 cell 更新為四個 exp1 比較對照圖！")

if __name__ == '__main__':
    fix_tradeoff_cell()



