# ~/ComfyUI/custom_nodes/Aiya_mmx/nodes/img_tools.py
from __future__ import annotations
import os
import re
import json
import uuid
import time
from pathlib import Path
from typing import List, Optional

import numpy as np
import torch
from PIL import Image

import folder_paths
from ..register import register_node

# --------------------------------------------------
#  1. 通用批量收图器  ImageBatchCollector_mmx
# --------------------------------------------------
class ImageBatchCollector_mmx:
    MAX_SLOTS = 9
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("images",)
    FUNCTION = "collect"
    CATEGORY = "utils/batch"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {},
            "optional": {f"image_{i}": ("IMAGE",) for i in range(1, cls.MAX_SLOTS + 1)}
        }

    def collect(self, **kwargs):
        images = [kwargs[f"image_{i}"] for i in range(1, self.MAX_SLOTS + 1) if kwargs.get(f"image_{i}") is not None]
        if not images:
            raise RuntimeError("ImageBatchCollector_mmx: 未收到任何图片输入！")
        base_h, base_w = images[0].shape[1], images[0].shape[2]
        resized = []
        for img in images:
            if img.shape[1] != base_h or img.shape[2] != base_w:
                img = torch.nn.functional.interpolate(img, size=(base_h, base_w), mode="bilinear", align_corners=False)
            resized.append(img)
        batch = torch.cat(resized, dim=0)
        return (batch,)

# --------------------------------------------------
#  2. 一键保存 JPG  save2JPG_mmx
# --------------------------------------------------
class save2JPG_mmx:
    def __init__(self):
        self.output_dir = folder_paths.get_output_directory()
        self.type = "output"
        self.prefix_append = ""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "images": ("IMAGE",),
                "filename_prefix": ("STRING", {"default": "ComfyUI"}),
                "quality": ("INT", {"default": 95, "min": 1, "max": 100, "step": 1, "display": "slider"}),
                "optimize": ("BOOLEAN", {"default": True}),
                "progressive": ("BOOLEAN", {"default": False}),
                "save_prompt_as_txt": ("BOOLEAN", {"default": True}),
            },
            "hidden": {"prompt": "PROMPT", "extra_pnginfo": "EXTRA_PNGINFO"}
        }

    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("prompt_text", "jpg_path")
    FUNCTION = "save_images"
    OUTPUT_NODE = True
    CATEGORY = "哎呀✦MMX/图像"

    def save_images(self, images, filename_prefix="ComfyUI", quality=95, optimize=True, progressive=False,
                    save_prompt_as_txt=True, prompt=None, extra_pnginfo=None):
        from ..date_variable import replace_date_vars
        filename_prefix = replace_date_vars(filename_prefix)
        os.makedirs(self.output_dir, exist_ok=True)
        filename_prefix += self.prefix_append
        full_output_folder, filename, counter, subfolder, filename_prefix = folder_paths.get_save_image_path(
            filename_prefix, self.output_dir, images[0].shape[1], images[0].shape[0])
        prompt_text = self._extract_prompt_text(prompt)
        saved_paths, results = [], []
        for image in images:
            i = 255. * image.cpu().numpy()
            img = Image.fromarray(np.clip(i, 0, 255).astype(np.uint8))
            file = f"{filename}_{counter:05}_.jpg"
            save_path = os.path.join(full_output_folder, file)
            img.save(save_path, format='JPEG', quality=quality, optimize=optimize, progressive=progressive)
            saved_paths.append(save_path)
            if save_prompt_as_txt:
                with open(save_path.replace(".jpg", "_prompt.txt"), "w", encoding="utf-8") as f:
                    f.write(prompt_text)
            results.append({"filename": file, "subfolder": subfolder, "type": self.type})
            counter += 1
        return {"ui": {"images": results}, "result": (prompt_text, saved_paths[0] if saved_paths else "")}

    def _extract_prompt_text(self, prompt):
        if not isinstance(prompt, dict):
            return ""
        texts = []
        for node in prompt.values():
            if isinstance(node, dict) and isinstance(node.get("inputs"), dict):
                t = node["inputs"].get("prompt")
                if isinstance(t, str) and t.strip():
                    texts.append(t.strip())
        return "\n".join(texts)

# --------------------------------------------------
#  3. 路径读图  LoadImageFromPath_mmx
# --------------------------------------------------
CACHE_DIR = Path(folder_paths.get_output_directory()) / "Aiya/Aiya_path"

