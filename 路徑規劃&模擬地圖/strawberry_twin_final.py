import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.colors import ListedColormap

# --- 1. 物理參數 ---
FIELD_L, FIELD_W = 23.0, 18.0
RIDGE_H = 0.15
PERIOD = 1.2  # 壟+溝週期
RIDGE_W_BASE = 0.7

def build_final_strawberry_twin():
    print(f"🚀 正在生成最終版並儲存圖片...")

    # A. 建立地形網格 (背景)
    x_map = np.linspace(0, FIELD_W, 300)
    y_map = np.linspace(0, FIELD_L, 100)
    X, Y = np.meshgrid(x_map, y_map)
    Z = np.zeros_like(X)
    Z[(X % PERIOD) < RIDGE_W_BASE] = RIDGE_H
    
    Z_centers = (Z[:-1, :-1] + Z[1:, 1:]) / 4.0
    fcolors = np.where(Z_centers > 0.005, '#2E7D32', '#D2B48C')

    # B. --- 核心：三色自然散佈點邏輯 ---
    NUM_POINTS = 180 
    np.random.seed(66) 
    
    bx, by, bz, b_colors = [], [], [], []
    
    color_map = {
        'ripe': '#D32F2F',    # 紅
        'semi': '#FBC02D',    # 黃
        'unripe': '#388E3C'   # 綠
    }

    count = 0
    while count < NUM_POINTS:
        rx = np.random.uniform(0, FIELD_W)
        ry = np.random.uniform(0, FIELD_L)
        if (rx % PERIOD) < RIDGE_W_BASE:
            bx.append(rx)
            by.append(ry)
            bz.append(RIDGE_H + 0.04) 
            
            rand_val = np.random.rand()
            if rand_val > 0.66:
                b_colors.append(color_map['ripe'])
            elif rand_val > 0.33:
                b_colors.append(color_map['semi'])
            else:
                b_colors.append(color_map['unripe'])
            count += 1

    # --- 2. 3D 繪圖 ---
    fig = plt.figure(figsize=(16, 12))
    ax = fig.add_subplot(111, projection='3d')

    # 1. 畫出實體田壟
    ax.plot_surface(X, Y, Z, facecolors=fcolors,
                    linewidth=0, antialiased=False, shade=True, alpha=0.6)

    # 2. 畫出草莓點 (注意 zorder=10 確保點在最上方)
    ax.scatter(bx, by, bz, 
               c=b_colors, 
               s=120, 
               edgecolors='white', 
               linewidth=1.0, 
               alpha=1.0, 
               zorder=10)

    # 3. 視覺優化
    ax.set_box_aspect((FIELD_W, FIELD_L, 1.2)) 
    ax.set_title("Strawberry Twin - Final 3-Color Decision Model", fontsize=20)
    ax.set_xlabel("Width (m)")
    ax.set_ylabel("Length (m)")
    ax.set_zlabel("Height (m)")
    
    ax.set_zticks([0, 0.15, 0.5])
    ax.set_zlim(0, 0.6)
    
    # --- 關鍵：多視角儲存邏輯 (放在函數內，ax 才有效) ---
    views = [
        (90, -90, "Top_View.png"),    
        (0, -90,  "Side_View.png"),   
        (30, -60, "Perspective.png")  
    ]

    for elev, azim, filename in views:
        ax.view_init(elev=elev, azim=azim)
        plt.draw() # 強制刷新畫布
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        print(f"📸 視角已儲存：{filename}")

    print("✅ 最終版生成完成！共計 {} 個隨機分佈點。".format(len(bx)))
    plt.show()

# ==========================================
# 🚀 這是最重要的一行：執行呼叫函數！
# ==========================================
if __name__ == "__main__":
    build_final_strawberry_twin()