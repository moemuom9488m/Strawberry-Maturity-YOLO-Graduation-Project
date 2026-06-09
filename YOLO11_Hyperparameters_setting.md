# 🍓 草莓成熟度監測：YOLOv11 超參數設定手冊

![YOLO11s/m Baseline vs. P2-CBAM Parameter Comparison (Academic Table)](yolo_parameter_academic_comparison.png)

本手冊整理了 **畢業專題：草莓成熟度監測自走車** 中所進行的四個對照模型（官方標準 Baseline 與 P2-CBAM 論文改進架構，各包含 S 與 M 版本）的核心訓練參數對照。**本手冊參數與 [train_all.py](train_all.py) 以及二階段訓練腳本 [train_phase2_1a_lite.py](train_phase2_1a_lite.py) 完全對齊一致。**

---

## 📊 1. 訓練模型差異化參數對照表 (Phase 1 & Phase 2)

本表格整理了 Phase 1（架構與規模比對）與 Phase 2（不同解析度微調）各實驗模型之差異化自變數與超參數設定：

| 模型名稱 (Model Variant) | 架構定義 (Config .yaml) | 權重來源 (Weights Source) | 批次大小 (Batch Size) | 輸入尺寸 (Image Size) | 總回合數 (Epochs) | 凍結層數 (Freeze) | 初始學習率 (lr0) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **YOLO11s Baseline (Ph1)** | 官方預設 (Default) | `yolo11s.pt` | **`32`** | `640` | `300` | `0` | `0.01` |
| **YOLO11m Baseline (Ph1)** | 官方預設 (Default) | `yolo11m.pt` | **`16`** | `640` | `300` | `0` | `0.01` |
| **YOLO11s P2-CBAM (Ph1)** | `yolo11-strawberry-p2-cbam-s.yaml` | `yolo11s.pt` | **`16`** | `640` | `300` | `0` | `0.01` |
| **YOLO11m P2-CBAM (Ph1)** | `yolo11-strawberry-p2-cbam-m.yaml` | `yolo11m.pt` | **`12`** | `640` | `300` | `0` | `0.01` |
| **YOLO11s Baseline (Ph2)** | 官方預設 (Default) | `Ph1 Best` | **`96`** | `640` | `150` | `10` | `0.005` |
| **YOLO11s Baseline (Ph2)** | 官方預設 (Default) | `Ph1 Best` | **`72`** | `800` | `150` | `10` | `0.005` |
| **YOLO11s Baseline (Ph2)** | 官方預設 (Default) | `Ph1 Best` | **`32`** | `1024` | `150` | `10` | `0.005` |

---

## 📋 2. 共通使用的核心控制變數 (Shared Hyperparameters)

以下參數在所有模型訓練中皆完全相同，作為實驗的控制變數，實質影響模型收斂與權重學習。不同階段（Phase 1 與 Phase 2）有差異的超參數（如 Epochs, Freeze, lr0）已完整呈現在上方三線表中，此處不再贅述以保持版面簡潔：

* **核心優化器與實驗設定**
  * `Optimizer` (優化器) = **`AdamW`**（訓練腳本中顯式指定，採用 AdamW 優化算法）
  * `Weight Decay` (權重衰減 / L2 正則化) **`[預設值 Default L2]`** = **`0.0005`**（腳本未設定，套用 YOLO 系統預設 L2 正則化懲罰強度）
  * `Cosine LR Decay` (餘弦退火 cos_lr) **`[預設值 Default]`** = **`False`**（腳本未設定，套用 YOLO 預設之線性退火排程）
  * `Patience` (早停機制) = **`100`**（顯式指定驗證集指標連續 100 回合無提升時提早中止）
  * `Seed` (隨機數種子) = **`42`**（顯式指定以確保實驗的隨機性可重複）

* **損失函數與標籤分配機制 (Loss Functions & Label Assignment)**
  YOLOv11 延續了 Anchor-Free 架構，預設總損失函數由三個損失加權組合而成，並採用 **`TAL` (Task-Aligned Loss, 任務對齊損失)** 機制進行動態的正負樣本分配 (Label Assignment)：
  * **分類損失 (cls_loss)：BCE Loss**
    * 預設函數：二元交叉熵損失（Binary Cross-Entropy Loss, BCE Loss），將每個類別視為獨立的二分類問題（使用 Sigmoid 代替 Softmax）以處理多標籤分類與類別重疊。
    * `Class Loss Weight` (分類權重 cls) **`[預設值 Default]`** = **`0.5`**
  * **邊界框回歸損失 (box_loss)：CIoU Loss**
    * 預設函數：完整交並比損失（Complete Intersection over Union Loss, CIoU Loss），同時考慮重疊面積、中心點距離以及長寬寬高比。
    * `Box Loss Weight` (定位框權重 box) **`[預設值 Default]`** = **`7.5`**
  * **分佈焦點損失 (dfl_loss)：Distribution Focal Loss (DFL)**
    * 預設函數：分佈焦點損失（Distribution Focal Loss），預設框與中心點之間距離的機率分佈，提升模糊邊界或小目標物體的精準度。
    * `DFL Loss Weight` (DFL 權重 dfl) **`[預設值 Default]`** = **`1.5`**