class LoadImageFromPath_mmx:
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)
    FUNCTION = "load"
    CATEGORY = "哎呀✦MMX/图像"
    OUTPUT_NODE = True

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "path": ("STRING", {"default": "", "multiline": False}),
                "cache_name": ("STRING", {"default": "default", "multiline": False}),
            },
            "optional": {"force_run": ("BOOLEAN", {"default": True})}
        }

    def load(self, path, cache_name, force_run=True):
        from ..date_variable import replace_date_vars
        path = path.strip()
        cache_name = cache_name.strip() or "default"
        path_file = CACHE_DIR / f"{cache_name}.txt"

        if path:
            path = replace_date_vars(path)
            CACHE_DIR.mkdir(parents=True, exist_ok=True)
            path_file.write_text(path, encoding="utf-8")

        if path_file.exists():
            path = path_file.read_text(encoding="utf-8").strip()
        if not path:
            print(f"[LoadImageFromPath_mmx] 无有效路径，返回空图 | cache={cache_name}")
            empty = torch.zeros((1, 1, 1, 3), dtype=torch.float32)
            return (empty,)

        path = Path(path).expanduser().resolve()
        if not path.exists():
            raise FileNotFoundError(f"LoadImageFromPath_mmx: 文件不存在 → {path}")
        img = Image.open(path).convert("RGB")
        img_np = np.array(img).astype(np.float32) / 255.0
        rgb = torch.from_numpy(img_np).unsqueeze(0)
        return (rgb,)

