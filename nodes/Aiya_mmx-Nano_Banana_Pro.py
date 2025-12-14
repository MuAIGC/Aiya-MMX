# ~/ComfyUI/custom_nodes/Aiya_mmx/nodes/Aiya-mmx-Nano_Banana_Pro.py
"""
💕 哎呀✦MMX Nano-Banana Pro 终极精简版
默认 2K / 前端隐藏 seed / info 输出
"""
from __future__ import annotations
import io
import random
import requests
import base64
import time
import re 
import numpy as np
from PIL import Image
from io import BytesIO
import torch
from ..register import register_node

# ========== 自给自足 utils ==========
def tensor2pil(t):
    if t.ndim == 4:
        t = t.squeeze(0)
    if t.ndim == 3 and t.shape[2] == 3:
        t = (t * 255).clamp(0, 255).byte() if t.is_floating_point() else t
        return [Image.fromarray(t.cpu().numpy(), "RGB")]
    raise ValueError("Unsupported tensor shape")

def pil2tensor(images):
    if not isinstance(images, list):
        images = [images]
    np_stack = np.stack([np.array(img).astype(np.float32) / 255.0 for img in images])
    return torch.from_numpy(np_stack)


class AiyaMMXNanoBananaPro:
    DESCRIPTION = (
        "💕 哎呀✦Nano-Banana Pro —— 文/图生图、14 图输入、自动抽卡\n\n"
        "1. 在 Endpoint URL 填接口地址\n"
        "2. 在 API Key 填密钥（可接上游配置节点）\n"
        "3. 默认输出 2K 最高分辨率图片\n\n"
        "English: Txt2img / img2img / 14 imgs / 2K / pick highest-res."
    )

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "endpoint_url": ("STRING", {
                    "default": "https://ai.t8star.cn/v1/images/generations",
                    "placeholder": "https://xxx/v1/images/generations"
                }),
                "api_key": ("STRING", {"default": "", "placeholder": "Your API key"}),
                "prompt": ("STRING", {"forceInput": True, "multiline": True}),
                "aspect_ratio": (["1:1", "2:3", "3:2", "3:4", "4:3", "4:5", "5:4", "9:16", "16:9", "21:9"], {"default": "1:1"}),
            },
            "optional": {f"input_image_{i}": ("IMAGE",) for i in range(1, 15)}
        }

    RETURN_TYPES = ("IMAGE", "STRING")
    RETURN_NAMES = ("image", "info")          # ← 下游预览字符串节点友好
    FUNCTION = "generate"
    CATEGORY = "哎呀✦MMX/生成"

    # ---------- 工具 ----------
    def add_random(self, p: str) -> str:
        # 内部固定随机，不暴露 seed
        return f"{p} [var-{random.randint(10000, 99999)}]"

    def build_payload(self, prompt, imgs, ar, ep):
        # 端口→数组索引映射（1-based）
        port_map = {idx + 1: idx + 1 for idx, img in enumerate(imgs) if img is not None}
        for port, arr in port_map.items():
            prompt = re.sub(rf"图{port}(?!\d)", f"图{arr}", prompt)

        parts = []
        for img in imgs:
            if img is not None:
                pil = tensor2pil(img)[0]
                buf = BytesIO()
                pil.save(buf, format="PNG")
                b64 = base64.b64encode(buf.getvalue()).decode()
                parts.append({"image": b64})          # OpenAI 风格
        parts.append({"text": self.add_random(prompt)})

        payload = {
            "model": "nano-banana-2",
            "prompt": parts[-1]["text"],
            "aspect_ratio": ar,
            "image_size": "2K",                     # 固定 2K
            "response_format": "url"
        }
        if parts[:-1]:
            payload["image"] = [p["image"] for p in parts[:-1]]
        return payload

    def decode_biggest(self, urls):
        decoded = []
        for url in urls:
            try:
                if url.startswith("data:"):
                    img = Image.open(BytesIO(base64.b64decode(url.split(",", 1)[1])))
                else:
                    img = Image.open(BytesIO(requests.get(url, timeout=60).content))
                img = img.convert("RGB")
                w, h = img.size
                decoded.append((pil2tensor(img), w * h, w, h))
            except Exception as e:
                print(f"[AiyaMMX] skip: {e}")
                continue
        if not decoded:
            raise RuntimeError("All images failed")
        decoded.sort(key=lambda x: x[1], reverse=True)
        best, _, w, h = decoded[0]
        print(f"[AiyaMMX] picked {w}x{h}")
        return best

    # ---------- 主入口 ----------
    def generate(self, endpoint_url, api_key, prompt, aspect_ratio, **img_ports):
        print("\n[AiyaMMX] ===== Nano-Banana =====")
        imgs = [img_ports.get(f"input_image_{i}") for i in range(1, 15)]
        cnt = len([i for i in imgs if i is not None])
        print(f"[AiyaMMX] imgs: {cnt}  ratio: {aspect_ratio}")

        payload = self.build_payload(prompt, imgs, aspect_ratio, endpoint_url)

        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        resp = requests.post(endpoint_url, headers=headers, json=payload, timeout=180)
        if resp.status_code != 200:
            raise RuntimeError(f"HTTP {resp.status_code}: {resp.text[:200]}")

        result = resp.json()
        urls = [item["url"] for item in result.get("data", []) if "url" in item]
        if not urls:
            raise RuntimeError("No image returned")
        best = self.decode_biggest(urls)

        txt = f"🍌 AiyaMMX Nano-Banana  {time.strftime('%Y-%m-%d %H:%M:%S')}\nendpoint: {endpoint_url}\nratio: {aspect_ratio}  size: 2K\ninput: {cnt}  success: True"
        return (best, txt)


# ---------- 注册 ----------
register_node(AiyaMMXNanoBananaPro, "Nano-Banana_Pro")
