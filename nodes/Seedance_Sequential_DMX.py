"""
╔══════════════════════════════════════════════════════════════════════════════╗
║          Seedance 超长视频连续生成节点 - 多模态视觉分析版                    ║
║  原理：LLM看图→提取视觉一致性→智能 timeline 切分→首尾帧接力→FFmpeg合并       ║
╚══════════════════════════════════════════════════════════════════════════════╝
💡 工作流程：
   1. LLM 视觉分析首帧图：提取人物服装、外貌、场景风格、气质音色
   2. 结合用户提示词（支持故障艺术/穿模/掉帧等特殊风格），生成时间线分镜
   3. 每段提示词强制锁定：视觉一致性 + 声音一致性 + 当前时段剧情
   4. 链式生成：段1尾帧→段2首帧... FFmpeg无损合并
"""

from __future__ import annotations
import os
import io
import re
import json
import time
import uuid
import base64
import random
import shutil
import subprocess
import requests
import cv2
import torch
import numpy as np
from pathlib import Path
from PIL import Image
from typing import List, Tuple, Optional, Dict

import folder_paths
from ..register import register_node

DEFAULT_API_URL = "https://www.dmxapi.cn"
SEEDANCE_MODEL = "doubao-seedance-1-5-pro-responses"
QUERY_MODEL = "seedance-get"
MAX_SEED = 4294967295

class Video:
    __slots__ = ("path", "_fps", "width", "height")
    def __init__(self, path: str, fps: float, width: int, height: int):
        self.path = path; self._fps = fps; self.width = width; self.height = height
    @property
    def fps(self): return self._fps
    def get_dimensions(self): return (self.width, self.height)
    def save_to(self, dst: str | Path, **kw):
        shutil.copy2(self.path, dst); return True
    def __repr__(self): return f"Video({self.path} {self._fps:.2f}fps {self.width}x{self.height})"


def image_to_base64(img_tensor) -> str:
    """ComfyUI tensor → base64 data URL"""
    if img_tensor is None: raise ValueError("输入图像为空")
    img = img_tensor[0] if img_tensor.dim() == 4 else img_tensor
    img = (img * 255).clamp(0, 255).byte().cpu().numpy()
    pil_img = Image.fromarray(img).convert("RGB")
    buffer = io.BytesIO()
    quality = 95
    while True:
        buffer.seek(0); buffer.truncate()
        pil_img.save(buffer, format="JPEG", quality=quality, optimize=True)
        if buffer.tell() < 19 * 1024 * 1024 or quality <= 10: break
        quality -= 5
    b64 = base64.b64encode(buffer.getvalue()).decode()
    return f"data:image/jpeg;base64,{b64}"


def tensor_from_pil(pil_img: Image.Image) -> torch.Tensor:
    img = np.array(pil_img.convert("RGB")).astype(np.float32) / 255.0
    tensor = torch.from_numpy(img)
    if tensor.dim() == 3: tensor = tensor.unsqueeze(0)
    return tensor


def extract_video_last_frame(video_path: Path) -> torch.Tensor:
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened(): raise RuntimeError(f"无法打开视频: {video_path}")
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    if total_frames <= 0: cap.release(); raise RuntimeError("视频帧数为0")
    cap.set(cv2.CAP_PROP_POS_FRAMES, total_frames - 1)
    ret, frame = cap.read()
    cap.release()
    if not ret or frame is None: raise RuntimeError("无法读取视频最后一帧")
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    return tensor_from_pil(Image.fromarray(frame_rgb))


