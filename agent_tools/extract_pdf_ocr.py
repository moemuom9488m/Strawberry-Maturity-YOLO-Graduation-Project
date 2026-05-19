import os
import fitz
import easyocr
import io
import sys
from PIL import Image

def extract_pdf_with_ocr(pdf_path: str, output_txt_path: str = None, threshold_len: int = 15):
    """
    Reads a PDF file. For any page that contains little to no text, 
    renders the page to an image in memory and runs OCR (EasyOCR) to extract text.
    """
    if not os.path.exists(pdf_path):
        print(f"Error: File not found at {pdf_path}")
        return False
        
    print(f"Opening PDF: {pdf_path}")
    doc = fitz.open(pdf_path)
    total_pages = len(doc)
    print(f"Total pages: {total_pages}")
    
    # Pre-initialize OCR reader only if needed, but we'll initialize it here to be ready
    reader = None
    
    extracted_content = []
    
    for page_idx in range(total_pages):
        page = doc.load_page(page_idx)
        native_text = page.get_text().strip()
        
        # Clean native text to judge if it is empty/blank (excluding page numbers and whitespace)
        clean_native = "".join(native_text.split())
        # Strip simple numbers (like page numbers) to see if there is actual content
        is_page_num_only = clean_native.isdigit() and len(clean_native) <= 3
        
        needs_ocr = False
        if len(clean_native) < threshold_len or is_page_num_only:
            needs_ocr = True
            
        print(f"Page {page_idx + 1}/{total_pages}: Native Text length = {len(clean_native)}...", end="")
        
        page_content = f"--- PAGE {page_idx + 1} ---\n"
        
        if needs_ocr:
            print(" [Triggered OCR]...", end="")
            if reader is None:
                print(" (Initializing EasyOCR)", end="")
                reader = easyocr.Reader(['ch_tra', 'en'])
            
            # Render page to PNG bytes in memory
            pix = page.get_pixmap(dpi=150)
            img_data = pix.tobytes("png")
            
            try:
                ocr_results = reader.readtext(img_data)
                ocr_texts = [text for (bbox, text, prob) in ocr_results]
                
                # Check if we got any meaningful text
                if ocr_texts:
                    ocr_merged = "\n".join(ocr_texts)
                    print(f" OCR extracted {len(ocr_merged)} chars.")
                    page_content += f"[NATIVE TEXT (Short/None)]:\n{native_text}\n\n[OCR EXTRACTED TEXT]:\n{ocr_merged}\n"
                else:
                    print(" OCR found no text (blank slide or raw graphics).")
                    page_content += f"[NATIVE TEXT]:\n{native_text}\n\n[PAGE VISUAL STATE]: Image/Blank slide with no text detected.\n"
            except Exception as e:
                print(f" OCR failed: {e}")
                page_content += f"[NATIVE TEXT]:\n{native_text}\n\n[OCR ERROR]: {e}\n"
        else:
            print(" [Native Text Used]")
            page_content += f"{native_text}\n"
            
        extracted_content.append(page_content)
        
    full_output = "\n".join(extracted_content)
    
    if output_txt_path:
        os.makedirs(os.path.dirname(output_txt_path), exist_ok=True)
        with open(output_txt_path, "w", encoding="utf-8") as f:
            f.write(full_output)
        print(f"\nSuccessfully extracted all pages to: {output_txt_path}")
        
    return full_output

if __name__ == "__main__":
    default_pdf = r"d:\銘澄專區\畢業專題工作區\畢業專題口試.pdf"
    default_out = r"d:\銘澄專區\畢業專題工作區\scratch\pdf_content_ocr.txt"
    
    # Allow command line arguments
    pdf = sys.argv[1] if len(sys.argv) > 1 else default_pdf
    out = sys.argv[2] if len(sys.argv) > 2 else default_out
    
    extract_pdf_with_ocr(pdf, out)
