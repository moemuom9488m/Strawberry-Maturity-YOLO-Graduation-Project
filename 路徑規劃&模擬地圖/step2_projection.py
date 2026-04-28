import cv2
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import gaussian_kde
from mpl_toolkits.mplot3d import Axes3D

# --- 1. 硬體與物理參數 ---
REAL_L = 23.0    # 田長 (m)
REAL_W = 18.0    # 田寬 (m)
RIDGE_H = 0.15   # 壟高 (m)
CAMERA_H = 5.0   # 假設相機拍攝高度 (m)

# 這是你剛才點出來的「金級座標」
IMAGE_CORNERS = [(8, 9), (1138, 5), (1174, 838), (18, 812)]

def run_projection_system():
    # 計算單應性矩陣 H
    src_pts = np.array(IMAGE_CORNERS, dtype=np.float32)
    dst_pts = np.array([[0,0], [REAL_W,0], [REAL_W,REAL_L], [0,REAL_L]], dtype=np.float32)
    H, _ = cv2.findHomography(src_pts, dst_pts)

    # --- 2. 偵測模擬 (接下來可以串接你的 MobileNetV2) ---
    # 這裡我們模擬 100 顆草莓的像素位置與成熟度 (0~1)
    np.random.seed(42)
    num_berries = 100
    mock_u = np.random.randint(10, 1100, num_berries)
    mock_v = np.random.randint(10, 800, num_berries)
    mock_maturity = np.random.rand(num_berries)

    real_world_points = []
    for u, v, m in zip(mock_u, mock_v, mock_maturity):
        # A. 基本平面轉換
        pixel_pt = np.array([[[u, v]]], dtype=np.float32)
        ground_pos = cv2.perspectiveTransform(pixel_pt, H)[0][0]
        
        # B. 2.5D 高度補償 (考慮 15cm 壟高)
        # 基於相似三角形原理，修正向邊緣偏移的誤差
        comp = (CAMERA_H - RIDGE_H) / CAMERA_H
        rx = ground_pos[0] * comp
        ry = ground_pos[1] * comp
        
        real_world_points.append([rx, ry, RIDGE_H, m])

    real_world_points = np.array(real_world_points)

    # --- 3. 視覺化回饋 ---
    fig = plt.figure(figsize=(14, 6))

    # [左圖] 2.5D 數位孿生點雲
    ax1 = fig.add_subplot(121, projection='3d')
    colors = plt.cm.RdYlGn_r(real_world_points[:, 3]) # 成熟度映射顏色
    ax1.scatter(real_world_points[:, 0], real_world_points[:, 1], real_world_points[:, 2], 
               c=colors, s=30, edgecolors='w')
    ax1.set_title("2.5D Strawberry Digital Twin")
    ax1.set_zlim(0, 1)
    ax1.set_xlabel("Width (m)"); ax1.set_ylabel("Length (m)")

    # [右圖] 成熟度熱力圖 (KDE)
    ax2 = fig.add_subplot(122)
    x, y = real_world_points[:, 0], real_world_points[:, 1]
    weights = real_world_points[:, 3]
    k = gaussian_kde(np.vstack([x, y]), weights=weights)
    xi, yi = np.mgrid[0:REAL_W:100j, 0:REAL_L:100j]
    zi = k(np.vstack([xi.flatten(), yi.flatten()]))
    
    im = ax2.pcolormesh(xi, yi, zi.reshape(xi.shape), shading='auto', cmap='YlOrRd')
    plt.colorbar(im, ax=ax2, label='Maturity Density')
    ax2.set_title("Harvest Decision Map (Heatmap)")
    ax2.set_xlabel("Width (m)"); ax2.set_ylabel("Length (m)")

    plt.tight_layout()
    print("✅ 2.5D 數位孿生投影完成！")
    plt.show()

if __name__ == "__main__":
    run_projection_system()