import torch
import numpy as np
import cv2

class Image:
    """
    与你已有 Video 容器对齐的简易 Image 包装。
    内部只存 0-1 float32 HWC 的 numpy，外界需要 4D torch 时再 unsqueeze。
    """
    def __init__(self, np_hwc, width, height):
        self.np = np_hwc          # float32 HWC
        self.width = width
        self.height = height

    def numpy(self):
        return self.np            # 返回 HWC