* **資料增強參數 (Data Augmentation - YOLOv11 預設與自訂參數)**
  * `Mixup` (影像混合) = **`0.1`**（顯式指定隨機融合兩張圖片的比例）
  * `Copy-Paste` (剪貼增強) = **`0.1`**（顯式指定剪下物體貼至其他背景的比例）
  * `Random Erasing` (隨機擦除 erasing) = **`0.4`**（顯式指定隨機遮擋影像部分區域的比例，提升局部特徵識別力）
  * `Mosaic` (馬賽克拼接) = **`1.0`**（顯式指定隨機拼接 4 張影像）
  * `Degrees` (隨機旋轉) = **`15.0`**（顯式指定影像最大隨機旋轉角度）
  * `Translate` (隨機平移) = **`0.1`**（顯式指定影像平移範圍比例）
  * `Scale` (隨機縮放) = **`0.5`**（顯式指定影像縮放變動範圍，即 50% 範圍內縮放）
  * `Fliplr` (左右翻轉) = **`0.5`**（顯式指定水平翻轉影像的機率）
  * `Flipud` (上下翻轉) = **`0.1`**（顯式指定垂直翻轉影像的機率）
  * `HSV` (色調/飽和度/亮度) = **`[0.015, 0.7, 0.4]`**（顯式指定影像色澤明暗的隨機抖動幅度）

*(註：本報告已排除 `Workers`, `Cache`, `Device` 等僅影響電腦讀取速度、不影響模型權重訓練與學習指標之硬體輔助參數。)*

---

## 📝 3. 學術論文 LaTeX / Word 三線表排版建議

根據國際學術期刊（如 IEEE、Elsevier、Springer、MDPI 等）的標準排版規範，**表格不應以「圖片」形式直接貼入論文中**，而應使用文書軟體的表格功能（如 Word 或 LaTeX）進行排版，並採用標準的**三線表（Three-line Table）**格式。

以下為您準備了可直接複製使用的 LaTeX 原始碼，以及 Word 的欄位優化排版建議：

### 🅰️ LaTeX 原始碼（使用 `booktabs` 與 `threeparttable` 套件）

```latex
\begin{table}[htbp]
\centering
\caption{Hyperparameter settings for YOLOv11 Phase 1 and Phase 2 training models.}
\label{tab:yolo_hyperparameters}
\begin{threeparttable}
\small
\setlength{\tabcolsep}{5pt}
\begin{tabular}{llcccccc}
\toprule
\textbf{Model Variant} & \textbf{Config (.yaml)} & \textbf{Weights Source} & \textbf{Batch Size} & \textbf{Image Size} & \textbf{Epochs} & \textbf{Freeze} & \textbf{lr0} \\
\midrule
YOLO11s Baseline (Ph1) & Default & yolo11s.pt & 32 & 640 & 300 & 0 & 0.01 \\
YOLO11m Baseline (Ph1) & Default & yolo11m.pt & 16 & 640 & 300 & 0 & 0.01 \\
YOLO11s P2-CBAM (Ph1)  & yolo11-strawberry-p2-cbam-s.yaml & yolo11s.pt & 16 & 640 & 300 & 0 & 0.01 \\
YOLO11m P2-CBAM (Ph1)  & yolo11-strawberry-p2-cbam-m.yaml & yolo11m.pt & 12 & 640 & 300 & 0 & 0.01 \\
\midrule
YOLO11s Baseline (Ph2) & Default & Ph1 Best & 96 & 640 & 150 & 10 & 0.005 \\
YOLO11s Baseline (Ph2) & Default & Ph1 Best & 72 & 800 & 150 & 10 & 0.005 \\
YOLO11s Baseline (Ph2) & Default & Ph1 Best & 32 & 1024 & 150 & 10 & 0.005 \\
\bottomrule
\end{tabular}
\begin{tablenotes}
\small
\item \textit{Note:} All models were trained using the AdamW optimizer (seed = 42, patience = 100). Default loss weights (box = 7.5, cls = 0.5, dfl = 1.5) and standard YOLOv11 data augmentation settings were applied.
\end{tablenotes}
\end{threeparttable}
\end{table}
```

### 🅱️ Word 排版步驟說明
1. **建立表格**：在 Word 中插入一個 $8 \times 8$ 的表格，填入上述差異化數據（包括新增的 Epochs、Freeze 和 lr0 欄位）。
2. **套用三線表**：
   * 選取整個表格，並在「設計」/「邊框」中，**取消所有框線**。
   * 單獨為表格加上**上邊框（頂線，1.5 pt 粗）**與**下邊框（底線，1.5 pt 粗）**。
   * 選取表頭列，並加上**下邊框（中線，0.75 pt 粗）**。
3. **新增註腳（Note）**：在表格正下方，以較小字級（例如 9 pt，Times New Roman 斜體）插入共通超參數說明（已大幅縮短，不再贅述表格中已有的參數）：
   > *Note: All models were trained using the AdamW optimizer (seed = 42, patience = 100). Default loss weights (box = 7.5, cls = 0.5, dfl = 1.5) and standard YOLOv11 data augmentation settings were applied.*

