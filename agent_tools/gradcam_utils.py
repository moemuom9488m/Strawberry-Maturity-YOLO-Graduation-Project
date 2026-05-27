"""
gradcam_utils.py
草莓成熟度 YOLO Grad-CAM 核心工具模組

提供 YOLOGradCAM 類別與 run_gradcam_visualization 函數，
可在任意 Jupyter Cell 或 Python 腳本中獨立 import 使用。

使用方式:
    from agent_tools.gradcam_utils import YOLOGradCAM, run_gradcam_visualization
"""

import os
import sys
import glob
import random
import numpy as np
import cv2
import matplotlib
import sys
# 若非在 Jupyter/IPython 環境，則使用 Agg 後端避免視窗卡住
if 'ipykernel' not in sys.modules:
    matplotlib.use("Agg")
import matplotlib.pyplot as plt

# 設定支援中文的字體（Windows: 微軟正黑體）
plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei', 'PingFang HK', 'SimHei', 'sans-serif']
plt.rcParams['axes.unicode_minus'] = False

import torch
import torch.nn.functional as F
from ultralytics import YOLO


# ==============================================================================
# 預設模型路徑與 device（可在 notebook 中用 gradcam_utils.MODEL_PATH = ... 覆蓋）
# ==============================================================================
MODEL_PATH = "runs/detect/exp1a_yolo11s_baseline/weights/best.pt"
device     = "cuda:0" if torch.cuda.is_available() else "cpu"

CLASSES_ZH = [
    "第一級 level_1 (未成熟/青綠色)",
    "第二級 level_2 (半熟/粉紅色)",
    "第三級 level_3 (完全成熟/鮮紅色)",
]


# ==============================================================================
# 輔助函數
# ==============================================================================

def cxcywh_to_xyxy(bboxes):
    x_c, y_c, w, h = bboxes[0], bboxes[1], bboxes[2], bboxes[3]
    x1 = x_c - w / 2
    y1 = y_c - h / 2
    x2 = x_c + w / 2
    y2 = y_c + h / 2
    return torch.stack([x1, y1, x2, y2], dim=0)


def calculate_iou(box1, box2):
    x1 = torch.max(box1[0], box2[0])
    y1 = torch.max(box1[1], box2[1])
    x2 = torch.min(box1[2], box2[2])
    y2 = torch.min(box1[3], box2[3])
    intersection = torch.clamp(x2 - x1, min=0) * torch.clamp(y2 - y1, min=0)
    area1 = (box1[2] - box1[0]) * (box1[3] - box1[1])
    area2 = (box2[2] - box2[0]) * (box2[3] - box2[1])
    union = area1 + area2 - intersection
    return intersection / torch.clamp(union, min=1e-6)


# ==============================================================================
# YOLOGradCAM 類別
# ==============================================================================

