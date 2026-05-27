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
- `training_logs/`: 集中存放所有訓練日誌與系統錯誤 Log。
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

---

## 📊 實驗評估與決策對照 (Experimental Results)

為確保巡檢自走車在戶外自然環境下具備最優的草莓成熟度偵測精準度與運算效率，我們針對 YOLOv11 進行了多維度對照實驗。以下為我們為簡報與實車部署精選的 4 組核心模型數據對比：

| 評估模型名稱 (YOLO Model) | 輸入影像尺寸 (Resolution) | 最佳精度 Best mAP@0.5 | 綜合精度 Best mAP@0.5:0.95 | 訓練耗時 (Time Cost) |
| :--- | :---: | :---: | :---: | :---: |
| 🏆 **exp2b_1d_img800** (P2-CBAM) | 800 x 800 px | **0.8749** | 0.6258 | 86.8 hr |
| 🥈 **exp1a_yolo11s_baseline** (S基準) | 640 x 640 px | **0.8699** | 0.6284 | 63.9 hr |
| 🥉 **exp2b_1a_img800** (S基準) | 800 x 800 px | **0.8692** | **0.6438** | 65.6 hr |
| ❌ **exp1b_yolo11m_baseline** (M基準) | 640 x 640 px | **0.8648** | 0.4389 | 89.8 hr |

* 完整對照實驗報告及 Loss 收斂折線圖詳見：[yolo_experiments_comparison.md](file:///d:/銘澄專區/畢業專題工作區/evaluation_results/yolo_experiments_comparison.md)

### 📈 雙 Y 軸 Tradeoff 決策分析圖
我們針對上述核心模型，繪製了精度 (mAP@0.5) 與計算耗時 (Hours) 的雙 Y 軸對照圖，做為自走車實車部署（選定 **YOLO11s P2-CBAM 800px**）的科學依據：
*   **決策圖實體路徑**：[evaluation_results/ppt_model_selection_comparison.png](file:///d:/銘澄專區/畢業專題工作區/evaluation_results/ppt_model_selection_comparison.png)

![簡報專用模型選擇與 Tradeoff 對比圖](file:///d:/銘澄專區/畢業專題工作區/evaluation_results/ppt_model_selection_comparison.png)

---

## 📜 維護協定
本專案遵循 `GEMINI.md` 中定義的技術標準，所有座標計算必須統一使用 **物理座標 (Meters)**，嚴禁直接操作像素座標以避免映射誤差。