# --------------------------------------------------
#  4. 图像等分切割  ImageSplitGrid_mmx
# --------------------------------------------------
class ImageSplitGrid_mmx:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "width_split": ("INT", {"default": 2, "min": 1, "max": 3, "step": 1, "display": "number", "label": "宽度切分数"}),
                "height_split": ("INT", {"default": 2, "min": 1, "max": 3, "step": 1, "display": "number", "label": "高度切分数"}),
            }
        }

    RETURN_TYPES = tuple(["IMAGE"] * 9)
    RETURN_NAMES = tuple([f"image_{i}" for i in range(1, 10)])
    FUNCTION = "split_image"
    CATEGORY = "哎呀✦MMX/图像"

    def split_image(self, image, width_split, height_split):
        if width_split < 1 or width_split > 3 or height_split < 1 or height_split > 3:
            raise ValueError("ImageSplitGrid_mmx: 切分数必须在 1-3 之间")
        total_parts = width_split * height_split
        if total_parts > 9:
            raise ValueError(f"ImageSplitGrid_mmx: 总切割数 {total_parts} 超过最大值9")

        if len(image.shape) == 4:
            if image.shape[0] != 1:
                raise ValueError("ImageSplitGrid_mmx: 暂不支持 batch > 1 的输入")
            image = image[0]
        height, width, channels = image.shape

        new_width = (width // width_split) * width_split
        new_height = (height // height_split) * height_split
        if new_width != width or new_height != height:
            image = image.permute(2, 0, 1).unsqueeze(0)
            image = torch.nn.functional.interpolate(image, size=(new_height, new_width), mode='bilinear', align_corners=False)
            image = image.squeeze(0).permute(1, 2, 0)

        part_w = new_width // width_split
        part_h = new_height // height_split
        parts = []
        for i in range(height_split):
            for j in range(width_split):
                sy, ey = i * part_h, (i + 1) * part_h
                sx, ex = j * part_w, (j + 1) * part_w
                parts.append(image[sy:ey, sx:ex, :].unsqueeze(0))

        result = []
        for i in range(9):
            result.append(parts[i] if i < len(parts) else
                          torch.zeros((1, part_h, part_w, channels), dtype=image.dtype, device=image.device))
        return tuple(result)

# --------------------------------------------------
#  5. 批量目录图片读取器  ImageFolderLoader_mmx
# --------------------------------------------------
class ImageFolderLoader_mmx:
    """
    💕 哎呀✦MMX/批量图片目录读取器
    
    【功能说明】
    • 自动扫描指定目录的所有图片，按文件名排序后顺序读取
    • 支持批量输出（最多9张）和单张输出
    • 读取进度自动记忆，每次运行前进指定步数
    • 跨平台支持：Windows路径(D:\img)和Linux路径(/mnt/img)均可
    
    【批次输出模式】
    • 保持原始比例：使用黑边填充(Letterbox)而非拉伸，避免图像变形
    • 统一尺寸：以批次第一张图为基准尺寸，其余图片等比缩放后居中填充
    """
    
    DESCRIPTION = (
        "💕 哎呀✦MMX —— 批量目录图片读取器 | "
        "Letterbox无拉伸批次输出 | 支持Win/Linux路径 | 进度自动记忆"
    )
    
    _path_cache: dict = {}
    _state_cache: dict = {}
    MAX_BATCH = 9
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "directory": ("STRING", { 
                    "default": "", 
                    "placeholder": "D:\\Photos\\input 或 /mnt/data/images",
                    "tooltip": "📁 图片所在目录的完整路径\n"
                               "• Windows示例: D:\\\\Photos\\\\input 或 D:/Photos/input\n"
                               "• Linux示例: /mnt/data/images\n"
                               "• 支持使用 ~ 表示用户主目录"
                }),
                "batch_count": ("INT", {
                    "default": 1, 
                    "min": 1, 
                    "max": cls.MAX_BATCH, 
                    "step": 1,
                    "tooltip": "📦 每次运行输出的图片数量（1-9张）\n"
                               "• 设为1：单张顺序读取模式\n"
                               "• 设为4：每次输出4张图组成的批次\n"
                               "批次内所有图将统一尺寸，但保持原始比例（黑边填充）"
                }),
                "step": ("INT", {
                    "default": 1, 
                    "min": 1, 
                    "max": 100, 
                    "step": 1,
                    "tooltip": "🚶 每次运行后索引前进的步数\n"
                               "• step=1：顺序连续读取（1,2,3...）\n"
                               "• step=2：隔一张读取（1,3,5...），产生重叠或跳跃效果\n"
                               "注意：step可以大于batch_count实现跳跃，也可以小于实现重叠"
                }),
                "reset": ("BOOLEAN", {
                    "default": False, 
                    "label_on": "🔄 重置", 
                    "label_off": "⏩ 继续",
                    "tooltip": "• 勾选：下次运行回到第一张图（索引归零）\n"
                               "• 不勾选：从上次记住的位置继续读取"
                }),
                "loop": ("BOOLEAN", {
                    "default": True, 
                    "label_on": "🔁 循环", 
                    "label_off": "⏹️ 停止",
                    "tooltip": "• 循环开启：读到末尾后回到开头继续\n"
                               "• 循环关闭：读到末尾后停留在最后一张"
                }),
            },
            "optional": {
                "file_pattern": ("STRING", {
                    "default": "*", 
                    "placeholder": "通配符如 *.jpg 或 frame_*.png",
                    "tooltip": "🔍 文件名过滤通配符（glob模式）\n"
                               "• * 或 *.*：加载所有图片（默认）\n"
                               "• *.jpg：只加载jpg格式\n"
                               "• frame_*.png：只加载frame_前缀的png\n"
                               "• img_??.jpg：加载img_01.jpg, img_02.jpg等"
                }),
            },
            "hidden": {"unique_id": "UNIQUE_ID"}
        }

    RETURN_TYPES = ("IMAGE", "IMAGE", "STRING", "INT", "INT")
    RETURN_NAMES = ("single_image", "batch", "current_file", "current_index", "total_files")
    FUNCTION = "load_images"
    CATEGORY = "哎呀✦MMX/图像/批量"

    @classmethod
    def IS_CHANGED(cls, **kwargs):
        """强制每次重新执行，避免ComfyUI缓存导致不读取下一张"""
        return time.time()

    def collect_images_letterbox(self, tensors: List[torch.Tensor]) -> torch.Tensor:
        """
        将多张图片合并为批次，使用Letterbox（黑边填充）保持原始比例
        避免直接拉伸导致的图像变形
        """
        if not tensors:
            raise RuntimeError("ImageFolderLoader_mmx: 没有可合并的图片")
        
        target_h, target_w = tensors[0].shape[1], tensors[0].shape[2]
        target_c = tensors[0].shape[3]
        
        processed = []
        for i, img in enumerate(tensors):
            _, h, w, c = img.shape
            
            if h == target_h and w == target_w:
                processed.append(img)
                continue
            
            scale = min(target_h / h, target_w / w)
            new_h = int(h * scale)
            new_w = int(w * scale)
            
            img_ncwh = img.permute(0, 3, 1, 2)
            img_resized = torch.nn.functional.interpolate(
                img_ncwh,
                size=(new_h, new_w), 
                mode="bilinear", 
                align_corners=False
            )
            
            letterbox = torch.zeros((1, target_c, target_h, target_w), dtype=img.dtype)
            pad_top = (target_h - new_h) // 2
            pad_left = (target_w - new_w) // 2
            letterbox[:, :, pad_top:pad_top+new_h, pad_left:pad_left+new_w] = img_resized
            img_final = letterbox.permute(0, 2, 3, 1)
            processed.append(img_final)
            
            if i > 0:
                print(f"[ImageFolderLoader_mmx] 图{i+1}尺寸调整: {h}x{w} -> 保持比例缩放至 {new_h}x{new_w} "
                      f"并填充至 {target_h}x{target_w}")
        
        batch = torch.cat(processed, dim=0)
        return batch

    def load_image_safe(self, path: Path) -> Optional[torch.Tensor]:
        """安全加载单张图片并转为 tensor [1,H,W,C]"""
        try:
            img = Image.open(path)
            if img.mode == 'RGBA':
                background = Image.new('RGB', img.size, (0, 0, 0))
                background.paste(img, mask=img.split()[3])
                img = background
            elif img.mode != 'RGB':
                img = img.convert('RGB')
            
            img_array = np.array(img).astype(np.float32) / 255.0
            tensor = torch.from_numpy(img_array).unsqueeze(0)
            return tensor
        except Exception as e:
            print(f"[ImageFolderLoader_mmx] 加载失败 {path}: {e}")
            return None

    def get_image_files(self, directory: str, pattern: str) -> List[Path]:
        """获取目录下所有图片文件，支持缓存和自然排序"""
        dir_path = Path(directory).expanduser().resolve()
        cache_key = f"{dir_path}_{pattern}"
        
        if cache_key in self._path_cache:
            return self._path_cache[cache_key]
        
        if not dir_path.exists():
            raise FileNotFoundError(f"目录不存在: {dir_path}")
        if not dir_path.is_dir():
            raise NotADirectoryError(f"路径不是目录: {dir_path}")
        
        valid_exts = {'.jpg', '.jpeg', '.png', '.webp', '.bmp', '.tiff', '.gif'}
        
        if pattern in ("", "*", "*.*"):
            files = [f for f in dir_path.iterdir() if f.is_file() and f.suffix.lower() in valid_exts]
        else:
            files = list(dir_path.glob(pattern))
            files = [f for f in files if f.is_file() and f.suffix.lower() in valid_exts]
        
        def natural_key(p: Path):
            return [int(s) if s.isdigit() else s.lower() for s in re.split(r'(\d+)', p.name)]
        
        files.sort(key=natural_key)
        
        if not files:
            raise RuntimeError(f"目录中未找到图片文件: {dir_path} (pattern: {pattern})")
        
        self._path_cache[cache_key] = files
        print(f"[ImageFolderLoader_mmx] 📂 扫描到 {len(files)} 张图片: {dir_path}")
        if len(files) <= 5:
            print(f"[ImageFolderLoader_mmx]   列表: {[f.name for f in files]}")
        return files

    def load_images(self, directory: str, batch_count: int, step: int, 
                   reset: bool, loop: bool, file_pattern: str = "*", 
                   unique_id: str = None):
        if not directory.strip():
            raise ValueError("directory 不能为空")
        
        state_key = str(unique_id) if unique_id else "default"
        image_files = self.get_image_files(directory, file_pattern)
        total = len(image_files)
        
        if reset or state_key not in self._state_cache:
            current_idx = 0
            print(f"[ImageFolderLoader_mmx] [{state_key}] 🔄 重置索引 | 共 {total} 张")
        else:
            current_idx = self._state_cache[state_key]
            if current_idx >= total:
                current_idx = 0 if loop else total - 1
        
        if current_idx >= total:
            if loop:
                current_idx = 0
        
        selected_files = []
        indices = []
        for i in range(batch_count):
            idx = current_idx + i
            if idx >= total:
                if loop:
                    idx = idx % total
                else:
                    break
            indices.append(idx)
            selected_files.append(image_files[idx])
        
        if not selected_files:
            raise RuntimeError("没有可选的图片，请检查索引设置和循环选项")
        
        tensors = []
        for fp in selected_files:
            t = self.load_image_safe(fp)
            if t is not None:
                tensors.append(t)
        
        if not tensors:
            raise RuntimeError("本次批次中所有图片加载失败")
        
        single_image = tensors[0]
        
        if len(tensors) == 1:
            batch = tensors[0]
        else:
            batch = self.collect_images_letterbox(tensors)
        
        next_idx = current_idx + step
        if loop:
            next_idx = next_idx % total
        else:
            next_idx = min(next_idx, total - 1)
        
        self._state_cache[state_key] = next_idx
        current_filename = selected_files[0].name if selected_files else ""
        
        print(f"[ImageFolderLoader_mmx] [{state_key}] ✅ 读取 [{current_idx}/{total}] {current_filename} | "
              f"批次 {len(tensors)} 张 | 步进 +{step} -> 下一位置 {next_idx}")
        
        return (single_image, batch, current_filename, current_idx, total)

# --------------------------------------------------
#  统一注册
# --------------------------------------------------
register_node(ImageBatchCollector_mmx, "ImageBatchCollector_mmx")
register_node(save2JPG_mmx, "save2JPG_mmx")
register_node(LoadImageFromPath_mmx, "LoadImageFromPath_mmx")
register_node(ImageSplitGrid_mmx, "ImageSplitGrid_mmx")
register_node(ImageFolderLoader_mmx, "ImageFolderLoader_mmx")
