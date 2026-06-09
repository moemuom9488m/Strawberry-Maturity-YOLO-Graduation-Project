# -*- coding: utf-8 -*-
import matplotlib.pyplot as plt
import os
from PIL import Image

def generate_parameter_table():
    # ── 1. 參數設定區：方便未來隨時調整參數數值 ──
    # (1) 左側表格數據 (已整合 Phase 1 架構比對 與 Phase 2 解析度/微調參數，並新增 Epochs, Freeze, lr0 欄位)
    columns = ["Model\nVariant", "Config\n(.yaml)", "Weights\nSource", "Batch\nSize", "Image\nSize", "Epochs", "Freeze", "lr0"]
    
    rows = [
        ["YOLO11s Baseline (Ph1)", "Default", "yolo11s.pt", "32", "640", "300", "0", "0.01"],
        ["YOLO11m Baseline (Ph1)", "Default", "yolo11m.pt", "16", "640", "300", "0", "0.01"],
        ["YOLO11s P2-CBAM (Ph1)", "yolo11-strawberry-\np2-cbam-s.yaml", "yolo11s.pt", "16", "640", "300", "0", "0.01"],
        ["YOLO11m P2-CBAM (Ph1)", "yolo11-strawberry-\np2-cbam-m.yaml", "yolo11m.pt", "12", "640", "300", "0", "0.01"],
        ["YOLO11s Baseline (Ph2)", "Default", "Ph1 Best", "96", "640", "150", "10", "0.005"],
        ["YOLO11s Baseline (Ph2)", "Default", "Ph1 Best", "72", "800", "150", "10", "0.005"],
        ["YOLO11s Baseline (Ph2)", "Default", "Ph1 Best", "32", "1024", "150", "10", "0.005"]
    ]
    
    # (2) 右側共通核心超參數 (可在此隨意增減)
    shared_params = [
        "Shared Hyperparameters:",
        "  Optimizer = AdamW",
        "  Patience = 100",
        "  Seed = 42",
        "  Mixup = 0.1",
        "  Copy-Paste = 0.1",
        "  Random Erasing = 0.4",
        "  Mosaic = 1.0",
        "  Degrees = 15.0",
        "  Translate = 0.1",
        "  Scale = 0.5",
        "  Fliplr = 0.5",
        "  Flipud = 0.1",
        "  HSV = [0.015, 0.7, 0.4]",
        "  Weight Decay (Default L2) = 0.0005",
        "  Box Loss (CIoU) = 7.5",
        "  Class Loss (BCE) = 0.5",
        "  DFL Loss (Default) = 1.5",
        "  cos_lr (Default) = False"
    ]

    # ── 2. 畫布初始化 (16:9 學術輸出規格 1920x1080，使用 add_axes 確保邊界不裁切) ──
    fig = plt.figure(figsize=(16, 9), dpi=120)  # 16 * 120 = 1920, 9 * 120 = 1080 像素
    fig.patch.set_facecolor('white')
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_facecolor('white')
    ax.axis('off')
    
    # 強制設定坐標系範圍為 [0, 1]，使相對坐標定位完全精準
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    
    # 字型設定：強制使用 Times New Roman
    plt.rcParams['font.family'] = 'serif'
    plt.rcParams['font.serif'] = ['Times New Roman'] + plt.rcParams['font.serif']
    
    # ── 【字體大小調整區】 ──
    # 在此調整各部分文字的 size 數值即可改變字體大小
    title_font = {'family': 'serif', 'weight': 'bold', 'size': 26, 'name': 'Times New Roman'}      # 大標題字體大小
    header_font = {'family': 'serif', 'weight': 'bold', 'size': 16, 'name': 'Times New Roman'}     # 表格表頭字體大小
    cell_font = {'family': 'serif', 'size': 15, 'name': 'Times New Roman'}                         # 表格內文細項字體大小
    list_title_font = {'family': 'serif', 'weight': 'bold', 'size': 17, 'name': 'Times New Roman'}# 右側參數清單標題大小
    list_font = {'family': 'serif', 'size': 15, 'name': 'Times New Roman'}                       # 右側參數清單細項大小

    # ── 3. 繪製標題 ──
    # 調整第一個參數 (0.5) 改變標題左右位移 (0 為最左，1 為最右)；調整第二個參數 (0.92) 改變上下位移
    plt.text(0.5, 0.92, "YOLO11s/m Baseline vs. P2-CBAM Parameter Comparison (Phase 1 & 2)", 
             ha='center', va='center', fontdict=title_font)

    # ── 4. 繪製左半部：學術三線表 ──
    # ── 【左側表格寬度與欄位間距調整】 ──
    # col_widths: 調整表格內各欄的寬度 (總和建議控制在 table_left 與 table_right 的範圍內)
    col_widths = [0.15, 0.13, 0.09, 0.055, 0.055, 0.055, 0.055, 0.04]
    # col_start_x[0]: 調整整個表格的「起點 x 座標」(調整第一個數值即可將整個表格向左/向右位移)
    col_start_x = [0.03]
    for w in col_widths[:-1]:
        col_start_x.append(col_start_x[-1] + w)
        
    y_header = 0.82
    y_row_height = 0.08
    y_rows = [y_header - (i + 1) * y_row_height for i in range(len(rows))]
    
    # 4.1 繪製表頭
    for idx, col_name in enumerate(columns):
        ax.text(col_start_x[idx] + col_widths[idx]/2, y_header, col_name, 
                ha='center', va='center', fontdict=header_font)
        
    # 4.2 繪製表格內容
    for row_idx, row_data in enumerate(rows):
        y_pos = y_rows[row_idx]
        for col_idx, cell_value in enumerate(row_data):
            ax.text(col_start_x[col_idx] + col_widths[col_idx]/2, y_pos, cell_value, 
                    ha='center', va='center', fontdict=cell_font)
            
    # 4.3 繪製標準學術三線表線條 (Top, Mid, Bottom Rules)
    # ── 【三線表左右範圍與位移調整】 ──
    # table_left:  調整三線表左側起點 (需與表格 x 起點 col_start_x 對齊)
    # table_right: 調整三線表右側終點
    table_left = 0.03
    table_right = 0.67
    
    # 頂線 (Thick top rule)
    ax.plot([table_left, table_right], [y_header + 0.04, y_header + 0.04], color='black', linewidth=2.5)
    # 中線 (Thin mid rule below header)
    ax.plot([table_left, table_right], [y_header - 0.04, y_header - 0.04], color='black', linewidth=1.2)
    # 底線 (Thick bottom rule)
    ax.plot([table_left, table_right], [y_rows[-1] - 0.04, y_rows[-1] - 0.04], color='black', linewidth=2.5)

    # ── 5. 繪製右半部：垂直共通參數列表 ──
    # ── 【右側清單位置與間距調整】 ──
    # start_x_list: 調整右側列表的「左右位置」(x 座標，調小向左移，調大向右移)
    # start_y_list: 調整右側列表的「上下位置」(y 座標)
    # y_list_gap:   調整清單中每一行之間的「行間距」
    start_x_list = 0.70
    start_y_list = 0.85
    y_list_gap = 0.035
    
    # 標題
    ax.text(start_x_list, start_y_list, shared_params[0], 
            ha='left', va='center', fontdict=list_title_font)
            
    # 列表內容 (垂直條列，一行一個參數，Times New Roman)
    for idx, item in enumerate(shared_params[1:]):
        y_pos = start_y_list - (idx + 1) * y_list_gap
        ax.text(start_x_list, y_pos, item, 
                ha='left', va='center', fontdict=list_font)

    # ── 6. 儲存與輸出影像 ──
    output_path = "yolo_parameter_academic_comparison.png"
    plt.savefig(output_path, dpi=120)  # 先以 120 DPI 輸出得到精準的 1920x1080 像素
    plt.close()
    
    # 使用 PIL 將解析度中繼資料 (DPI) 強制重寫為 600 DPI，確保高畫質輸出
    im = Image.open(output_path)
    im.save(output_path, dpi=(600, 600))
    print(f"🎉 [SUCCESS] 學術對照表格圖已成功儲存至: {output_path}")

if __name__ == "__main__":
    generate_parameter_table()
