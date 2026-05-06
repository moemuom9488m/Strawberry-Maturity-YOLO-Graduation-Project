@echo off
title YOLO 訓練啟動器 - Phase 2 Lite
echo 🚀 正在初始化環境...

:: 1. 啟動 Anaconda 環境 (指向你的 pytorch 環境)
call D:\Program\anaconda3\Scripts\activate.bat D:\Program\anaconda3\envs\pytorch

:: 2. 執行訓練腳本
echo 🟢 環境已就緒，開始執行 Phase 2 [1a] 實驗...
python train_phase2_1a_lite.py

:: 3. 結束後暫停，讓你看到結果
echo.
echo ✅ 訓練任務結束或已中斷。
pause
