# ~/ComfyUI/custom_nodes/ComfyUI-Aiya-MMX/nodes/gemini_API.py
from __future__ import annotations
import io
import json
import base64
import time
import uuid
import random
import re
import requests
import cv2
import torch
import numpy as np
from pathlib import Path
from PIL import Image
from datetime import datetime
from ..register import register_node
from ..mmx_utils import pil2tensor, tensor2pil   # 统一复用
from ..video_adapter import Video               # Veo 需要

# ---------- 通用工具 ----------
def tensor2pil_single(t: torch.Tensor) -> Image.Image:
    """比 mmx_utils 更严格的单张转换，供 Nano-Banana 专用"""
    if t.dim() == 4:
        t = t.squeeze(0)
    t = (t.clamp(0, 1) * 255).byte().cpu()
    return Image.fromarray(t.numpy())

# ===================================================================
#  1. Nano-Banana Pro
# ===================================================================
class NanoBananaPro:
    DESCRIPTION = (
        "💕 哎呀✦Nano-Banana Pro —— 文/图生图、14 图输入、自动抽卡\n"
        "默认 2K 最高分辨率；前端隐藏 seed；info 输出下游友好"
    )

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "endpoint_url": ("STRING", {
                    "default": "https://ai.t8star.cn/v1/images/generations",
                    "placeholder": "https://xxx/v1/images/generations"
                }),
                "api_key": ("STRING", {"default": "", "placeholder": "sk-***"}),
                "prompt": ("STRING", {"forceInput": True, "multiline": True}),
                "aspect_ratio": (["1:1", "2:3", "3:2", "3:4", "4:3", "4:5", "5:4", "9:16", "16:9", "21:9"], {"default": "1:1"}),
                "model": ("STRING", {"default": "nano-banana-2"}),
            },
            "optional": {f"input_image_{i}": ("IMAGE",) for i in range(1, 15)}
        }

    RETURN_TYPES = ("IMAGE", "STRING")
    RETURN_NAMES = ("image", "info")
    FUNCTION = "generate"
    CATEGORY = "哎呀✦MMX/图像"

    def add_random(self, p: str) -> str:
        return f"{p} [var-{random.randint(10000, 99999)}]"

    def build_payload(self, prompt, imgs, ar, model: str):
        # 端口→数组索引映射
        port_map = {idx + 1: idx + 1 for idx, img in enumerate(imgs) if img is not None}
        for port, arr in port_map.items():
            prompt = re.sub(rf"图{port}(?!\d)", f"图{arr}", prompt)

        parts = []
        for img in imgs:
            if img is not None:
                buf = io.BytesIO()
                tensor2pil_single(img).save(buf, format="PNG")
                b64 = base64.b64encode(buf.getvalue()).decode()
                parts.append({"image": b64})
        parts.append({"text": self.add_random(prompt)})

        payload = {
            "model": model,
            "prompt": parts[-1]["text"],
            "aspect_ratio": ar,
            "image_size": "2K",
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
                    im = Image.open(io.BytesIO(base64.b64decode(url.split(",", 1)[1])))
                else:
                    im = Image.open(io.BytesIO(requests.get(url, timeout=60).content))
                im = im.convert("RGB")
                w, h = im.size
                decoded.append((pil2tensor(im), w * h))
            except Exception as e:
                print(f"[NanoBanana] skip: {e}")
                continue
        if not decoded:
            raise RuntimeError("All images failed")
        decoded.sort(key=lambda x: x[1], reverse=True)
        best, _ = decoded[0]
        print(f"[NanoBanana] picked largest")
        return best

    def generate(self, endpoint_url, api_key, prompt, aspect_ratio, model, **img_ports):
        imgs = [img_ports.get(f"input_image_{i}") for i in range(1, 15)]
        cnt = sum(1 for i in imgs if i is not None)
        print(f"[NanoBanana] model={model} imgs={cnt} ratio={aspect_ratio}")

        payload = self.build_payload(prompt, imgs, aspect_ratio, model)
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        resp = requests.post(endpoint_url, headers=headers, json=payload, timeout=180)
        if resp.status_code != 200:
            raise RuntimeError(f"HTTP {resp.status_code}: {resp.text[:200]}")

        urls = [item["url"] for item in resp.json().get("data", []) if "url" in item]
        if not urls:
            raise RuntimeError("No image returned")
        best = self.decode_biggest(urls)

        info = f"🍌 NanoBanana {time.strftime('%Y-%m-%d %H:%M:%S')}\nendpoint: {endpoint_url}\nmodel: {model}\nratio: {aspect_ratio}  size: 2K\ninput: {cnt}  success: True"
        return (best, info)


# ===================================================================
#  2. Gemini-3-Vision
# ===================================================================
class Gemini3Vision:
    DESCRIPTION = "💕 哎呀✦Gemini-3 视觉对话（纯文本返回）"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "system_prompt": ("STRING", {"multiline": True, "default": "You are a helpful assistant."}),
                "user_prompt": ("STRING", {"multiline": True, "default": ""}),
                "model": ("STRING", {"default": "gemini-3-flash-preview"}),
            },
            "optional": {
                "api_url": ("STRING", {"default": "https://ai.t8star.cn/v1/chat/completions"}),
                "image": ("IMAGE",),
                "seed": ("INT", {"default": 0, "min": 0, "max": 2147483647}),
                "max_tokens": ("INT", {"default": 4096, "min": 1, "max": 8192}),
                "temperature": ("FLOAT", {"default": 0.7, "min": 0.0, "max": 2.0, "step": 0.01}),
                "api_key": ("STRING", {"default": ""}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("text",)
    FUNCTION = "run"
    CATEGORY = "哎呀✦MMX/text"

    def image_to_base64(self, tensor: torch.Tensor) -> str:
        if tensor.dim() == 4:
            tensor = tensor[0]
        tensor = (tensor.clamp(0, 1) * 255).byte().cpu()
        buf = io.BytesIO()
        Image.fromarray(tensor.numpy()).save(buf, format="PNG")
        return base64.b64encode(buf.getvalue()).decode()

    def run(self, system_prompt, user_prompt, model, api_url,
            image=None, seed=0, max_tokens=4096, temperature=0.7, api_key=""):
        if not api_key.strip():
            return ("[Gemini3Vision] API key 缺失",)

        messages = [{"role": "system", "content": system_prompt}]
        content = [{"type": "text", "text": user_prompt}]
        if image is not None:
            b64 = self.image_to_base64(image)
            content.append({"type": "image_url", "image_url": {"url": f"data:image/png;base64,{b64}"}})
        messages.append({"role": "user", "content": content})

        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "seed": seed if seed > 0 else None,
        }

        try:
            rsp = requests.post(api_url,
                              headers={"Authorization": f"Bearer {api_key}",
                                      "Content-Type": "application/json"},
                              json=payload, timeout=120)
            rsp.raise_for_status()
            reply = rsp.json()["choices"][0]["message"]["content"]
        except Exception as e:
            reply = f"[Gemini3Vision] 请求失败: {e}"

        print(f"[Gemini3Vision] 模型={model} 返回长度={len(reply)}")
        return (reply,)


# ===================================================================
#  3. Veo3.1 文生视频
# ===================================================================
def build_video_obj(video_path: Path) -> Video:
    cap = cv2.VideoCapture(str(video_path))
    fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    cap.release()
    return Video(str(video_path), fps, w, h)


def download_file(url: str, dst: Path, max_retry: int = 3, timeout: int = 120):
    for attempt in range(1, max_retry + 1):
        try:
            print(f"[Veo3.1 Download] 第 {attempt}/{max_retry} 次：{url}")
            with requests.get(url, stream=True, timeout=timeout) as r:
                r.raise_for_status()
                with open(dst, "wb") as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
            print(f"[Veo3.1 Download] 成功 → {dst}")
            return
        except Exception as e:
            print(f"[Veo3.1 Download] 第 {attempt} 次失败：{e}")
            if attempt == max_retry:
                raise RuntimeError(f"下载失败（重试 {max_retry} 次）：{e}")
            time.sleep(2)


class Veo3_1:
    DESCRIPTION = (
        "💕 哎呀✦MMX/Veo3.1 谷歌文生视频\n"
        "文本 → 视频张量 + URL + 任务信息；支持 4K/增强/上采样"
    )
    RETURN_TYPES = ("VIDEO", "STRING", "STRING")
    RETURN_NAMES = ("video", "video_url", "info")
    FUNCTION = "generate_video"
    CATEGORY = "哎呀✦MMX/Video"

    def __init__(self):
        self.timeout = 120
        self.poll_interval = 2
        self.max_poll = 150

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "api_key": ("STRING", {"default": "", "placeholder": "sk-***************************"}),
                "base_url": ("STRING", {"default": "https://ai.t8star.cn", "placeholder": "API 根地址"}),
                "prompt": ("STRING", {"multiline": True, "default": "A cinematic aerial shot of a neon-lit cyberpunk city at night, 4K, ultra detailed"}),
                "model": ("STRING", {"default": "veo3.1", "placeholder": "veo3.1 / veo3.1-fast / veo3.1-pro / ..."}),
                "duration": (["5", "10", "15", "20", "25"], {"default": "10"}),
                "aspect_ratio": (["16:9", "9:16"], {"default": "16:9"}),
                "enhance_prompt": ("BOOLEAN", {"default": True}),
                "enable_upsample": ("BOOLEAN", {"default": False}),
            },
            "optional": {
                "image1": ("IMAGE",), "image2": ("IMAGE",), "image3": ("IMAGE",),
                "seed": ("INT", {"default": 0, "min": 0, "max": 2147483647}),
            }
        }

    def image_to_base64(self, img_tensor):
        if img_tensor is None:
            return None
        pil = tensor2pil(img_tensor)[0]
        buf = io.BytesIO()
        pil.save(buf, format="PNG")
        return base64.b64encode(buf.getvalue()).decode()

    def generate_video(self, api_key, base_url, prompt, model, duration, aspect_ratio,
                       enhance_prompt, enable_upsample,
                       image1=None, image2=None, image3=None, seed=0):
        if not api_key.strip():
            return (Video.create_empty(), "", "❌ API Key 为空")

        root = base_url.rstrip("/")
        submit_url = f"{root}/v2/videos/generations"
        query_url = f"{root}/v2/videos/generations/{{}}"

        images_b64 = []
        for img in (image1, image2, image3):
            if img is not None:
                b64 = self.image_to_base64(img)
                if b64:
                    images_b64.append(f"data:image/png;base64,{b64}")

        payload = {
            "model": model,
            "prompt": prompt,
            "duration": int(duration),
            "aspect_ratio": aspect_ratio,
            "enhance_prompt": enhance_prompt,
            "enable_upsample": enable_upsample,
        }
        if images_b64:
            payload["images"] = images_b64
        if seed > 0:
            payload["seed"] = seed

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key.strip()}"
        }

        try:
            # 1. 提交任务
            resp = requests.post(submit_url, headers=headers, json=payload, timeout=self.timeout)
            resp.raise_for_status()
            data = resp.json()
            task_id = data.get("task_id")
            if not task_id:
                return (Video.create_empty(), "", "❌ 未返回 task_id")
            print(f"[Veo3.1] 任务已提交: {task_id}")

            # 2. 轮询状态
            for i in range(self.max_poll):
                time.sleep(self.poll_interval)
                st = requests.get(query_url.format(task_id), headers=headers, timeout=30)
                st.raise_for_status()
                st_data = st.json()
                status = st_data.get("status", "")

                if status == "SUCCESS":
                    video_url = st_data.get("data", {}).get("output", "")
                    if video_url:
                        import folder_paths
                        temp_dir = Path(folder_paths.get_temp_directory())
                        temp_dir.mkdir(parents=True, exist_ok=True)
                        temp_file = temp_dir / f"veo3_1_{int(time.time()*1000)}.mp4"
                        download_file(video_url, temp_file)
                        video_obj = build_video_obj(temp_file)
                        info_json = {
                            "task_id": task_id,
                            "model": model,
                            "prompt": prompt,
                            "duration": duration,
                            "aspect_ratio": aspect_ratio,
                            "enhance": enhance_prompt,
                            "upsample": enable_upsample,
                            "seed": seed if seed > 0 else "auto",
                            "video_url": video_url,
                        }
                        return (video_obj, video_url, json.dumps(info_json, ensure_ascii=False, indent=2))
                    else:
                        return (Video.create_empty(), "", f"❌ 状态成功但无视频 URL: {st_data}")

                elif status == "FAILURE":
                    reason = st_data.get("fail_reason", "Unknown")
                    return (Video.create_empty(), "", f"❌ 任务失败: {reason}")

            return (Video.create_empty(), "", f"❌ 轮询超时（>{self.max_poll * self.poll_interval}s）")

        except requests.exceptions.Timeout:
            return (Video.create_empty(), "", "❌ 请求超时 (120s)")
        except Exception as e:
            return (Video.create_empty(), "", f"❌ 异常: {str(e)}")


# ===================================================================
#  统一注册
# ===================================================================
register_node(NanoBananaPro, "NanoBanana_Pro_mmx")
register_node(Gemini3Vision, "Gemini3Vision_mmx")
register_node(Veo3_1, "Veo3.1_mmx")
