"""
💕 哎呀✦MMX 通用视频下载节点
自动下载 + 返回本地路径字符串 → 下游接「LoadVideo」即可
文件：Aiya_mmx_DownloadVideo.py
注册：DownloadVideo
"""
from __future__ import annotations
import os
import time
import requests
from pathlib import Path
from datetime import datetime
import folder_paths
from ..register import register_node
from ..date_variable import replace_date_vars   # 与你 saveJPG 完全相同

OUTPUT_DIR = Path(folder_paths.get_output_directory())
OUTPUT_DIR.mkdir(exist_ok=True)


class DownloadVideo:
    DESCRIPTION = (
        "💕 哎呀✦通用视频下载节点\n\n"
        "输入：http/https 直链（.mp4/.mov/.avi 等）\n"
        "输出：本地文件路径字符串 → 下游接「LoadVideo」即可\n\n"
        "文件名：支持与你 saveJPG 完全相同的日期变量\n"
        "例如 %Aiya:yyyyMMdd%  → 20251213\n"
        "保存路径：官方 output 目录，自动防重名"
    )
    RETURN_TYPES = ("STRING",)   # ← 路径字符串
    RETURN_NAMES = ("path",)
    FUNCTION = "download"
    CATEGORY = "哎呀✦MMX/video"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "download_url": ("STRING", {"default": "", "multiline": False, "placeholder": "https://example.com/video.mp4"}),
                "filename_prefix": ("STRING", {"default": "%Aiya:yyyyMMdd%", "multiline": False}),
                "timeout_seconds": ("INT", {"default": 300, "min": 30, "max": 1800, "step": 30}),
            }
        }

    def download(self, download_url: str, filename_prefix: str, timeout_seconds: int):
        if not download_url.strip():
            raise RuntimeError("❌ 下载链接为空")

        url = download_url.strip()
        # 1. 与你 saveJPG 完全相同的变量替换 + 路径安全
        prefix = replace_date_vars(filename_prefix.strip(), safe_path=True)
        # 2. 官方防重名 + 自动子目录
        full_output_folder, filename, counter, subfolder, filename_prefix = folder_paths.get_save_image_path(
            prefix, folder_paths.get_output_directory(), 1920, 1080)
        # 3. 短文件名：前缀_00001.mp4
        fname = f"{filename}_{counter:05}.mp4"
        video_path = Path(full_output_folder) / fname

        print(f"[DownloadVideo] 开始下载 → {url}")
        try:
            with requests.get(url, stream=True, timeout=timeout_seconds) as r:
                r.raise_for_status()
                total = int(r.headers.get("content-length", 0))
                down = 0
                with open(video_path, "wb") as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        if not chunk:
                            continue
                        f.write(chunk)
                        down += len(chunk)
                        if total:
                            print(f"\r[DownloadVideo] 进度 {down}/{total}  {down*100/total:.1f}%", end="")
                print()
        except Exception as e:
            raise RuntimeError(f"下载失败：{e}")

        print(f"[DownloadVideo] 已保存 → {video_path}")
        # 只返回路径字符串
        return (str(video_path),)


register_node(DownloadVideo, "DownloadVideo")