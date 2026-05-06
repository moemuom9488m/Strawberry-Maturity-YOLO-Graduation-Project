import torch
import torch.nn as nn

class ChannelAttention(nn.Module):
    def __init__(self, channels, reduction=16):
        super().__init__()
        self.avg_pool = nn.AdaptiveAvgPool2d(1)
        self.max_pool = nn.AdaptiveMaxPool2d(1)
        self.fc = nn.Sequential(
            nn.Conv2d(channels, channels // reduction, 1, bias=False),
            nn.ReLU(inplace=True),
            nn.Conv2d(channels // reduction, channels, 1, bias=False)
        )
        self.sigmoid = nn.Sigmoid()

    def forward(self, x):
        avg_out = self.fc(self.avg_pool(x))
        max_out = self.fc(self.max_pool(x))
        return self.sigmoid(avg_out + max_out)

class SpatialAttention(nn.Module):
    def __init__(self, kernel_size=7):
        super().__init__()
        self.conv = nn.Conv2d(2, 1, kernel_size, padding=kernel_size//2, bias=False)
        self.sigmoid = nn.Sigmoid()

    def forward(self, x):
        avg_out = torch.mean(x, dim=1, keepdim=True)
        max_out, _ = torch.max(x, dim=1, keepdim=True)
        out = torch.cat([avg_out, max_out], dim=1)
        out = self.conv(out)
        return self.sigmoid(out)

class CBAM(nn.Module):
    """Convolutional Block Attention Module"""
    def __init__(self, channels, reduction=16, kernel_size=7):
        super().__init__()
        self.ca = ChannelAttention(channels, reduction)
        self.sa = SpatialAttention(kernel_size)

    def forward(self, x):
        # 依照論文順序：先 Channel 再 Spatial
        x_out = x * self.ca(x)
        return x_out * self.sa(x_out)

def register_yolo_modules():
    """將自定義模組注入 Ultralytics 命名空間，確保解析 YAML 時能找到"""
    try:
        import ultralytics.nn.modules as modules
        import ultralytics.nn.tasks as tasks
        
        # 1. 注入到 nn.modules (大部分版本從這裡找)
        setattr(modules, 'CBAM', CBAM)
        
        # 2. 注入到 nn.tasks 的 globals (有些版本會從 globals 找)
        setattr(tasks, 'CBAM', CBAM)
        
        # 3. 注入到 block 分組 (保險起見)
        if hasattr(modules, 'block'):
            setattr(modules.block, 'CBAM', CBAM)
            
        # 4. 注入到 torch.nn (極少數情況下的回退方案)
        import torch.nn as nn
        setattr(nn, 'CBAM', CBAM)
        
        return True
    except Exception:
        return False

def find_latest_model_path(base_dir='runs/detect'):
    """自動搜尋最新的模型權重路徑 (支援 train*, exp* 與 best_weights/)"""
    import glob
    import os
    
    # 1. 優先搜尋 runs/detect/ 下的實驗資料夾
    search_patterns = [os.path.join(base_dir, 'train*'), os.path.join(base_dir, 'exp*')]
    dirs = []
    for pattern in search_patterns:
        dirs.extend(glob.glob(pattern))
    
    if dirs:
        # 過濾出含有 weights/best.pt 的資料夾
        valid_dirs = [d for d in dirs if os.path.exists(os.path.join(d, 'weights', 'best.pt'))]
        if valid_dirs:
            latest_dir = max(valid_dirs, key=os.path.getmtime)
            return os.path.join(latest_dir, 'weights', 'best.pt')

    # 2. 若 runs 下無結果，搜尋 best_weights/ 資料夾
    best_weights_dir = 'best_weights'
    if os.path.exists(best_weights_dir):
        weights = glob.glob(os.path.join(best_weights_dir, '*.pt'))
        if weights:
            # 傳回最新修改的權重
            return max(weights, key=os.path.getmtime)

    # 3. 最終備案
    return 'yolov11n.pt'
