import pandas as pd
import os

results = []
folders = [
    ("Phase 1 Baseline (640)", r"d:\銘澄專區\畢業專題工作區\runs\detect\exp1a_yolo11s_baseline\results.csv"),
    ("Phase 2 - imgsz 640", r"d:\銘澄專區\畢業專題工作區\runs\detect\exp2a_1a_img640\results.csv"),
    ("Phase 2 - imgsz 800", r"d:\銘澄專區\畢業專題工作區\runs\detect\Strawberry_YOLOv11_4060ti\exp2b_1a_img800\results.csv"),
    ("Phase 2 - imgsz 1024", r"d:\銘澄專區\畢業專題工作區\runs\detect\exp2c_1a_img1024\results.csv")
]

for name, path in folders:
    if os.path.exists(path):
        try:
            df = pd.read_csv(path)
            df.columns = df.columns.str.strip()
            best_row = df.loc[df['metrics/mAP50(B)'].idxmax()]
            results.append({
                "Experiment": name,
                "Best mAP50": best_row['metrics/mAP50(B)'],
                "Best mAP50-95": best_row['metrics/mAP50-95(B)'],
                "Epoch": int(best_row['epoch'])
            })
        except Exception as e:
            print(f"Error reading {path}: {e}")

summary = pd.DataFrame(results)
print(summary.to_markdown(index=False))
