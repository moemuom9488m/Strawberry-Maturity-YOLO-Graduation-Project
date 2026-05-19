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
2.  **路徑規劃測試**:
    開啟 `路徑規劃&模擬地圖/SAM2D+CCPP路徑規劃.ipynb` 進行模擬。
3.  **影片偵測**:
    執行 `影片偵測.ipynb` 對錄製好的草莓田影片進行分析。

---

## 📜 維護協定
本專案遵循 `GEMINI.md` 中定義的技術標準，所有座標計算必須統一使用 **物理座標 (Meters)**，嚴禁直接操作像素座標以避免映射誤差。
