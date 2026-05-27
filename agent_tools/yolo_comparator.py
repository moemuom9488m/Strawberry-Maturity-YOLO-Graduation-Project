#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
草莓監測機器人畢業專題 - YOLO 多維度實驗對比分析工具 (YOLO Experiment Comparator)
==============================================================================
功能：
1. 自動掃描指定目錄 (預設為 runs/detect/) 下的所有訓練實驗結果 (results.csv)。
2. 清理與解析各項核心訓練指標 (Precision, Recall, mAP50, mAP50-95, Loss)。
3. 提取每個實驗的「最佳模型狀態 (Best mAP50)」與「最終模型狀態 (Last Epoch)」。
4. 匯出結構化的 CSV 表格至 evaluation_results/yolo_experiments_comparison.csv。
5. 自動產生 Markdown 格式的精美對比報表 evaluation_results/yolo_experiments_comparison.md。
6. 使用 Matplotlib & Seaborn 繪製高品質、具平滑曲線 (EMA) 且無亂碼的繁體中文對比折線圖：
   - yolo_metrics_comparison.png (mAP50 與 mAP50-95 學習曲線)
   - yolo_loss_comparison.png (Box & Class 損失收斂曲線)
==============================================================================
說明：已移除所有 Emoji 字元，避免在 Windows (cp950) 終端機環境下產生 UnicodeEncodeError。
"""

import os
import argparse
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# ------------------------------------------------------------------------------
# 1. 視覺美化與繁體中文字型自癒配置
# ------------------------------------------------------------------------------
def setup_theme_and_font():
    """設定 Matplotlib 圖表美化主題與繁體中文字型，防止豆腐塊亂碼"""
    # 質感配色調色盤
    sns.set_theme(style="whitegrid", context="talk")
    
    # 設定繁體中文字型順序 (優先採用 Windows 與 Mac 常用繁中字型)
    plt.rcParams['font.sans-serif'] = [
        'Microsoft JhengHei',  # 微軟正黑體
        'DFKai-SB',            # 標楷體
        'PingFang TC',         # 蘋果繁中
        'Heiti TC',            # 蘋果黑體
        'SimHei',              # 簡體黑體 (備用)
        'sans-serif'
    ]
    plt.rcParams['axes.unicode_minus'] = False  # 正常顯示負號
    
    # 額外美化配置
    plt.rcParams['figure.titlesize'] = 22
    plt.rcParams['axes.titlesize'] = 16
    plt.rcParams['axes.labelsize'] = 14
    plt.rcParams['xtick.labelsize'] = 12
    plt.rcParams['ytick.labelsize'] = 12
    plt.rcParams['legend.fontsize'] = 12
    plt.rcParams['figure.dpi'] = 150

# ------------------------------------------------------------------------------
# 2. 指數移動平均 (EMA) 平滑化演算法
# ------------------------------------------------------------------------------
def smooth_curve(points, factor=0.6):
    """
    對折線圖進行指數移動平均 (EMA) 平滑處理，以利清晰觀察指標變化趨勢。
    factor: 平滑係數，介於 0 到 1 之間。數值越高越平滑。
    """
    smoothed = []
    for point in points:
        if np.isnan(point):
            smoothed.append(point)
            continue
        if not smoothed or np.isnan(smoothed[-1]):
            smoothed.append(point)
        else:
            previous = smoothed[-1]
            smoothed.append(previous * factor + point * (1 - factor))
    return smoothed

# ------------------------------------------------------------------------------
# 3. 實驗資料掃描與解析
# ------------------------------------------------------------------------------
def scan_yolo_experiments(runs_dir, selected_only=True):
    """
    掃描 runs_dir 底下特定簡報決策模型的 results.csv。
    """
    experiments = {}
    if not os.path.exists(runs_dir):
        print(f"[WARN] 找不到指定的 YOLO 運行目錄: {runs_dir}")
        return experiments
        
    # 簡報與抉擇故事線核心指定的 4 組對照模型
    target_models = [
        "exp1a_yolo11s_baseline",
        "exp1b_yolo11m_baseline",
        "exp2b_1a_img800",
        "exp2b_1d_img800"
    ]
    
    if selected_only:
        print(f"[SCAN] 開始掃描簡報指定之 YOLO 決策模型結果: {runs_dir}")
    else:
        print(f"[SCAN] 開始掃描 YOLO 實驗結果目錄: {runs_dir}")
    
    for root, dirs, files in os.walk(runs_dir):
        # 排除 val 等驗證專用的目錄，聚焦於含有 results.csv 的訓練目錄
        if 'results.csv' in files:
            exp_name = os.path.basename(root)
            # 略過單純的 val 目錄
            if exp_name.startswith('val') and not 'exp' in exp_name:
                continue
                
            # 若啟用僅篩選簡報模型且該實驗不在名單中，則略過
            if selected_only and exp_name not in target_models:
                continue
                
            csv_path = os.path.join(root, 'results.csv')
            try:
                # 讀取 CSV
                df = pd.read_csv(csv_path)
                # 清除列名首尾空格 (YOLOv8/v11 產出的標頭常帶空格)
                df.columns = [c.strip() for c in df.columns]
                
                # 確保必要欄位存在
                required_cols = ['epoch', 'metrics/mAP50(B)', 'metrics/mAP50-95(B)']
                if all(col in df.columns for col in required_cols):
                    experiments[exp_name] = {
                        'path': root,
                        'data': df
                    }
                    print(f"   [OK] 成功載入實驗: {exp_name} ({len(df)} epochs)")
                else:
                    missing = [col for col in required_cols if col not in df.columns]
                    print(f"   [SKIP] 略過實驗 {exp_name}: 缺少關鍵指標欄位 {missing}")
            except Exception as e:
                print(f"   [ERROR] 讀取 {csv_path} 時發生錯誤: {e}")
                
    print(f"[LOADED] 共成功載入 {len(experiments)} 組 YOLO 訓練實驗結果。\n")
    return experiments

# ------------------------------------------------------------------------------
# 4. 指標彙整與提取
# ------------------------------------------------------------------------------
def compile_comparison_table(experiments):
    """
    分析各實驗數據，彙整最佳 (Best mAP50) 與最末 (Last Epoch) 指標。
    """
    summary_data = []
    
    for exp_name, info in experiments.items():
        df = info['data']
        
        # 取得最後一個 Epoch 的行數據
        last_row = df.iloc[-1]
        
        # 找出 mAP50(B) 最大值所在的行 (Best Epoch)
        # 處理潛在的 NaN 數值
        valid_map50 = df['metrics/mAP50(B)'].dropna()
        if valid_map50.empty:
            continue
        best_idx = valid_map50.idxmax()
        best_row = df.loc[best_idx]
        
        # 提取時間總和 (若有 time 欄位)
        total_time_sec = df['time'].sum() if 'time' in df.columns else np.nan
        total_time_str = f"{total_time_sec/3600:.2f} hr" if not np.isnan(total_time_sec) else "N/A"
        
        summary_data.append({
            '實驗名稱': exp_name,
            '訓練Epochs': len(df),
            '總訓練時間': total_time_str,
            # Best 狀態指標
            '最佳Epoch': int(best_row['epoch']),
            'Best_mAP50': best_row['metrics/mAP50(B)'],
            'Best_mAP50-95': best_row['metrics/mAP50-95(B)'],
            'Best_Precision': best_row.get('metrics/precision(B)', np.nan),
            'Best_Recall': best_row.get('metrics/recall(B)', np.nan),
            # Last 狀態指標
            '最末Epoch': int(last_row['epoch']),
            'Last_mAP50': last_row['metrics/mAP50(B)'],
            'Last_mAP50-95': last_row['metrics/mAP50-95(B)'],
            'Last_Precision': last_row.get('metrics/precision(B)', np.nan),
            'Last_Recall': last_row.get('metrics/recall(B)', np.nan)
        })
        
    summary_df = pd.DataFrame(summary_data)
    # 依 Best_mAP50 從高到低排序
    if not summary_df.empty:
        summary_df = summary_df.sort_values(by='Best_mAP50', ascending=False).reset_index(drop=True)
    return summary_df

# ------------------------------------------------------------------------------
# 5. 繪製高品質比較圖表
# ------------------------------------------------------------------------------
def plot_comparison_graphs(experiments, output_dir, smooth_factor=0.6):
    """
    繪製學習曲線折線圖與 Loss 變化曲線圖。
    """
    if not experiments:
        return
        
    os.makedirs(output_dir, exist_ok=True)
    
    # 預先定義一組優雅且具對比的高質感 HSL 和弦配色
    palette = [
        '#4361EE',  # 皇家藍 (皇家科技風)
        '#F72585',  # 霓虹粉 (高亮突顯)
        '#4CC9F0',  # 天空藍 (亮色對比)
        '#7209B7',  # 深紫 (典雅風範)
        '#FF9F1C',  # 琥珀橘 (暖色調)
        '#2EC4B6',  # 薄荷綠 (自然風)
        '#E63946',  # 胭脂紅
        '#1D3557'   # 深海藍
    ]
    
    # --------------------------------------------------------------------------
    # 圖表 1：mAP50 與 mAP50-95 學習曲線對比
    # --------------------------------------------------------------------------
    fig, axes = plt.subplots(1, 2, figsize=(18, 7))
    
    for idx, (exp_name, info) in enumerate(experiments.items()):
        df = info['data']
        color = palette[idx % len(palette)]
        
        epochs = df['epoch']
        map50 = df['metrics/mAP50(B)']
        map50_95 = df['metrics/mAP50-95(B)']
        
        # 平滑處理
        map50_smooth = smooth_curve(map50, smooth_factor)
        map50_95_smooth = smooth_curve(map50_95, smooth_factor)
        
        # 子圖 1: mAP50
        axes[0].plot(epochs, map50_smooth, label=exp_name, color=color, linewidth=2.0)
        # 標出最大值位置
        best_idx = map50.idxmax()
        axes[0].scatter(epochs[best_idx], map50[best_idx], color=color, s=80, edgecolors='black', zorder=5)
        
        # 子圖 2: mAP50-95
        axes[1].plot(epochs, map50_95_smooth, label=exp_name, color=color, linewidth=2.0)
        best_idx_95 = map50_95.idxmax()
        axes[1].scatter(epochs[best_idx_95], map50_95[best_idx_95], color=color, s=80, edgecolors='black', zorder=5)
        
    axes[0].set_title("mAP@0.5 Learning Curves (Smooth Factor: {})".format(smooth_factor))
    axes[0].set_xlabel("Epochs")
    axes[0].set_ylabel("mAP50")
    axes[0].set_ylim(0, 1.02)
    # 使用 ncol=2 與較小字型，避免遮擋數據曲線，背景設置半透明
    axes[0].legend(loc="lower right", frameon=True, facecolor='white', edgecolor='none', ncol=2, fontsize=8.5, framealpha=0.8)
    
    axes[1].set_title("mAP@0.5:0.95 Learning Curves (Smooth Factor: {})".format(smooth_factor))
    axes[1].set_xlabel("Epochs")
    axes[1].set_ylabel("mAP50-95")
    axes[1].set_ylim(0, 1.02)
    axes[1].legend(loc="lower right", frameon=True, facecolor='white', edgecolor='none', ncol=2, fontsize=8.5, framealpha=0.8)
    
    plt.tight_layout()
    metrics_img_path = os.path.join(output_dir, 'yolo_metrics_comparison.png')
    plt.savefig(metrics_img_path, dpi=200, bbox_inches='tight')
    plt.close()
    print(f"[PLOT] 學習指標對比圖已儲存至: {metrics_img_path}")
    
    # --------------------------------------------------------------------------
    # 圖表 2：驗證集 Box Loss 與 Class Loss 收斂曲線對比
    # --------------------------------------------------------------------------
    fig, axes = plt.subplots(1, 2, figsize=(18, 7))
    
    for idx, (exp_name, info) in enumerate(experiments.items()):
        df = info['data']
        color = palette[idx % len(palette)]
        
        epochs = df['epoch']
        
        # 尋找 val loss 欄位 (YOLOv8/v11 欄位為 val/box_loss, val/cls_loss)
        box_loss_col = 'val/box_loss' if 'val/box_loss' in df.columns else 'train/box_loss'
        cls_loss_col = 'val/cls_loss' if 'val/cls_loss' in df.columns else 'train/cls_loss'
        
        if box_loss_col in df.columns:
            box_loss_smooth = smooth_curve(df[box_loss_col].dropna(), smooth_factor)
            axes[0].plot(epochs[:len(box_loss_smooth)], box_loss_smooth, label=exp_name, color=color, linewidth=2.0)
            
        if cls_loss_col in df.columns:
            cls_loss_smooth = smooth_curve(df[cls_loss_col].dropna(), smooth_factor)
            axes[1].plot(epochs[:len(cls_loss_smooth)], cls_loss_smooth, label=exp_name, color=color, linewidth=2.0)
            
    axes[0].set_title("Bounding Box Loss Convergence ({})".format("Val" if "val" in box_loss_col else "Train"))
    axes[0].set_xlabel("Epochs")
    axes[0].set_ylabel("Loss")
    axes[0].legend(loc="upper right", frameon=True, facecolor='white', edgecolor='none', ncol=2, fontsize=8.5, framealpha=0.8)
    
    axes[1].set_title("Classification Loss Convergence ({})".format("Val" if "val" in cls_loss_col else "Train"))
    axes[1].set_xlabel("Epochs")
    axes[1].set_ylabel("Loss")
    axes[1].legend(loc="upper right", frameon=True, facecolor='white', edgecolor='none', ncol=2, fontsize=8.5, framealpha=0.8)
    
    plt.tight_layout()
    loss_img_path = os.path.join(output_dir, 'yolo_loss_comparison.png')
    plt.savefig(loss_img_path, dpi=200, bbox_inches='tight')
    plt.close()
    print(f"[PLOT] 損失收斂圖已儲存至: {loss_img_path}")

# ------------------------------------------------------------------------------
# 6. 自動輸出 Markdown 格式的精美報告
# ------------------------------------------------------------------------------
def export_markdown_report(summary_df, output_dir):
    """
    根據比較 DataFrame，自動產出排版精美的 Markdown 報告。
    """
    os.makedirs(output_dir, exist_ok=True)
    report_path = os.path.join(output_dir, 'yolo_experiments_comparison.md')
    
    # 構造 Markdown 格式
    md_content = []
    md_content.append("# YOLOv11 草莓偵測實驗多維度對比報告\n")
    md_content.append(f"> **生成時間**: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    md_content.append("## 實驗結果總覽表格 (按 Best mAP@0.5 降序排列)\n")
    
    # 將 DataFrame 轉為 Markdown (手動格式化，避免對 tabulate 的依賴)
    styled_df = summary_df.copy()
    float_cols = ['Best_mAP50', 'Best_mAP50-95', 'Best_Precision', 'Best_Recall', 
                  'Last_mAP50', 'Last_mAP50-95', 'Last_Precision', 'Last_Recall']
    for col in float_cols:
        if col in styled_df.columns:
            styled_df[col] = styled_df[col].map(lambda x: f"{x:.4f}" if not pd.isna(x) else "N/A")
            
    # 手動生成 Markdown 表格字串
    headers = list(styled_df.columns)
    table_lines = []
    table_lines.append("| " + " | ".join(str(h) for h in headers) + " |")
    table_lines.append("| " + " | ".join(["---"] * len(headers)) + " |")
    for _, row in styled_df.iterrows():
        row_strs = [str(x) for x in row]
        table_lines.append("| " + " | ".join(row_strs) + " |")
    markdown_table = "\n".join(table_lines)
    
    md_content.append(markdown_table)
    md_content.append("\n\n## 視覺化分析圖表\n")
    md_content.append("### 1. 學習指標對比 (mAP@0.5 & mAP@0.5:0.95)\n")
    md_content.append("![學習指標對比](yolo_metrics_comparison.png)\n\n")
    md_content.append("### 2. 損失收斂曲線對比 (Box & Class Loss)\n")
    md_content.append("![損失收斂對比](yolo_loss_comparison.png)\n\n")
    
    md_content.append("## 關鍵實驗結論與建議\n")
    
    # 自動做一些初步分析
    if len(summary_df) >= 2:
        best_exp = summary_df.iloc[0]
        second_exp = summary_df.iloc[1]
        diff = (best_exp['Best_mAP50'] - second_exp['Best_mAP50']) * 100
        
        md_content.append(f"- **表現最佳模型**: 本次對比中，**{best_exp['實驗名稱']}** 表現最優，其最佳 mAP@0.5 達到了 **{best_exp['Best_mAP50']:.4f}**，領先第二名 **{second_exp['實驗名稱']}** 約 **{diff:.2f}%**。\n")
        md_content.append(f"- **早停與過擬合評估**: \n")
        for _, row in summary_df.iterrows():
            gap = (row['Best_mAP50'] - row['Last_mAP50']) * 100
            if gap > 1.5:
                md_content.append(f"  - 警告：實驗 {row['實驗名稱']} 的最佳 Epoch 為 {row['最佳Epoch']}，但最終 Epoch 衰退至 {row['Last_mAP50']:.4f} (衰退 {gap:.2f}%)，顯示在訓練後期有輕微的過擬合現象。建議在實車部署時使用 `best.pt` 而非 `last.pt`。\n")
            else:
                md_content.append(f"  - 正常：實驗 {row['實驗名稱']} 收斂穩定，最佳與最末指標無顯著衰退。\n")
    else:
        md_content.append("- 當前對比的實驗數量較少，建議加入更多對比維度以獲得完整結論。\n")
        
    # 寫入檔案
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(md_content))
        
    print(f"[EXPORT] Markdown 對比報告已儲存至: {report_path}")

# ------------------------------------------------------------------------------
# 7. 主程式邏輯
# ------------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="YOLO 實驗指標對比與繪圖工具")
    parser.add_argument('--runs-dir', type=str, default='runs/detect', help='YOLO 訓練輸出根目錄')
    parser.add_argument('--output-dir', type=str, default='evaluation_results', help='比較結果與圖表儲存目錄')
    parser.add_argument('--smooth', type=float, default=0.6, help='曲線平滑化 EMA 係數 (0.0~1.0)')
    parser.add_argument('--all', action='store_true', help='比較所有實驗而非僅限簡報指定的4組模型')
    args = parser.parse_args()
    
    # 1. 設置字型主題
    setup_theme_and_font()
    
    # 2. 掃描載入實驗數據
    selected_only = not args.all
    experiments = scan_yolo_experiments(args.runs_dir, selected_only=selected_only)
    
    if not experiments:
        print("[ERROR] 未在該目錄下找到任何有效的 results.csv，程序結束。")
        return
        
    # 3. 編譯數據對比總表
    summary_df = compile_comparison_table(experiments)
    
    if summary_df.empty:
        print("[ERROR] 編譯對比表格時無有效數據，程序結束。")
        return
        
    # 4. 輸出 CSV
    os.makedirs(args.output_dir, exist_ok=True)
    csv_out_path = os.path.join(args.output_dir, 'yolo_experiments_comparison.csv')
    summary_df.to_csv(csv_out_path, index=False, encoding='utf-8-sig')
    print(f"[SAVE] 彙整 CSV 資料表已儲存至: {csv_out_path}")
    
    # 5. 繪製圖表
    plot_comparison_graphs(experiments, args.output_dir, smooth_factor=args.smooth)
    
    # 6. 匯出 Markdown 報告
    export_markdown_report(summary_df, args.output_dir)
    
    # 7. 終端機漂亮印出
    print("\n" + "="*80)
    print("YOLO 實驗彙整對比結果 (按 Best mAP@0.5 排序)")
    print("="*80)
    # 設定 pandas 印出寬度
    pd.set_option('display.max_columns', 20)
    pd.set_option('display.width', 1000)
    # 只印出核心精選欄位
    display_cols = ['實驗名稱', '訓練Epochs', '最佳Epoch', 'Best_mAP50', 'Best_mAP50-95', 'Best_Precision', 'Best_Recall']
    print(summary_df[display_cols].to_string(index=False))
    print("="*80 + "\n")
    
    print("實驗對比分析完成！所有產出已整理至: " + os.path.abspath(args.output_dir))

if __name__ == '__main__':
    main()
