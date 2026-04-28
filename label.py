import os
import sys

# --- 腳本設定 ---
# 您的標註檔 (e.g., image001.txt) 所在的資料夾
DATA_DIR = './labelImg-master/trainimg' 

# 您的類別定義檔 (classes.txt) 的完整路徑
CLASSES_FILE = './labelImg-master/trainimg/classes.txt'

# 支援的圖片副檔名 (您可以自行增減)
IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png'} # 增加常見的副檔名
# --- 結束設定 ---


def analyze_labels_with_progress():
    """
    統計標註資料夾中的圖片總數、已標註數量與各類別的物件數量。
    """
    class_names = []
    
    # --- 步驟 1: 讀取 classes.txt ---
    try:
        # 使用 'utf-8' 編碼，確保中文字符正確讀取
        with open(CLASSES_FILE, 'r', encoding='utf-8') as f:
            # 過濾掉空行並去除前後空白
            class_names = [line.strip() for line in f if line.strip()]
        
        if not class_names:
            print(f"錯誤: 類別檔案 '{CLASSES_FILE}' 是空的。")
            return
        
        print(f"成功讀取 {len(class_names)} 個類別: {class_names}")
    
    except FileNotFoundError:
        print(f"錯誤: 找不到類別檔案 '{CLASSES_FILE}'")
        print(f"請確認路徑 '{CLASSES_FILE}' 是否正確。")
        return
    except Exception as e:
        print(f"讀取類別檔案時發生錯誤: {e}")
        return

    # --- 步驟 2: 初始化計數器 ---
    # 類別計數器，初始化為 0
    class_counts = {name: 0 for name in class_names}
    total_objects = 0
    
    # 使用 set 來存放檔名 (不含副檔名)，以便比對
    annotated_files_base = set() # 存放有標註檔 (.txt) 的檔名
    total_image_files_base = set() # 存放所有圖片的檔名
    
    classes_filename = os.path.basename(CLASSES_FILE)

    # --- 步驟 3: 遍歷資料夾 (DATA_DIR) ---
    try:
        all_files = os.listdir(DATA_DIR)
    except FileNotFoundError:
        print(f"錯誤: 找不到資料夾 '{DATA_DIR}'")
        print("請確認路徑是否正確。")
        return

    print(f"\n正在分析 '{DATA_DIR}' 中的檔案...")

    for filename in all_files:
        # 分離檔名和副檔名
        file_base_name, file_extension = os.path.splitext(filename)
        file_extension_lower = file_extension.lower()

        # 1. 檢查是否為圖片檔
        if file_extension_lower in IMAGE_EXTENSIONS:
            total_image_files_base.add(file_base_name)
            continue # 繼續檢查下一個檔案

        # 2. 檢查是否為標註檔 (且不是 classes.txt)
        if file_extension_lower == '.txt' and filename != classes_filename:
            
            # 將這個檔案的基礎名稱加入 "已標註" 清單
            annotated_files_base.add(file_base_name)
            
            file_path = os.path.join(DATA_DIR, filename)
            
            try:
                # 讀取標註檔內容
                with open(file_path, 'r') as f:
                    for line_number, line in enumerate(f, 1):
                        line = line.strip()
                        if not line:
                            continue # 跳過空行
                        
                        parts = line.split()
                        
                        if not parts:
                            continue 
                            
                        try:
                            # 取得第一個數字 (類別索引)
                            class_index = int(parts[0])
                        except ValueError:
                            print(f"  [警告] 格式錯誤 (非數字): 檔案 '{filename}', 行 {line_number}")
                            continue
                        
                        # 根據索引找到類別名稱
                        if 0 <= class_index < len(class_names):
                            class_name = class_names[class_index]
                            class_counts[class_name] += 1
                            total_objects += 1
                        else:
                            print(f"  [警告] 索引無效: 檔案 '{filename}', 行 {line_number}, 索引: {class_index}")
                            
            except Exception as e:
                print(f"  [錯誤] 讀取檔案 '{filename}' 失敗: {e}")

    # --- 步驟 4: 輸出統計結果 ---
    
    # "已標註圖片總數" 是指找到的 .txt 檔案數量，且這些 .txt 檔名必須對應到圖片檔名
    # 但原程式碼邏輯是：只要有 .txt 檔就算已標註 (annotated_files_base)，
    # 接著再計算圖片檔總數 (total_image_files_base)。
    # 這裡的 "已標註圖片總數" 應取兩者的交集，但為了保持原邏輯，我們只計算有 .txt 檔案的數量
    
    # 找出「同時擁有圖片和標註檔」的數量
    image_with_labels_base = total_image_files_base.intersection(annotated_files_base)
    annotated_count = len(image_with_labels_base)

    # "圖片總數" 是指找到的 圖片檔 數量
    total_image_count = len(total_image_files_base)
    
    # 找出 "未標註" 的圖片
    unannotated_images = total_image_files_base - image_with_labels_base
    not_annotated_count = len(unannotated_images)


    print("\n" + "="*30)
    print("--- 標註進度與統計 ---")
    print("="*30)
    
    if total_image_count == 0:
        print(f"在 '{DATA_DIR}' 中未找到任何圖片檔。")
        print(f"(支援的副檔名: {', '.join(IMAGE_EXTENSIONS)})")
    else:
        # 計算進度條
        if total_image_count > 0:
            progress_percentage = (annotated_count / total_image_count) * 100
            bar_length = 25 # 進度條長度
            filled_length = int(bar_length * annotated_count // total_image_count)
            bar = '█' * filled_length + '-' * (bar_length - filled_length)
            
            print(f"標註進度: [{bar}]")
            print(f"           {annotated_count} / {total_image_count} 張圖片已標註 ({progress_percentage:.1f}%)")
            print(f"           ({not_annotated_count} 張圖片尚未標註)")
        else:
             print("找不到圖片檔案，無法計算進度。")


    print("\n" + "-"*30)
    print(f"已標註物件總數: {total_objects}")
    print("\n--- 各類別數量 ---")
    
    if not class_counts:
        print("未統計到任何類別。")
        return
        
    # 找到最長的類別名稱，用於對齊
    try:
        # class_names 已經確定被讀取 (步驟 1)
        max_len = max(len(name) for name in class_names) + 2
    except ValueError:
        max_len = 10 # 預設寬度
        
    for name, count in class_counts.items():
        # 使用左對齊，並填充空白直到達到 max_len 寬度
        print(f"  - {name:<{max_len}} {count} 個")

    print("="*30)
    print("統計完成。")


# --- 執行腳本 ---
if __name__ == "__main__":
    analyze_labels_with_progress()
