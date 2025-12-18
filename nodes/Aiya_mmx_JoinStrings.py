# Aiya_mmx_JoinStrings.py
"""
💕 哎呀✦多字符串拼接节点
输入：5 个 STRING 口（拉线即增）
输出：橙色 STRING → 下游任意字符串节点即插即用
注册：JoinStrings_mmx
"""
from __future__ import annotations
from ..register import register_node
from ..date_variable import replace_date_vars


class JoinStrings_mmx:
    DESCRIPTION = (
        "💕 哎呀✦多字符串拼接节点（STRING 输出）\n\n"
        "输入：5 个 STRING 口（拉线即增）\n"
        "输出：橙色 STRING → 下游任意字符串节点即插即用\n\n"
        "连接符：可空；空=换行拼接"
    )
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("string",)
    FUNCTION = "join"
    CATEGORY = "哎呀✦MMX/text"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "connector": ("STRING", {"default": "", "multiline": False}),
            },
            "optional": {
                "text1": ("STRING",),   # 拉线输入
                "text2": ("STRING",),
                "text3": ("STRING",),
                "text4": ("STRING",),
                "text5": ("STRING",),
            }
        }

    def join(self, connector: str,
             text1: str = "", text2: str = "",
             text3: str = "", text4: str = "",
             text5: str = "") -> tuple[str,]:
        # 日期变量替换
        connector = replace_date_vars(connector, safe_path=False)
        # 空分隔符自动换行
        if connector == "":
            connector = "\n"

        # 收集非空输入，保留空行和前后空格
        parts = [t for t in (text1, text2, text3, text4, text5) if t is not None]
        result = connector.join(parts)
        print(f"[JoinStrings_mmx] 拼接完成 → {repr(result)}")
        return (result,)


register_node(JoinStrings_mmx, "JoinStrings_mmx")
