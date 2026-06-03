# -*- coding: utf-8 -*-
import matplotlib.pyplot as plt
import matplotlib.patches as patches

def draw_layer_bg(ax, x, y, width, height, title, bg_color):
    """繪製四大層級的大型背景外框（含層級標題）"""
    rect = patches.FancyBboxPatch((x, y), width, height, boxstyle="round,pad=0.02",
                                  facecolor=bg_color, edgecolor='#aaaaaa', linewidth=1, alpha=0.3)
    ax.add_patch(rect)
    # 層級大標題（置於背景框左上角附近）
    ax.text(x + 0.02, y + height - 0.04, title, fontsize=14, weight='bold', color='#333333', ha='left', va='top')

def draw_block(ax, x, y, width, height, title, details, facecolor, edgecolor='black', lw=1.5):
    """繪製層級內部的功能模組方框（標題加粗 + 詳細技術說明）"""
    box = patches.FancyBboxPatch((x, y), width, height, boxstyle="round,pad=0.03",
                                 facecolor=facecolor, edgecolor=edgecolor, linewidth=lw)
    ax.add_patch(box)
    
    # 模組標題
    ax.text(x + width/2, y + height - 0.03, title, ha='center', va='top', fontsize=12, weight='bold', color='black')
    # 模組技術細節 (靠左對齊，置中偏下)
    ax.text(x + 0.02, y + 0.02, details, ha='left', va='bottom', fontsize=9.5, color='#444444', linespacing=1.3)

def draw_arrow(ax, x1, y1, x2, y2, text=""):
    """繪製模組間的資料流向箭頭，可自由加上資料名稱文字"""
    ax.annotate(text, xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle="-|>", lw=2, color='#444444', mutation_scale=15),
                ha='center', va='bottom', fontsize=10, weight='bold', color='darkblue')

def main():
    # 建立一個適合放進簡報的 16:9 寬螢幕畫布
    fig, ax = plt.subplots(figsize=(15, 9))
    ax.axis('off')

    # 全域大標題
    ax.text(0.5, 1.05, 'Air-Ground Collaborative Dual-Camera Strawberry Maturity Monitoring System — System Pipeline', 
            ha='center', va='center', fontsize=20, weight='bold', color='#1a1a1a')

    # =========================================================================
    # STAGE 1: 全局建圖層 (Mapping & Pre-processing)
    # =========================================================================
    draw_layer_bg(ax, 0.02, 0.73, 0.96, 0.24, 'STAGE 1: Global Mapping Layer (Mapping & Pre-processing)', '#ffeeee')
    
    draw_block(ax, 0.04, 0.75, 0.30, 0.14, 
               '1A. Aerial Survey & Image Capture', 
               '• UAV high-altitude top-down photography\n• Acquire global RGB images of orchard\n• Transmit to ground workstation', '#ffcccc')
    
    draw_block(ax, 0.62, 0.75, 0.34, 0.14, 
               '1B. HSV Color Segmentation &\nSkeleton Extraction', 
               '• CLAHE equalization removes glare/shadows\n• Morphological close filters weed noise\n• Extract physical centerlines of ridges & trenches', '#ffcc99')

    # 資料流箭頭：航測影像送到分割模組
    draw_arrow(ax, 0.34, 0.82, 0.62, 0.82, 'Global RGB Image')

    # =========================================================================
    # STAGE 2: 導航策略層 (Planning)
    # =========================================================================
    draw_layer_bg(ax, 0.02, 0.49, 0.96, 0.21, 'STAGE 2: Navigation Strategy Layer (Planning)', '#eedeec')
    
    draw_block(ax, 0.28, 0.51, 0.44, 0.13, 
               '2. CCPP Full Coverage Path Planning', 
               '• Auto-generate sequential zigzag cruise trajectories\n• Traverse each trench sequentially without skipping rows\n• CCPP planner ensures smooth obstacle avoidance & transitions', '#e6ccff', edgecolor='darkmagenta', lw=2)

    # 從 Stage 1B 輸出網格地圖到 Stage 2
    draw_arrow(ax, 0.79, 0.75, 0.50, 0.64, 'Grid Map (farm_grid_map.csv)')

    # =========================================================================
    # STAGE 3: 感知執行層 (Perception & Actuation)
    # =========================================================================
    draw_layer_bg(ax, 0.02, 0.20, 0.96, 0.26, 'STAGE 3: Perception & Actuation Layer', '#eeffee')
    
    draw_block(ax, 0.03, 0.22, 0.28, 0.17, 
               '3A. AGV Dual-Camera\nDynamic Side-view Capture', 
               '• AGV drives along CCPP trajectory\n• Dual side cameras capture ridges\n  simultaneously\n• Discard homography; dynamic local\n  projection based on vehicle pose\n  and depth d', '#ccffcc')
    
    draw_block(ax, 0.34, 0.22, 0.30, 0.17, 
               '3B. YOLOv11s Perception &\nTracking', 
               '• Lock to lightweight S scale (cuda:0)\n• Accurate maturity recognition\n  & ID tracking\n• Tiny object detection head (P2 head)\n  with CBAM suppresses glare and noise', '#ccffcc', edgecolor='red', lw=2.5)
    
    draw_block(ax, 0.67, 0.22, 0.29, 0.17, 
               '3C. Spatial Deduplication &\nFusion', 
               '• 10cm Euclidean distance point cloud\n  clustering\n• Cross-frame repeated detection\n  deduplication\n• Dynamically update global physical\n  coordinates & average maturity', '#ccffcc')

    # 導航策略層下發路徑點到自走車
    draw_arrow(ax, 0.50, 0.51, 0.17, 0.39, 'Inspection Waypoints (coverage_path)')
    
    # 感知執行層內部的資訊流
    draw_arrow(ax, 0.31, 0.305, 0.34, 0.305, 'Real-time\nVideo Stream')
    draw_arrow(ax, 0.64, 0.305, 0.67, 0.305, 'Maturity\nFeature Points')

    # =========================================================================
    # STAGE 4: 展示決策層 (Visualization)
    # =========================================================================
    draw_layer_bg(ax, 0.02, 0.01, 0.96, 0.16, 'STAGE 4: Visualization & Decision Layer', '#fffeee')
    
    draw_block(ax, 0.28, 0.02, 0.44, 0.12, 
               '4. Interactive Digital Twin Dashboard', 
               '• Accumulate global point cloud data of strawberry maturity\n• Generate maturity decision heatmaps (KDE)\n• Intuitively guide farmers for precise harvesting strategies', '#ffffcc', edgecolor='darkgoldenrod', lw=2)

    # 從 Stage 3C 輸出最終沉澱數據到展示層
    draw_arrow(ax, 0.81, 0.22, 0.50, 0.14, 'Deduplicated Point Cloud Data')

    # 儲存並輸出圖片
    output_path = './strawberry_system_pipeline_en.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight', pad_inches=0.4, facecolor='white')
    print(f'Success! System pipeline diagram saved to: {output_path}')

if __name__ == '__main__':
    main()