import json
import os
import sys

# Reconfigure stdout to use UTF-8 to avoid encoding errors in PowerShell
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

def clear_outputs(ipynb_path):
    if not os.path.exists(ipynb_path):
        print(f"⚠️ 找不到檔案: {ipynb_path}")
        return False
        
    size_before = os.path.getsize(ipynb_path) / (1024 * 1024)
    if size_before < 0.1:
        print(f"ℹ️ {os.path.basename(ipynb_path)} 大小為 {size_before*1024:.1f} KB，無需清理。")
        return False

    try:
        with open(ipynb_path, 'r', encoding='utf-8') as f:
            nb = json.load(f)
            
        for cell in nb.get('cells', []):
            if cell.get('cell_type') == 'code':
                cell['outputs'] = []
                cell['execution_count'] = None
                
        with open(ipynb_path, 'w', encoding='utf-8') as f:
            json.dump(nb, f, indent=1, ensure_ascii=False)
            
        size_after = os.path.getsize(ipynb_path) / (1024 * 1024)
        print(f"✅ 已成功清理 {os.path.basename(ipynb_path)} 輸出快取：{size_before:.2f} MB -> {size_after:.2f} MB")
        return True
    except Exception as e:
        print(f"❌ 清理 {os.path.basename(ipynb_path)} 時發生錯誤: {e}")
        return False

if __name__ == "__main__":
    workspace_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    target_notebooks = [
        os.path.join(workspace_dir, "影片偵測.ipynb"),
        os.path.join(workspace_dir, "標註用.ipynb"),
        os.path.join(workspace_dir, "爬蟲.ipynb"),
        os.path.join(workspace_dir, "roboflow資料集用.ipynb"),
        os.path.join(workspace_dir, "讀取訓練結果.ipynb")
    ]
    
    print("🧹 開始清理 Jupyter Notebook 巨大輸出快取以加速 VSCode 渲染...")
    print("=================================================================")
    for nb_path in target_notebooks:
        clear_outputs(nb_path)
    print("=================================================================")
    print("🎉 清理完成！請在 VSCode 中重新載入或開啟 Notebook 試試。")
