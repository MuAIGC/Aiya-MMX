# ~/ComfyUI/custom_nodes/ComfyUI-Aiya-MMX/nodes/shot_picker.py
from __future__ import annotations
import torch
import re
from ..register import register_node

# ================= 镜头语表 =================
SHOT_TOKENS: list[str] = [
    "<sks> front view low-angle shot close-up",
    "<sks> front-right quarter view low-angle shot close-up",
    "<sks> right side view low-angle shot close-up",
    "<sks> back-right quarter view low-angle shot close-up",
    "<sks> back view low-angle shot close-up",
    "<sks> back-left quarter view low-angle shot close-up",
    "<sks> left side view low-angle shot close-up",
    "<sks> front-left quarter view low-angle shot close-up",
    "<sks> front view eye-level shot close-up",
    "<sks> front-right quarter view eye-level shot close-up",
    "<sks> right side view eye-level shot close-up",
    "<sks> back-right quarter view eye-level shot close-up",
    "<sks> back view eye-level shot close-up",
    "<sks> back-left quarter view low-angle shot close-up",
    "<sks> left side view eye-level shot close-up",
    "<sks> front-left quarter view eye-level shot close-up",
    "<sks> front view elevated shot close-up",
    "<sks> front-right quarter view elevated shot close-up",
    "<sks> right side view elevated shot close-up",
    "<sks> back-right quarter view elevated shot close-up",
    "<sks> back view elevated shot close-up",
    "<sks> back-left quarter view elevated shot close-up",
    "<sks> left side view elevated shot close-up",
    "<sks> front-left quarter view elevated shot close-up",
    "<sks> front view high-angle shot close-up",
    "<sks> front-right quarter view high-angle shot close-up",
    "<sks> right side view high-angle shot close-up",
    "<sks> back-right quarter view high-angle shot close-up",
    "<sks> back view high-angle shot close-up",
    "<sks> back-left quarter view high-angle shot close-up",
    "<sks> left side view high-angle shot close-up",
    "<sks> front-left quarter view high-angle shot close-up",
    "<sks> front view low-angle shot medium shot",
    "<sks> front-right quarter view low-angle shot medium shot",
    "<sks> right side view low-angle shot medium shot",
    "<sks> back-right quarter view low-angle shot medium shot",
    "<sks> back view low-angle shot medium shot",
    "<sks> back-left quarter view low-angle shot medium shot",
    "<sks> left side view low-angle shot medium shot",
    "<sks> front-left quarter view low-angle shot medium shot",
    "<sks> front view eye-level shot medium shot",
    "<sks> front-right quarter view eye-level shot medium shot",
    "<sks> right side view eye-level shot medium shot",
    "<sks> back-right quarter view eye-level shot medium shot",
    "<sks> back view eye-level shot medium shot",
    "<sks> back-left quarter view eye-level shot medium shot",
    "<sks> left side view eye-level shot medium shot",
    "<sks> front-left quarter view eye-level shot medium shot",
    "<sks> front view elevated shot medium shot",
    "<sks> front-right quarter view elevated shot medium shot",
    "<sks> right side view elevated shot medium shot",
    "<sks> back-right quarter view elevated shot medium shot",
    "<sks> back view elevated shot medium shot",
    "<sks> back-left quarter view elevated shot medium shot",
    "<sks> left side view elevated shot medium shot",
    "<sks> front-left quarter view elevated shot medium shot",
    "<sks> front view high-angle shot medium shot",
    "<sks> front-right quarter view high-angle shot medium shot",
    "<sks> right side view high-angle shot medium shot",
    "<sks> back-right quarter view high-angle shot medium shot",
    "<sks> back view high-angle shot medium shot",
    "<sks> back-left quarter view high-angle shot medium shot",
    "<sks> left side view high-angle shot medium shot",
    "<sks> front-left quarter view high-angle shot medium shot",
    "<sks> front view low-angle shot wide shot",
    "<sks> front-right quarter view low-angle shot wide shot",
    "<sks> right side view low-angle shot wide shot",
    "<sks> back-right quarter view low-angle shot wide shot",
    "<sks> back view low-angle shot wide shot",
    "<sks> back-left quarter view low-angle shot wide shot",
    "<sks> left side view low-angle shot wide shot",
    "<sks> front-left quarter view low-angle shot wide shot",
    "<sks> front view eye-level shot wide shot",
    "<sks> front-right quarter view eye-level shot wide shot",
    "<sks> right side view eye-level shot wide shot",
    "<sks> back-right quarter view eye-level shot wide shot",
    "<sks> back view eye-level shot wide shot",
    "<sks> back-left quarter view eye-level shot wide shot",
    "<sks> left side view eye-level shot wide shot",
    "<sks> front-left quarter view eye-level shot wide shot",
    "<sks> front view elevated shot wide shot",
    "<sks> front-right quarter view elevated shot wide shot",
    "<sks> right side view elevated shot wide shot",
    "<sks> back-right quarter view elevated shot wide shot",
    "<sks> back view elevated shot wide shot",
    "<sks> back-left quarter view elevated shot wide shot",
    "<sks> left side view elevated shot wide shot",
    "<sks> front-left quarter view elevated shot wide shot",
    "<sks> front view high-angle shot wide shot",
    "<sks> front-right quarter view high-angle shot wide shot",
    "<sks> right side view high-angle shot wide shot",
    "<sks> back-right quarter view high-angle shot wide shot",
    "<sks> back view high-angle shot wide shot",
    "<sks> back-left quarter view high-angle shot wide shot",
    "<sks> left side view high-angle shot wide shot",
    "<sks> front-left quarter view high-angle shot wide shot",
]

