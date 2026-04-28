import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# --- 1. 物理參數 (維持你的 18m x 23m) ---
FIELD_L, FIELD_W = 23.0, 18.0
RIDGE_H = 0.15        
RIDGE_W_TOP = 0.5     
RIDGE_W_BASE = 0.7    
TRENCH_W = 0.8        # 稍微加寬溝渠，讓平地視覺感更強

def build_expansive_field():
    print(f"🚀 正在拉大長寬比例，建立開闊場景...")

    # A. 高解析度網格
    x = np.linspace(0, FIELD_W, 500) 
    y = np.linspace(0, FIELD_L, 150)
    X, Y = np.meshgrid(x, y)

    # B. 梯形幾何數據
    period = RIDGE_W_BASE + TRENCH_W
    local_x = X % period
    slope_w = (RIDGE_W_BASE - RIDGE_W_TOP) / 2
    
    Z = np.zeros_like(X)
    # 左斜坡
    m1 = (local_x >= 0) & (local_x < slope_w)
    Z[m1] = (local_x[m1] / slope_w) * RIDGE_H
    # 平坦頂部
    m2 = (local_x >= slope_w) & (local_x < (RIDGE_W_BASE - slope_w))
    Z[m2] = RIDGE_H
    # 右斜坡
    m3 = (local_x >= (RIDGE_W_BASE - slope_w)) & (local_x < RIDGE_W_BASE)
    Z[m3] = RIDGE_H - ((local_x[m3] - (RIDGE_W_BASE - slope_w)) / slope_w) * RIDGE_H

    # C. 逐面著色 (Face Colors) - 確保顏色邊界乾淨
    Z_centers = (Z[:-1, :-1] + Z[1:, :-1] + Z[:-1, 1:] + Z[1:, 1:]) / 4.0
    fcolors = np.where(Z_centers > 0.005, '#2E7D32', '#D2B48C')

    # --- 2. 3D 繪圖 ---
    fig = plt.figure(figsize=(20, 10)) # 加寬畫布比例
    ax = fig.add_subplot(111, projection='3d')

    surf = ax.plot_surface(X, Y, Z, facecolors=fcolors,
                           linewidth=0, antialiased=False, shade=True)

    # --- 關鍵修正：極致壓平 Z 軸 ---
    # 這裡將 Z 的比例設為 1.0 (原本是 3.0 或更大)
    # 這會讓 18m 和 23m 的長度顯得非常巨大，而 15cm 的壟會變得非常平緩、寫實
    ax.set_box_aspect((FIELD_W, FIELD_L, 1.0)) 

    # 視覺優化
    ax.set_title("3D Expansive Strawberry Field Model", fontsize=18)
    ax.set_xlabel("Width (m)")
    ax.set_ylabel("Length (m)")
    ax.set_zlabel("Height (m)")
    
    # 固定高度範圍，不要讓它跳出來
    ax.set_zlim(0, 1.5) 
    
    # 降低視角，從低處看過去更像真實田野
    ax.view_init(elev=15, azim=-65)

    print("✅ 成功！現在場景看起來會非常寬廣平坦，就像真實的大型草莓田。")
    plt.show()

if __name__ == "__main__":
    build_expansive_field()