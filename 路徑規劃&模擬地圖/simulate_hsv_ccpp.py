import cv2
import numpy as np
import matplotlib.pyplot as plt
import sys
import os

sys.path.append(os.path.dirname(__file__))
from ccpp_planner import CCPPPlanner

# 輔助函式：使用純 Python/NumPy 實作的路徑平滑化 (拉普拉斯平滑)，避免直角硬折
def smooth_path(path_pts, passes=3):
    if len(path_pts) < 3:
        return path_pts
    pts = list(path_pts)
    for _ in range(passes):
        new_pts = [pts[0]]
        for i in range(1, len(pts) - 1):
            y = 0.25 * pts[i-1][0] + 0.5 * pts[i][0] + 0.25 * pts[i+1][0]
            x = 0.25 * pts[i-1][1] + 0.5 * pts[i][1] + 0.25 * pts[i+1][1]
            new_pts.append((y, x))
        new_pts.append(pts[-1])
        pts = new_pts
    return pts

def generate_simulation():
    print("🎨 正在生成高品質莫蘭迪風格模擬平面圖...")
    
    # 1. 物理參數設定
    resolution = 0.1 # 0.1m / grid
    field_l, field_w = 15.0, 10.0 # 15m x 10m
    rows = int(field_l / resolution) # 150
    cols = int(field_w / resolution) # 100
    
    # 初始化 BGR 畫布 (高級米色/沙色, hex: #F4EAE1 -> BGR: 225, 234, 244)
    img = np.full((rows, cols, 3), (225, 234, 244), dtype=np.uint8)
    
    # 2. 繪製對稱草莓壟 (高級莫蘭迪綠, hex: #3A5A40 -> BGR: 64, 90, 58)
    # 壟寬度固定為 4，間距為 12，完美對稱
    ridge_columns = [4, 16, 28, 40, 52, 64, 76, 88]
    for c in ridge_columns:
        img[10:140, c:c+4] = (64, 90, 58)
        
    # 3. 模擬「挖掉壟區塊」作為可行走通道 (溫和灰色, hex: #CAD2C5 -> BGR: 197, 210, 202)
    # 將 Ridge 3, Ridge 4, Ridge 5 的 row 60-90 整平為灰色通道
    img[60:90, 40:44] = (197, 210, 202)
    img[60:90, 52:56] = (197, 210, 202)
    img[60:90, 64:68] = (197, 210, 202)
    
    # 左下角整平一片區域 (row 120-140, col 0-32，切齊 Ridge 2 的邊界)
    img[120:140, 0:33] = (197, 210, 202)
    
    # 為了展現路徑規劃，在走道中設置崩塌障礙物（高級深炭灰色, hex: #2F3E46 -> BGR: 70, 62, 47）
    # 阻斷 Aisle 3 (col 44-51) 的 row 60-75
    img[60:75, 44:52] = (70, 62, 47)
    # 阻斷 Aisle 4 (col 56-63) 的 row 75-90
    img[75:90, 56:64] = (70, 62, 47)
    
    # 4. 模擬使用 BGR 範圍提取可行走區域
    mask_tan = cv2.inRange(img, (220, 230, 240), (230, 240, 250))
    mask_grey = cv2.inRange(img, (190, 200, 195), (205, 220, 210))
    
    grid_map = np.zeros((rows, cols), dtype=int)
    grid_map[(mask_tan > 0) | (mask_grey > 0)] = 1 # 1 為可行走區域
    
    # 將地圖邊界設為障礙，避免超出
    grid_map[0, :] = 0
    grid_map[-1, :] = 0
    grid_map[:, 0] = 0
    grid_map[:, -1] = 0

    print("🗺️ 成功提取 HSV 走道遮罩，開始執行 CCPP 全區域路徑規劃...")
    
    # 5. CCPP 路徑規劃
    planner = CCPPPlanner(grid_map, resolution)
    
    # 走道中心線所在的列 (與壟完美對稱，Aisle 在兩壟的正中央)
    trench_columns = [12, 24, 36, 48, 60, 72, 84, 96]
    
    # 解析出各個走道中的可行走線段 (避開障礙物)
    segments_by_col = {}
    for c in trench_columns:
        walkable_rows = []
        for r in range(10, 141):
            if grid_map[r, c] == 1:
                walkable_rows.append(r)
        
        if not walkable_rows:
            continue
        
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

    # 起點設定在左上角的迴車道 (row=5, col=12)，消除「二刷」問題
    start_pos = (0.5, 1.2) 
    
    full_path = []
    transitions = []  # 儲存 A* 換行/繞道軌跡
    scans = []        # 儲存垂直掃描軌跡
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
                p_start = (r_start * resolution, c * resolution)
                transition = planner.plan(current_pos, p_start)
                if transition:
                    # 套用平滑化處理，讓過彎不再是死板直角
                    smoothed_trans = smooth_path(transition)
                    full_path.extend(smoothed_trans)
                    transitions.append(smoothed_trans)
                
                # 直線掃描該區間 (實體覆蓋)
                scan_steps = int((r_end - r_start) + 1)
                scan_seq = []
                for r in np.linspace(r_start, r_end, scan_steps):
                    pt = (r * resolution, c * resolution)
                    scan_seq.append(pt)
                    if not full_path or full_path[-1] != pt:
                        full_path.append(pt)
                scans.append(scan_seq)
                current_pos = (r_end * resolution, c * resolution)
            downwards = False
        else:
            # 由下往上走：區間按 row 從大到小排序
            segments = sorted(segments, key=lambda x: x[1], reverse=True)
            for r_start, r_end in segments:
                p_start = (r_end * resolution, c * resolution)
                transition = planner.plan(current_pos, p_start)
                if transition:
                    # 套用平滑化處理
                    smoothed_trans = smooth_path(transition)
                    full_path.extend(smoothed_trans)
                    transitions.append(smoothed_trans)
                
                # 直線掃描該區間 (向上掃描)
                scan_steps = int((r_end - r_start) + 1)
                scan_seq = []
                for r in np.linspace(r_end, r_start, scan_steps):
                    pt = (r * resolution, c * resolution)
                    scan_seq.append(pt)
                    if not full_path or full_path[-1] != pt:
                        full_path.append(pt)
                scans.append(scan_seq)
                current_pos = (r_start * resolution, c * resolution)
            downwards = True
            
    # 6. 視覺化
    plt.figure(figsize=(9, 12), dpi=150) # 提升解析度適合列印與海報
    
    # 輔助函式：計算路徑的視覺偏移，防止重疊軌跡，並動態分流多車道
    def apply_visual_offset(path_pts, is_scan=False, downward=True, index=0):
        if len(path_pts) == 0:
            return [], []
        offset_y = []
        offset_x = []
        
        # 1. 如果是縱向作業掃描線 (固定向左或向右微調)
        if is_scan:
            shift_x = -1.2 if downward else 1.2
            for p in path_pts:
                offset_y.append(p[0]/resolution)
                offset_x.append(p[1]/resolution + shift_x)
            return offset_x, offset_y
            
        # 2. 如果是過渡/繞行路徑 (依方向動態調整，並依 index 進行分流，避免多線重疊)
        n = len(path_pts)
        for i in range(n):
            y_val = path_pts[i][0] / resolution
            x_val = path_pts[i][1] / resolution
            
            if i < n - 1:
                ny = path_pts[i+1][0] / resolution
                nx = path_pts[i+1][1] / resolution
            else:
                if n > 1:
                    y_prev = path_pts[i-1][0] / resolution
                    x_prev = path_pts[i-1][1] / resolution
                    dy = y_val - y_prev
                    dx = x_val - x_prev
                    if abs(dx) > abs(dy): # 橫向
                        # 分流偏移量：依據 index 計算平行軌跡
                        shift_y = (-1.5 - index * 0.8) if y_val < 75 else (1.5 + index * 0.8)
                        shift_x = 0
                    else: # 縱向
                        shift_x = -1.5 if dy > 0 else 1.5
                        shift_y = 0
                    offset_y.append(y_val + shift_y)
                    offset_x.append(x_val + shift_x)
                    continue
                else:
                    offset_y.append(y_val)
                    offset_x.append(x_val)
                    continue
            
            dy = ny - y_val
            dx = nx - x_val
            shift_x, shift_y = 0, 0
            if abs(dx) > abs(dy): # 橫向移動 (往左或往右)
                # 分流偏移量
                shift_y = (-1.5 - index * 0.8) if y_val < 75 else (1.5 + index * 0.8)
            else: # 縱向移動 (往下或往上)
                shift_x = -1.5 if dy >= 0 else 1.5
                
            offset_y.append(y_val + shift_y)
            offset_x.append(x_val + shift_x)
            
        return offset_x, offset_y

    # 使用帶有透明度的地圖底圖，讓路徑更鮮明
    plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB), alpha=0.9)
    
    plotted_scans_offsets = []
    plotted_transitions_offsets = []

    # 繪製掃描路徑 (實線，綠色/青色系列代表作業中)
    for i, scan in enumerate(scans):
        downward = (scan[0][0] < scan[-1][0])
        sx, sy = apply_visual_offset(scan, is_scan=True, downward=downward)
        plotted_scans_offsets.append((sx, sy))
        
        # 只在第一條線段加 label 避免 legend 重複
        label = 'Trench Scan Path' if i == 0 else ""
        plt.plot(sx, sy, color='#2A9D8F', linewidth=3.5, label=label, zorder=3)
        
        # 在每條走道正中間繪製一個方向箭頭，乾淨俐落
        if len(sx) > 10:
            mid = len(sx) // 2
            dx = sx[mid+1] - sx[mid]
            dy = sy[mid+1] - sy[mid]
            norm = np.sqrt(dx**2 + dy**2)
            if norm > 0:
                plt.arrow(sx[mid], sy[mid], (dx/norm)*2, (dy/norm)*2, 
                          shape='full', color='#264653', lw=0, length_includes_head=True, head_width=2.5, zorder=4)
                
    # 繪製過彎與 A* 避障繞道軌跡 (橘色虛線代表過渡/換行)
    for i, trans in enumerate(transitions):
        tx, ty = apply_visual_offset(trans, is_scan=False, index=i)
        plotted_transitions_offsets.append((tx, ty))
        
        label = 'A* Transition / Bypass' if i == 0 else ""
        plt.plot(tx, ty, color='#E76F51', linewidth=2.5, linestyle='--', label=label, zorder=3)
        
        # 只在換行轉折點繪製少量方向箭頭
        if len(tx) > 15:
            mid = len(tx) // 2
            dx = tx[mid+1] - tx[mid]
            dy = ty[mid+1] - ty[mid]
            norm = np.sqrt(dx**2 + dy**2)
            if norm > 0:
                plt.arrow(tx[mid], ty[mid], (dx/norm)*1.5, (dy/norm)*1.5, 
                          shape='full', color='#E76F51', lw=0, length_includes_head=True, head_width=2.0, zorder=4)

    # 獲取完美對齊後的起點與終點坐標 (從繪製偏移後的線條端點抓取，保證視覺上完美銜接)
    # 起點是第一條 transition 的起點，終點是最後一條 scan 的終點
    if plotted_transitions_offsets:
        start_x_visual = plotted_transitions_offsets[0][0][0]
        start_y_visual = plotted_transitions_offsets[0][1][0]
    else:
        start_x_visual = start_pos[1]/resolution
        start_y_visual = start_pos[0]/resolution
        
    if plotted_scans_offsets:
        end_x_visual = plotted_scans_offsets[-1][0][-1]
        end_y_visual = plotted_scans_offsets[-1][1][-1]
    else:
        end_x_visual = full_path[-1][1]/resolution
        end_y_visual = full_path[-1][0]/resolution

    # 繪製起點與終點 (置頂，完美對齊軌跡線頭尾)
    plt.scatter([start_x_visual], [start_y_visual], c='#1D3557', s=200, marker='o', label='Start (Middle)', zorder=10)
    plt.scatter([end_x_visual], [end_y_visual], c='#E63946', s=200, marker='o', label='End (Goal)', zorder=10)
        
    plt.title("Strawberry Robot CCPP Path Planning (Poster Edition)", fontsize=16, fontweight='bold', pad=15)
    plt.xlabel("X (0.1m/grid)", fontsize=12)
    plt.ylabel("Y (0.1m/grid)", fontsize=12)
    
    # 漂亮的 Legend 配置
    plt.legend(bbox_to_anchor=(1.02, 1), loc='upper left', borderaxespad=0, fontsize=11, frameon=True, shadow=True)
    
    save_path = os.path.join(os.path.dirname(__file__), "hsv_simulation_result.png")
    plt.savefig(save_path, bbox_inches='tight')
    print(f"📸 模擬結果已儲存至：{save_path}")

if __name__ == "__main__":
    generate_simulation()