# ================= 镜头语中文翻译（带编号） =================
SHOT_TOKENS_CN_WITH_INDEX = []
for i, shot in enumerate(SHOT_TOKENS, 1):
    # 从英文生成简单的中文描述
    shot_lower = shot.lower()
    
    # 提取角度
    if "low-angle" in shot_lower:
        angle = "低角度"
    elif "eye-level" in shot_lower:
        angle = "平视"
    elif "elevated" in shot_lower:
        angle = "微仰拍"
    elif "high-angle" in shot_lower:
        angle = "俯拍"
    else:
        angle = ""
    
    # 提取景别
    if "close-up" in shot_lower:
        framing = "特写"
    elif "medium shot" in shot_lower:
        framing = "中景"
    elif "wide shot" in shot_lower:
        framing = "广角"
    else:
        framing = ""
    
    # 提取视角
    if "front view" in shot_lower:
        view = "正面"
    elif "front-right quarter view" in shot_lower:
        view = "前右四分之三侧面"
    elif "right side view" in shot_lower:
        view = "右侧面"
    elif "back-right quarter view" in shot_lower:
        view = "后右四分之三侧面"
    elif "back view" in shot_lower:
        view = "背面"
    elif "back-left quarter view" in shot_lower:
        view = "后左四分之三侧面"
    elif "left side view" in shot_lower:
        view = "左侧面"
    elif "front-left quarter view" in shot_lower:
        view = "前左四分之三侧面"
    else:
        view = ""
    
    # 组合中文描述
    cn_desc = f"{view}{angle}{framing}"
    SHOT_TOKENS_CN_WITH_INDEX.append(f"{i:02d}. {cn_desc}")


