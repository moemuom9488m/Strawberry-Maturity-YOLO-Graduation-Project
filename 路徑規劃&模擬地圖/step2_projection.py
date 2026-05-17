import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import gaussian_kde
from mpl_toolkits.mplot3d import Axes3D

# --- 1. 物理與硬體參數 ---
REAL_L = 23.0    # 田長 (m)
REAL_W = 18.0    # 田寬 (m)
RIDGE_H = 0.15   # 壟高 (m)
PERIOD = 1.2     # 壟+溝週期
RIDGE_W_BASE = 0.7
W_OFFSET = 0.2   # 雙側相機安裝橫向偏移量 (m)
DEDUPLICATE_DIST = 0.1 # 10cm 空間去重閾值

def simulate_strawberry_ground_truth(num_berries=250):
    """
    在田壟上隨機散佈草莓的真實物理座標
    """
    np.random.seed(88)
    bx, by, bz, b_maturity = [], [], [], []
    count = 0
    while count < num_berries:
        rx = np.random.uniform(0, REAL_W)
        ry = np.random.uniform(1.0, REAL_L - 1.0)
        # 必須在田壟上
        if (rx % PERIOD) < RIDGE_W_BASE:
            bx.append(rx)
            by.append(ry)
            bz.append(RIDGE_H)
            b_maturity.append(np.random.rand())
            count += 1
    return np.column_stack([bx, by, bz, b_maturity])

def generate_ccpp_path(resolution=0.1):
    """
    生成與 ccpp_planner 一致的 CCPP 順序 (無跳行，每行全覆蓋) 巡檢路徑
    """
    trench_centers = []
    period_cells = int(1.2 / resolution)
    cols_num = int(REAL_W / resolution)
    rows_num = int(REAL_L / resolution)
    
    for c in range(0, cols_num, period_cells):
        center_x = c + int(0.95 / resolution)
        if center_x < cols_num:
            trench_centers.append(center_x * resolution)
            
    path = []
    direction = 1
    for x_m in trench_centers:
        y_top = 1.0
        y_bottom = REAL_L - 1.0
        y_steps = np.linspace(y_top, y_bottom, 120)
        if direction == -1:
            y_steps = y_steps[::-1]
            
        for y in y_steps:
            path.append((x_m, y))
        direction *= -1
    return path

