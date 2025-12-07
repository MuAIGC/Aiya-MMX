# MMXTools/ComfyUI/custom_nodes/Aiya_mmx/nodes/MMX-nodes_image_stable.py
"""
💕 哎呀✦MMX 图像水印节点（内存安全版）
支持下拉选择 + 按钮刷新
"""
from __future__ import annotations
import torch
import numpy as np
from PIL import Image
import folder_paths
from pathlib import Path
from ..register import register_node

# 水印工具函数
_NODES_DIR = Path(__file__).parent
from ..watermark_util import pick_random_watermark, fit_watermark, apply_watermark_np


class MMXImageWatermarkStable:
    """内存安全图像水印，支持下拉选择+按钮刷新"""

    DESCRIPTION = (
        "💕 哎呀✦一键给图片加水印，内存安全，4K 无压力\n\n"
        "使用步骤：\n"
        "1. 把水印 PNG 放进 `Aiya_mmx/watermarks/` 目录\n"
        "2. 选择「位置」「透明度」「边距」→ 实时预览效果\n"
        "3. 点「🔄 刷新」可立即识别新放入的水印文件（需 F5 刷新网页）\n\n"
        "Tips：\n"
        "• 透明度 0.8 左右最自然；边距 0.02 ≈ 2%\n"
        "• 输出图像与原图分辨率完全一致，可继续后续流程\n"
        "• 支持批量（Batch），每张图会随机挑选同款水印"
    )

    @classmethod
    def INPUT_TYPES(cls):
        # 扫描水印池
        cls._watermark_files = list((_NODES_DIR.parent / "watermarks").glob("*.png"))
        if not cls._watermark_files:
            cls._watermark_files = list(_NODES_DIR.glob("watermark*.png"))
        if not cls._watermark_files:
            cls._watermark_files = [_NODES_DIR / "watermark.png"]
        cls._watermark_names = [p.stem for p in cls._watermark_files]

        return {
            "required": {
                "图像": ("IMAGE",),
                "位置": (["左上", "右上", "左下", "右下", "居中"], {"default": "左上"}),
                "透明度": ("FLOAT", {"default": 1.0, "min": 0.2, "max": 1.0, "step": 0.05}),
                "边距": ("FLOAT", {"default": 0.02, "min": 0.01, "max": 0.15, "step": 0.01}),
                "水印选择": (cls._watermark_names, {"default": cls._watermark_names[0] if cls._watermark_names else "default"}),
                "刷新水印": ("BOOLEAN", {"default": False, "label_on": "🔄 刷新", "label_off": "已刷新"}),
            }
        }

    RETURN_TYPES = ("IMAGE", "BOOLEAN")
    RETURN_NAMES = ("图像", "刷新回弹")
    FUNCTION = "apply"
    CATEGORY = "哎呀✦MMX/图像"

    def apply(self, 图像, 位置, 透明度, 边距, 水印选择, 刷新水印):
        # 上升沿触发刷新
        if 刷新水印:
            self.__class__._watermark_files = list((_NODES_DIR.parent / "watermarks").glob("*.png"))
            if not self.__class__._watermark_files:
                self.__class__._watermark_files = list(_NODES_DIR.glob("watermark*.png"))
            if not self.__class__._watermark_files:
                self.__class__._watermark_files = [_NODES_DIR / "watermark.png"]
            self.__class__._watermark_names = [p.stem for p in self.__class__._watermark_files]
            print(f"💕 哎呀✦已刷新水印列表，共 {len(self._watermark_names)} 个")
            print(f"💕 哎呀✦请 F5 刷新页面，下拉列表才会更新！")
            print("当前可选：", self._watermark_names)

        # 根据下拉名找文件
        try:
            idx = self._watermark_names.index(水印选择)
            wm_path = self._watermark_files[idx]
        except (ValueError, IndexError):
            wm_path = self._watermark_files[0]  # 兜底

        # torch → numpy → 水印 → torch
        img_np = (图像.cpu().numpy() * 255).astype(np.uint8)[0]
        wm_pil = Image.open(wm_path).convert("RGBA")
        wm_pil = fit_watermark(wm_pil, 图像.shape[2], 图像.shape[1])
        if 透明度 != 1.0:
            wm_pil = wm_pil.point(lambda p: int(p * 透明度) if p < 255 else 255)
        wm_np = np.array(wm_pil)
        img_np = apply_watermark_np(img_np, wm_np, 位置, 透明度, margin_ratio=边距)
        img_tensor = torch.from_numpy(img_np.astype(np.float32) / 255.0).unsqueeze(0)

        # 返回图像 + 强制 False（自动回弹）
        return (img_tensor, False)


# ---------- 注册 ----------
register_node(MMXImageWatermarkStable, "图像稳定水印")