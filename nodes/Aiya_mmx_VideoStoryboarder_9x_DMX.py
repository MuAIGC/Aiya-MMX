# video_storyboarder_9x_dmx.py
from __future__ import annotations
import io
import base64
import json
import re
import requests
from PIL import Image
import torch
import numpy as np
from ..register import register_node

# ---------- utils ----------
def tensor2pil(t):
    if t.ndim == 4:
        t = t.squeeze(0)
    if t.ndim == 3 and t.shape[2] == 3:
        t = (t * 255).clamp(0, 255).byte() if t.is_floating_point() else t
        return Image.fromarray(t.cpu().numpy(), "RGB")
    raise ValueError("Unsupported tensor shape")

def pil2tensor(img: Image.Image):
    return torch.from_numpy(np.array(img).astype(np.float32) / 255.0).unsqueeze(0)

def image_to_data_url(image_tensor) -> str:
    pil = tensor2pil(image_tensor)
    buf = io.BytesIO()
    pil.save(buf, format="PNG")
    buf.seek(0)
    b64 = base64.b64encode(buf.read()).decode()
    return f"data:image/png;base64,{b64}"

# ---------- 9 镜 system prompt 模板 ----------
SYSTEM_9X_TPL = """你是专业广告分镜师+音效指导。根据用户主题「{theme}」，输出严格 9 镜 JSON 数组，字段：
- id: 镜号
- cn_prompt: 中文图提示（300 字左右，自然语言，必含“主角外貌锚点”“主场景锚点”“色调#主色码”“镜头语言”，每个分镜如有人物出现，就要重复一遍人物特征，不能使用“同上”这类词语，人物的外貌、服装、年龄要具体，不能写范围、笼统的描述。）
- duration: 单镜秒数（9 镜总和={duration}s）
- shot_size: 景别（中文，≤30 字）
- camera: 运镜（中文，≤30 字）
- content: 画面简述（中文，≤30 字）
- audio_txt: 旁白中文（≤28 字，≈4 秒 220 字/分钟）
- env: 环境音关键词（中文，≤10 词）
- sfx: 动作/特效音关键词（中文，≤10 词）
- subtitle: 字幕（格式：入点|出点|内容，≤20 中文字）
要求：同一主角外貌+同一主场景+统一色调锁；节奏递进；裸 JSON 数组，勿解释。"""

# ---------- 节点 ----------
class VideoStoryboarder_9x_DMX:
    DESCRIPTION = (
        "💕 哎呀✦9 镜分镜脚本生成器（9 口输出，||| 分隔，可接系统提示）\n\n"
        "每口格式：prompt|||duration|||shot_size|||camera|||content|||audio|||env|||sfx|||subtitle\n"
        "新增 system_prompt 输入口，可接风格预设节点"
    )
    RETURN_TYPES = tuple(["STRING"] * 9)
    RETURN_NAMES = tuple([f"shot_{i}" for i in range(1, 10)])
    FUNCTION = "storyboard"
    CATEGORY = "哎呀✦MMX/DMXAPI"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "api_key": ("STRING", {"default": "", "placeholder": "sk-***************************"}),
                "theme": ("STRING", {"multiline": True, "placeholder": "主题一句话，如：未来城市清晨的咖啡广告"}),
                "duration": ("INT", {"default": 50, "min": 3, "max": 120, "step": 1}),
                "separator": ("STRING", {"default": "|||", "multiline": False, "placeholder": "分隔符，默认 |||"}),
            },
            "optional": {
                "reference_image": ("IMAGE",),
                "system_prompt": ("STRING", {"multiline": True, "placeholder": "可选：直接传入 system prompt，留空即用内部模板"}),
            }
        }

    def storyboard(self, api_key, theme, duration, separator="|||", reference_image=None, system_prompt=""):
        if not api_key.strip():
            raise RuntimeError("❌ api_key 不能为空")

        # 1. system prompt：优先用外部传入，否则用内部模板
        if system_prompt and system_prompt.strip():
            sys_text = system_prompt.strip()
        else:
            sys_text = SYSTEM_9X_TPL.format(theme=theme, duration=duration)

        # 2. 用户内容
        content = [{"type": "input_text", "text": f"主题：{theme}"}]
        if reference_image is not None:
            content.append({"type": "input_image", "image_url": image_to_data_url(reference_image)})

        payload = {
            "model": "gpt-5-mini",
            "input": [
                {"role": "system", "content": [{"type": "input_text", "text": sys_text}]},
                {"role": "user", "content": content}
            ]
        }
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key.strip()}"
        }

        resp = requests.post("https://www.dmxapi.cn/v1/responses", headers=headers, json=payload, timeout=120)
        if resp.status_code != 200:
            raise RuntimeError(f"Responses 接口异常 HTTP {resp.status_code}: {resp.text[:200]}")

        try:
            out_list = resp.json()["output"]
            text_block = next(x for x in out_list if x["type"] == "message")["content"]
            full_text = next(x for x in text_block if x["type"] == "output_text")["text"]
            json_str = re.search(r"\[.*\]", full_text, flags=re.S).group(0)
            boards = json.loads(json_str)
            if len(boards) != 9:
                raise ValueError("未返回 9 个分镜")
        except Exception as e:
            raise RuntimeError(f"解析失败：{e}")

        # 3. 组装 9 口（全部转字符串）
        shots = []
        for b in boards:
            seg = separator.join([
                b["cn_prompt"],
                str(b["duration"]),
                b["shot_size"],
                b["camera"],
                b["content"],
                b["audio_txt"],
                b["env"],
                b["sfx"],
                b["subtitle"]
            ])
            shots.append(seg)
        return tuple(shots)

register_node(VideoStoryboarder_9x_DMX, "VideoStoryboarder_9x_DMX")
