# Aiya_mmx_Hailuo23_FL2V_DMX.py
# 💕 哎呀✦MiniMax-Hailuo-02 首尾帧生视频（内置运镜选单 + 提示词模板）
from __future__ import annotations
import cv2
import time
import requests
import base64
import io
import uuid
from pathlib import Path
from PIL import Image
import folder_paths
from ..register import register_node
from ..video_adapter import Video
from .MMX_nodes_image_save_jpg import ImageSaveJPG as _save_jpg

BASE_URL = "https://www.dmxapi.cn"
MODEL = "MiniMax-Hailuo-02"          # 首尾帧专用模型
POLL_INT = 2
MAX_POLL = 200

# ===== 官方 15 种运镜指令 =====
CAMERA_MOVES = [
    "无", "[左移]", "[右移]",
    "[左摇]", "[右摇]", "[推进]", "[拉远]",
    "[上升]", "[下降]", "[上摇]", "[下摇]",
    "[变焦推近]", "[变焦拉远]", "[晃动]", "[跟随]", "[固定]"
]

# ===== 常用镜头模板 =====
SHOT_TEMPLATE = {
    "无": "",
    "人物特写": "a close-up shot of a person, ",
    "半身中景": "a medium shot of upper body, ",
    "全身远景": "a full-body long shot, ",
    "推镜特写": "a smooth push-in close-up shot, ",
    "拉镜远景": "a smooth pull-out long shot, ",
    "左移跟随": "camera pans left following subject, ",
    "右移跟随": "camera pans right following subject, ",
    "上升俯视": "camera rises to overhead view, ",
    "下降仰视": "camera descends to low-angle view, "
}


# ---------- 工具 ----------
def image_to_base64(path: str) -> str:
    """图片→base64，自动压缩到 <20 MB，边长≤7680"""
    path = Path(path).expanduser().resolve()
    if not path.exists():
        raise RuntimeError(f"指定图片不存在：{path}")
    with Image.open(path) as img:
        img = img.convert("RGB")
        w, h = img.size
        if w * h > 7680 * 7680:
            img.thumbnail((7680, 7680), Image.LANCZOS)
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG", quality=95)
        if buffer.tell() > 19 * 1024 * 1024:          # >19 MB 再压
            buffer.seek(0); buffer.truncate()
            img.save(buffer, format="JPEG", quality=75)
        buffer.seek(0)
        b64 = base64.b64encode(buffer.read()).decode()
        return f"data:image/jpeg;base64,{b64}"


def _download_file(url: str, dst: Path, max_retry: int = 3, timeout: int = 120):
    for attempt in range(1, max_retry + 1):
        try:
            print(f"[Download] 第 {attempt}/{max_retry} 次：{url}")
            with requests.get(url, stream=True, timeout=timeout) as r:
                r.raise_for_status()
                with open(dst, "wb") as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                print(f"[Download] 成功 → {dst}")
                return
        except Exception as e:
            print(f"[Download] 第 {attempt} 次失败：{e}")
            if attempt == max_retry:
                raise RuntimeError(f"下载失败（重试 {max_retry} 次）：{e}")
            time.sleep(2)


