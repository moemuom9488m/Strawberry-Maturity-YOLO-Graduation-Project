# 分析切分後的類別分佈
import os
import yaml
import pandas as pd

# --- 設定路徑 ---
# 指向指定的資料夾 (配合畢業專題 Roboflow 匯出路徑)
YOLO_DATA_DIR = 'strawberry-maturity-yolo-graduate-1' 
DATA_YAML_PATH = os.path.join(YOLO_DATA_DIR, 'data.yaml')

# --- 函數：讀取並統計標註 ---
def count_labels(label_dir, class_names):
    """
    遍歷指定資料夾內的 .txt 標註檔，並統計:
    1. 每個類別的物件數量
    2. 純背景圖片 (空標註檔) 的數量
    """
    counts = {name: 0 for name in class_names}
    total_files = 0
    total_objects = 0
    background_files = 0
    
    if not os.path.exists(label_dir):
        print(f"[WARN] 找不到路徑 {label_dir}。跳過此分割。")
        return counts, 0, 0, 0

    for filename in os.listdir(label_dir):
        if filename.endswith('.txt'):
            file_path = os.path.join(label_dir, filename)
            total_files += 1
            
            try:
                # 檢查是否為空檔案 (0 bytes)
                if os.path.getsize(file_path) == 0:
                    background_files += 1
                    continue

                has_objects = False
                with open(file_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if not line:
                            continue
                        
                        has_objects = True 
                        
                        try:
                            # YOLO 格式: <class_id> <x> <y> <w> <h>
                            class_id_str = line.split()[0]
                            class_index = int(class_id_str)
                            
                            if 0 <= class_index < len(class_names):
                                class_name = class_names[class_index]
                                counts[class_name] += 1
                                total_objects += 1
                        except (ValueError, IndexError):
                            continue 
                
                if not has_objects:
                    background_files += 1
                                    
            except Exception as e:
                print(f"[ERROR] 讀取標註檔 {filename} 失敗: {e}")
                continue

    return counts, total_files, total_objects, background_files


# --- 主程式流程 ---
def analyze_split_distribution():
    # 1. 載入類別名稱
    try:
        # 確保以 utf-8 讀取，避免中文字元問題
        with open(DATA_YAML_PATH, 'r', encoding='utf-8') as f:
            data_yaml = yaml.safe_load(f)
        
        class_names = data_yaml.get('names')
        if not class_names:
            raise ValueError("在 data.yaml 中找不到 'names' 列表。")
        
        print(f"[OK] 成功讀取 {len(class_names)} 個類別: {class_names}")
    
    except FileNotFoundError:
        print(f"[ERROR] 找不到 data.yaml 檔案: {DATA_YAML_PATH}")
        return
    except Exception as e:
        print(f"[ERROR] 解析 data.yaml 失敗: {e}")
        return

    # 2. 統計各個分割集 (配合 Roboflow 結構將 'val' 改為 'valid')
    splits = ['train', 'valid', 'test']
    results = {}

    for s in splits:
        label_dir = os.path.join(YOLO_DATA_DIR, s, 'labels')
        counts, files, objects, bg = count_labels(label_dir, class_names)
        results[s] = {
            'counts': counts,
            'files': files,
            'objects': objects,
            'bg': bg
        }

    # 3. 整理資料夾物件分佈表格
    df_data = {
        'Train Objects': results['train']['counts'],
        'Valid Objects': results['valid']['counts'],
        'Test Objects': results['test']['counts']
    }
    df = pd.DataFrame(df_data).T 
    df['Total Objects'] = df.sum(axis=1)
    
    # 4. 輸出總結
    print("\n" + "="*60)
    print("--- 訓練 / 驗證 / 測試資料集統計總結 ---")
    print("="*60)
    
    for s in splits:
        icon = "[T]" if s == 'train' else ("[V]" if s == 'valid' else "[E]")
        name = s.capitalize()
        res = results[s]
        print(f"{icon} {name} Set:")
        print(f"   - 總圖片數:      {res['files']}")
        print(f"   - 有物件圖片:    {res['files'] - res['bg']}")
        print(f"   - 純背景圖片:    {res['bg']} (負樣本)")
        print(f"   - 標註物件總數:  {res['objects']}")
        print("-" * 40)
    
    # 輸出詳細的類別分佈表
    print("\n[INFO] 類別物件數量分佈 (Object Counts)")
    print(df.to_string())

    # 5. 檢查分佈平衡性 (比例分析)
    print("\n[INFO] 平衡性檢查 (以 Train 為基準的比例)")
    print(f"{'Class Name':<15} | {'Train:Valid':<12} | {'Train:Test':<10}")
    print("-" * 48)

    def get_ratio_str(train_val, target_val):
        if target_val == 0:
            return "Inf" if train_val > 0 else "0.0"
        return f"{train_val / target_val:.1f}"

    # 背景圖比例
    bg_v = get_ratio_str(results['train']['bg'], results['valid']['bg'])
    bg_t = get_ratio_str(results['train']['bg'], results['test']['bg'])
    print(f"{'[Background]':<15} | {bg_v:<12} | {bg_t:<10}")

    for class_name in class_names:
        tr_c = results['train']['counts'].get(class_name, 0)
        va_c = results['valid']['counts'].get(class_name, 0)
        te_c = results['test']['counts'].get(class_name, 0)
        
        ratio_v = get_ratio_str(tr_c, va_c)
        ratio_t = get_ratio_str(tr_c, te_c)

        print(f"{class_name:<15} | {ratio_v:<12} | {ratio_t:<10}")
    
    print("\n(註：若比例設定為 8:1:1，建議比例約為 8.0)")     
    print("="*60)


if __name__ == "__main__":
    analyze_split_distribution()
