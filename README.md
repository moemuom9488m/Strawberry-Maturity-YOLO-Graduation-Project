# 🍓 草莓監測機器人畢業專題 (Strawberry Monitoring Robot)

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.0+-EE4C2C.svg?style=for-the-badge&logo=pytorch&logoColor=white)](https://pytorch.org/)
[![YOLO11](https://img.shields.io/badge/YOLO-v11-00FFFF.svg?style=for-the-badge)](https://github.com/ultralytics/ultralytics)
[![Hardware](https://img.shields.io/badge/GPU-RTX%204060%20Ti-76B900.svg?style=for-the-badge&logo=nvidia&logoColor=white)](https://www.nvidia.com/)

本專案旨在開發一套全自動草莓成熟度監測系統，結合 **YOLO11** 目標偵測演算法與 **CCPP (Complete Coverage Path Planning)** 全覆蓋路徑規劃，實現自走車在草莓田中的雙側側拍精密導航與成熟度數位孿生建構。

---

## 🚀 核心功能
1.  **成熟度辨識**: 使用 YOLO11 進行草莓偵測，區分「成熟、半熟、未成熟」三種狀態。
2.  **2D 數位孿生**: 利用輕量自適應 HSV 色彩分割與形態學骨架化演算法，將空拍圖或模擬影像轉化為 2D 物理網格地圖，高效率提取田壟與溝渠中心線。
3.  **CCPP 全覆蓋路徑規劃**: 
    - 採用 0.1m 解析度。
    - 實作 **CCPP 雙側相機全覆蓋 (無跳行 zigzag)** 遍歷策略，符合車載雙側側拍巡檢規範。
    - 支援動態避障與 CCPP 銜接軌跡優化。
4.  **自動化維護**: 具備訓練日誌自動備份、錯誤監控與權重保護機制 (詳見 `GEMINI.md`)。

---

## 📂 資料夾結構
- `agent_tools/`: 存放 AI 代理撰寫的輔助腳本與演算法工具。
- `best_weights/`: 存放經過驗證的最佳模型權重 (`.pt`)。
- `logs/`: 集中存放所有訓練日誌與系統錯誤 Log。
- `路徑規劃&模擬地圖/`:
    - `ccpp_planner.py`: CCPP 全覆蓋路徑規劃核心模組。
    - `ccpp_test.ipynb`: CCPP 模擬與中心線路徑測試（包含輕量化 HSV+骨架化提取實行）。
    - `SAM2D+CCPP路徑規劃.ipynb`: CCPP 與 SAM2 整合比較展示。
    - `farm_grid_map.csv`: 0.1m 解析度的田野物理網格。
    - `strawberry_twin_final.py`: 草莓田 3D 模擬與數位孿生可視化。
- `yolo訓練程式碼.ipynb`: 模型訓練主程式。
- `影片偵測.ipynb`: 實時影片推論與座標映射。

---

## 🛠️ 技術規格
- **硬體環境**: Intel i7-14700F / NVIDIA RTX 4060 Ti (cuda:0)
- **演算法**:
    - **偵測**: YOLO11 (含 CBAM 模組優化)。
    - **導航**: CCPP (Complete Coverage Path Planning) 全覆蓋路徑規劃。
- **解析度**: 地圖固定為 **0.1m/grid**。

---

## 📖 快速開始
1.  **安裝環境**:
    ```bash
    pip install -r requirements.txt
    ```
2.  **實驗數據對比**:
    執行比較工具，自動提取 runs/detect 下的結果並繪製對比圖：
    ```bash
    python agent_tools/yolo_comparator.py
    ```
3.  **路徑規劃測試**:
    開啟 `路徑規劃&模擬地圖/SAM2D+CCPP路徑規劃.ipynb` 進行模擬。
4.  **影片偵測**:
    執行 `影片偵測.ipynb` 對錄製好的草莓田影片進行分析。
5.  **學術超參數表格編譯 (LaTeX)**:
    使用 `pdflatex` 指令將 LaTeX 表格原始碼編譯生成學術排版 PDF：
    ```bash
    pdflatex yolo_hyperparameters_table.tex
    ```

---

## 📊 實驗評估與模型排行榜 (Experimental Results & Leaderboard)

本專案所有 YOLO 訓練實驗數據均遵循單一事實來源，以 [實驗結果.md](實驗結果.md) 的排行榜為準。以下是精選的核心模型精度表現與排行榜：

### 🏆 核心模型排行榜 (精選自 [實驗結果.md](實驗結果.md))

| 排名 | 訓練名稱 / 權重檔案 | 影像尺寸 (imgsz) | 最佳 mAP50 (偵測率) | 最佳 mAP50-95 (綜合精度) | 備註 / 實車部署與簡報定位 |
| :---: | :--- | :---: | :---: | :---: | :--- |
| 🥇 **1** | `train1` (Legacy Champion) | 640 px | **0.89500** | **0.69729** | **歷史表現最優**，口試與論文展示首選。收錄於 `best_weights/best_train1_legacy_20260505.pt` |
| 🥈 **2** | `train3` (Legacy) | 640 px | 0.88359 | 0.67133 | 綜合表現次優。收錄於 `best_weights/best_train3_legacy_20260505.pt` |
| 🥉 **3** | `exp2b_1a_img800` (S Baseline) | 800 px | 0.86921 | 0.64423 | **實車巡檢 FPS 優化首選**。收錄於 `best_weights/best_exp2b_img800_20260505.pt` |
| **4** | `exp2a_1a_img640` (S Baseline) | 640 px | 0.86571 | 0.63694 | 一階段 Baseline 微調（640px 控制組） |
| **7** | `exp2b_1d_img800` (P2-CBAM) | 800 px | 0.87493 | 0.63063 | YOLO11m 注意力機制優化（簡報主推部署對照） |

* 完整 13 組實驗的歷史排行榜、精確率 (Precision) 與召回率 (Recall) 數據詳見：[實驗結果.md](實驗結果.md)
* 完整對照實驗報告及 Loss 收斂折線圖詳見：[yolo_experiments_comparison.md](evaluation_results/yolo_experiments_comparison.md)

### 📈 雙 Y 軸 Tradeoff 決策分析與部署選擇
為了平衡實車巡檢的精度與算力，我們針對 Baseline 與注意力改進模型進行了 Tradeoff 決策分析：
*   **決策圖實體路徑**：[evaluation_results/ppt_model_selection_comparison.png](evaluation_results/ppt_model_selection_comparison.png)

![簡報專用模型選擇與 Tradeoff 對比圖](evaluation_results/ppt_model_selection_comparison.png)

自走車巡檢系統最終選用 **YOLO11s Baseline (800px)**（即 `exp2b_1a_img800`，實車巡檢 FPS 優化首選）或 **train1 (640px)** 作為實車部署的核心，確保在 RTX 4060 Ti 上能夠流暢運行並獲得精確的成熟度辨識結果。

---

## 📜 維護協定
本專案遵循 `GEMINI.md` 中定義的技術標準，所有座標計算必須統一使用 **物理座標 (Meters)**，嚴禁直接操作像素座標以避免映射誤差。