def merge_videos_ffmpeg(video_paths: List[Path], output_path: Path) -> bool:
    try:
        list_file = output_path.parent / f"concat_list_{uuid.uuid4().hex[:8]}.txt"
        with open(list_file, "w", encoding="utf-8") as f:
            for vp in video_paths:
                path_str = str(vp).replace("\\", "/").replace("'", "'\\''")
                f.write(f"file '{path_str}'\n")
        cmd = [
            "ffmpeg", "-y", "-f", "concat", "-safe", "0",
            "-i", str(list_file), "-c", "copy", "-movflags", "+faststart",
            str(output_path)
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        list_file.unlink(missing_ok=True)
        if result.returncode != 0:
            print(f"[FFmpeg] 失败: {result.stderr[:200]}"); return False
        print(f"[FFmpeg] 合并成功（含音频）: {output_path.name}"); return True
    except FileNotFoundError:
        print("[FFmpeg] 未找到，回退到 OpenCV"); return False
    except Exception as e:
        print(f"[FFmpeg] 异常: {e}"); return False


def merge_videos_opencv(video_paths: List[Path], output_path: Path):
    if not video_paths: raise ValueError("视频路径为空")
    first_cap = cv2.VideoCapture(str(video_paths[0]))
    if not first_cap.isOpened(): raise RuntimeError(f"无法打开: {video_paths[0]}")
    ref_w = int(first_cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    ref_h = int(first_cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    ref_fps = first_cap.get(cv2.CAP_PROP_FPS) or 25.0
    first_cap.release()
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    writer = cv2.VideoWriter(str(output_path), fourcc, ref_fps, (ref_w, ref_h))
    if not writer.isOpened(): raise RuntimeError("VideoWriter 失败")
    total_frames = 0
    try:
        for idx, vp in enumerate(video_paths):
            cap = cv2.VideoCapture(str(vp))
            if not cap.isOpened(): print(f"[OpenCV] 跳过: {vp}"); continue
            curr_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            curr_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            need_resize = (curr_w != ref_w) or (curr_h != ref_h)
            while True:
                ret, frame = cap.read()
                if not ret: break
                if need_resize: frame = cv2.resize(frame, (ref_w, ref_h), interpolation=cv2.INTER_LANCZOS4)
                writer.write(frame); total_frames += 1
            cap.release()
            print(f"[OpenCV] 第 {idx+1}段完成")
    finally: writer.release()
    if total_frames == 0: raise RuntimeError("无帧写入")
    print(f"[OpenCV] 合并完成（无声）: {output_path.name}")


def merge_videos(video_paths: List[Path], output_path: Path):
    if len(video_paths) == 1: shutil.copy2(video_paths[0], output_path); return
    if merge_videos_ffmpeg(video_paths, output_path): return
    print("[Merge] 回退到 OpenCV..."); merge_videos_opencv(video_paths, output_path)


def build_video_obj(video_path: Path) -> Video:
    cap = cv2.VideoCapture(str(video_path))
    fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    cap.release()
    return Video(str(video_path), fps, w, h)


class StoryboardLLM:
    """多模态分镜导演：先看图，再切分时间线"""
    
    def __init__(self, api_url: str, api_key: str, model: str = "gpt-4o"):
        self.api_url = api_url.rstrip("/")
        self.api_key = api_key
        self.model = model
        
    def calculate_segments(self, total_seconds: int) -> List[int]:
        """计算分段：尽量10s，余数5s"""
        segments = []
        remaining = total_seconds
        while remaining > 0:
            if remaining >= 10: segments.append(10); remaining -= 10
            elif remaining >= 5: segments.append(5); remaining -= 5
            else: segments.append(5); remaining = 0
        return segments
    
    def analyze_and_split(self, 
                          user_prompt: str, 
                          total_seconds: int,
                          first_frame_b64: str,
                          system_override: Optional[str] = None) -> Tuple[List[Tuple[int, str]], Dict, str]:
        """
        多模态分析：看图 + 读提示词 → 提取一致性 → 时间线切分
        返回: (segments, analysis_dict, raw_llm_output)
        """
        segments = self.calculate_segments(total_seconds)
        n_segments = len(segments)
        
        # 构造多模态消息（图+文）
        user_content = [
            {
                "type": "image_url",
                "image_url": {"url": first_frame_b64, "detail": "high"}
            },
            {
                "type": "text",
                "text": f"""分析这张首帧图，并结合以下创意描述，生成{total_seconds}秒视频的分镜脚本（共{n_segments}段）。

【用户创意描述】：
{user_prompt}

【特殊风格说明】
如果提示词包含"穿模"、"掉帧"、"贴图错误"、"手Bug"等词汇，这是故意的"故障艺术"（Glitch Art）风格，不是真的渲染错误。请在分镜中延续这种"AI恐怖谷"美学。

【任务要求】
1. 先详细描述图中的人物外貌、服装、环境光线（提取视觉一致性）
2. 分析人物性别年龄，推断应该匹配的音色特征（提取声音一致性）
3. 将用户创意按时间线切分为{n_segments}段，每段必须是剧情的延续，严禁重复
4. 每段提示词必须包含：一致性锁定 + 该时段的具体画面 + 运镜

【输出格式 - 严格JSON】
{{
  "visual_analysis": {{
    "person": "人物详细外貌服装",
    "environment": "场景光线色调",
    "style": "画面风格关键词"
  }},
  "audio_analysis": {{
    "voice_type": "音色描述（如年轻女性清脆声线）",
    "speaking_style": "语速语气（如连珠炮机械音）"
  }},
  "consistency_lock": "总结所有必须保持一致的视觉和声音要素",
  "timeline": [
    {{"segment_id": 1, "time_range": "0-10s", "prompt": "第1段独有的画面描述，包含故障艺术细节"}},
    {{"segment_id": 2, "time_range": "10-20s", "prompt": "第2段全新的画面，接续前段剧情"}}
  ]
}}"""
            }
        ]
        
        default_system = """你是专业的AI视频分镜导演，擅长多模态视觉分析。
规则：
1. 必须严格按时间线推进，第2段绝对不能重复第1段内容
2. 故障艺术风格（穿模/掉帧）是feature不是bug，要延续
3. 画面严禁出现文字、字幕、UI元素
4. 只输出JSON，不要任何解释"""

        system_msg = system_override if system_override else default_system
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        raw_content = ""
        try:
            resp = requests.post(
                f"{self.api_url}/v1/chat/completions",
                headers=headers,
                json={
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": system_msg},
                        {"role": "user", "content": user_content}
                    ],
                    "temperature": 0.4,
                    "max_tokens": 3000,
                    "response_format": {"type": "json_object"}  # 强制JSON输出
                },
                timeout=90
            )
            resp.raise_for_status()
            raw_content = resp.json()["choices"][0]["message"]["content"]
            print(f"[LLM Vision Raw]\n{raw_content[:800]}...")
            
            data = json.loads(raw_content)
            
            # 提取分析结果
            analysis = {
                "visual": data.get("visual_analysis", {}),
                "audio": data.get("audio_analysis", {}),
                "consistency": data.get("consistency_lock", "")
            }
            
            # 提取时间线
            timeline = data.get("timeline", [])
            if not timeline or len(timeline) < n_segments:
                raise ValueError(f"分镜数量不足，期望{n_segments}，实际{len(timeline) if timeline else 0}")
            
            # 构造最终segments
            result = []
            consistency_text = analysis["consistency"]
            
            for i, item in enumerate(timeline[:n_segments]):
                duration = segments[i]
                seg_prompt = item.get("prompt", "")
                time_range = item.get("time_range", f"{i*10}-{(i+1)*10}s")
                
                # 强制注入一致性描述
                if consistency_text and consistency_text not in seg_prompt:
                    seg_prompt = f"{consistency_text}。{seg_prompt}"
                
                # 强制时间线标记
                seg_prompt = f"[{time_range}|Segment {i+1}/{n_segments}] {seg_prompt}"
                
                # 清理污染词
                seg_prompt = re.sub(r'\b(字幕|文字|text|subtitle|caption|重复|again)\b', '', seg_prompt, flags=re.IGNORECASE)
                
                result.append((duration, seg_prompt))
            
            return result, analysis, raw_content
            
        except Exception as e:
            print(f"[StoryboardLLM] 视觉分析失败: {e}，使用文本强制切分")
            # Fallback：按句子数切分
            return self._fallback_split(user_prompt, segments), {}, raw_content + f"\n[Error: {e}]"
    
    def _fallback_split(self, user_prompt: str, segments: List[int]) -> List[Tuple[int, str]]:
        """文本强制切分：按长度均匀分配"""
        # 简单按逗号/句号切分
        parts = [p.strip() for p in re.split(r'[。，,；;！!？?]', user_prompt) if p.strip()]
        total_parts = len(parts)
        lines_per_seg = max(1, total_parts // len(segments))
        
        result = []
        for i, duration in enumerate(segments):
            start = i * lines_per_seg
            end = start + lines_per_seg if i < len(segments) - 1 else total_parts
            seg_text = "，".join(parts[start:end]) if parts else user_prompt
            seg_text = f"[强制切分|第{i+1}段] {seg_text}"
            result.append((duration, seg_text))
        
        return result


class SeedanceSequentialVideo:
    """🎬 多模态超长视频生成：LLM看图→智能分镜→链式生成"""
    
    DESCRIPTION = """
💡 哎呀✦Seedance 视觉分析版 —— LLM先看首帧图，再生成一致性分镜
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ 工作流程：
   1. 多模态分析：LLM识别首帧图中的人物服装/外貌/环境/气质
   2. 智能分镜：结合用户提示词（支持故障艺术风格），按时间线切分
   3. 一致性锁定：视觉+声音特征在所有分镜中强制复现
   4. 链式生成：尾帧接力，FFmpeg无损合并

⚠️ 提示：
   • 支持"穿模/掉帧/贴图错误"等故障艺术风格，LLM会理解这是 intentional glitch
   • 若LLM vision不可用，自动回退到文本切分
    """
    
    RETURN_TYPES = ("VIDEO", "STRING", "STRING", "STRING", "IMAGE")
    RETURN_NAMES = ("video", "segments_info", "final_url", "llm_analysis", "preview_last_frame")
    FUNCTION = "generate_sequence"
    CATEGORY = "哎呀✦MMX/DMXAPI"
    
    @classmethod
    def INPUT_TYPES(cls):
        default_system = """你是专业的AI视频分镜导演，擅长分析图像并生成时间线分镜。
核心规则：
1. 先详细描述首帧图的视觉信息（人物服装、外貌、光线）
2. 分析人物气质，确定音色特征（性别、年龄、语速）
3. 将剧情按时间线推进，第N段必须是第N-1段的延续，绝对禁止重复
4. 支持故障艺术（Glitch Art）：穿模、掉帧、贴图错误是美的表达，不是Bug
5. 输出严格JSON，画面严禁文字/字幕"""
        
        return {
            "required": {
                "api_url": ("STRING", {"default": DEFAULT_API_URL, "multiline": False}),
                "api_key": ("STRING", {"default": "sk-", "multiline": False}),
                "first_frame": ("IMAGE",),
                "total_duration_sec": ("INT", {"default": 20, "min": 10, "max": 120, "step": 10}),
                "prompt": ("STRING", {
                    "multiline": True,
                    "default": "人物自信逼近镜头，故障艺术风格，穿模掉帧",
                    "placeholder": "描述剧情，支持故障艺术/穿模/掉帧等特殊风格..."
                }),
                "system_prompt": ("STRING", {
                    "default": default_system,
                    "multiline": True,
                    "placeholder": "多模态分析系统提示词..."
                }),
                "resolution": (["480p", "720p", "1080p"], {"default": "720p"}),
                "ratio": (["16:9", "9:16", "1:1", "4:3", "3:4", "21:9"], {"default": "9:16"}),
                "llm_model": ("STRING", {"default": "gpt-4o", "multiline": False}),
            },
            "optional": {
                "seed": ("INT", {"default": -1, "min": -1, "max": MAX_SEED}),
                "generate_audio": (["开启", "关闭"], {"default": "开启"}),
                "watermark": (["无", "添加"], {"default": "无"}),
            }
        }
    
    def submit_segment(self, api_url: str, token: str, prompt: str, 
                       first_frame_b64: str, resolution: str, ratio: str, 
                       duration: int, seed: int, generate_audio: bool, 
                       watermark: bool) -> str:
        ratio_clean = ratio
        input_arr = [
            {"type": "text", "text": prompt},
            {"type": "image_url", "image_url": {"url": first_frame_b64}, "role": "first_frame"}
        ]
        actual_seed = random.randint(0, MAX_SEED) if seed == -1 else seed
        if actual_seed > MAX_SEED: actual_seed = actual_seed % (MAX_SEED + 1)
        payload = {
            "model": SEEDANCE_MODEL,
            "input": input_arr,
            "callback_url": "",
            "return_last_frame": False,
            "generate_audio": generate_audio,
            "resolution": resolution,
            "ratio": ratio_clean,
            "duration": duration,
            "seed": actual_seed,
            "camera_fixed": False,
            "watermark": watermark
        }
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token.strip()}"
        }
        url = f"{api_url.rstrip('/')}/v1/responses"
        resp = requests.post(url, json=payload, headers=headers, timeout=30)
        resp.raise_for_status()
        result = resp.json()
        if "id" not in result: raise RuntimeError(f"提交失败: {result}")
        return result["id"]
    
    def query_segment(self, api_url: str, task_id: str, token: str) -> str:
        url = f"{api_url.rstrip('/')}/v1/responses"
        payload = {"model": QUERY_MODEL, "input": task_id, "stream": True}
        headers = {"Content-Type": "application/json", "Authorization": f"Bearer {token.strip()}"}
        video_url = None
        with requests.post(url, json=payload, headers=headers, stream=True, timeout=180) as resp:
            resp.raise_for_status()
            for line in resp.iter_lines():
                if not line: continue
                line_str = line.decode('utf-8').strip()
                if line_str.startswith('data: '): line_str = line_str[6:]
                try:
                    data = json.loads(line_str)
                    if data.get('type') == "response.completed":
                        text = data.get('response', {}).get('output', [{}])[0].get('content', [{}])[0].get('text', '')
                        matches = re.findall(r'(https://[^\s\n\"]+(?:\.mp4|\.mov)[^\s\n\"]*)', text)
                        if matches: video_url = matches[0].rstrip('.,;')
                except: continue
        if not video_url: raise RuntimeError("未获取视频URL")
        return video_url
    
    def download_segment(self, url: str, save_path: Path):
        for attempt in range(3):
            try:
                with requests.get(url, stream=True, timeout=120) as r:
                    r.raise_for_status()
                    with open(save_path, "wb") as f:
                        for chunk in r.iter_content(chunk_size=8192):
                            if chunk: f.write(chunk)
                return
            except Exception as e:
                print(f"[Download] 第{attempt+1}次失败: {e}")
                if attempt == 2: raise
                time.sleep(2 ** attempt)
    
    def generate_sequence(self, api_url, api_key, first_frame, total_duration_sec, 
                         prompt, system_prompt, resolution, ratio, llm_model,
                         seed=-1, generate_audio="开启", watermark="无"):
        
        token = api_key.strip()
        if not token or token == "sk-": raise RuntimeError("API Key 无效")
        
        output_dir = Path(folder_paths.get_output_directory()) / "seedance_sequential"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # 1. 准备首帧 base64
        first_frame_b64 = image_to_base64(first_frame)
        
        # 2. LLM 多模态分析 + 分镜
        print(f"[Sequential] 多模态分析首帧图 + 生成 {total_duration_sec}s 分镜...")
        print(f"[Sequential] 使用模型: {llm_model}")
        
        llm = StoryboardLLM(api_url, token, llm_model)
        segments, analysis, raw_llm = llm.analyze_and_split(
            prompt, total_duration_sec, first_frame_b64, system_prompt
        )
        
        segment_count = len(segments)
        print(f"[Sequential] 分镜完成: {segment_count} 段")
        
        # 打印分析结果
        if analysis:
            print(f"  [视觉分析] {analysis.get('visual', {}).get('person', 'N/A')[:50]}...")
            print(f"  [声音锁定] {analysis.get('audio', {}).get('voice_type', 'N/A')}")
        
        for i, (d, p) in enumerate(segments, 1):
            print(f"  段{i} ({d}s): {p[:70]}...")
        
        # 3. 逐段生成
        video_files = []
        current_frame = first_frame
        segment_infos = []
        last_frame_tensor = None
        
        for idx, (duration, seg_prompt) in enumerate(segments, 1):
            print(f"\n[Sequential] 生成第 {idx}/{segment_count} 段（{duration}s）...")
            
            try:
                frame_b64 = image_to_base64(current_frame)
                seg_seed = seed + idx - 1 if seed != -1 else -1
                
                task_id = self.submit_segment(
                    api_url, token, seg_prompt, frame_b64,
                    resolution, ratio, duration,
                    seg_seed,
                    generate_audio == "开启",
                    watermark == "添加"
                )
                
                video_url = self.query_segment(api_url, task_id, token)
                
                video_path = output_dir / f"seq_{idx:03d}_{uuid.uuid4().hex[:6]}.mp4"
                self.download_segment(video_url, video_path)
                video_files.append(video_path)
                
                segment_infos.append({
                    "segment": idx,
                    "duration": duration,
                    "prompt": seg_prompt,
                    "video_file": str(video_path.name),
                    "url": video_url
                })
                
                # 抽取尾帧作为下一段首帧
                if idx < segment_count:
                    print(f"[Sequential] 抽取尾帧...")
                    last_frame_tensor = extract_video_last_frame(video_path)
                    current_frame = last_frame_tensor
                else:
                    # 最后一段也抽帧，作为预览输出
                    last_frame_tensor = extract_video_last_frame(video_path)
                    
            except Exception as e:
                print(f"[Sequential] 第 {idx} 段失败: {e}")
                info_path = output_dir / f"failed_at_seg_{idx}.json"
                with open(info_path, "w", encoding="utf-8") as f:
                    json.dump({
                        "failed_at": idx, "error": str(e), 
                        "completed": [str(p) for p in video_files],
                        "llm_raw": raw_llm
                    }, f, ensure_ascii=False, indent=2)
                raise RuntimeError(f"第 {idx} 段失败: {e}")
        
        # 4. 合并
        final_name = f"seedance_long_{total_duration_sec}s_{uuid.uuid4().hex[:8]}.mp4"
        final_video = output_dir / final_name
        
        if len(video_files) == 1:
            shutil.copy2(video_files[0], final_video)
        else:
            print(f"[Sequential] 合并 {len(video_files)} 段...")
            merge_videos(video_files, final_video)
        
        # 5. 输出
        video_obj = build_video_obj(final_video)
        info_text = json.dumps({
            "total_duration": total_duration_sec,
            "segments_count": segment_count,
            "final_video": str(final_video),
            "llm_model": llm_model,
            "segments": segment_infos,
            "analysis": analysis
        }, ensure_ascii=False, indent=2)
        
        final_url = segment_infos[-1]["url"] if segment_infos else ""
        analysis_text = json.dumps(analysis, ensure_ascii=False, indent=2) if analysis else raw_llm
        
        return (video_obj, info_text, final_url, analysis_text, last_frame_tensor)


register_node(SeedanceSequentialVideo, "Seedance15Pro-超长视频生成-DMX")