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

def fix_evaluation_notebook():
    notebook_path = r"d:\銘澄專區\畢業專題工作區\模型評估與特徵視覺化.ipynb"
    if not os.path.exists(notebook_path):
        print(f"❌ 找不到目標檔案: {notebook_path}")
        return

    with open(notebook_path, 'r', encoding='utf-8') as f:
        nb = json.load(f)

    # 1. 尋找並更新 MODEL_PATH
    model_path_updated = False
    for idx, cell in enumerate(nb.get('cells', [])):
        if cell.get('cell_type') == 'code':
            source_lines = cell.get('source', [])
            source_text = "".join(source_lines)
            if "MODEL_PATH = " in source_text:
                new_source = []
                for line in source_lines:
                    if "MODEL_PATH = " in line:
                        # 保持原始縮排
                        indent = line[:line.find("MODEL_PATH")]
                        new_source.append(f"{indent}MODEL_PATH = \"runs/detect/exp2b_1a_img800/weights/best.pt\"\n")
                    else:
                        new_source.append(line)
                cell['source'] = new_source
                model_path_updated = True
                print(f"✅ 成功將模型路徑修改為第2階段最佳 Baseline: cell index {idx}")

    # 2. 尋找並更新批次視覺化為單張視覺化
    visualization_updated = False
    for idx, cell in enumerate(nb.get('cells', [])):
        if cell.get('cell_type') == 'code':
            source_text = "".join(cell.get('source', []))
            if "批次執行視覺化" in source_text:
                new_visual_source = [
                    "# ==============================================================================\n",
                    "# 6. 執行視覺化 (自動生成單一影像的 Grad-CAM 成果圖並保存)\n",
                    "# ==============================================================================\n",
                    "import random\n",
                    "valid_images = glob.glob(\"strawberry-maturity-yolo-graduate-1/valid/images/*.jpg\")\n",
                    "if valid_images:\n",
                    "    print(\"⏳ 正在對驗證集進行篩選，以獲取適合論文插圖的影像...\")\n",
                    "    detector = YOLO(MODEL_PATH)\n",
                    "    selected_img = None\n",
                    "    \n",
                    "    # 優先尋找含有至少 2 個偵測目標的影像以方便對比\n",
                    "    random.shuffle(valid_images)\n",
                    "    for img_path in valid_images:\n",
                    "        res = detector.predict(img_path, conf=0.25, verbose=False)[0]\n",
                    "        if len(res.boxes) >= 2:\n",
                    "            selected_img = img_path\n",
                    "            break\n",
                    "            \n",
                    "    if not selected_img and len(valid_images) > 0:\n",
                    "        selected_img = valid_images[0]\n",
                    "        \n",
                    "    if selected_img:\n",
                    "        print(f\"🚀 開始生成與保存選定影像 {selected_img} 的 Grad-CAM 特徵圖...\")\n",
                    "        # 針對第一個偵測到的實體進行視覺化解釋\n",
                    "        run_gradcam_visualization(image_path=selected_img, target_instance_idx=0, conf_threshold=0.25)\n",
                    "        print(\"\\n🎉 特徵圖生成與保存完成！已保存在 evaluation_results/ 資料夾中，可用於簡報或論文展示。\")\n",
                    "    else:\n",
                    "        print(\"❌ 找不到適合的驗證圖片！\")\n",
                    "else:\n",
                    "    print(\"❌ 找不到 valid/images 目錄或裡面沒有 JPG 圖片！\")\n"
                ]
                cell['source'] = new_visual_source
                visualization_updated = True
                print(f"✅ 成功將批次生成改為單張展示生成: cell index {idx}")
                break

    # 3. 尋找並更新混淆矩陣繪製以儲存至本地
    cm_plot_updated = False
    for idx, cell in enumerate(nb.get('cells', [])):
        if cell.get('cell_type') == 'code':
            source_lines = cell.get('source', [])
            source_text = "".join(source_lines)
            if "繪製混淆矩陣" in source_text:
                new_plot_source = [
                    "# ==============================================================================\n",
                    "# 3. 繪製混淆矩陣 (Matplotlib + Seaborn)\n",
                    "# ==============================================================================\n",
                    "# 建立圖表：僅展示原始計數混淆矩陣 (Raw Counts)\n",
                    "fig, ax = plt.subplots(figsize=(9, 7.5))\n",
                    "\n",
                    "# 3.1 繪製原始計數矩陣 (Raw Counts)\n",
                    "# 先將 cm_data 轉換成 int，避免 seaborn 對 float 在使用 fmt='d' 時報錯 ValueError\n",
                    "cm_data_int = cm_data.astype(int)\n",
                    "sns.heatmap(\n",
                    "    cm_data_int,\n",
                    "    annot=True,\n",
                    "    fmt='d',\n",
                    "    cmap='Blues',\n",
                    "    xticklabels=x_labels,\n",
                    "    yticklabels=y_labels,\n",
                    "    ax=ax,\n",
                    "    cbar=True,\n",
                    "    annot_kws={\"size\": 12, \"weight\": \"bold\"},\n",
                    "    linewidths=0.5,\n",
                    "    linecolor='gray'\n",
                    ")\n",
                    "ax.set_title(\"草莓成熟度檢測混淆矩陣 (原始計數 Raw Counts)\", fontsize=15, pad=15, weight='bold')\n",
                    "ax.set_xlabel(\"真實類別 (Ground Truth)\", fontsize=12, labelpad=10)\n",
                    "ax.set_ylabel(\"預測類別 (Predictions)\", fontsize=12, labelpad=10)\n",
                    "\n",
                    "plt.tight_layout()\n",
                    "\n",
                    "# 儲存混淆矩陣圖片至本地\n",
                    "model_dir_name = os.path.basename(os.path.dirname(os.path.dirname(MODEL_PATH)))\n",
                    "save_dir = os.path.join('evaluation_results', model_dir_name)\n",
                    "os.makedirs(save_dir, exist_ok=True)\n",
                    "save_path = os.path.join(save_dir, f'confusion_matrix_{model_dir_name}.png')\n",
                    "plt.savefig(save_path, dpi=150, bbox_inches='tight')\n",
                    "print(f\"💾 混淆矩陣圖表已成功儲存至: {save_path}\")\n",
                    "\n",
                    "plt.show()\n"
                ]
                cell['source'] = new_plot_source
                cm_plot_updated = True
                print(f"✅ 成功將混淆矩陣繪製改為單圖佈局並支援本地儲存: cell index {idx}")
                break

    if model_path_updated or visualization_updated or cm_plot_updated:
        with open(notebook_path, 'w', encoding='utf-8') as f:
            json.dump(nb, f, indent=1, ensure_ascii=False)
        print("🎉 筆記本修改成功！")
    else:
        print("⚠️ 未發現需要修改的內容。")

if __name__ == '__main__':
    fix_evaluation_notebook()