class YOLOGradCAM:
    """
    針對 YOLOv8/v11 架構實作多尺度 (Multi-scale) 與實體級 (Instance-level) Grad-CAM。
    """

    def __init__(self, model):
        self.model = model
        # YOLOv11s 的 Detect 頭在第 23 層
        self.detect = self.model.model[23]

        # 三個偵測尺度的目標層（128 channels）
        self.target_layers = [
            self.detect.cv3[0][1],  # stride 8  (小物件)
            self.detect.cv3[1][1],  # stride 16 (中物件)
            self.detect.cv3[2][1],  # stride 32 (大物件)
        ]

        self.activations = [None, None, None]
        self.gradients   = [None, None, None]
        self.hooks = []

        for i, layer in enumerate(self.target_layers):
            self.hooks.append(layer.register_forward_hook(self._make_save_activation(i)))
            self.hooks.append(layer.register_full_backward_hook(self._make_save_gradient(i)))

    def _make_save_activation(self, idx):
        def save_activation(model, input, output):
            self.activations[idx] = output
        return save_activation

    def _make_save_gradient(self, idx):
        def save_gradient(model, grad_input, grad_output):
            self.gradients[idx] = grad_output[0]
        return save_gradient

    def __call__(self, x, class_idx, instance_bbox=None, conf_threshold=0.25, iou_threshold=0.5):
        """
        計算並回傳 Grad-CAM 熱力圖。
        x            : 前處理後的 Tensor，shape [1, 3, H, W]
        class_idx    : 目標類別索引 (0: level_1, 1: level_2, 2: level_3)
        instance_bbox: 在 800×800 座標系下的 [x1,y1,x2,y2]（實體模式）；None 為全圖模式
        """
        self.model.zero_grad()
        self.gradients = [None, None, None]

        with torch.set_grad_enabled(True):
            outputs = self.model(x)
        preds = outputs[0]  # shape: [1, 7, 13125]

        class_scores = preds[0, 4 + class_idx, :]

        if instance_bbox is not None:
            anchor_bboxes_xyxy = cxcywh_to_xyxy(preds[0, :4, :])
            target_box_tensor  = torch.tensor(instance_bbox, dtype=torch.float32, device=preds.device)
            ious = calculate_iou(anchor_bboxes_xyxy, target_box_tensor)

            mask = (ious >= iou_threshold) & (class_scores > conf_threshold)
            if mask.sum().item() > 0:
                score = class_scores[mask].sum()
            else:
                best_idx = ious.argmax().item()
                score = class_scores[best_idx]
            score.backward(retain_graph=True)
        else:
            mask = class_scores > conf_threshold
            if mask.sum() > 0:
                score = class_scores[mask].sum()
                score.backward(retain_graph=True)
            else:
                return None, 0.0

        # 多尺度 CAM 融合
        h_target, w_target = x.shape[2], x.shape[3]
        cam_total = torch.zeros((h_target, w_target), device=x.device)

        for i in range(3):
            act  = self.activations[i]
            grad = self.gradients[i]
            if grad is not None and act is not None:
                weights     = torch.mean(grad, dim=(2, 3), keepdim=True)
                cam         = torch.sum(weights * act, dim=1, keepdim=True)
                cam         = torch.clamp(cam, min=0)
                cam_resized = F.interpolate(cam, size=(h_target, w_target), mode="bilinear", align_corners=False)
                cam_total  += cam_resized[0, 0]

        cam_np = cam_total.cpu().detach().numpy()
        if cam_np.max() > 0:
            cam_np = cam_np / cam_np.max()

        return cam_np, score.item()

    def release(self):
        for hook in self.hooks:
            hook.remove()
        print("🔓 hooks 已成功釋放。")


# ==============================================================================
# run_gradcam_visualization — 完整視覺化流程
# ==============================================================================

