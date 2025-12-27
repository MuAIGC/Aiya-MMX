# Aiya_mmx_PromptProcessor_DMX.py
from __future__ import annotations
import requests
from ..register import register_node

# ---------- 节点 ----------
class PromptProcessor_DMX:
    DESCRIPTION = (
        "💡 哎呀✦通用提示词处理器\n\n"
        "支持自定义系统提示 + 主题内容提示 | 可手动填 key 或接上游\n"
        "输出模型返回文本 + 任务信息（成功/异常）"
    )
    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("response", "log")
    FUNCTION = "process"
    CATEGORY = "哎呀✦MMX/DMXAPI"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "system_prompt": ("STRING", {"multiline": True, "placeholder": "系统提示词（可空）"}),
                "user_prompt": ("STRING", {"multiline": True, "placeholder": "主题内容提示词"}),
                "api_key": ("STRING", {"default": "", "placeholder": "sk-***************************"}),
            }
        }

    def process(self, system_prompt: str, user_prompt: str, api_key: str):
        if not api_key.strip():
            return ("", "❌ api_key 为空，已拦截")

        messages = []
        if system_prompt.strip():
            messages.append({"role": "system", "content": system_prompt.strip()})
        messages.append({"role": "user", "content": user_prompt.strip()})

        payload = {
            "model": "gpt-5-mini",
            "input": messages
        }
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key.strip()}"
        }

        try:
            resp = requests.post("https://www.dmxapi.cn/v1/responses",
                                 headers=headers, json=payload, timeout=120)
            if resp.status_code != 200:
                return ("", f"❌ HTTP {resp.status_code}: {resp.text[:200]}")
            out_list = resp.json()["output"]
            text_block = next(x for x in out_list if x["type"] == "message")["content"]
            answer = next(x for x in text_block if x["type"] == "output_text")["text"]
            return (answer, "✅ 处理成功")
        except Exception as e:
            return ("", f"❌ 解析失败: {e}")


register_node(PromptProcessor_DMX, "提示词处理器_DMX")