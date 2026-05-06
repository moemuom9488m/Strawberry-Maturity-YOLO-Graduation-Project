import os
import json
import warnings

def clean_notebook(file_path):
    print(f"Cleaning: {file_path}")
    with open(file_path, 'r', encoding='utf-8') as f:
        try:
            data = json.load(f)
        except Exception as e:
            print(f"Failed to read {file_path}: {e}")
            return

    changed = False
    for cell in data.get('cells', []):
        if cell.get('cell_type') == 'code':
            new_source = []
            for line in cell.get('source', []):
                old_line = line
                # 1. 替換安裝指令
                line = line.replace('!pip install pynvml', '!pip install nvidia-ml-py')
                
                # 2. 加入警告過濾 (更加魯棒的偵測)
                if 'pynvml' in line and 'import' in line and 'warnings.filterwarnings' not in "".join(cell['source']):
                    # 尋找插入點：在 import 語句後加入 warnings
                    line = line.replace('import ', 'import warnings; warnings.filterwarnings("ignore", category=FutureWarning, message=".*pynvml.*"); import ')
                
                if line != old_line:
                    changed = True
                new_source.append(line)
            cell['source'] = new_source

    if changed:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=1, ensure_ascii=False)
        print(f"Updated: {file_path}")
    else:
        print(f"No changes needed: {file_path}")

if __name__ == "__main__":
    notebooks = [f for f in os.listdir('.') if f.endswith('.ipynb')]
    for nb in notebooks:
        clean_notebook(nb)
