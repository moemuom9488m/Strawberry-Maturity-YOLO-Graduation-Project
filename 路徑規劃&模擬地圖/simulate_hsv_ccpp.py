import cv2
import numpy as np
import matplotlib.pyplot as plt
import sys
import os

sys.path.append(os.path.dirname(__file__))
from ccpp_planner import CCPPPlanner

def generate_simulation():
    print("🎨 正在生成 Minecraft 風格模擬平面圖...")
    
    # 1. 物理參數設定
    resolution = 0.1 # 0.1m / grid
    field_l, field_w = 15.0, 10.0 # 15m x 10m
    rows = int(field_l / resolution) # 150
    cols = int(field_w / resolution) # 100
    
    # 初始化 BGR 畫布 (泥土色/走道色: Tan, RGB: 210, 180, 140 -> BGR: 140, 180, 210)
    img = np.full((rows, cols, 3), (140, 180, 210), dtype=np.uint8)
    
    # 2. 繪製草莓壟 (綠色方塊) - 留出上下端點的迴車道
    period = 12
    for c in range(2, cols, period):
        # 草莓壟色: Forest Green, RGB: 34, 139, 34 -> BGR: 34, 139, 34
        img[10:140, c:c+5] = (34, 139, 34)
        
    # 3. 模擬「挖掉中間區塊」或不規則障礙物
    # 在場地正中央挖掉一個區塊 (障礙物: 深灰色)
    img[60:90, 40:70] = (105, 105, 105)
    
    # 左下角也挖掉一塊
    img[120:150, 0:30] = (105, 105, 105)
    
    # 4. 模擬使用 HSV 提取走道 (Walkable Space)
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    # 泥土色的 HSV 範圍 (大約)
    # BGR (140, 180, 210) 轉換後的 HSV
    # 為了簡化與穩定，這裡我們直接用 BGR 範圍去抓，或者用 HSV
    # 其實 OpenCV 的 cv2.inRange 也可以直接對 BGR 提取
    mask_walkable = cv2.inRange(img, (130, 170, 200), (150, 190, 220))
    
    grid_map = np.zeros((rows, cols), dtype=int)
    grid_map[mask_walkable > 0] = 1 # 1 為可行走區域
    
    # 將地圖邊界也設為障礙，避免超出
    grid_map[0, :] = 0
    grid_map[-1, :] = 0
    grid_map[:, 0] = 0
    grid_map[:, -1] = 0

    print("🗺️ 成功提取 HSV 走道遮罩，開始執行 CCPP 全區域路徑規劃...")
    
    # 5. CCPP 路徑規劃
    planner = CCPPPlanner(grid_map, resolution)
    
    # 走道中心線所在的列 (與壟畫法一致，壟在 2, 14, 26, 38, 50, 62, 74, 86, 98)
    # 走道在這些壟之間，中心點列座標分別是：
    trench_columns = [10, 22, 34, 46, 58, 70, 82, 94]
    
    # 解析出各個走道中的可行走線段 (避開障礙物)
    segments_by_col = {}
    for c in trench_columns:
        walkable_rows = []
        for r in range(10, 141): # 壟高 10 到 140
            if grid_map[r, c] == 1:
                walkable_rows.append(r)
        
        if not walkable_rows:
            continue
        
        # 尋找連續的區間
        col_segments = []
        start_r = walkable_rows[0]
        prev_r = walkable_rows[0]
        for r in walkable_rows[1:]:
            if r - prev_r > 1:
                col_segments.append((start_r, prev_r))
                start_r = r
            prev_r = r
        col_segments.append((start_r, prev_r))
        segments_by_col[c] = col_segments

    # 起點設定在走道 3 的上方 (例如: row=40, col=46)
    start_pos = (4.0, 4.6) 
    
    full_path = []
    current_pos = start_pos
    downwards = True
    
    # 按順序遍歷走道，生成雙側 CCPP zigzag 覆蓋路徑
    for c in trench_columns:
        if c not in segments_by_col:
            continue
        segments = segments_by_col[c]
        
        if downwards:
            # 由上往下走：區間按 row 從小到大排序
            segments = sorted(segments, key=lambda x: x[0])
            for r_start, r_end in segments:
                # 規劃連接到該區間起點 (r_start, c) 的 A* 路徑
                p_start = (r_start * resolution, c * resolution)
                transition = planner.plan(current_pos, p_start)
                if transition:
                    full_path.extend(transition)
                
                # 直線掃描該區間 (實體覆蓋)
                scan_steps = int((r_end - r_start) + 1)
                for r in np.linspace(r_start, r_end, scan_steps):
                    pt = (r * resolution, c * resolution)
                    if not full_path or full_path[-1] != pt:
                        full_path.append(pt)
                current_pos = (r_end * resolution, c * resolution)
            downwards = False
        else:
            # 由下往上走：區間按 row 從大到小排序
            segments = sorted(segments, key=lambda x: x[1], reverse=True)
            for r_start, r_end in segments:
                # 規劃連接到該區間起點 (r_end, c) 的 A* 路徑
                p_start = (r_end * resolution, c * resolution)
                transition = planner.plan(current_pos, p_start)
                if transition:
                    full_path.extend(transition)
                
                # 直線掃描該區間 (向上掃描)
                scan_steps = int((r_end - r_start) + 1)
                for r in np.linspace(r_end, r_start, scan_steps):
                    pt = (r * resolution, c * resolution)
                    if not full_path or full_path[-1] != pt:
                        full_path.append(pt)
                current_pos = (r_start * resolution, c * resolution)
            downwards = True
            
    # 6. 視覺化
    plt.figure(figsize=(10, 12))
    plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    
    if full_path:
        print(f"✅ 成功規劃完整 CCPP 覆蓋路徑！總節點數: {len(full_path)}")
        py = [p[0]/resolution for p in full_path]
        px = [p[1]/resolution for p in full_path]
        plt.plot(px, py, color='red', linewidth=2.5, label='CCPP Route')
        
        # 繪製路徑方向箭頭 (每隔 30 步畫一個箭頭)
        for idx in range(15, len(px) - 15, 30):
            dx = px[idx+1] - px[idx]
            dy = py[idx+1] - py[idx]
            norm = np.sqrt(dx**2 + dy**2)
            if norm > 0:
                plt.arrow(px[idx], py[idx], (dx/norm)*2, (dy/norm)*2, 
                          shape='full', color='blue', lw=0, length_includes_head=True, head_width=2.0)
            
        plt.scatter([start_pos[1]/resolution], [start_pos[0]/resolution], c='blue', s=150, marker='*', label='Start (Middle)')
        plt.scatter([px[-1]], [py[-1]], c='gold', s=150, marker='X', label='End')
    else:
        print("❌ 無法規劃覆蓋路徑。")
        
    plt.title("Minecraft-Style Map & CCPP Path Planning Demonstration", fontsize=16)
    plt.xlabel("X (0.1m/grid)")
    plt.ylabel("Y (0.1m/grid)")
    plt.legend(loc='upper right')
    
    save_path = os.path.join(os.path.dirname(__file__), "hsv_simulation_result.png")
    plt.savefig(save_path, bbox_inches='tight')
    print(f"📸 模擬結果已儲存至：{save_path}")

if __name__ == "__main__":
    generate_simulation()
