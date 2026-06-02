# -*- coding: utf-8 -*-
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

def setup_theme_and_font():
    sns.set_theme(style="whitegrid", context="talk")
    plt.rcParams['font.sans-serif'] = [
        'Microsoft JhengHei',
        'DFKai-SB',
        'PingFang TC',
        'sans-serif'
    ]
    plt.rcParams['axes.unicode_minus'] = False
    plt.rcParams['figure.dpi'] = 150

def smooth_curve(points, factor=0.6):
    points_filled = pd.Series(points).replace([np.inf, -np.inf], np.nan).ffill().bfill()
    smoothed = []
    for point in points_filled:
        if np.isnan(point):
            smoothed.append(point)
            continue
        if not smoothed or np.isnan(smoothed[-1]):
            smoothed.append(point)
        else:
            previous = smoothed[-1]
            smoothed.append(previous * factor + point * (1 - factor))
    return smoothed

def main():
    setup_theme_and_font()
    
    experiments = {
        "640px": "runs/detect/exp2a_1a_img640/results.csv",
        "800px": "runs/detect/exp2b_1a_img800/results.csv",
        "1024px": "runs/detect/exp2c_1a_img1024/results.csv"
    }
    
    palette = ['#4361EE', '#FF9F1C', '#E63946']
    
    fig, axes = plt.subplots(1, 2, figsize=(18, 7))
    
    # ==========================================
    # 💡 可以在這裡調整曲線平滑度 (預設 0.6)
    # 數值介於 0.0 ~ 1.0 之間，越高越平滑
    # ==========================================
    smooth_factor = 0.6  
    
    for idx, (label, csv_path) in enumerate(experiments.items()):
        if not os.path.exists(csv_path):
            print(f"[WARN] 找不到檔案: {csv_path}")
            continue
            
        df = pd.read_csv(csv_path)
        df.columns = [c.strip() for c in df.columns]
        
        epochs = df['epoch']
        color = palette[idx % len(palette)]
        
        box_loss_col = 'val/box_loss' if 'val/box_loss' in df.columns else 'train/box_loss'
        cls_loss_col = 'val/cls_loss' if 'val/cls_loss' in df.columns else 'train/cls_loss'
        
        if box_loss_col in df.columns:
            box_loss_smooth = smooth_curve(df[box_loss_col], smooth_factor)
            axes[0].plot(epochs, box_loss_smooth, label=label, color=color, linewidth=2.5)
            
        if cls_loss_col in df.columns:
            cls_loss_smooth = smooth_curve(df[cls_loss_col], smooth_factor)
            axes[1].plot(epochs, cls_loss_smooth, label=label, color=color, linewidth=2.5)
            
    axes[0].set_title("Bounding Box Loss 邊界框損失 (Val)", fontsize=16, fontweight='bold', pad=15)
    axes[0].set_xlabel("Epochs", fontsize=14, labelpad=10)
    axes[0].set_ylabel("Loss", fontsize=14, labelpad=10)
    axes[0].legend(loc="upper right", frameon=True, facecolor='white', edgecolor='none', fontsize=12, framealpha=0.9)
    axes[0].set_xlim(0, 150)
    
    axes[1].set_title("Classification Loss 分類損失 (Val)", fontsize=16, fontweight='bold', pad=15)
    axes[1].set_xlabel("Epochs", fontsize=14, labelpad=10)
    axes[1].set_ylabel("Loss", fontsize=14, labelpad=10)
    axes[1].legend(loc="upper right", frameon=True, facecolor='white', edgecolor='none', fontsize=12, framealpha=0.9)
    axes[1].set_xlim(0, 150)
    
    output_dir = "evaluation_results"
    os.makedirs(output_dir, exist_ok=True)
    img_path = os.path.join(output_dir, "resolution_loss_comparison.png")
    
    plt.tight_layout()
    plt.savefig(img_path, dpi=200, bbox_inches='tight')
    plt.close()
    
    print(f"🎉 [SUCCESS] 解析度損失曲線對比圖已儲存至: {img_path}")

if __name__ == "__main__":
    main()