# ---------- 节点 ----------
class Hailuo23FirstLast2Video:
    DESCRIPTION = (
        "💕 哎呀✦MiniMax-Hailuo-02 首尾帧生视频（官方 15 种运镜 + 镜头模板）\n\n"
        "【必填】\n"
        "  api_key   : 平台 sk-********************************\n"
        "  prompt    : 视频描述，最大 2000 字符，支持 [运镜] 语法\n"
        "  first_image : 首帧（决定输出分辨率）\n"
        "  last_image  : 尾帧（尺寸不一致时自动裁剪）\n\n"
        "【选单】\n"
        "  shot_template : 镜头模板（无 / 人物特写 / 半身中景 / 全身远景 / 推镜特写 / 拉镜远景 / 左移跟随 / 右移跟随 / 上升俯视 / 下降仰视）\n"
        "  camera_move   : 15 种官方运镜指令\n"
        "  duration      : 6 s 或 10 s（1080P 仅 6 s）\n"
        "  resolution    : 768P（默认）或 1080P\n"
        "  seed          : -1 随机，≥0 固定\n\n"
        "【运镜语法】\n"
        "  组合：同一 [] 内逗号分隔，如 [左摇,上升]，建议 ≤3 个\n"
        "  顺序：prompt 中前后依次生效，如 “...[推进], 然后...[拉远]”\n"
        "  节点已自动拼接“镜头模板 + 运镜指令 + 用户 prompt”\n\n"
        "【图片要求】\n"
        "  格式：JPG/JPEG/PNG/WebP，<20 MB，短边 >300 px，长宽比 2:5~5:2\n"
        "  节点内部自动缩图 & 二次压缩，保证 ≤19 MB\n\n"
        "【时长×分辨率】\n"
        "  MiniMax-Hailuo-02\n"
        "  6s：768P 或 1080P\n"
        "  10s：仅 768P\n\n"
        "【返回】\n"
        "  video        : ComfyUI VIDEO 对象\n"
        "  download_url : 公网直链，24 h 有效\n\n"
        "【限速】单任务轮询上限 400 s，失败自动抛异常"
    )
    RETURN_TYPES = ("VIDEO", "STRING")
    RETURN_NAMES = ("video", "download_url")
    FUNCTION = "generate"
    CATEGORY = "哎呀✦MMX/video"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "api_key": ("STRING", {"default": "", "multiline": False}),
                "first_image": ("IMAGE",),
                "last_image": ("IMAGE",),
                "shot_template": (list(SHOT_TEMPLATE.keys()), {"default": "无"}),
                "camera_move": (CAMERA_MOVES, {"default": "无"}),
                "prompt": ("STRING", {"default": "", "multiline": True,
                                      "placeholder": "在此写主体描述，如：A little girl grow up."}),
                "duration": (["6", "10"], {"default": "6"}),
                "resolution": (["768P", "1080P"], {"default": "768P"}),
                "seed": ("INT", {"default": -1, "min": -1, "max": 0xffffffffffffffff}),
            }
        }

    def generate(self, api_key, first_image, last_image, shot_template,
                 camera_move, prompt, duration, resolution, seed):
        if not api_key.strip():
            raise RuntimeError("❌ API-Key 为空")
        token = api_key.strip()

        # ① 保存首帧、尾帧 → 临时 JPG
        saver = _save_jpg()
        first_path = saver.save_images(
            images=first_image, filename_prefix="temp/hailuo23_fl2v_first",
            quality=95, optimize=True, progressive=False,
            save_prompt_as_txt=False, prompt=None, extra_pnginfo=None
        )["result"][1]
        last_path = saver.save_images(
            images=last_image, filename_prefix="temp/hailuo23_fl2v_last",
            quality=95, optimize=True, progressive=False,
            save_prompt_as_txt=False, prompt=None, extra_pnginfo=None
        )["result"][1]
        print(f"[Hailuo23-FL2Vid] 首帧路径：{first_path}")
        print(f"[Hailuo23-FL2Vid] 尾帧路径：{last_path}")

        # ② 拼 prompt
        shot = SHOT_TEMPLATE.get(shot_template, "")
        move = camera_move if camera_move != "无" else ""
        final_prompt = f"{shot}{move}{prompt.strip()}".strip()
        print(f"[Hailuo23-FL2Vid] 最终 prompt：{final_prompt}")

        # ③ Base64 首尾帧
        first_b64 = image_to_base64(first_path)
        last_b64 = image_to_base64(last_path)

        # ④ 提交任务
        submit_url = f"{BASE_URL}/v1/video_generation"
        payload = {
            "model": MODEL,
            "prompt": final_prompt,
            "first_frame_image": first_b64,
            "last_frame_image": last_b64,
            "duration": int(duration),
            "resolution": resolution,
            "prompt_optimizer": True,
            "aigc_watermark": False,
        }
        if seed != -1:
            payload["seed"] = int(seed)

        print("[Hailuo23-FL2Vid] 提交首尾帧任务...")
        resp = requests.post(submit_url, json=payload,
                             headers={"Content-Type": "application/json",
                                      "Authorization": f"Bearer {token}"},
                             timeout=90)
        if resp.status_code != 200:
            raise RuntimeError(f"提交失败 HTTP {resp.status_code}: {resp.text[:300]}")
        task_id = resp.json()["task_id"]
        print(f"[Hailuo23-FL2Vid] task_id = {task_id}")

        # ⑤ 轮询
        query_url = f"{BASE_URL}/v1/query/video_generation"
        start_t = time.time()
        for cnt in range(1, MAX_POLL + 1):
            time.sleep(POLL_INT)
            q = requests.get(query_url, params={"task_id": task_id},
                             headers={"Authorization": f"Bearer {token}"}, timeout=30)
            if q.status_code != 200:
                print(f"[Hailuo23-FL2Vid] 查询异常 HTTP {q.status_code}，重试…")
                continue
            raw = q.json()
            status = raw.get("status") or raw.get("state") or "unknown"
            file_id = raw.get("file_id")
            if status.lower() == "processing":
                used = time.time() - start_t
                remain = (MAX_POLL - cnt) * POLL_INT
                print(f"\r[Hailuo23-FL2Vid] 处理中… {cnt}/{MAX_POLL} "
                      f"已用 {used:.1f}s 预估剩余 {remain:.1f}s", end="")
                continue
            if status.lower() == "success" and file_id:
                print("\r[Hailuo23-FL2Vid] 任务完成！           ")
                break
            if status.lower() == "failed":
                raise RuntimeError(f"任务失败: {raw}")
        else:
            raise RuntimeError("⏰ 轮询超时")

        # ⑥ 获取下载链接
        retrieve_url = f"{BASE_URL}/v1/files/retrieve"
        dl_resp = requests.get(retrieve_url,
                               params={"file_id": file_id, "task_id": task_id},
                               headers={"Authorization": f"Bearer {token}"}, timeout=30)
        if dl_resp.status_code != 200:
            raise RuntimeError(f"获取下载链接失败 HTTP {dl_resp.status_code}")
        download_url = dl_resp.json()["file"]["download_url"]
        print(f"[Hailuo23-FL2Vid] 下载链接：{download_url}")

        # ⑦ 下载 → VIDEO 对象
        output_dir = Path(folder_paths.get_output_directory())
        output_dir.mkdir(exist_ok=True)
        video_path = output_dir / f"hailuo23_fl2v_{uuid.uuid4().hex[:8]}.mp4"
        _download_file(download_url, video_path)

        cap = cv2.VideoCapture(str(video_path))
        fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
        w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        cap.release()
        video = Video(str(video_path), fps, w, h)
        print(f"[Hailuo23-FL2Vid] VIDEO 对象已生成：{video}")
        return (video, download_url)


register_node(Hailuo23FirstLast2Video, "Hailuo23-首尾帧生视频-DMX")