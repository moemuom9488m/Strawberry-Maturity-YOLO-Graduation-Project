# -*- coding: utf-8 -*-
import matplotlib.pyplot as plt
import seaborn as sns
import os
import numpy as np

# --- 環境與中文字型初始化 ---
sns.set_theme(style='whitegrid')
plt.rcParams['font.sans-serif'] = [
    'Microsoft JhengHei',  # 微軟正黑體
    'DFKai-SB',            # 標楷體
    'PingFang TC',         # 蘋果繁中
    'sans-serif'
]
plt.rcParams['axes.unicode_minus'] = False

# 1. 準備數據
res = ['640px', '800px', '1024px']
m50 = [0.86488, 0.86523, 0.86593]
m95 = [0.63694, 0.64423, 0.63683]

# =====================================================================
# 2. 創建畫布 (精準設定為 1920x1080)
#    公式：figsize(寬, 高) * dpi = 像素
#    9.6 * 200 = 1920, 5.4 * 200 = 1080
# =====================================================================
fig, ax = plt.subplots(figsize=(9.6, 5.4), dpi=200)

c1 = '#4361EE'  # 皇家藍
c2 = '#F72585'  # 霓虹粉

# 繪製折線
ax.plot(res, m50, marker='o', color=c1, linewidth=2.5, markersize=8, label='Best mAP@0.5')
ax.plot(res, m95, marker='s', color=c2, linewidth=2.5, linestyle='--', markersize=8, label='Best mAP@0.5:0.95')

ax.set_xlabel('輸入影像解析度 (Resolution)', fontsize=12, labelpad=10, fontweight='bold')
ax.set_ylabel('mAP Score', fontsize=12, labelpad=10, fontweight='bold')
ax.set_ylim(0.58, 0.92)

# 3. 標註數據數值
for i, v in enumerate(m50):
    ax.annotate(f'{v:.5f}', (res[i], m50[i]), xytext=(0, 10), textcoords='offset points', ha='center', fontsize=9, color=c1, fontweight='bold')
    
for i, v in enumerate(m95):
    ax.annotate(f'{v:.5f}', (res[i], m95[i]), xytext=(0, 10), textcoords='offset points', ha='center', fontsize=9, color=c2, fontweight='bold')

# 4. 圖例移到圖表右側邊緣
ax.legend(loc="upper left", bbox_to_anchor=(1.02, 1.0), frameon=True, facecolor='#F8F9FA', fontsize=10)

plt.title('影像輸入解析度對偵測精度之邊際效應對比圖', fontsize=14, fontweight='bold', pad=15)

# 調整圖表在畫布中的位置，將圖表壓縮在左邊的 60% 空間，留出右方空白
plt.subplots_adjust(left=0.08, right=0.6, top=0.85, bottom=0.15)

# 5. 在右側空白處加入列點文字
text_content = (
    "• Engineering Trade-off\n\n"
    "• Background Noise Overfitting\n\n"
    "• Both in 150 Epochs training\n\n"
    "• The Optimal Sweet Spot: 800px"
)

# =====================================================================
# 💡 【微調區塊】如何移動右邊的文字？
# 修改下方的 `x` 與 `y` 數值：
# - x (預設 0.72): 控制左右位置。0 是最左邊，1 是最右邊。數值越大越靠右。
# - y (預設 0.5): 控制上下位置。0 是最下方，1 是最上方。0.5 代表垂直置中。
# =====================================================================
text_x = 0.67
text_y = 0.5
fig.text(text_x, text_y, text_content, fontsize=14, va='center', ha='left', fontweight='bold', color='#2b2b2b', linespacing=1.8)

# 6. 儲存圖片
output_dir = "evaluation_results"
os.makedirs(output_dir, exist_ok=True)
img_path = os.path.join(output_dir, "resolution_tradeoff_comparison_1920x1080.png")

# 儲存時指定白色背景，且不使用 tight_layout，以保留我們手動調的邊界
plt.savefig(img_path, dpi=200, facecolor='white')
plt.close()
print(f"🎉 [SUCCESS] 1920x1080 解析度對比圖已成功生成並儲存: {img_path}")
