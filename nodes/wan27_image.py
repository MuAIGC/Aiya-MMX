# ~/ComfyUI/custom_nodes/Aiya-MMX/nodes/wan27_image.py
"""
💕哎呀✦Wan2.7-Image — 万相 2.7 图像生成与编辑
文生图 / 图像编辑 / 组图生成，通过 token-plan OpenAI 兼容接口调用
端点: {base_url}/v1/chat/completions
"""
from __future__ import annotations
import io
import json
import time
import base64
import requests
from PIL import Image
import torch
from ..register import register_node
from ..mmx_utils import pil2tensor, tensor2pil


# 比例 × K值 → "宽x高"
# K = 长边像素，宽高须为16的倍数，宽高比 1:8 ~ 8:1
# 万相：1K≈1024², 2K≈2048², 4K≈4096²
_RES = {
    # 比例     1K         2K          4K
    ("1", "1"):   ("1024x1024", "2048x2048", "4096x4096"),
    ("16", "9"):  ("1024x576",  "2048x1152",  "4096x2304"),
    ("9", "16"):  ("576x1024",  "1152x2048",  "2304x4096"),
    ("3", "2"):   ("1024x684",  "2048x1364",  "4096x2732"),
    ("2", "3"):   ("684x1024",  "1364x2048",  "2732x4096"),
    ("4", "3"):   ("1024x768",  "2048x1536",  "4096x3072"),
    ("3", "4"):   ("768x1024",  "1536x2048",  "3072x4096"),
    ("5", "4"):   ("1024x820",  "2048x1638",  "4096x3276"),
    ("4", "5"):   ("820x1024",  "1638x2048",  "3276x4096"),
    ("21", "9"):  ("1024x440",  "2048x878",   "4096x1756"),
    ("9", "21"):  ("440x1024",  "878x2048",   "1756x4096"),
    ("7", "3"):   ("1024x440",  "2048x878",   "4096x1756"),
    ("3", "7"):   ("440x1024",  "878x2048",   "1756x4096"),
    ("5", "3"):   ("1024x614",  "2048x1228",  "4096x2458"),
    ("3", "5"):   ("614x1024",  "1228x2048",  "2458x4096"),
    ("11", "4"):  ("1024x372",  "2048x744",   "4096x1490"),
    ("4", "11"):  ("372x1024",  "744x2048",   "1490x4096"),
    ("13", "4"):  ("1024x316",  "2048x628",   "4096x1256"),
    ("4", "13"):  ("316x1024",  "628x2048",   "1256x4096"),
    ("8", "1"):   ("1024x128",  "2048x256",   "4096x512"),
    ("1", "8"):   ("128x1024",  "256x2048",   "512x4096"),
}

_ASPECT_RATIOS = [
    "1:1", "16:9", "9:16", "3:2", "2:3", "4:3", "3:4",
    "5:4", "4:5", "21:9", "9:21", "7:3", "3:7",
    "5:3", "3:5", "11:4", "4:11", "13:4", "4:13",
    "8:1", "1:8"
]
_K_LABELS = ["1K (~1024)", "2K (~2048)", "4K (~4096)"]
_K_MAP = {"1K (~1024)": 0, "2K (~2048)": 1, "4K (~4096)": 2}
_MAX_IMAGES = 9


def _pil2b64uri(p):
    buf = io.BytesIO()
    p.save(buf, format="PNG")
    b64 = base64.b64encode(buf.getvalue()).decode()
    return f"data:image/png;base64,{b64}"


def _urlt(url):
    r = requests.get(url, stream=True, timeout=120)
    r.raise_for_status()
    total = int(r.headers.get("Content-Length", 0))
    chunks, got = [], 0
    for chunk in r.iter_content(chunk_size=8192):
        if chunk:
            chunks.append(chunk)
            got += len(chunk)
            if total > 0:
                print(f"\r  [Wan2.7] ↓ {min(got/total*100,100):.0f}% ({got/1024:.0f}KB)", end="", flush=True)
            else:
                print(f"\r  [Wan2.7] ↓ {got/1024:.0f}KB...", end="", flush=True)
    print()
    return pil2tensor(Image.open(io.BytesIO(b"".join(chunks))).convert("RGB"))


def _empty(h=1024, w=1024):
    return torch.zeros(1, h, w, 3)


