# -*- coding: utf-8 -*-
"""
草莓監測機器人畢業專題 - QR Code 自動生成工具
功能：將專題相關的線上 Canva 簡報、YouTube 模擬展示影片連結等，快速生成為高解析度 QR Code 圖片，以利黏貼於學術展示海報或投影片中。
"""

import os
import sys
import argparse
import qrcode

def generate_qr(data, output_path, box_size=10, border=4, fill_color="black", back_color="white", print_cli=True):
    """
    生成 QR Code 圖片並儲存，可選擇是否在終端機輸出 ASCII 預覽。
    """
    try:
        # 1. 初始化 QR Code 配置
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,  # 高容錯率 (30%)，利於海報列印折損時仍可掃描
            box_size=box_size,
            border=border,
        )
        
        # 2. 加入資料
        qr.add_data(data)
        qr.make(fit=True)
        
        # 3. 建立影像並儲存
        img = qr.make_image(fill_color=fill_color, back_color=back_color)
        
        # 確保輸出目錄存在
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
            
        img.save(output_path)
        print(f"[OK] QR Code 圖片已成功儲存至: {os.path.abspath(output_path)}")
        
        # 4. 在終端機輸出 ASCII 預覽（適用於 CLI 模式）
        if print_cli:
            try:
                print("\n[PREVIEW] 終端機 QR Code 預覽：")
                qr.print_ascii(invert=True)
            except Exception:
                # 若終端機不支援特殊字元，則不輸出預覽
                pass
            
    except Exception as e:
        print(f"[ERROR] 生成 QR Code 失敗: {e}", file=sys.stderr)

def main():
    parser = argparse.ArgumentParser(description="專題 QR Code 自動生成工具 (支持命令列參數與互動式模式)")
    parser.add_argument("-d", "--data", type=str, help="欲編碼的 URL 網址或文字內容")
    parser.add_argument("-o", "--output", type=str, help="輸出圖片路徑 (預設儲存於 qrcodes/ 目錄下)")
    parser.add_argument("--box", type=int, default=10, help="每個 QR 模組的像素大小 (預設: 10)")
    parser.add_argument("--border", type=int, default=4, help="邊界空白厚度 (預設: 4)")
    parser.add_argument("--no-preview", action="store_true", help="關閉終端機 ASCII 預覽")
    
    args = parser.parse_args()
    
    # 支援互動式輸入
    data = args.data
    if not data:
        print("🍓 歡迎使用草莓監測專題 QR Code 生成器 🍓")
        try:
            data = input("💬 請輸入要生成的 URL 網址或文字：").strip()
            if not data:
                print("[WARN] 輸入內容不能為空！")
                return
        except KeyboardInterrupt:
            print("\n[EXIT] 已取消操作。")
            return
            
    output_path = args.output
    if not output_path:
        # 自動根據輸入特徵生成預設檔名
        filename = "qrcode_output.png"
        if "youtu" in data:
            filename = "youtube_demo_qr.png"
        elif "canva" in data:
            filename = "canva_slides_qr.png"
            
        # 預設存放在專案目錄下的 qrcodes 資料夾中
        output_path = os.path.join("qrcodes", filename)
        
        # 在互動模式下詢問是否修改
        if not args.data:
            user_output = input(f"💬 請確認輸出路徑 (預設為 {output_path})，直接 Enter 確認，或輸入自訂路徑：").strip()
            if user_output:
                output_path = user_output

    # 執行生成
    generate_qr(
        data=data,
        output_path=output_path,
        box_size=args.box,
        border=args.border,
        print_cli=not args.no_preview
    )

if __name__ == "__main__":
    main()