class FlexibleShotPicker_mmx:
    DESCRIPTION = (
        "💕 哎呀✦灵活镜头语选择器\n\n"
        "三种选择方式（按优先级排序）：\n"
        "1. 编号选择框（最高优先级）：输入镜头编号，如 '1,2,4-6,9'，可重复选择\n"
        "2. 下拉菜单（中等优先级）：单个镜头选择，显示中文描述\n"
        "3. 自定义提示词（最低优先级）：自由输入任意提示词\n\n"
        "编号示例：\n"
        "• 1,3,5,7,9  # 选择奇数镜头\n"
        "• 1-6        # 选择第1到6个镜头\n"
        "• 1,2,2,3,3,3  # 可重复选择\n"
        "• 1,5,9,13,17,21  # 间隔选择\n\n"
        "输出：每行一个选中的镜头语，可直接复制到KSampler"
    )
    RETURN_TYPES = ("STRING", "INT", "INT", "LATENT")
    RETURN_NAMES = ("prompt", "width", "height", "latent")
    FUNCTION = "pick"
    CATEGORY = "哎呀✦MMX/文本"

    @classmethod
    def INPUT_TYPES(cls):
        # 镜头语下拉菜单（显示带编号的中文）
        shot_options = ["自定义"] + SHOT_TOKENS_CN_WITH_INDEX
        
        # 长宽比选项（中文）
        aspect_ratios = [
            "自定义",
            "1:1 (正方形)",
            "3:4 (竖屏)",
            "4:3 (横屏)",
            "2:3 (竖屏)",
            "3:2 (横屏)",
            "9:16 (手机)",
            "16:9 (宽屏)",
        ]

        return {
            "required": {
                "镜头编号选择": ("STRING", {
                    "default": "1,2,3,4,5,6", 
                    "multiline": False,
                    "placeholder": "输入编号，如：1,3,5 或 1-6 或 1,2,2,3 (可重复)"
                }),
                "下拉菜单选择": (shot_options, {"default": "01. 正面低角度特写"}),
                "自定义提示词": ("STRING", {
                    "default": "", 
                    "multiline": True, 
                    "placeholder": "在此输入自定义提示词（优先级最低）"
                }),
                "画面比例": (aspect_ratios, {"default": "1:1 (正方形)"}),
                "宽度": ("INT", {"default": 1024, "min": 64, "max": 8192, "step": 8}),
                "高度": ("INT", {"default": 1024, "min": 64, "max": 8192, "step": 8}),
                "批次数": ("INT", {"default": 1, "min": 1, "max": 64, "step": 1}),
            }
        }

    def pick(self, 镜头编号选择, 下拉菜单选择, 自定义提示词, 画面比例, 宽度, 高度, 批次数=1):
        # 初始化prompt_out
        prompt_out = ""
        
        # 优先级1：编号选择框
        if 镜头编号选择 and 镜头编号选择.strip():
            try:
                # 解析编号选择
                selected_indices = self.parse_shot_selection(镜头编号选择)
                if selected_indices:
                    # 获取对应的镜头语
                    prompts = []
                    for idx in selected_indices:
                        if 1 <= idx <= len(SHOT_TOKENS):
                            prompts.append(SHOT_TOKENS[idx-1])
                        else:
                            # 编号越界，使用第一个
                            prompts.append(SHOT_TOKENS[0])
                    
                    prompt_out = "\n".join(prompts)
            except Exception as e:
                print(f"[FlexibleShotPicker_mmx] 解析编号选择时出错: {e}")
        
        # 优先级2：下拉菜单选择
        if not prompt_out:
            if 下拉菜单选择 and 下拉菜单选择 != "自定义":
                # 从中文描述中提取编号
                match = re.match(r'^(\d{2})\.', 下拉菜单选择)
                if match:
                    idx = int(match.group(1))
                    if 1 <= idx <= len(SHOT_TOKENS):
                        prompt_out = SHOT_TOKENS[idx-1]
                    else:
                        prompt_out = SHOT_TOKENS[0]
                else:
                    prompt_out = SHOT_TOKENS[0]
        
        # 优先级3：自定义提示词
        if not prompt_out and 自定义提示词 and 自定义提示词.strip():
            prompt_out = 自定义提示词.strip()
        
        # 如果都没有选择，使用第一个镜头语
        if not prompt_out:
            prompt_out = SHOT_TOKENS[0]
        
        # 确保prompt_out是字符串
        if isinstance(prompt_out, list):
            prompt_out = "\n".join(prompt_out)
        
        # 分辨率逻辑
        if 画面比例 != "自定义":
            ratio_map = {
                "1:1 (正方形)": (1, 1),
                "3:4 (竖屏)": (3, 4),
                "4:3 (横屏)": (4, 3),
                "2:3 (竖屏)": (2, 3),
                "3:2 (横屏)": (3, 2),
                "9:16 (手机)": (9, 16),
                "16:9 (宽屏)": (16, 9),
            }
            if 画面比例 in ratio_map:
                rw, rh = ratio_map[画面比例]
                高度 = int(宽度 * rh / rw)
                高度 = (高度 // 8) * 8

        宽度  = max(64, (宽度  // 8) * 8)
        高度 = max(64, (高度 // 8) * 8)

        # 根据批次数和选择的镜头数量创建latent
        # 先计算实际选择的镜头数量
        shot_count = len(prompt_out.split('\n')) if prompt_out else 1
        actual_batch_size = 批次数 * shot_count
        
        latent = torch.zeros([actual_batch_size, 4, 高度 // 8, 宽度 // 8])
        
        print(f"[FlexibleShotPicker_mmx] 输出 → {shot_count}个镜头语")
        lines = prompt_out.split('\n')
        for i, line in enumerate(lines[:10], 1):  # 最多显示10行
            if len(line) > 50:
                print(f"  镜头{i}: {line[:50]}...")
            else:
                print(f"  镜头{i}: {line}")
        if len(lines) > 10:
            print(f"  ... 还有{len(lines)-10}个镜头")
        print(f"  分辨率: {宽度}×{高度}, 批次数: {批次数}")
        
        return (prompt_out, 宽度, 高度, {"samples": latent})
    
    def parse_shot_selection(self, selection_str):
        """解析镜头选择字符串，支持范围、重复、混合模式"""
        if not selection_str or not selection_str.strip():
            return []
        
        indices = []
        
        # 支持多种分隔符：逗号、空格、中文逗号
        # 先替换中文标点
        selection_str = selection_str.replace('，', ',').replace('、', ',').replace('；', ',')
        selection_str = selection_str.replace(' ', ',')
        
        # 分割各部分
        parts = [part.strip() for part in selection_str.split(',') if part.strip()]
        
        for part in parts:
            if '-' in part:
                # 处理范围，如 1-6
                try:
                    start_end = part.split('-')
                    if len(start_end) == 2:
                        start = int(start_end[0])
                        end = int(start_end[1])
                        # 确保顺序正确
                        if start <= end:
                            indices.extend(range(start, end + 1))
                        else:
                            indices.extend(range(end, start + 1))
                    elif len(start_end) > 2:
                        # 处理 1-6-10 这样的格式，取第一个和最后一个
                        start = int(start_end[0])
                        end = int(start_end[-1])
                        if start <= end:
                            indices.extend(range(start, end + 1))
                        else:
                            indices.extend(range(end, start + 1))
                except ValueError:
                    continue
            else:
                # 处理单个编号
                try:
                    idx = int(part)
                    indices.append(idx)
                except ValueError:
                    continue
        
        # 保留重复项（允许重复选择）
        # 不限制数量，可以任意数量
        return indices


# ---------- 同时保留原来的节点 ----------
class ShotPickerAndResolution_mmx:
    DESCRIPTION = (
        "💕 哎呀✦镜头语选择器 + 分辨率（下拉 + 自定义）\n\n"
        "下拉：96 条预置镜头语\n"
        "自定义：任意提示词字符串（优先级高于下拉）\n\n"
        "其余功能：\n"
        "• 常见比例一键切换，宽高自动对齐 8 的倍数\n"
        "• batch_size 可一次生成多张\n"
        "• 直接输出 prompt / width / height / latent\n\n"
        "English:\n"
        "Shot-token picker + resolution. "
        "Aspect ratios auto-lock to 8-multiple. "
        "Outputs prompt, W/H, and empty latent ready for KSampler."
    )
    RETURN_TYPES = ("STRING", "INT", "INT", "LATENT")
    RETURN_NAMES = ("prompt", "width", "height", "latent")
    FUNCTION = "pick"
    CATEGORY = "哎呀✦MMX/文本"

    @classmethod
    def INPUT_TYPES(cls):
        # 镜头语下拉菜单（显示中文，但实际值是英文token）
        shot_options = ["自定义"] + SHOT_TOKENS_CN_WITH_INDEX
        
        # 长宽比选项（中文）
        aspect_ratios = [
            "自定义",
            "1:1 (正方形)",
            "3:4 (竖屏)",
            "4:3 (横屏)",
            "2:3 (竖屏)",
            "3:2 (横屏)",
            "9:16 (手机)",
            "16:9 (宽屏)",
        ]

        return {
            "required": {
                "镜头语选择": (shot_options, {"default": "01. 正面低角度特写"}),
                "自定义提示词": ("STRING", {"default": "", "multiline": True, "placeholder": "在此输入自定义提示词，优先级高于镜头语选择"}),
                "画面比例": (aspect_ratios, {"default": "1:1 (正方形)"}),
                "宽度": ("INT", {"default": 1024, "min": 64, "max": 8192, "step": 8}),
                "高度": ("INT", {"default": 1024, "min": 64, "max": 8192, "step": 8}),
                "批次数": ("INT", {"default": 1, "min": 1, "max": 64, "step": 1}),
            }
        }

    def pick(self, 镜头语选择, 自定义提示词, 画面比例, 宽度, 高度, 批次数=1):
        # 自定义优先
        if 自定义提示词.strip():
            prompt_out = 自定义提示词.strip()
        else:
            # 如果是"自定义"选项或没有对应的映射，使用第一个镜头语
            if 镜头语选择 == "自定义":
                prompt_out = SHOT_TOKENS[0]
            else:
                # 从中文描述中提取编号
                match = re.match(r'^(\d{2})\.', 镜头语选择)
                if match:
                    idx = int(match.group(1))
                    if 1 <= idx <= len(SHOT_TOKENS):
                        prompt_out = SHOT_TOKENS[idx-1]
                    else:
                        prompt_out = SHOT_TOKENS[0]
                else:
                    prompt_out = SHOT_TOKENS[0]

        # 分辨率逻辑
        if 画面比例 != "自定义":
            ratio_map = {
                "1:1 (正方形)": (1, 1),
                "3:4 (竖屏)": (3, 4),
                "4:3 (横屏)": (4, 3),
                "2:3 (竖屏)": (2, 3),
                "3:2 (横屏)": (3, 2),
                "9:16 (手机)": (9, 16),
                "16:9 (宽屏)": (16, 9),
            }
            if 画面比例 in ratio_map:
                rw, rh = ratio_map[画面比例]
                高度 = int(宽度 * rh / rw)
                高度 = (高度 // 8) * 8

        宽度  = max(64, (宽度  // 8) * 8)
        高度 = max(64, (高度 // 8) * 8)

        latent = torch.zeros([批次数, 4, 高度 // 8, 宽度 // 8])
        print(f"[ShotPickerAndResolution_mmx] 输出 → {prompt_out}  {宽度}×{高度}")
        return (prompt_out, 宽度, 高度, {"samples": latent})


# ---------- 注册 ----------
register_node(FlexibleShotPicker_mmx, "FlexibleShotPicker_mmx")
register_node(ShotPickerAndResolution_mmx, "ShotPickerAndResolution_mmx")