def run_gradcam_visualization(
    image_path=None,
    target_instance_idx=None,
    conf_threshold=0.25,
    iou_threshold=0.5,
    model_path=None,
    device_id=None,
):
    """
    對單張草莓影像執行 Grad-CAM 視覺化，並將結果儲存至:
        evaluation_results/<model_dir_name>/gradcam_<model>_<img>_<mode>_conf<n>_iou<n>.png

    參數
    ----
    image_path          : 影像路徑；None 時從 valid/images 隨機挑選
    target_instance_idx : 整數 → 單一實體模式；None → 全圖模式
    conf_threshold      : 置信度門檻（預設 0.25）
    iou_threshold       : IoU 匹配門檻（預設 0.50）
    model_path          : 覆蓋預設 MODEL_PATH
    device_id           : 覆蓋預設 device
    """
    # 允許從函數參數覆蓋全域設定
    _model_path = model_path if model_path else MODEL_PATH
    _device     = device_id  if device_id  else device

    if image_path is None:
        valid_images = glob.glob("strawberry-maturity-yolo-graduate-1/valid/images/*.jpg")
        if not valid_images:
            print("❌ 找不到 valid/images 目錄或裡面沒有 JPG 圖片！")
            return
        image_path = random.choice(valid_images)

    print(f"📸 處理影像路徑: {image_path}")

    img_bgr = cv2.imread(image_path)
    if img_bgr is None:
        print(f"❌ 無法讀取影像：{image_path}")
        return

    h_org, w_org, _ = img_bgr.shape
    img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)

    img_resized = cv2.resize(img_rgb, (800, 800))
    x_tensor = torch.from_numpy(img_resized).permute(2, 0, 1).float() / 255.0
    x_tensor = x_tensor.unsqueeze(0).to(_device)
    x_tensor.requires_grad = True

    detector = YOLO(_model_path)
    results  = detector.predict(image_path, conf=conf_threshold, imgsz=800, verbose=False)[0]

    temp_model = YOLO(_model_path)
    py_model   = temp_model.model.to(_device)
    py_model.eval()

    grad_cam = YOLOGradCAM(py_model)

    # --- 判斷模式 ---
    if target_instance_idx is not None:
        if len(results.boxes) == 0:
            print("⚠️ 影像中沒有偵測到任何目標，自動切換至全圖模式。")
            target_instance_idx = None
        elif target_instance_idx >= len(results.boxes):
            print(f"⚠️ 指定實體索引 [{target_instance_idx}] 溢位，自動切換至實體 [0]。")
            target_instance_idx = 0

    if target_instance_idx is not None:
        # ---- 實體級模式 (2x2) ----
        fig, axes = plt.subplots(2, 2, figsize=(14, 12))
        axes = axes.ravel()

        box     = results.boxes[target_instance_idx]
        cls_idx = int(box.cls.item())
        xyxy    = box.xyxy[0].cpu().numpy()

        # 子圖 0：原圖 + 所有框
        img_annotate = img_rgb.copy()
        for j, b in enumerate(results.boxes):
            b_xyxy  = b.xyxy[0].cpu().numpy().astype(int)
            b_cls   = int(b.cls.item())
            b_conf  = b.conf.item()
            color     = (0, 255, 0) if j == target_instance_idx else (255, 0, 0)
            thickness = 3           if j == target_instance_idx else 1
            cv2.rectangle(img_annotate, (b_xyxy[0], b_xyxy[1]), (b_xyxy[2], b_xyxy[3]), color, thickness)
            cv2.putText(img_annotate, f"[{j}] L{b_cls+1} {b_conf:.2f}",
                        (b_xyxy[0], b_xyxy[1]-10), cv2.FONT_HERSHEY_SIMPLEX, 0.65, color, 2)

        axes[0].imshow(img_annotate)
        axes[0].set_title(f"原始影像 (綠框=目標實體[{target_instance_idx}]，紅框=其他)", fontsize=12, weight="bold")
        axes[0].axis("off")

        # 子圖 1：實體級 Grad-CAM
        xyxy_800 = [
            xyxy[0] * 800.0 / w_org,
            xyxy[1] * 800.0 / h_org,
            xyxy[2] * 800.0 / w_org,
            xyxy[3] * 800.0 / h_org,
        ]
        cam_inst, score_inst = grad_cam(x_tensor, cls_idx, instance_bbox=xyxy_800,
                                        conf_threshold=conf_threshold, iou_threshold=iou_threshold)
        if cam_inst is not None:
            heatmap = cv2.applyColorMap(np.uint8(255 * cv2.resize(cam_inst, (w_org, h_org))), cv2.COLORMAP_JET)
            heatmap = cv2.cvtColor(heatmap, cv2.COLOR_BGR2RGB)
            overlay = cv2.addWeighted(img_rgb, 0.6, heatmap, 0.4, 0)
            cv2.rectangle(overlay, (int(xyxy[0]), int(xyxy[1])), (int(xyxy[2]), int(xyxy[3])), (0, 255, 0), 3)
            axes[1].imshow(overlay)
            axes[1].set_title(f"實體 [{target_instance_idx}] ({CLASSES_ZH[cls_idx]}) 實體級 Grad-CAM\n"
                              f"(對應激活 Score: {score_inst:.4f})", fontsize=12, weight="bold")
        else:
            axes[1].imshow(img_rgb)
            axes[1].set_title(f"實體 [{target_instance_idx}] Grad-CAM (無激活)", fontsize=12, color="gray")
        axes[1].axis("off")

        # 子圖 2：同類別全圖 Grad-CAM
        cam_global, score_global = grad_cam(x_tensor, cls_idx, instance_bbox=None, conf_threshold=conf_threshold)
        if cam_global is not None:
            heatmap = cv2.applyColorMap(np.uint8(255 * cv2.resize(cam_global, (w_org, h_org))), cv2.COLORMAP_JET)
            heatmap = cv2.cvtColor(heatmap, cv2.COLOR_BGR2RGB)
            overlay = cv2.addWeighted(img_rgb, 0.6, heatmap, 0.4, 0)
            cv2.rectangle(overlay, (int(xyxy[0]), int(xyxy[1])), (int(xyxy[2]), int(xyxy[3])), (255, 255, 0), 2)
            axes[2].imshow(overlay)
            axes[2].set_title(f"同類別全域關注 (Global CAM)\n(全域激活 Score: {score_global:.4f})", fontsize=12, weight="bold")
        else:
            axes[2].imshow(img_rgb)
            axes[2].set_title("全域關注圖 (無激活)", fontsize=12, color="gray")
        axes[2].axis("off")

        # 子圖 3：其他類別 Grad-CAM
        other_cls = (cls_idx + 1) % 3
        cam_other, score_other = grad_cam(x_tensor, other_cls, instance_bbox=None, conf_threshold=conf_threshold)
        if cam_other is not None:
            heatmap = cv2.applyColorMap(np.uint8(255 * cv2.resize(cam_other, (w_org, h_org))), cv2.COLORMAP_JET)
            heatmap = cv2.cvtColor(heatmap, cv2.COLOR_BGR2RGB)
            overlay = cv2.addWeighted(img_rgb, 0.6, heatmap, 0.4, 0)
            axes[3].imshow(overlay)
            axes[3].set_title(f"對比類別關注：{CLASSES_ZH[other_cls]}\n(全域激活 Score: {score_other:.4f})", fontsize=12, weight="bold")
        else:
            gray = cv2.merge([cv2.cvtColor(img_rgb, cv2.COLOR_RGB2GRAY)] * 3)
            faded = cv2.addWeighted(img_rgb, 0.3, gray, 0.7, 0)
            axes[3].imshow(faded)
            axes[3].set_title(f"對比類別 {CLASSES_ZH[other_cls]} (無此類草莓)", fontsize=12, color="gray")
            axes[3].text(w_org // 2, h_org // 2, "此類別無激活", color="yellow", fontsize=12, weight="bold",
                         horizontalalignment="center", verticalalignment="center",
                         bbox=dict(facecolor="black", alpha=0.6, boxstyle="round,pad=0.4"))
        axes[3].axis("off")

        save_mode_str = f"instance{target_instance_idx}"

    else:
        # ---- 全圖模式 (2x2) ----
        fig, axes = plt.subplots(2, 2, figsize=(14, 12))
        axes = axes.ravel()

        axes[0].imshow(img_rgb)
        axes[0].set_title(f"原始影像 ({os.path.basename(image_path)})", fontsize=12, weight="bold")
        axes[0].axis("off")

        for i, cls_name in enumerate(CLASSES_ZH):
            cam, score = grad_cam(x_tensor, i, conf_threshold=conf_threshold)
            if cam is not None:
                heatmap = cv2.applyColorMap(np.uint8(255 * cv2.resize(cam, (w_org, h_org))), cv2.COLORMAP_JET)
                heatmap = cv2.cvtColor(heatmap, cv2.COLOR_BGR2RGB)
                overlay = cv2.addWeighted(img_rgb, 0.6, heatmap, 0.4, 0)
                axes[i+1].imshow(overlay)
                axes[i+1].set_title(f"{cls_name}\n(激活強度 Score: {score:.4f})", fontsize=12, pad=10, weight="bold")
            else:
                gray = cv2.merge([cv2.cvtColor(img_rgb, cv2.COLOR_RGB2GRAY)] * 3)
                faded = cv2.addWeighted(img_rgb, 0.3, gray, 0.7, 0)
                axes[i+1].imshow(faded)
                axes[i+1].set_title(f"{cls_name}\n(影像中無此類草莓)", fontsize=12, pad=10, color="gray", style="italic")
                axes[i+1].text(w_org // 2, h_org // 2, "此類別無激活",
                               color="yellow", fontsize=14, weight="bold",
                               horizontalalignment="center", verticalalignment="center",
                               bbox=dict(facecolor="black", alpha=0.6, boxstyle="round,pad=0.5"))
            axes[i+1].axis("off")

        save_mode_str = "global"

    plt.tight_layout()

    # --- 儲存：模型子資料夾 + 參數標籤 ---
    model_dir_name = os.path.basename(os.path.dirname(os.path.dirname(_model_path)))
    save_dir = os.path.join("evaluation_results", model_dir_name)
    os.makedirs(save_dir, exist_ok=True)

    img_basename = os.path.splitext(os.path.basename(image_path))[0]
    # 檔案名稱只保留編號 (例如 1008_jpg.rf... -> 1008)
    if "_jpg" in img_basename:
        img_basename = img_basename.split("_jpg")[0]
        
    conf_tag     = f"conf{int(conf_threshold * 100):02d}"
    iou_tag      = f"iou{int(iou_threshold  * 100):02d}"
    save_path    = os.path.join(
        save_dir,
        f"gradcam_{model_dir_name}_{img_basename}_{save_mode_str}_{conf_tag}_{iou_tag}.png",
    )

    plt.savefig(save_path, dpi=150, bbox_inches="tight")
    print(f"💾 Grad-CAM 特徵圖已成功儲存至: {save_path}")
    
    # 避免在 Agg 後端觸發 non-interactive 警告
    if matplotlib.get_backend().lower() != 'agg':
        plt.show()
    else:
        plt.close()

    grad_cam.release()
