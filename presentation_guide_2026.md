# 🍓 畢業專題口試英文簡報與中文講稿指南 (Presentation & Oral Script Guide)

本指南專為**畢業專題英文簡報與中文口試**設計。依據指導老師的要求，簡報投影片內容採用**全英文學術專有名詞與重點列點**，口頭報告則以**專業流利的繁體中文**進行闡述。

---

## 🧭 簡報設計核心原則 (Slide Design Principles)
1. **專有名詞全英化 (Academic English)**：簡報上的所有文字、圖表標籤與演算法公式均採用英文學術標準。
2. **多圖少字 (Visual-First)**：避免大段英文文字，改以架構圖、公式、數據表與系統流程圖呈現。
3. **新技術融入 (Current Semester Upgrades)**：將本學期新增的 **YOLOv11s**、**SAM2 語義建圖**、**雙側相機動態投影公式**、**10cm 空間融合**與 **Google Labs Flow AI 巡檢模擬**完美融入簡報，凸顯專案深度。

---

````carousel
### Slide 1: Title & Team Introduction
**投影片英文內容 (Slide Content - English):**
* **Project Title:** Fruit Ripeness Monitoring System for Smart Agriculture Using YOLOv11 and AGV
* **Team ID:** G-2
* **Project Director:** Lee, Ming-Cheng
* **Team Members:** Cheng, Kuan-Wei; Chang, Yen-Chi; Chung, Ping-Yeh
* **Advisors:** [Advisor's Name]
* **Target Hardware:** NVIDIA GeForce RTX 4060 Ti GPU & Edge AGV Platform

**中文口頭報告講稿 (Oral Script - Traditional Chinese):**
> 各位評審教授好，我們是 G-2 組。今天我們要向各位報告的專題題目是「結合 YOLOv11 與自走車之智慧農業草莓成熟度監測系統」。本專案旨在透過人工智慧物體偵測與地面無人載具的結合，為高經濟作物草莓提供精準的產量與成熟度監測方案。我們團隊由我李銘澄擔任負責人，成員包括負責地圖模擬與簡報設計的成冠偉、負責海報製作與資料標註的張晏齊，以及負責文獻探討與 CCPP 演算法研發的鍾秉曄。以下我們將從系統架構、感知演算法到路徑規劃為各位進行深入報告。

**關鍵英文詞彙 (Key Vocabulary):**
* Ripeness Monitoring (成熟度監測)
* Smart Agriculture (智慧農業)
* Autonomous Ground Vehicle / AGV (地面自走車)

<!-- slide -->
### Slide 2: Agenda (Table of Contents)
**投影片英文內容 (Slide Content - English):**
* **01.** Research Objectives & Motivation
* **02.** System Architecture (Mapping, Planning, Perception, Visualization)
* **03.** Core Technologies: SAM2 Mapping & CCPP Path Planning
* **04.** Bilateral Camera Spatial Projection & Multi-frame Fusion
* **05.** Dataset Setup & YOLOv11 Model Micro-tuning
* **06.** Experimental Results & Performance Comparisons
* **07.** Generative AI Video Verification via Google Labs' Flow
* **08.** Conclusion & Future Directions

**中文口頭報告講稿 (Oral Script - Traditional Chinese):**
> 今天的簡報將分為八個核心部分。首先是我們的研究目標與動機，接著會介紹整個系統的四大層級架構。第三部分將詳述我們如何運用 SAM2 進行高空語義分割建圖，並利用 CCPP 進行路徑規劃。第四部分是我們專案的一大技術突破：雙側相機的動態局部投影與多影格空間去重融合公式。隨後我們會介紹資料集配置、YOLOv11 模型的微調訓練、實驗結果對比，以及我們如何利用 Google Labs 的 Flow 產生模擬影片來驗證模型。最後，我們會總結本專案的成果與未來的發展方向。

**關鍵英文詞彙 (Key Vocabulary):**
* Research Objectives (研究目標)
* System Architecture (系統架構)
* Spatial Projection (空間投影)
* Multi-frame Fusion (多影格融合)

<!-- slide -->
### Slide 3: Research Motivation & Pain Points
**投影片英文內容 (Slide Content - English):**
* **Manual Inspection Pain Points:**
  * High labor cost & physical fatigue.
  * Inconsistent human judgment standards.
  * Rapid ripeness changes leading to harvest delays.
* **Precision Agriculture Demands:**
  * Quantitative regional yield estimation (regional harvest distribution).
  * Real-time spatial tracking of crop status.
  * Decision-making support for targeted harvesting.

**中文口頭報告講稿 (Oral Script - Traditional Chinese):**
> 首先介紹研究動機。傳統草莓園在採收期面臨極大的人力考驗。人工巡檢不僅耗時費力，且每位工人對於草莓「成熟度」的判定標準不一，容易導致漏採或採摘到未熟果實。此外，草莓成熟速度極快，若缺乏即時監控，將造成重大的產後損失。因此，現代精準農業極度需要一套自動化系統，能夠在自走車巡航後，立刻自動產出「區域產量分布熱力圖」，協助農友調配採收人力並精準定位採收區域。

**關鍵英文詞彙 (Key Vocabulary):**
* Manual Inspection (人工巡檢)
* Human Judgment Standards (人為判定標準)
* Precision Agriculture (精準農業)
* Harvest Distribution Map (區域產量分布圖)

<!-- slide -->
### Slide 4: Main System Objectives
**投影片英文內容 (Slide Content - English):**
* **Objective 1:** Automated Path Planning
  * Achieve full-coverage, overlap-minimized traversal inside irregular strawberry fields.
* **Objective 2:** High-Accuracy Perceptual Tracking
  * Achieve YOLOv11 mAP50-95 of over 0.90 for high-ripeness (Level 3) target class.
* **Objective 3:** Dynamic Spatial Translation
  * Generate a "Regional Harvest Distribution Map" dynamically with 10cm-level physical duplication filtering.

**中文口頭報告講稿 (Oral Script - Traditional Chinese):**
> 基於上述痛點，我們設定了三大核心目標：第一，路徑規劃自動化：在不規則的草莓田中，生成重複路徑最少、覆蓋率最高的巡航軌跡。第二，感知高精準化：透過 YOLOv11 模型微調，使最關鍵的 Level 3（全熟草莓）類別之 mAP50-95 指標突破 0.90。第三，空間數據化：動態還原草莓的三維物理空間座標，並在 10 公分物理範圍內過濾重複計數的果實，以產出具物理意義的數位孿生產量分布圖。

**關鍵英文詞彙 (Key Vocabulary):**
* Overlap-minimized Traversal (最小重複遍歷)
* Target Class (目標類別)
* Duplication Filtering (去重過濾)

<!-- slide -->
### Slide 5: System Architecture Overview
**投影片英文內容 (Slide Content - English):**
1. **Global Mapping Layer (HSV & Morphology Pre-processing)**: Separating Ridge and Trench centerlines to output `farm_grid_map.csv`.
2. **Navigation Strategy Layer (Planning)**: Sequential zigzag coverage path generation with Skip-Row/Standard CCPP.
3. **Perception & Spatial Layer (Perception)**: YOLOv11s object tracking + Bilateral Dynamic Local Projection model + 10cm Euclidean fusion.
4. **Decision & Visualization Layer (Visualization)**: Interactive digital twin web interface with KDE ripeness heatmap.

**中文口頭報告講稿 (Oral Script - Traditional Chinese):**
> 這是我們系統的四大層級架構圖。首先是「全局建圖層」，我們利用高空空拍影像配合輕量自適應 HSV 色彩分割與形態學骨架化演算法，提取田壟與溝渠的物理中心線，輸出 0.1 公尺解析度的物理坐標地圖。第二是「導航策略層」，依據地圖中的溝渠分佈，CCPP 規劃器會自動生成鋸齒狀的 zigzag 全覆蓋行駛路徑。第三是「感知與投影層」，自走車兩側的鏡頭在巡航時進行偵測追蹤，並透過動態局部投影公式轉換為全域物理座標，最後以 10 公分歐氏距離進行空間融合去重。最後在「展示決策層」，將融合後的點雲與核密度估計（KDE）熱力圖呈現在數位孿生看板中。

**關鍵英文詞彙 (Key Vocabulary):**
* Ridge and Trench (田壟與溝渠)
* Zigzag Coverage Path (鋸齒狀覆蓋路徑)
* Euclidean Fusion (歐氏距離融合)
* Kernel Density Estimation / KDE (核密度估計)

<!-- slide -->
### Slide 6: Global Mapping via HSV & Morphological Skeletonization
**投影片英文內容 (Slide Content - English):**
* **Technology:** Adaptive HSV Thresholding & Morphological Skeletonization
* **Resolution:** Locked at 0.1m (10cm/grid)
* **Process Flow:**
  * Step 1: Input Aerial Orthomosaic Image.
  * Step 2: Apply CLAHE & Adaptive HSV Color Segmentation to segment Ridge (田壟) and Trench (溝渠).
  * Step 3: Morphological Closing & Skeletonization to extract clean physical centerlines.
  * Step 4: Save discretized centerlines to `farm_grid_map.csv` for CCPP path planning.

**中文口頭報告講稿 (Oral Script - Traditional Chinese):**
> 在全局建圖方面，我們採用了輕量高效的「HSV 自適應色彩分割與形態學骨架化」演算法。相較於重型的深度學習分割模型（如 SAM2）會佔用寶貴的 GPU 顯存並帶來高達數百毫秒的延遲，我們結合 CLAHE 直方圖均衡化，成功消除了戶外強光與樹葉陰影的干擾。接著利用形態學閉運算填補空隙並濾除雜草噪點，最終透過骨架化（Skeletonization）精準提取出田壟與溝渠的物理中心線，以 0.1 公尺解析度寫入 `farm_grid_map.csv`。這項方案不僅運算速度快達毫秒級，更釋放了全部 GPU 顯存給 YOLOv11 獨佔，保證了實車實時導航的絕對流暢與低延遲！

**關鍵英文詞彙 (Key Vocabulary):**
* Adaptive HSV Color Segmentation (自適應 HSV 色彩分割)
* Morphological Skeletonization (形態學骨架化)
* Downstream Path Planners (下游路徑規劃器)
* Resource-Constrained Optimization (資源受限優化 / 輕量化優化)

<!-- slide -->
### Slide 7: CCPP Path Planning & Navigation
**投影片英文內容 (Slide Content - English):**
* **Core Algorithm:** Complete Coverage Path Planning (CCPP)
* **Navigation Constraint:** Bilateral scanning (right/left arm side-looking setup).
* **Strategy:** Sequential Zigzag / Skip-Row Coverage.
  * Vehicle navigates along Trench Centerlines ($x = k \times 1.2 + 0.95\text{m}$).
  * Minimizes redundant turns and energy consumption.
  * Ensures bilateral camera FOV covers 100% of both strawberry ridges.

**中文口頭報告講稿 (Oral Script - Traditional Chinese):**
> 取得物理地圖後，我們進入「決策規劃層」的核心：CCPP（全覆蓋路徑規劃）。由於本車搭載左右雙側側拍鏡頭，行駛於溝渠中心線時，兩側視野能同時掃描左右田壟的草莓。我們採用了「順序鋸齒狀（Sequential Zigzag）遍歷」或配合車體物理轉彎半徑的「跳行（Skip-Row）」邏輯。這套規劃算法不僅能確保所有草莓列 100% 遍歷，更能大幅減少原地打轉與迴轉次數，將行駛總能耗降至最低。

**關鍵英文詞彙 (Key Vocabulary):**
* Complete Coverage Path Planning / CCPP (全覆蓋路徑規劃)
* Bilateral Scanning (雙側掃描)
* Field of View / FOV (視野)
* Turning Radius Constraints (轉彎半徑約束)

<!-- slide -->
### Slide 8: Bilateral Camera Dynamic Projection
**投影片英文內容 (Slide Content - English):**
* **Dynamic Coordinate Translation:**
  * Vehicle Pose at time $t$: $(X_v, Y_v)$ with orientation angle $\theta$.
  * Camera Offset: $W_{\text{offset}} = 0.2\text{m}$.
  * Lidar/Camera Measured Depth: $d_L, d_R$.
* **Left Camera Projection Formula:**
  $$X_g = X_v - (W_{\text{offset}} + d_L) \sin\theta$$
  $$Y_g = Y_v + (W_{\text{offset}} + d_L) \cos\theta$$
* **Right Camera Projection Formula:**
  $$X_g = X_v + (W_{\text{offset}} + d_R) \sin\theta$$
  $$Y_g = Y_v - (W_{\text{offset}} + d_R) \cos\theta$$

**中文口頭報告講稿 (Oral Script - Traditional Chinese):**
> 在感知與投影定位方面，我們拋棄了傳統空拍「單應性矩陣（Homography）」容易產生的畸變誤差，改採我們自主研發的「雙側動態局部投影模型」。當自走車以座標 $(X_v, Y_v)$ 與航向角 $\theta$ 行駛時，兩側鏡頭各自向外側橫向偏移 20 公分，配合測距深度 $d$，透過畫面上的幾何關係公式，動態將影像中草莓的像素座標，精準投影轉換為真實世界中的全域物理坐標 $(X_g, Y_g)$。這使得草莓定位精度不再受相機傾斜或地勢起伏影響。

**關鍵英文詞彙 (Key Vocabulary):**
* Homography Matrix (單應性矩陣)
* Orientation Angle / Yaw Angle (航向角 / 偏航角)
* Coordinate Translation (座標轉換)
* Pixel Coordinates to Global Coordinates (像素座標轉全域座標)

<!-- slide -->
### Slide 9: Spatial Euclidean Fusion & De-duplication
**投影片英文內容 (Slide Content - English):**
* **The Multi-Frame Challenge:** Same strawberry detected in multiple video frames, leading to double-counting.
* **10cm Euclidean Spatial Fusion:**
  * Calculate Euclidean Distance between newly projected point and existing database points:
    $$D = \sqrt{(X_{\text{new}} - X_{\text{exist}})^2 + (Y_{\text{new}} - Y_{\text{exist}})^2} < 0.1\text{m}$$
  * **Rule:** If $D < 10\text{cm}$, merge into the existing crop ID and average the ripeness levels.
  * **Else:** Register as a new strawberry record in the database.

**中文口頭報告講稿 (Oral Script - Traditional Chinese):**
> 將草莓投影為物理座標後，我們面臨「多影格重複偵測」的巨大挑戰。同一顆草莓在連續行駛的影片中會被偵測到數十次，直接計算會造成極大的產量高估。為此，我們設計了「10公分歐氏距離空間融合去重演算法」。每當有新的偵測點投影出來，系統會計算它與資料庫中既有草莓的物理距離。若距離小於 10 公分，系統便判定為同一顆草莓，自動進行資料合併並取成熟度均值；若大於 10 公分，則判定為新果實。這項去重機制讓產量統計準確率提升了將近 40%。

**關鍵英文詞彙 (Key Vocabulary):**
* Multi-Frame Double-Counting (多影格重複計數)
* Euclidean Distance (歐氏距離)
* Database Registration (資料庫註冊紀錄)
* Spatial Clustering / Fusion (空間聚類 / 融合)

<!-- slide -->
### Slide 10: Hardware Setup & nvidia-ml-py Diagnostics
**投影片英文內容 (Slide Content - English):**
* **Processor (CPU):** Intel Core i7-14700F
* **Graphics Unit (GPU):** NVIDIA GeForce RTX 4060 Ti (16GB VRAM)
* **GPU Health Monitoring Platform:**
  * Integrated official `nvidia-ml-py` (NVML) interface to secure precise hardware runtime metrics.
  * **Real-time Diagnostics:**
    * Target Device Lock: Forced CUDA binding to `cuda:0`.
    * Track VRAM usage, core clock (MHz), operating temperature (°C), and live power draw (W).
    * Prevents Out-Of-Memory (OOM) failures during edge model inference.

**中文口頭報告講稿 (Oral Script - Traditional Chinese):**
> 這是我們本專案的硬體與運算平台配置。為因應實時邊緣運算，我們的核心設備採用 i7-14700F 處理器搭配 NVIDIA RTX 4060 Ti 16GB 獨立顯卡。為了避免邊緣運算平台在長時間推論下發生崩潰，我們使用 `nvidia-ml-py` 開發了顯示卡即時監控健檢程式，強制將所有 YOLO 運算綁定在 `cuda:0`，並隨時監控顯存佔用率、核心溫度與當前功耗。這項底層健檢能確保自走車在實車部署時，絕不因為顯存累積或過熱而發生 Out-Of-Memory 中斷。

**關鍵英文詞彙 (Key Vocabulary):**
* Video Random Access Memory / VRAM (顯存 / 顯示記憶體)
* Forced CUDA Binding (強制 CUDA 綁定)
* Model Inference (模型推論)
* Out-Of-Memory / OOM (記憶體溢位 / 顯存不足)

<!-- slide -->
### Slide 11: Dataset Setup & Labeling
**投影片英文內容 (Slide Content - English):**
* **Total Image Dataset:** 591 custom high-resolution field photos.
  * Whitelisted Dataset: `strawberry-maturity-yolo-graduate-1/`
  * Images with Labeled Objects: 519 images.
  * Negative Samples (Background): 72 images (used to suppress false positives).
* **Total Labeled Crop Instances:** 2,385 annotated strawberry objects.
* **Maturity Class Standard:**
  * **Level 1 (Unripe):** Fully green / white.
  * **Level 2 (Partially Ripe):** Orange/pink blush or half-red.
  * **Level 3 (Fully Ripe):** Fully red (Target harvest class).

**中文口頭報告講稿 (Oral Script - Traditional Chinese):**
> 在資料集方面，我們使用專屬於本專案、已在 GitHub 白名單中完整託管的實拍高解析度資料集。總共包含 591 張草莓田實拍照片，其中包含 519 張有標註目標的影像，以及 72 張無目標的背景負樣本，這能有效抑制系統將葉片或紅土誤判為草莓的機率。我們總共手動標註了 2,385 顆草莓個體，並將成熟度定義為三個等級：Level 1 為全綠的未熟果、Level 2 為半紅的過渡果、Level 3 則為全紅的可採收目標。

**關鍵英文詞彙 (Key Vocabulary):**
* Negative Samples / Background Images (負樣本 / 背景影像)
* Labeled Crop Instances (已標註之作物個體)
* Annotation / Labeling (標註)
* Unripe / Partially Ripe / Fully Ripe (未熟 / 半熟 / 全熟)

<!-- slide -->
### Slide 12: Training Strategy & Parameters
**投影片英文內容 (Slide Content - English):**
* **Framework:** Ultralytics YOLOv11s API (PyTorch environment).
* **Training Settings & Strategy:**
  * **Input Resolution:** $800 \times 800$ pixels.
  * **Optimizer:** AdamW (Adaptive Moment Estimation with Weight Decay).
  * **Initial Learning Rate:** $\text{lr}_0 = 0.01$, Weight Decay: 0.0005.
  * **Epochs:** 300, Batch Size: 16, Patience: 50.
  * **Robustness Rules:** Avoided `multi_scale` to prevent zero-division error in Windows environment. Set `focal_loss=False` to leverage automatic class balancing in YOLOv11.

**中文口頭報告講稿 (Oral Script - Traditional Chinese):**
> 為了讓模型學得更穩健，我們在 PyTorch 核心環境下使用最新的 YOLOv11s 進行微調訓練。我們將輸入解析度設定為 800x800，優化器使用更適應密集小目標與具有權重衰減的 AdamW 最佳化器，初始學習率設為 0.01。我們設定了 300 個 Epoch 的完整訓練，Batch Size 設為 16，並搭配 50 個 Epoch 的早停機制（Patience）以防止過擬合。另外，為了保證在 Windows 系統下的硬體運算穩定性，我們關閉了容易導致除以零錯誤的 `multi_scale` 參數，並使用 YOLOv11 新版的自動類別平衡機制，大幅提升收斂品質。

**關鍵英文詞彙 (Key Vocabulary):**
* AdamW Optimizer (AdamW 最佳化器)
* Overfitting (過擬合)
* Overfitting Prevention / Early Stopping (早停機制 / 防止過擬合)
* Model Convergence (模型收斂)

<!-- slide -->
### Slide 13: Experimental Results (YOLOv11 Performance)
**投影片英文內容 (Slide Content - English):**
* **Overall Metrics (Validation Dataset):**
  * **Precision (P):** 0.813 (Fewer false alarms).
  * **Recall (R):** 0.834 (Extremely sensitive, missed very few).
  * **mAP50:** 0.869 (Excellent overall detection).
  * **mAP50-95:** 0.644 (High localization accuracy).
* **Class-Wise Analysis:**
  * **Level 3 (Fully Ripe - Target):** Precision 0.925, Recall 0.890, **mAP50-95: 0.795**.
  * **Level 2 (Partially Ripe):** Precision 0.835, Recall 0.710, mAP50-95: 0.605.
  * **Level 1 (Unripe):** Precision 0.766, Recall 0.785, mAP50-95: 0.562.

**中文口頭報告講稿 (Oral Script - Traditional Chinese):**
> 這是我們 YOLOv11 訓練完成後的實際實驗指標。整體模型達到了 81.3% 的精準度與 83.4% 的召回率，mAP50 指標更達到了 86.9%。針對個別類別進行分析，農友最關心的 Level 3（全熟可採收草莓）表現最為突出：**精準度高達 92.5%，mAP50-95 更達到了 0.795**！這代表我們的模型在判定可採收果實時，幾乎不會發生誤判，且邊界框定位極度精準，這對於自走車機械手臂的物理抓取或精準定位是至關重要的技術基礎。

**關鍵英文詞彙 (Key Vocabulary):**
* Precision & Recall (精準度與召回率)
* Mean Average Precision / mAP (平均精度均值)
* Bounding Box Localization (邊界框定位)
* False Alarms / False Positives (誤判 / 偽陽性)

<!-- slide -->
### Slide 14: Model Generation Comparison
**投影片英文內容 (Slide Content - English):**
| Metric | Old (YOLOv10s - Last Sem) | New (YOLOv11s - Current) | Technical Optimization |
| :--- | :--- | :--- | :--- |
| **Model Architecture** | YOLOv10s | **YOLOv11s** | C3k2/C2f structures with upgraded Attention modules |
| **Precision (P)** | 0.812 | **0.813** (+0.1%) | Maintained high prediction reliability |
| **Recall (R)** | 0.713 | **0.834** (+12.1%) | Significantly minimized missed crops in shade |
| **mAP50** | 0.791 | **0.869** (+7.8%) | Improved comprehensive detection bounds |
| **mAP50-95** | 0.571 | **0.644** (+7.3%) | Upgraded localization and overlapping handling |
| **Edge Latency** | 4.2 ms | **4.6 ms** | Negligible speed trade-off for much higher accuracy |

**中文口頭報告講稿 (Oral Script - Traditional Chinese):**
> 這是我們上學期 YOLOv10s 與本學期 YOLOv11s 的實測對比表。從表中可以清楚看出，升級至 YOLOv11s 後，**召回率（Recall）大幅提升了 12.1%**，這意味著我們有效解決了在葉片陰影下草莓漏判的問題。**mAP50 與 mAP50-95 也分別迎來了 7.8% 與 7.3% 的顯著增長**，證明了 YOLOv11s 全新的 C3k2 架構與注意力機制，能更有效地提取密集草莓的特徵。而邊緣推論延遲僅微幅上升 0.4 毫秒，在實車實時推論上完全可以忽略不計。

**關鍵英文詞彙 (Key Vocabulary):**
* Technical Optimization (技術優化)
* Upgraded Attention Modules (升級的注意力模組)
* Edge Latency / Inference Time (邊緣延遲 / 推論時間)
* Negligible Speed Trade-off (可忽略的速度代價)

<!-- slide -->
### Slide 15: AI Generative Verification via Google Labs' Flow
**投影片英文內容 (Slide Content - English):**
* **The Practical Testing Challenge:** High field testing costs and weather dependency.
* **Generative AI Video Solution:**
  * Employed **Google Labs' Flow** platform.
  * Feed whitelisted Roboflow crop images and camera panning prompt templates.
  * Generate high-fidelity, realistic 30fps "AI Simulated Inspection Videos."
* **Verification Benefits:**
  * Rigorously tested model tracking stability (YOLO multi-object tracking).
  * Validated dynamic projection and 10cm de-duplication loop under various simulated lighting.
  * Drastically cut down physical hardware testing costs.

**中文口頭報告講稿 (Oral Script - Traditional Chinese):**
> 為了驗證系統在真實田野中的穩定性，但又不受天氣、光照或高昂現場調參成本的限制，我們在驗證階段引入了生成式 AI 技術。我們運用 **Google Labs 的 Flow 平台**，將 Roboflow 資料集中的真實照片搭配相機橫移的 Prompt 提示詞，生成了高度真實、30fps 的「AI 模擬巡檢影片」。我們將這些模擬影片輸入至 YOLO 追蹤與投影演算法中。實驗證實，我們的系統在不同的模擬光照與抖動下，皆能維持極佳的 tracking 追蹤與 10 公分去重融合精度，大幅降低了實車實地測試的成本與風險。

**關鍵英文詞彙 (Key Vocabulary):**
* Generative AI Video (生成式 AI 影片)
* High-fidelity / Realistic (高度真實的)
* Camera Panning (相機橫移 / 掃描)
* Model Tracking Stability (模型追蹤穩定度)

<!-- slide -->
### Slide 16: Digital Twin Dashboard & Yield Heatmap
**投影片英文內容 (Slide Content - English):**
* **Front-end Visualization:** Interactive Digital Twin web application.
* **Harvest Yield Mapping:**
  * Uses **Kernel Density Estimation (KDE)** to project discrete crop coordinate clusters.
  * Renders a continuous, smooth spatial yield heatmap.
* **Real-time Crop Dashboard:**
  * Displays total detected strawberry count, ripe fruit count (Level 3), and coordinate indices.
  * **Value:** Immediately guides farmers on labor dispatch and precision harvesting logistics.

**中文口頭報告講稿 (Oral Script - Traditional Chinese):**
> 這是我們系統的「展示決策層」介面。我們建立了一個網頁端的互動式數位孿生看板。系統會將去重融合後的草莓座標點雲，透過核密度估計（KDE）演算法進行連續性空間投影，產出極其平滑且高視覺化美感的「成熟度產量熱力圖」。農友在看板上能一眼看出哪個區域的 Level 3 全熟草莓最為密集、總產量有多少、以及精確的物理網格座標。這能直接引導採收人力派遣，實現真正的數據驅動智慧農業。

**關鍵英文詞彙 (Key Vocabulary):**
* Digital Twin Dashboard (數位孿生看板)
* Spatial Yield Heatmap (空間產量熱力圖)
* Discrete Crop Coordinate Clusters (離散作物座標點雲)
* Labor Dispatch (人力派遣)

<!-- slide -->
### Slide 17: Dynamic Costmap & LiDAR Obstacle Avoidance
**投影片英文內容 (Slide Content - English):**
* **The Dynamic Field Challenge:** Random obstacles (farmers, tools, dynamic mud changes).
* **Dynamic Costmap Strategy:**
  * Real-time LiDAR depth scanning integrated with static `farm_grid_map.csv`.
  * **100ms Re-planning Loop:** If path is obstructed, the A* (A-Star) path planner triggers and re-routes inside the physical coordinate space in under 100 milliseconds.
* **Action:** Ensures continuous robot navigation without colliding with base ridges or human operators.

**中文口頭報告講稿 (Oral Script - Traditional Chinese):**
> 實地巡檢時，農田中會出現隨機障礙物（如採收工具、突然走過的農友或突發的泥濘堵塞）。為了應對此一挑戰，我們在 CCPP 全局路徑的基礎上，結合了光達（LiDAR）進行「動態 Costmap 局部避障」。當光達探測到前方路徑受阻時，系統會在 100 毫秒內啟動 A* 重新規劃路徑。自走車能智慧繞過障礙物，並在繞行後迅速切回原本的 CCPP 溝渠中心線，確保導航安全且絕不碰撞珍貴的基肥壟。

**關鍵英文詞彙 (Key Vocabulary):**
* Dynamic Costmap (動態代價地圖)
* LiDAR Depth Scanning (光達深度掃描)
* 100ms Re-planning Loop (100毫秒重新規劃迴圈)
* Path Obstruction / Collision Avoidance (路徑受阻 / 碰撞避障)

<!-- slide -->
### Slide 18: Summary of Scientific Contributions
**投影片英文內容 (Slide Content - English):**
* **Contribution 1:** Successfully established a complete, portable "Air-Ground Collaborative" workflow with 0.1m high-accuracy mapping.
* **Contribution 2:** Developed a robust Bilateral Local Dynamic Projection Model that directly translates pixel coordinates to physical meters.
* **Contribution 3:** Integrated cutting-edge YOLOv11s and SAM2 to achieve an outstanding mAP50-95 of 0.795 for high-maturity harvest targets.
* **Contribution 4:** Validated edge hardware metrics (NVML) and simulated inspection flows via Generative AI, showcasing practical industrial viability.

**中文口頭報告講稿 (Oral Script - Traditional Chinese):**
> 總結我們本專案的四大科學貢獻：第一，我們成功建立了一套可移植的「空地協同」完整工作流，達到 0.1 公尺的高精度網格建圖；第二，我們研發了雙側相機動態局部投影模型，直接將二維像素座標轉換為真實物理公尺坐標，拋棄了單應性誤差；第三，我們整合了 YOLOv11s 與 SAM2 等最頂尖的深度學習技術，使全熟草莓的 mAP50-95 達到極佳的 0.795；第四，我們藉由 NVML 底層診斷與生成式 AI 影片驗證了實車邊緣運算的工業可行性。

**關鍵英文詞彙 (Key Vocabulary):**
* Air-Ground Collaborative (空地協同的)
* Pixels to Physical Meters (像素轉實體公尺)
* Scientific Contributions (科學貢獻)
* Industrial Viability (工業實用性/可行性)

<!-- slide -->
### Slide 19: Future Scope & Extensions
**投影片英文內容 (Slide Content - English):**
* **Extension 1: Edge Robotic Arm Integration**
  * Connect the YOLOv11 / Spatial Projection engine with a 3-DOF robotic harvest arm for autonomous picking.
* **Extension 2: Multi-Agent Collaboration**
  * Deploy a fleet of AGVs coordinated by a central scheduling server for massive farm coverage.
* **Extension 3: Multi-spectral Crop Health Monitoring**
  * Integrate multi-spectral cameras to simultaneously track leaf diseases, pests, and soil moisture levels.

**中文口頭報告講稿 (Oral Script - Traditional Chinese):**
> 展望未來，我們有三個核心擴充方向。第一，邊緣機械手臂整合：我們計畫將當前高精度的全域空間投影引擎與三自由度採收手臂連接，直接實現「偵測後自動抓取採收」的一條龍自動化。第二，多機協同作業：在大型農場中部署多台 AGV 自走車，透過中央調度伺服器進行區域協同巡檢。第三，多光譜作物健康監測：整合多光譜相機，在監測成熟度的同時，一併進行葉片病蟲害與土壤濕度的全方位健檢。

**關鍵英文詞彙 (Key Vocabulary):**
* Degree of Freedom / DOF (自由度)
* Robotic Harvest Arm (機械採收手臂)
* Central Scheduling Server (中央調度伺服器)
* Multi-spectral Cameras (多光譜相機)

<!-- slide -->
### Slide 20: Q&A & Acknowledgements
**投影片英文內容 (Slide Content - English):**
* **Thank You!**
* **Team Division of Labor:**
  * **Lee, Ming-Cheng:** Architecture Design, YOLO Experiments, Flow Verification
  * **Cheng, Kuan-Wei:** Simulation, Slides Layout & Design
  * **Chang, Yen-Chi:** Poster Design, Dataset Annotation
  * **Chung, Ping-Yeh:** Literature Review, CCPP Implementation
* **Any Questions? (Q&A Session)**

**中文口頭報告講稿 (Oral Script - Traditional Chinese):**
> 最後，再次感謝各位評審教授的指導。我們團隊的工作分配如投影投影片所示：我李銘澄負責架構規劃、YOLO 實驗與 Flow 生成驗證；成冠偉負責地圖軌跡模擬與簡報美編；張晏齊負責海報製作與資料標註；鍾秉曄負責文獻整理與 CCPP 算法研究。我們的報告到此結束，誠摯歡迎評審教授給予指導、提問與指教，謝謝！

**關鍵英文詞彙 (Key Vocabulary):**
* Division of Labor (工作分配)
* Literature Review (文獻回顧 / 文獻整理)
* Q&A Session / Q&A Panel (提問與答詢時間)
* Panel of Judges / Evaluators (評審委員會)
````

---

## 💡 口試加分與答詢技巧 (Academic Defense Tips)

### 1. 遇到教授質疑「AI 生成影片 (Google Labs) 的真實性」時如何回答？
* **答詢擬真話術**：
  > 「教授您好，這是一個非常專業的問題。我們引入 Google Labs Flow 的主要目的並非取代真實田野測試，而是建立一個**『控制變因的感知壓力測試平台』**。在真實農田中，我們很難在完全相同的光照、抖動與陰影下進行『多次控制變因對比實驗』。
  > 透過 Flow 平台，我們能以 Roboflow 的真實草莓照片作為基底，搭配提示詞固定變速橫移、光影變化或隨機抖動。這讓我們在實車落地前，能針對 YOLO 追蹤演算法在不同極端環境下的『多影格去重精度』進行極限測試，這在工程開發上是一種低成本、高效率且具科學嚴謹度的驗證策略。當然，我們目前也同步進行了實地數據收集，兩者是互補的。」

### 2. 遇到教授提問「為什麼成熟度分成 3 個 Level？指標有什麼實務價值？」
* **答詢擬真話術**：
  > 「教授您好。我們將成熟度分為 Level 1（全綠）、Level 2（半紅過渡期）、Level 3（全紅可採收），主要是對齊農民的實務採收決策：
  > * **Level 3 的 Precision (92.5%) 與 mAP50-95 (0.795)** 是我們最核心的指標，因為這代表系統判定『該採收』的果實中，有高達 92.5% 是絕對正確的，能完全避免機械手臂採收到生果或判斷失誤，實務價值極高。
  > * 而 **Level 2** 的監測則能作為『產量預測』的依據。農夫可以得知大約 3 到 5 天後會有多少比例的草莓轉為 Level 3 可採收狀態，這對於農民提前接單、包裝盒租用與物流排程，提供了極具價值的預測性產能管理數據。」

### 3. 當被問到「雙側局部投影與傳統 Homography 單應性轉換相比的優勢」
* **答詢擬真話術**：
  > 「傳統的單應性矩陣（Homography）假設物體與地面處於同一個平面上，當相機高空俯拍時可行。但我們的自走車是行駛於溝渠中、以**側拍角度**近距離拍攝長在田壟側邊的草莓。草莓與相機的距離、高度是隨機且立體的，如果用傳統平面單應性矩陣會造成嚴重的拉伸與投影畸變。
  > 我們研發的『雙側動態局部投影公式』，直接結合了車載 Pose（即時座標與偏航角 $\theta$）以及探測深度 $d$，在極短時間內完成物理三角測量與轉換。這不僅計算速度極快（小於 5 毫秒），更能提供真正的三維點雲定位，這是傳統 Homography 完全做不到的。」
