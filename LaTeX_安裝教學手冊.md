# 🍓 LaTeX 環境安裝與編譯教學手冊 (LaTeX Installation Guide)

本手冊介紹如何在 Windows 系統上從零開始安裝 LaTeX 編譯環境（`pdflatex` 工具），並設定 VS Code 的 `LaTeX Workshop` 套件以利編譯學術三線表格。

---

## ❓ 1. pdflatex 需要安裝嗎？

**是的，需要安裝！** 
`pdflatex` 是 LaTeX 排版系統的核心編譯器。Windows 系統預設沒有內建 LaTeX 編譯器，因此若直接在終端機執行 `pdflatex yolo_hyperparameters_table.tex`，系統會回報「找不到指令」的錯誤。

要取得 `pdflatex`，必須安裝一個 **LaTeX 發行版（TeX Distribution）**。Windows 下最推薦的兩大發行版為：
1. **MiKTeX**（推薦，輕量級且支援隨用隨下載套件）
2. **TeX Live**（完整包，體積較大但套件最齊全）

---

## 🛠️ 2. Windows 環境安裝步驟 (MiKTeX 方案)

### 步驟 A：下載並安裝 MiKTeX
1. 前往 MiKTeX 官方網站下載頁面：[https://miktex.org/download](https://miktex.org/download)
2. 下載 Windows 專用的 Installer 檔案 (例如 `miktex-xxx-x64.exe`)。
3. 執行安裝程式：
   - 建議選擇 **"Install MiKTeX for only me"**（僅供當前使用者安裝）。
   - 設定 **"Preferred paper size"** 為 **A4**。
   - **重要設定**：在 **"Always install missing packages on the fly"** 中，建議選擇 **"Yes"**（這樣在編譯時若缺少套件如 `booktabs`，編譯器會自動下載，無須手動配置）。
4. 完成安裝。

### 步驟 B：設定環境變數 (Environment Variables)
通常 MiKTeX 安裝程式會自動將路徑加入 PATH。您可以開啟新的 PowerShell 或 CMD 視窗，輸入以下指令驗證：
```powershell
pdflatex --version
```
* **若有顯示版本資訊** (如 `pdfTeX, Version 3.141592653...`)，代表安裝成功！
* **若顯示找不到指令**，請手動將 MiKTeX 的 `bin` 目錄（一般在 `C:\Users\<您的使用者名稱>\AppData\Local\Programs\MiKTeX\miktex\bin\x64\`）加入 Windows 系統環境變數的 `Path` 中，並重啟終端機。

---

## 💻 3. VS Code 整合設定 (LaTeX Workshop 套件)

為了在 VS Code 裡實現「按儲存自動編譯成 PDF」，請依序完成以下配置：

1. **安裝 Extension**：
   - 在 VS Code 側邊欄的 Extensions 搜尋並安裝 **`LaTeX Workshop`**（由 James Yu 開發）。

2. **設定 User Settings (JSON)**：
   - 按下 `Ctrl + Shift + P`，輸入 `Preferences: Open User Settings (JSON)`，在設定檔中加入以下 LaTeX Workshop 的編譯鏈配置（以便在編譯時正確呼叫 `pdflatex`）：
   ```json
   {
       "latex-workshop.latex.tools": [
           {
               "name": "pdflatex",
               "command": "pdflatex",
               "args": [
                   "-synctex=1",
                   "-interaction=nonstopmode",
                   "-file-line-error",
                   "%DOC%"
               ],
               "env": {}
           }
       ],
       "latex-workshop.latex.recipes": [
           {
               "name": "pdflatex ➞ pdf",
               "tools": [
                   "pdflatex"
               ]
           }
       ],
       "latex-workshop.view.pdf.viewer": "tab"
   }
   ```

3. **如何編譯與預覽**：
   - 打開 [yolo_hyperparameters_table.tex](yolo_hyperparameters_table.tex)。
   - 使用快捷鍵 `Ctrl + Alt + B` 開始編譯。
   - 編譯成功後，點選 VS Code 右上角的「放大鏡/PDF 圖示」即可在編輯器分頁中預覽輸出的 `yolo_hyperparameters_table.pdf`。

---

## 📝 4. 常用編譯指令說明

如果您偏好使用終端機（PowerShell），可在專案根目錄下使用以下指令手動進行轉換：

* **標準編譯 (輸出為 PDF)**：
  ```powershell
  pdflatex -interaction=nonstopmode yolo_hyperparameters_table.tex
  ```
* **清理快取暫存檔 (編譯後會產生 `.aux`、`.log` 等臨時檔)**：
  如果您想維持工作目錄整潔，可在編譯完成後，執行以下指令清除快取：
  ```powershell
  Remove-Item yolo_hyperparameters_table.aux, yolo_hyperparameters_table.log -ErrorAction SilentlyContinue
  ```
  *(註：本專案已在 `.gitignore` 中設定自動忽略這些暫存檔，即使不清理也不會上傳至 GitHub)*
