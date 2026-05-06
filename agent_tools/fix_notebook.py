import json
import os

"""
🛠️ Notebook 批量修復/更新工具 (Agent 專用)
---
用途：用於修改 .ipynb 檔案中的特定儲存格。
使用方法：修改 ipynb_path 與 target_cell_index，並在 new_source 中填入新代碼。
"""

# 1. 設定目標檔案
ipynb_path = r"d:\銘澄專區\畢業專題工作區\影片偵測.ipynb"
target_cell_index = 0  # 要修改的儲存格索引 (0 為最上方)

# 2. 定義新原始碼 (以 List 形式，每行需含 \n)
new_source = [
    "# 此工具已就緒，隨時可用於下一次修改。\n"
]

def update_notebook():
    if not os.path.exists(ipynb_path):
        print(f"❌ 找不到目標檔案: {ipynb_path}")
        return

    with open(ipynb_path, 'r', encoding='utf-8') as f:
        nb = json.load(f)

    if target_cell_index >= len(nb['cells']):
        print(f"❌ 索引 {target_cell_index} 超出範圍 (總長度 {len(nb['cells'])})")
        return

    # 執行覆寫
    nb['cells'][target_cell_index]['source'] = new_source

    with open(ipynb_path, 'w', encoding='utf-8') as f:
        json.dump(nb, f, indent=1, ensure_ascii=False)
    
    print(f"✅ 已成功更新 {os.path.basename(ipynb_path)} 的第 {target_cell_index} 個儲存格。")

if __name__ == "__main__":
    # update_notebook() # 預設註解掉，避免誤執行
    print("ℹ️ 請在 fix_notebook.py 中填入內容並取消註解 update_notebook() 後執行。")
