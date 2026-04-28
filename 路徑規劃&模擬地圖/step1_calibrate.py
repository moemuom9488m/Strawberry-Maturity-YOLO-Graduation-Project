import cv2
import numpy as np
import os

# --- 1. 支援中文路徑的讀取函數 ---
def imread_unicode(path):
    try:
        # 先用 numpy 讀取二進制數據，再由 OpenCV 解碼
        return cv2.imdecode(np.fromfile(path, dtype=np.uint8), cv2.IMREAD_COLOR)
    except Exception as e:
        print(f"讀取錯誤: {e}")
        return None

# --- 2. 設定參數 ---
# 請確認檔名與你資料夾中的檔案一模一樣
img_path = '草莓田範圍空拍.jpg' 
points = []

# --- 3. 點擊事件回調函數 ---
def click_event(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        print(f"✅ 已標記點 {len(points)+1}: ({x}, {y})")
        points.append((x, y))
        # 在顯示用的圖上畫紅點
        cv2.circle(display_img, (x, y), 7, (0, 0, 255), -1)
        # 標註序號
        cv2.putText(display_img, str(len(points)), (x + 10, y + 10), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 255), 3)
        cv2.imshow('Calibration', display_img)

# --- 4. 執行讀取與顯示 ---
img = imread_unicode(img_path)

if img is None:
    print(f"❌ 錯誤：找不到檔案 『{img_path}』")
    print(f"💡 目前路徑是: {os.getcwd()}")
    print("請確認檔案是否真的在資料夾內，且副檔名(jpg/png)完全正確。")
    exit()

# 建立一個副本用來顯示，避免畫完點後無法重來
display_img = img.copy()

cv2.namedWindow('Calibration', cv2.WINDOW_NORMAL) # 讓視窗可以縮放
cv2.imshow('Calibration', display_img)
cv2.setMouseCallback('Calibration', click_event)

print("--- 操作說明 ---")
print("請在視窗中依序點擊 23x18m 區域的四個角落：")
print("1. 左上 ➔ 2. 右上 ➔ 3. 右下 ➔ 4. 左下")
print("點完 4 個點後，按鍵盤『任何鍵』結束。")

cv2.waitKey(0)
cv2.destroyAllWindows()

# --- 5. 輸出結果 ---
if len(points) == 4:
    print("\n" + "="*30)
    print("🎉 標定成功！請複製以下座標：")
    print(f"IMAGE_CORNERS = {points}")
    print("="*30)
    
    # 驗證矩陣
    src_pts = np.array(points, dtype=np.float32)
    dst_pts = np.array([[0,0], [18,0], [18,23], [0,23]], dtype=np.float32)
    H, _ = cv2.findHomography(src_pts, dst_pts)
    print("\n單應性矩陣 H 已生成，座標系統準備就緒。")
else:
    print(f"\n⚠ 警告：你點了 {len(points)} 個點，系統需要『4個點』。請關閉視窗重新執行。")