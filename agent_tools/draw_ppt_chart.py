#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
草莓監測機器人畢業專題 - 簡報專用模型選擇對比圖繪製工具
==============================================================================
說明：
為簡報（PPT）繪製一張高品質、雙Y軸（精度 mAP vs 訓練耗時）的柱狀與折線對照圖。
聚焦於簡報故事線所提及的 4 個關鍵決策模型：
1. YOLO11s Baseline (640px)
2. YOLO11m Baseline (640px)
3. YOLO11s Baseline (800px)
4. YOLO11s P2-CBAM (800px) [最佳實車部署候選]
==============================================================================
"""

import os
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

def main():
    # 1. 設置中文字型與美化主題
    sns.set_theme(style="whitegrid")
    plt.rcParams['font.sans-serif'] = [
        'Microsoft JhengHei',  # 微軟正黑體
        'DFKai-SB',            # 標楷體
        'PingFang TC',         # 蘋果繁中
        'sans-serif'
    ]
    plt.rcParams['axes.unicode_minus'] = False
    
    # 2. 準備數據
    models = [
        "YOLO11s Baseline\n(640px)",
        "YOLO11m Baseline\n(640px)",
        "YOLO11s Baseline\n(800px)",
        "YOLO11m P2-CBAM\n(800px)"
    ]
    
    map50 = [0.8675, 0.8560, 0.8652, 0.8740]
    map50_95 = [0.6307, 0.4389, 0.6442, 0.6306]
    train_time_min = [25.0, 41.0, 51.0, 68.0]
    
    x = np.arange(len(models))
    width = 0.4  # 柱子寬度
    
    # 3. 創建畫布 (高解析度 1920*1080)
    fig, ax1 = plt.subplots(figsize=(9.6, 5.4), dpi=200)
    
    # 質感 HSL 漸層配色
    bar_colors = ['#4CC9F0', '#4361EE', '#FF9F1C', '#F72585']  # s_640, m_640, s_800, s_P2CBAM_800
    
    # 4. 繪製左軸：Best mAP@0.5 與 mAP@0.5:0.95 (重疊柱狀圖)
    # 4.1 繪製底層的 mAP@0.5 柱狀圖
    bars = ax1.bar(x, map50, width, color=bar_colors, alpha=0.85, edgecolor='black', linewidth=1.2, zorder=3, label='mAP@0.5')
    
    # 4.2 覆蓋上層的 mAP@0.5:0.95 虛線斜線柱狀圖 (採用半透明白色磨砂玻璃效果 + 斜線填充 Hatch)
    bars_95 = ax1.bar(x, map50_95, width, color='white', alpha=0.35, edgecolor='black', linestyle='--', linewidth=1.8, hatch='//', zorder=4, label='mAP@0.5:0.95')
    
    ax1.set_xlabel("評估實驗模型與影像尺寸組合", fontsize=14, labelpad=15, fontweight='bold')
    ax1.set_ylabel("Best\nmAP", fontsize=14, color='#4361EE', fontweight='bold', labelpad=30, rotation=0, va='center', ha='center')
    ax1.tick_params(axis='y', labelcolor='#4361EE', labelsize=12)
    ax1.set_ylim(0.35, 0.95)  # 擴大範圍以完整容納兩種指標
    ax1.set_xticks(x)
    ax1.set_xticklabels(models, fontsize=12, fontweight='bold')
    
    # 在 mAP50 柱狀圖上方標註數值
    for bar in bars:
        height = bar.get_height()
        ax1.annotate(f'{height:.4f}',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 5),  # 向上偏移 5 點
                    textcoords="offset points",
                    ha='center', va='bottom', fontsize=11, fontweight='bold', color='black')
                    
    # 在 mAP50-95 柱狀圖內部頂端標註數值
    for bar in bars_95:
        height = bar.get_height()
        ax1.annotate(f'{height:.4f}',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, -15),  # 往下偏移 15 點
                    textcoords="offset points",
                    ha='center', va='top', fontsize=10, fontweight='bold', color='black')
        
    # 5. 繪製右軸：訓練耗時 (折線圖，表示計算成本)
    ax2 = ax1.twinx()
    line_color = '#E63946'
    line = ax2.plot(x, train_time_min, color=line_color, marker='o', markersize=10, 
                     linewidth=3, linestyle='--', label="訓練耗時 (分鐘)", zorder=4)
    ax2.set_ylabel("訓\n練\n時\n間\n\n(min)", fontsize=14, color=line_color, fontweight='bold', labelpad=30, rotation=0, va='center', ha='center')
    ax2.tick_params(axis='y', labelcolor=line_color, labelsize=12)
    ax2.set_ylim(10, 80)
    
    # 在折線圖點上方標註時間數值 (改為向下偏移，避免與柱子數值重疊)
    for i, txt in enumerate(train_time_min):
        ax2.annotate(f'{txt:.0f} min', (x[i], train_time_min[i]), 
                    xytext=(0, -22), textcoords='offset points', 
                    ha='center', fontsize=11, fontweight='bold', color=line_color)
        
    # 6. 圖表美化設計 (無邊框、精緻格線)
    ax1.grid(True, linestyle=':', alpha=0.6, zorder=0)
    
    # 7. 建立統一圖例 (包含 mAP@0.5, mAP@0.5:0.95 與訓練時間)
    import matplotlib.patches as mpatches
    import matplotlib.lines as mlines
    map50_patch = mpatches.Patch(facecolor='#4361EE', alpha=0.85, edgecolor='black', label='mAP@0.5 (柱狀圖)')
    map95_patch = mpatches.Patch(facecolor='white', alpha=0.35, edgecolor='black', linestyle='--', linewidth=1.5, hatch='//', label='mAP@0.5:0.95 (虛線區塊)')
    time_line = mlines.Line2D([], [], color='#E63946', marker='o', markersize=8, linestyle='--', linewidth=2, label='訓練時間 (右軸折線)')
    ax1.legend(handles=[map50_patch, map95_patch, time_line], loc='upper left', bbox_to_anchor=(0.02, 0.98), fontsize=9, frameon=True, facecolor='#F8F9FA')
    

    
    # 8. 儲存圖片 (精準 1920*1080 像素，無裁切)
    output_dir = "evaluation_results"
    os.makedirs(output_dir, exist_ok=True)
    img_path = os.path.join(output_dir, "ppt_model_selection_comparison.png")
    plt.tight_layout()
    plt.savefig(img_path, dpi=200)
    plt.close()
    print(f"[SUCCESS] 簡報專用決策圖已成功生成: {img_path}")

if __name__ == "__main__":
    main()
