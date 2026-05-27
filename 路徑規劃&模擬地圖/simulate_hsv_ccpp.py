import cv2
import numpy as np
import matplotlib.pyplot as plt
import sys
import os

sys.path.append(os.path.dirname(__file__))
from ccpp_planner import CCPPPlanner

# 拉普拉斯平滑，讓軌跡更有「自走車平滑過彎」的流線感
def smooth_path(path_pts, passes=5):
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
    print("🎨 正在生成極致美學與工程邏輯兼具的 AI 路徑規劃圖...")
    
    # 1. 物理參數設定
    resolution = 0.1
    field_l, field_w = 15.0, 10.0
    rows = int(field_l / resolution)
    cols = int(field_w / resolution)
    
    # 畫布底色 (莫蘭迪米色, Hex: #F4EAE1)
    img = np.full((rows, cols, 3), (225, 234, 244), dtype=np.uint8)
    
    # 2. 完美對稱草莓壟 (莫蘭迪深綠, Hex: #3A5A40)
    ridge_columns = [4, 16, 28, 40, 52, 64, 76, 88]
    for c in ridge_columns:
        img[10:140, c:c+4] = (64, 90, 58)
        
    # 3. 移除中央障礙物與灰色捷徑，全域唯一的障礙物即為草莓田 (綠色壟)
    
    # 4. 遮罩提取
    mask_tan = cv2.inRange(img, (220, 230, 240), (230, 240, 250))
    mask_grey = cv2.inRange(img, (190, 200, 195), (205, 220, 210)) # 目前會是空的，保留以防日後擴充
    
    # 全域可行走區域 (泥土 + 灰色捷徑)
    grid_map = np.zeros((rows, cols), dtype=int)
    grid_map[(mask_tan > 0) | (mask_grey > 0)] = 1
    
    grid_map[0, :] = 0
    grid_map[-1, :] = 0
    grid_map[:, 0] = 0
    grid_map[:, -1] = 0

    print("🗺️ 成功提取遮罩，開始計算路徑...")
    planner = CCPPPlanner(grid_map, resolution)
    trench_columns = [12, 24, 36, 48, 60, 72, 84, 96]
    
    # 【關鍵邏輯升級】只提取「泥土區」作為掃描目標，灰色捷徑區只用於繞道，不用於掃描！
    segments_by_col = {}
    for c in trench_columns:
        scan_rows = []
        for r in range(10, 141):
            if mask_tan[r, c] > 0: # 只有泥土才掃描
                scan_rows.append(r)
        
        if not scan_rows:
            continue
            
        col_segments = []
        start_r = scan_rows[0]
        prev_r = scan_rows[0]
        for r in scan_rows[1:]:
            if r - prev_r > 1:
                col_segments.append((start_r, prev_r))
                start_r = r
            prev_r = r
        col_segments.append((start_r, prev_r))
        segments_by_col[c] = col_segments

    # 起點設定在左上角 (消滅二刷)
    start_pos = (0.5, 1.2) 
    
    full_path = []
    transitions = []
    scans = []
    current_pos = start_pos
    downwards = True
    
    for c in trench_columns:
        if c not in segments_by_col:
            continue
        segments = segments_by_col[c]
        
        if downwards:
            segments = sorted(segments, key=lambda x: x[0])
            for r_start, r_end in segments:
                p_start = (r_start * resolution, c * resolution)
                transition = planner.plan(current_pos, p_start)
                if transition:
                    smoothed_trans = smooth_path(transition)
                    full_path.extend(smoothed_trans)
                    transitions.append(smoothed_trans)
                
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
            segments = sorted(segments, key=lambda x: x[1], reverse=True)
            for r_start, r_end in segments:
                p_start = (r_end * resolution, c * resolution)
                transition = planner.plan(current_pos, p_start)
                if transition:
                    smoothed_trans = smooth_path(transition)
                    full_path.extend(smoothed_trans)
                    transitions.append(smoothed_trans)
                
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
            
    # 視覺化
    plt.figure(figsize=(9, 12), dpi=150)
    
    plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB), alpha=0.9)
    
    # 繪製掃描路徑 (實線，綠色/青色系列代表作業中)
    for i, scan in enumerate(scans):
        sy = [p[0]/resolution for p in scan]
        sx = [p[1]/resolution for p in scan]
        
        label = 'Trench Scan Path' if i == 0 else ""
        plt.plot(sx, sy, color='#2A9D8F', linewidth=3.5, label=label, zorder=3)
        
        if len(sx) > 10:
            mid = len(sx) // 2
            dx = sx[mid+1] - sx[mid]
            dy = sy[mid+1] - sy[mid]
            norm = np.sqrt(dx**2 + dy**2)
            if norm > 0:
                plt.arrow(sx[mid], sy[mid], (dx/norm)*2, (dy/norm)*2, 
                          shape='full', color='#264653', lw=0, length_includes_head=True, head_width=2.5, zorder=4)
                
    # 繪製過彎與換行軌跡 (橘色虛線代表過渡/換行)
    for i, trans in enumerate(transitions):
        ty = [p[0]/resolution for p in trans]
        tx = [p[1]/resolution for p in trans]
        
        label = 'CCPP Transition / Highway' if i == 0 else ""
        plt.plot(tx, ty, color='#E76F51', linewidth=2.5, linestyle='--', label=label, zorder=3)
        
        if len(tx) > 15:
            mid = len(tx) // 2
            dx = tx[mid+1] - tx[mid]
            dy = ty[mid+1] - ty[mid]
            norm = np.sqrt(dx**2 + dy**2)
            if norm > 0:
                plt.arrow(tx[mid], ty[mid], (dx/norm)*1.5, (dy/norm)*1.5, 
                          shape='full', color='#E76F51', lw=0, length_includes_head=True, head_width=2.0, zorder=4)

    # 獲取起點與終點坐標
    start_x_visual = start_pos[1]/resolution
    start_y_visual = start_pos[0]/resolution
    end_x_visual = full_path[-1][1]/resolution
    end_y_visual = full_path[-1][0]/resolution

    # 起點與終點，加入 edgecolors 讓它更有高級感
    plt.scatter([start_x_visual], [start_y_visual], c='#1D3557', s=250, marker='o', edgecolors='white', linewidths=2.5, label='Start Node', zorder=10)
    plt.scatter([end_x_visual], [end_y_visual], c='#E63946', s=250, marker='o', edgecolors='white', linewidths=2.5, label='End Node', zorder=10)
        
    plt.title("Intelligent CCPP Path Planning", fontsize=18, fontweight='bold', pad=15)
    plt.xlabel("X (0.1m/grid)", fontsize=12)
    plt.ylabel("Y (0.1m/grid)", fontsize=12)
    
    plt.legend(bbox_to_anchor=(1.02, 1), loc='upper left', borderaxespad=0, fontsize=11, frameon=True, shadow=True)
    
    save_path = os.path.join(os.path.dirname(__file__), "hsv_simulation_result.png")
    plt.savefig(save_path, bbox_inches='tight')
    print(f"📸 模擬結果已儲存至：{save_path}")

if __name__ == "__main__":
    generate_simulation()