def _resolve_size(aspect_ratio, resolution, has_images, enable_sequential, model):
    """比例 + K值 → (size_str, warning_or_none)"""
    is_pro = "wan2.7-image-pro" in model
    k_idx = _K_MAP.get(resolution, 1)  # default 2K

    # 4K 限制
    if k_idx == 2:  # 4K
        if has_images or enable_sequential:
            k_idx = 1  # 降级2K
        elif not is_pro:
            k_idx = 1
            # fall through to warn below

    w, h = aspect_ratio.split(":")
    key = (w.strip(), h.strip())
    if key not in _RES:
        return "2K", f"⚠️ 未知比例 {aspect_ratio}，使用 2K"

    size_str = _RES[key][k_idx]

    # 4K 降级警告
    if k_idx == 1 and resolution == "4K (~4096)":
        if has_images or enable_sequential:
            return size_str, "⚠️ 编辑/组图不支持4K，已降级到2K"
        elif not is_pro:
            return size_str, "⚠️ 该模型不支持4K，已降级到2K"

    return size_str, None


# ===================================================================
class Wan27_Image:
    DESCRIPTION = (
        "💕哎呀✦Wan2.7-Image — 万相 2.7\n"
        "无图→文生图 | 有图→编辑 | enable_sequential→组图\n"
        "通过 OpenAI 兼容 chat/completions 端点调用"
    )

    @classmethod
    def INPUT_TYPES(cls):
        img_ports = {f"image_{i}": ("IMAGE",) for i in range(1, _MAX_IMAGES + 1)}
        return {
            "required": {
                "base_url": ("STRING", {
                    "default": "https://token-plan.cn-beijing.maas.aliyuncs.com/compatible-mode/v1",
                    "tooltip": "API 根地址，兼容 OpenAI 接口协议"
                }),
                "api_key": ("STRING", {
                    "default": "", "placeholder": "sk-***",
                    "tooltip": "API Key"
                }),
                "model": ("STRING", {
                    "default": "wan2.7-image-pro",
                    "tooltip": "模型：wan2.7-image-pro / wan2.7-image / qwen-image-2.0 / qwen-image-2.0-pro"
                }),
                "prompt": ("STRING", {
                    "multiline": True, "default": "",
                    "tooltip": "图像描述，支持中英文，长度不超过5000字符"
                }),
                "aspect_ratio": (_ASPECT_RATIOS, {
                    "default": "1:1",
                    "tooltip": (
                        "画面比例。21种预设含极限比例 8:1/1:8\n"
                        "K值决定具体分辨率，1K=长边1024，2K=2048，4K=4096"
                    )
                }),
                "resolution": (_K_LABELS, {
                    "default": "2K (~2048)",
                    "tooltip": "分辨率等级：1K=长边1024，2K=2048，4K=4096（仅wan2.7-image-pro文生图）"
                }),
            },
            "optional": {
                "n": ("INT", {
                    "default": 1, "min": 1, "max": 12,
                    "tooltip": "生成数量：普通1-4，组图1-12"
                }),
                "watermark": ("BOOLEAN", {
                    "default": False,
                    "tooltip": "右下角'AI生成'水印"
                }),
                "thinking_mode": ("BOOLEAN", {
                    "default": True,
                    "tooltip": "思考模式，增强推理（仅文生图有效）"
                }),
                "seed": ("INT", {
                    "default": 0, "min": 0, "max": 2147483647,
                    "tooltip": "随机种子，0=自动随机"
                }),
                "enable_sequential": ("BOOLEAN", {
                    "default": False,
                    "tooltip": "组图模式：生成前后一致的多张图片"
                }),
                "timeout": ("INT", {
                    "default": 120, "min": 30, "max": 600, "step": 30,
                    "tooltip": "请求超时（秒），通常10-60s返回"
                }),
                "retries": ("INT", {
                    "default": 2, "min": 0, "max": 10,
                    "tooltip": "失败重试次数"
                }),
                "extra_json": ("STRING", {
                    "multiline": True, "default": "",
                    "placeholder": '{"image_size": "1K"}',
                    "tooltip": "额外参数 JSON 格式，合并到请求体"
                }),
                **img_ports,
            },
        }

    RETURN_TYPES = ("IMAGE", "STRING")
    RETURN_NAMES = ("images", "info")
    FUNCTION = "run"
    CATEGORY = "哎呀✦MMX/图像"
    OUTPUT_NODE = True

    def run(self, base_url, api_key, model, prompt,
            aspect_ratio="1:1", resolution="2K (~2048)",
            n=1, watermark=False, thinking_mode=True, seed=0,
            enable_sequential=False, timeout=120, retries=2, extra_json="",
            **img_ports):

        if not api_key.strip():
            print("[Wan2.7] ❌ API Key 缺失")
            return (_empty(), "Error: API Key 缺失")

        images = []
        for i in range(1, _MAX_IMAGES + 1):
            img = img_ports.get(f"image_{i}")
            if img is not None:
                images.append(img)

        has_images = len(images) > 0
        if enable_sequential:
            mode = "组图"
        elif has_images:
            mode = "编辑"
        else:
            mode = "文生图"

        is_pro = "wan2.7-image-pro" in model
        size_val, size_warn = _resolve_size(
            aspect_ratio, resolution, has_images, enable_sequential, model
        )
        if size_warn:
            print(f"[Wan2.7] {size_warn}")
        if size_val is None:
            return (_empty(), f"Error: 分辨率无效 - {size_warn}")

        # n 限制
        max_n = 12 if enable_sequential else 4
        if n > max_n:
            print(f"[Wan2.7] ⚠️ n 超过限制({max_n})，已截断")
            n = max_n

        endpoint = base_url.rstrip("/") + "/chat/completions"
        auth = f"Bearer {api_key.strip()}"

        # extra
        extra = {}
        e = (extra_json or "").strip()
        if e:
            try:
                extra = json.loads(e)
            except json.JSONDecodeError:
                print(f"[Wan2.7] ⚠️ extra_json 解析失败")

        # content 数组：image 在前，text 在最后
        content = []
        for idx, img in enumerate(images):
            pil_img = tensor2pil(img)[0]
            content.append({"type": "image", "image": _pil2b64uri(pil_img)})
            print(f"[Wan2.7] 输入图{idx+1}: {pil_img.size[0]}x{pil_img.size[1]}")
        content.append({"type": "text", "text": prompt})

        # payload - OpenAI 兼容格式
        payload = {
            "model": model.strip(),
            "messages": [{"role": "user", "content": content}],
            "image_size": size_val,
            "n": n,
            "watermark": watermark,
        }

        if not enable_sequential and not has_images and thinking_mode:
            payload["thinking_mode"] = True
        if enable_sequential:
            payload["enable_sequential"] = True
        if seed > 0:
            payload["seed"] = seed

        payload.update(extra)

        # 日志
        print(f"[Wan2.7] ═══════════════════════════════════════")
        print(f"[Wan2.7] [{mode}] 开始任务")
        print(f"[Wan2.7]  端点: {endpoint}")
        print(f"[Wan2.7]  模型: {model}")
        print(f"[Wan2.7]  数量: {n} | 尺寸: {size_val}")
        if enable_sequential:
            print(f"[Wan2.7]  组图模式: 开启")
        if has_images:
            print(f"[Wan2.7]  输入图: {len(images)} 张")
        print(f"[Wan2.7]  水印: {'有' if watermark else '无'} | 思考: {'开' if thinking_mode else '关'}")
        if seed > 0:
            print(f"[Wan2.7]  Seed: {seed}")
        print(f"[Wan2.7]  提示词: {prompt[:80]}{'...' if len(prompt) > 80 else ''}")
        print(f"[Wan2.7] ═══════════════════════════════════════")

        t_start = time.time()
        r = self._post_json(endpoint, auth, payload, timeout, retries)

        if r is None:
            elapsed = time.time() - t_start
            return (_empty(), f"❌ 请求失败 (耗时={elapsed:.1f}s)")

        status = r.status_code
        print(f"[Wan2.7] [{mode}] HTTP {status} ({time.time()-t_start:.1f}s)")

        if status != 200:
            self._print_error(r)
            return (_empty(), f"❌ HTTP {status}")

        result = r.json()

        # 解析响应 - chat/completions 格式
        # {"output":{"choices":[{"message":{"content":[{"type":"image","image":"URL"}]}}]}}
        # 或 OpenAI 标准格式: {"choices":[{"message":{"content":"..."}}]}
        urls = self._extract_urls(result)

        if not urls:
            print(f"[Wan2.7] 响应: {json.dumps(result, ensure_ascii=False)[:300]}")
            return (_empty(), "⚠️ 无返回图片")

        print(f"[Wan2.7] [{mode}] 获取 {len(urls)} 张图片 URL，开始下载...")

        tensors = []
        last_h, last_w = 1024, 1024
        for idx, url in enumerate(urls):
            try:
                t = _urlt(url)
                if t.dim() == 3:
                    t = t.unsqueeze(0)
                last_h, last_w = t.shape[1], t.shape[2]
                print(f"[Wan2.7]   图{idx+1} ✅ {last_w}x{last_h}")
                tensors.append(t)
            except Exception as e:
                print(f"[Wan2.7]   图{idx+1} ❌ 下载失败: {e}")

        t_total = time.time() - t_start
        req_id = result.get("request_id", "")

        if tensors:
            out = torch.cat(tensors, dim=0)
            kb = out.numel() * 4 / 1024
            info = (
                f"✅ {mode} 成功 | {len(tensors)}/{n} 张 | {t_total:.1f}s\n"
                f"模型: {model} | 尺寸: {size_val}\n"
                f"输出: {list(out.shape)} ({kb:.0f}KB)\n"
                f"Request ID: {req_id}"
            )
            print(f"[Wan2.7] [{mode}] ✅ 完成 | {len(tensors)}/{n} 张 | {t_total:.1f}s")
            return (out, info)
        else:
            return (_empty(), f"⚠️ 全部下载失败 (耗时={t_total:.1f}s)")

    def _extract_urls(self, result):
        """从响应中提取图片 URL，支持多种格式"""
        urls = []

        # 格式1: DashScope 原生格式
        # {"output":{"choices":[{"message":{"content":[{"type":"image","image":"URL"}]}}]}}
        output = result.get("output", {})
        choices = output.get("choices", [])
        if choices:
            for choice in choices:
                msg = choice.get("message", {})
                for item in msg.get("content", []):
                    if item.get("type") == "image" and item.get("image"):
                        urls.append(item["image"])
            if urls:
                return urls

        # 格式2: OpenAI 标准格式 (data 数组)
        # {"data":[{"url":"..."},{"b64_json":"..."}]}
        data = result.get("data", [])
        if data:
            for item in data:
                if "url" in item and item["url"]:
                    urls.append(item["url"])
                elif "b64_json" in item and item["b64_json"]:
                    urls.append(f"data:image/png;base64,{item['b64_json']}")
            if urls:
                return urls

        # 格式3: choices 中 message.content 为字符串（含 data URI）
        choices2 = result.get("choices", [])
        if choices2:
            for choice in choices2:
                msg = choice.get("message", {})
                content = msg.get("content", "")
                if isinstance(content, str) and content.startswith("data:image"):
                    urls.append(content)
                elif isinstance(content, list):
                    for item in content:
                        if isinstance(item, dict):
                            if item.get("type") == "image" and item.get("image"):
                                urls.append(item["image"])
                            elif item.get("image_url", {}).get("url"):
                                urls.append(item["image_url"]["url"])
            if urls:
                return urls

        return urls

    def _post_json(self, url, auth, payload, timeout=120, retries=2):
        headers = {
            "Authorization": auth,
            "Content-Type": "application/json"
        }
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        for i in range(1, retries + 2):
            try:
                r = requests.post(url, headers=headers, data=body, timeout=timeout)
                if r.status_code == 429:
                    ra = r.headers.get("Retry-After")
                    wait = float(ra) if ra else 5.0 * i
                    print(f"[Wan2.7] ⚠️ 429限流，第{i}/{retries}次重试，等{wait:.1f}s")
                    time.sleep(wait)
                    continue
                return r
            except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
                if i <= retries:
                    print(f"[Wan2.7] ⚠️ {type(e).__name__}，重试{i}/{retries}")
                    time.sleep(3.0)
                    continue
                return None

    def _print_error(self, r):
        try:
            d = r.json()
            msg = d.get("message", d.get("code", "unknown"))
            print(f"[Wan2.7] ❌ {msg}")
        except:
            print(f"[Wan2.7] ❌ HTTP {r.status_code}: {r.text[:300]}")


# ===================================================================
register_node(Wan27_Image, "Wan2.7-Image")