def run_projection_system():
    print("🍓 正在啟動雙側相機 CCPP 地面投影感知去重系統...")
    
    # 1. 產生草莓真實物理座標與 CCPP 路徑
    gt_berries = simulate_strawberry_ground_truth()
    path = generate_ccpp_path()
    
    # 2. 模擬自走車行駛並進行雙側動態側拍
    detected_raw_points = []
    
    # 遍歷路徑段，計算位姿 angle
    for i in range(1, len(path)):
        x1, y1 = path[i-1]
        x2, y2 = path[i]
        
        # AGV 當前位置與朝向角
        x_v, y_v = (x1 + x2) / 2.0, (y1 + y2) / 2.0
        theta = np.arctan2(y2 - y1, x2 - x1)
        
        # 朝向與側向單位向量
        v_head = np.array([np.cos(theta), np.sin(theta)])
        v_left = np.array([-np.sin(theta), np.cos(theta)])
        v_right = np.array([np.sin(theta), -np.cos(theta)])
        
        # 尋找當前視野內的草莓 (距離 AGV 行進軸向前後 0.5m，橫向 1.0m 內)
        for berry in gt_berries:
            bx, by, bz, bm = berry
            v_berry = np.array([bx - x_v, by - y_v])
            
            # 投影到前向與側向
            dist_long = np.dot(v_berry, v_head)
            dist_lat = np.dot(v_berry, v_left) # 左側為正，右側為負
            
            # 若草莓在相機 FOV 內 (橫向 0.4 到 0.8m 之間，前向 0.3m 內)
            if abs(dist_long) < 0.3:
                # 判斷是左側還是右側相機檢測到
                if 0.4 <= dist_lat <= 0.8: # 左側相機檢測
                    d_sensor = dist_lat - W_OFFSET
                    # 引入傳感器量測雜訊
                    d_sensor += np.random.normal(0, 0.015)
                    # 透過左側投影公式還原
                    rx = x_v + (W_OFFSET + d_sensor) * v_left[0]
                    ry = y_v + (W_OFFSET + d_sensor) * v_left[1]
                    detected_raw_points.append([rx, ry, RIDGE_H, bm])
                elif -0.8 <= dist_lat <= -0.4: # 右側相機檢測
                    d_sensor = -dist_lat - W_OFFSET
                    d_sensor += np.random.normal(0, 0.015)
                    # 透過右側投影公式還原
                    rx = x_v + (W_OFFSET + d_sensor) * v_right[0]
                    ry = y_v + (W_OFFSET + d_sensor) * v_right[1]
                    detected_raw_points.append([rx, ry, RIDGE_H, bm])
                    
    detected_raw_points = np.array(detected_raw_points)
    print(f"📊 模擬側拍完成：雙側相機共偵測到 {len(detected_raw_points)} 訊框草莓特徵點")
    
    # 3. 實作 10cm 歐氏距離點雲空間去重與多訊框融合
    unique_berries = []
    for pt in detected_raw_points:
        rx, ry, rz, rm = pt
        if len(unique_berries) == 0:
            unique_berries.append([rx, ry, rz, rm, 1]) # [x, y, z, maturity, count]
        else:
            # 計算與既有去重點的最短距離
            unique_np = np.array(unique_berries)
            dists = np.sqrt((unique_np[:, 0] - rx)**2 + (unique_np[:, 1] - ry)**2)
            min_idx = np.argmin(dists)
            
            if dists[min_idx] < DEDUPLICATE_DIST:
                # 歐氏距離小於10cm，進行特徵融合同步均值
                cnt = unique_berries[min_idx][4]
                unique_berries[min_idx][0] = (unique_berries[min_idx][0] * cnt + rx) / (cnt + 1)
                unique_berries[min_idx][1] = (unique_berries[min_idx][1] * cnt + ry) / (cnt + 1)
                unique_berries[min_idx][3] = (unique_berries[min_idx][3] * cnt + rm) / (cnt + 1)
                unique_berries[min_idx][4] += 1
            else:
                unique_berries.append([rx, ry, rz, rm, 1])
                
    unique_berries = np.array(unique_berries)
    print(f"✨ 10cm 空間去重融合完畢：原始 {len(detected_raw_points)} 點融合為 {len(unique_berries)} 顆獨立草莓")
    
    # 4. 繪製數位孿生與熱力圖
    fig = plt.figure(figsize=(15, 7))
    
    # [左圖] 2.5D 雙側側拍數位孿生點雲
    ax1 = fig.add_subplot(121, projection='3d')
    colors = plt.cm.RdYlGn_r(unique_berries[:, 3])
    ax1.scatter(unique_berries[:, 0], unique_berries[:, 1], unique_berries[:, 2], 
                c=colors, s=40, edgecolors='black', linewidth=0.5, alpha=0.9)
    
    # 繪製 CCPP 巡檢軌跡線
    path_np = np.array(path)
    ax1.plot(path_np[:, 0], path_np[:, 1], np.zeros(len(path)), 'b-', alpha=0.4, label='CCPP Path')
    
    ax1.set_title("2.5D Dual-Camera Bilateral Digital Twin", fontsize=12)
    ax1.set_zlim(0, 0.5)
    ax1.set_xlabel("Width (m)")
    ax1.set_ylabel("Length (m)")
    ax1.legend()
    
    # [右圖] 去重後的成熟度熱力圖 (KDE)
    ax2 = fig.add_subplot(122)
    x, y = unique_berries[:, 0], unique_berries[:, 1]
    weights = unique_berries[:, 3]
    
    k = gaussian_kde(np.vstack([x, y]), weights=weights)
    xi, yi = np.mgrid[0:REAL_W:100j, 0:REAL_L:100j]
    zi = k(np.vstack([xi.flatten(), yi.flatten()]))
    
    im = ax2.pcolormesh(xi, yi, zi.reshape(xi.shape), shading='auto', cmap='YlOrRd')
    plt.colorbar(im, ax=ax2, label='Maturity Density')
    ax2.set_title("Patrol Maturity Decision Map (Heatmap)", fontsize=12)
    ax2.set_xlabel("Width (m)")
    ax2.set_ylabel("Length (m)")
    
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    run_projection_system()