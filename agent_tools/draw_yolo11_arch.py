# -*- coding: utf-8 -*-
import matplotlib.pyplot as plt
import matplotlib.patches as patches

def draw_box(ax, x, y, width, height, text, facecolor='#eeeeee', edgecolor='black', lw=1.5):
    """
    在指定的地圖坐標上繪製一個圓角矩形方框，並在中央填入文字。
    
    參數:
        ax: Matplotlib 的畫布坐標軸物件
        x, y: 方框左下角的坐標位置
        width: 方框的寬度
        height: 方框的高度
        text: 要顯示的文字內容
        facecolor: 方框內部的填滿顏色（預設為淺灰色）
        edgecolor: 方框邊線的顏色（預設為黑色）
        lw: 邊線的粗細（預設為 1.5）
    """
    # 建立圓角矩形物件（FancyBboxPatch）
    box = patches.FancyBboxPatch((x, y), width, height,
                                 boxstyle="round,pad=0.05", # round 代表圓角，pad 決定圓角的弧度與外擴大小
                                 facecolor=facecolor,
                                 edgecolor=edgecolor,
                                 linewidth=lw)
    ax.add_patch(box) # 將方框繪製到畫布上
    
    # 這裡可以調整「方框內文字」的大小 (fontsize=13)
    # 透過 x + width/2 與 y + height/2 計算出幾何中心，使文字完美置中
    ax.text(x + width/2, y + height/2, text, 
            ha='center', va='center',      # 水平與垂直皆置中對齊
            fontsize=13, weight='bold',    # 字型大小設為 13，並加粗
            color='black')                  # 文字顏色固定為黑色

def draw_arrow(ax, x1, y1, x2, y2):
    """
    繪製一條從 (x1, y1) 指向 (x2, y2) 的向下箭頭，用來表示模型的資料流向。
    """
    ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle="->", lw=2, color='gray')) # 箭頭樣式為標準單向箭頭，顏色為灰色

def main():
    # 建立畫布，設定尺寸為 14 x 8 英吋
    fig, ax = plt.subplots(figsize=(14, 8))
    ax.axis('off') # 隱藏背景的 X、Y 軸刻度與外框線，保持圖表乾淨

    # 設定左右兩側的頂部標題文字 - 這裡可以調整「標題文字」的大小 (fontsize=18)
    # 左側標題：原生 YOLO11 架構 (Baseline)
    ax.text(0.25, 1.05, 'YOLO11 Base Architecture\n(Baseline)', 
            ha='center', va='center', fontsize=18, weight='bold')
    
    # 右側標題：本研究提出的改良架構 (Paper)，使用深紅色突顯
    ax.text(0.75, 1.05, 'Proposed Framework Architecture\n(Paper)', 
            ha='center', va='center', fontsize=18, weight='bold', color='darkred')

    # =========================================================================
    # 繪製左半邊：YOLO11 原始基礎架構 (Base Architecture)
    # =========================================================================
    # 依序繪製：輸入層 -> 主幹網路 -> 頸部網路 -> 檢測頭
    draw_box(ax, 0.1, 0.80, 0.3, 0.1, 'Input Image', facecolor='#ffcccc')              # 淺紅色
    draw_box(ax, 0.1, 0.55, 0.3, 0.1, 'Backbone\n(Feature Extractor)', facecolor='#ccffcc') # 淺綠色
    
    # 【調整】將左邊 Neck (紫色方框) 寬度從 0.3 改為 0.34，X 坐標從 0.1 移到 0.08（中心點依然保持 0.25）
    draw_box(ax, 0.08, 0.30, 0.34, 0.1, 'Neck\n(Feature Aggregation)', facecolor='#ccccff')
    
    draw_box(ax, 0.1, 0.05, 0.3, 0.1, 'Head\n(Detection Output)', facecolor='#ffffcc')     # 淺黃色

    # 繪製左半邊模組之間的連接箭頭（維持在 X=0.25 垂直向下，完美置中）
    draw_arrow(ax, 0.25, 0.80, 0.25, 0.65) # Input -> Backbone
    draw_arrow(ax, 0.25, 0.55, 0.25, 0.40) # Backbone -> Neck
    draw_arrow(ax, 0.25, 0.30, 0.25, 0.15) # Neck -> Head

    # =========================================================================
    # 繪製右半邊：本研究提出的改良架構 (Proposed Architecture)
    # =========================================================================
    # 1. 輸入層 (維持與原架構相同)
    draw_box(ax, 0.6, 0.80, 0.3, 0.1, 'Input Image', facecolor='#ffcccc')
    
    # 2. 改良後的 Backbone：加入 C3K2-FB 並標註動態雜訊抑制（加粗紅框 lw=2.5，代表創新點）
    draw_box(ax, 0.6, 0.55, 0.3, 0.1, 
             'Backbone\n( C3K2-FB + SPPF + C2PSA)\n[Dynamic Noise Suppression]', 
             facecolor='#ccffcc', edgecolor='red', lw=2.5)
    
    # 3. 【調整】改良後的 Neck：將右邊 Neck 寬度從 0.3 改為 0.34，X 坐標從 0.6 移到 0.58（中心點依然保持 0.75）
    # 這樣文字 ( MS_FPN: MS_Fusion + Frequency Enhancer) 左右就會有充足的留白空間！
    draw_box(ax, 0.58, 0.30, 0.34, 0.1, 
             'Neck\n( MS_FPN: MS_Fusion + Frequency Enhancer)', 
             facecolor='#ccccff', edgecolor='red', lw=2.5)
    
    # 4. 改良後的 Head：擴充為 4 個檢測頭，並整合小目標 RFCBAM 注意力機制（加粗紅框 lw=2.5）
    draw_box(ax, 0.6, 0.05, 0.3, 0.1, 
             'Head\n(4 Heads: +  Small-Detect w/ RFCBAM)', 
             facecolor='#ffffcc', edgecolor='red', lw=2.5)

    # 繪製右半邊模組之間的連接箭頭（維持在 X=0.75 垂直向下，完美置中）
    draw_arrow(ax, 0.75, 0.80, 0.75, 0.65) # Input -> Backbone
    draw_arrow(ax, 0.75, 0.55, 0.75, 0.40) # Backbone -> Neck
    draw_arrow(ax, 0.75, 0.30, 0.75, 0.15) # Neck -> Head

    # =========================================================================
    # 繪製中央分界線與圖表輸出
    # =========================================================================
    # 在 X=0.5 處繪製一條貫穿 Y=0.0 到 Y=1.0 的灰色虛線 (--), 用來左右區隔對比
    ax.plot([0.5, 0.5], [0.0, 1.0], color='gray', linestyle='--', linewidth=2)

    # 設定圖片儲存路徑
    output_path = './yolo11_architecture_comparison.png'
    
    # 將繪製好的圖表儲存為高解析度圖片 (300 DPI)
    plt.savefig(output_path, dpi=300, bbox_inches='tight', pad_inches=0.5, facecolor='white')
    
    # 在終端機列印成功訊息
    print(f'Image successfully saved to {output_path}')

if __name__ == '__main__':
    main()