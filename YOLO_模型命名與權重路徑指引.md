# 🍓 畢業專題：YOLOv11 草莓偵測模型命名邏輯與訓練權重對照表

本文件用於記錄本畢業專題中所有 YOLOv11 訓練實驗模型的命名邏輯，並彙整當前 `runs/detect/` 目錄下所有實驗的最佳（Best）與最末（Last）權重路徑的相對連結，方便快速調用與部署。

---

## 🏗️ 1. 模型實驗命名邏輯 (Model Naming Architecture)

我們的 YOLO 訓練實驗共分為兩個核心階段（Phase 1 & Phase 2），命名語法遵循以下結構化規則：

### 階段一：模型架構與注意力機制實驗 (Phase 1)
主要用於尋找最佳的 YOLOv11 基礎模型尺寸，並對比引入 **P2 微小目標檢測頭**與 **CBAM 注意力機制** 後的效能改進。
*   **命名結構**：`exp1[a/b/c/d]_yolo11[scale]_[architecture]`
*   **欄位拆解說明**：
    *   `exp1`：代表第一階段實驗（架構優化對照）。
    *   `a / b / c / d`：流水編號，代表不同的模型與結構變量。
    *   `scale`：模型大小規模（`s` 為 Small 輕量模型；`m` 為 Medium 中型模型）。
    *   `architecture`：優化架構類型（`baseline` 為 Ultralytics 官方基準結構；`p2cbam` 為加入 P2 微小目標特徵檢測層 + CBAM 通道與空間注意力機制）。

### 階段二：輸入影像解析度對比實驗 (Phase 2)
主要用於在固定架構下，對照不同輸入影像大小（640 / 800 / 1024 像素）對草莓成熟度偵測精準度的影響。
*   **命名結構**：`exp2[a/b/c]_[baseline/best_group]_img[size]`
*   **欄位拆解說明**：
    *   `exp2`：代表第二階段實驗（影像解析度對照）。
    *   `a / b / c`：解析度流水號（`a` 為 640px；`b` 為 800px；`c` 為 1024px）。
    *   `1a / 1d`：對比的第一階段模型代號（`1a` 對照組為 `exp1a` Baseline；`1d` 對照組為 `exp1d` P2-CBAM）。
    *   `img[size]`：輸入模型的像素邊長（如 `img640`、`img800`、`img1024`）。

---

## 📊 2. 當前訓練實驗與權重路徑對照表 (Relative Path Links)

以下表格彙整了 `runs/detect/` 下的所有實驗，並提供權重檔案的**相對路徑連結**。您可以直接在 Markdown 編輯器或 VS Code 中點選連結直接定位權重檔案。

| 排序 | 實驗資料夾名稱 (Runs Directory) | 階段與模型架構詳細說明 (Experiment Description) | Best mAP50 | 最佳權重相對路徑 (Best Weights) | 最末權重相對路徑 (Last Weights) |
| :---: | :--- | :--- | :---: | :--- | :--- |
| **1** | **exp2c_1d_img1024** | 階段二：P2-CBAM 模型 + **1024px** 超高解析度輸入 | **0.8750** | [best.pt](runs/detect/exp2c_1d_img1024/weights/best.pt) | [last.pt](runs/detect/exp2c_1d_img1024/weights/last.pt) |
| **2** | **exp2b_1d_img800** | 階段二：P2-CBAM 模型 + **800px** 高解析度輸入 | **0.8749** | [best.pt](runs/detect/exp2b_1d_img800/weights/best.pt) | [last.pt](runs/detect/exp2b_1d_img800/weights/last.pt) |
| **3** | **exp1d_yolo11m_p2cbam** | 階段一：YOLOv11m + P2 微小頭 + CBAM 注意力機制 | **0.8706** | [best.pt](runs/detect/exp1d_yolo11m_p2cbam/weights/best.pt) | [last.pt](runs/detect/exp1d_yolo11m_p2cbam/weights/last.pt) |
| **4** | **exp1a_yolo11s_baseline** | 階段一：YOLOv11s Baseline 官方基準（S 規模） | **0.8699** | [best.pt](runs/detect/exp1a_yolo11s_baseline/weights/best.pt) | [last.pt](runs/detect/exp1a_yolo11s_baseline/weights/last.pt) |
| **5** | **exp2b_1a_img800** | 階段二：YOLOv11s Baseline + **800px** 高解析度輸入 | **0.8692** | [best.pt](runs/detect/exp2b_1a_img800/weights/best.pt) | [last.pt](runs/detect/exp2b_1a_img800/weights/last.pt) |
| **6** | **exp2a_1d_img640** | 階段二：P2-CBAM 模型 + **640px** 官方標準解析度 | **0.8673** | [best.pt](runs/detect/exp2a_1d_img640/weights/best.pt) | [last.pt](runs/detect/exp2a_1d_img640/weights/last.pt) |
| **7** | **exp2c_1a_img1024** | 階段二：YOLOv11s Baseline + **1024px** 超高解析度 | **0.8668** | [best.pt](runs/detect/exp2c_1a_img1024/weights/best.pt) | [last.pt](runs/detect/exp2c_1a_img1024/weights/last.pt) |
| **8** | **exp2a_1a_img640** | 階段二：YOLOv11s Baseline + **640px** 官方標準解析度 | **0.8657** | [best.pt](runs/detect/exp2a_1a_img640/weights/best.pt) | [last.pt](runs/detect/exp2a_1a_img640/weights/last.pt) |
| **9** | **exp1b_yolo11m_baseline** | 階段一：YOLOv11m Baseline 官方基準（M 規模） | **0.8648** | [best.pt](runs/detect/exp1b_yolo11m_baseline/weights/best.pt) | [last.pt](runs/detect/exp1b_yolo11m_baseline/weights/last.pt) |
| **10** | **exp1c_yolo11s_p2cbam** | 階段一：YOLOv11s + P2 微小頭 + CBAM 注意力機制 | **0.8602** | [best.pt](runs/detect/exp1c_yolo11s_p2cbam/weights/best.pt) | [last.pt](runs/detect/exp1c_yolo11s_p2cbam/weights/last.pt) |

> 💡 **小撇步**：
> - 點選表格中的 `[best.pt]` 或 `[last.pt]` 相對連結，可以直接跳轉或在程式中直接以該相對路徑載入權重。例如在 Python 偵測腳本中載入：
>   ```python
>   from ultralytics import YOLO
>   # 使用相對路徑載入最優模型
>   model = YOLO("runs/detect/exp2c_1d_img1024/weights/best.pt")
>   ```

---

## 🔒 3. 實車部署權重保護協定 (Best Weights Backup)

為了防止 YOLO 訓練過程中的覆蓋與意外損壞，我們制定了**實車部署權重防護備份**機制。

我們將當前表現最佳的前兩名模型抽取複製，並集中保護存放在專案根目錄的 `best_weights/` 資料夾下，檔名已進行重命名標記：
*   **備份路徑一**：`best_weights/best_exp2c_1d_img1024.pt` (mAP50: 0.8750)
*   **備份路徑二**：`best_weights/best_exp2b_1d_img800.pt` (mAP50: 0.8749)

在後續的自走車系統對接或 Gradio Web 介面展示時，建議優先從 `best_weights/` 下調用這些已確認穩定且表現最佳的權重檔案！
