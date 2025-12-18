# ~/ComfyUI/custom_nodes/Aiya_mmx/nodes/string_tools.py
from __future__ import annotations
from ..date_variable import replace_date_vars
from ..register import register_node


class JoinStrings_mmx:
    DESCRIPTION = (
        "💕 哎呀✦多字符串拼接节点（STRING 输出）\n\n"
        "输入：9 个 STRING 口（拉线即增）\n"
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
                "text1": ("STRING",),
                "text2": ("STRING",),
                "text3": ("STRING",),
                "text4": ("STRING",),
                "text5": ("STRING",),
                "text6": ("STRING",),
                "text7": ("STRING",),
                "text8": ("STRING",),
                "text9": ("STRING",),
            }
        }

    def join(self, connector: str,
             text1: str = "", text2: str = "",
             text3: str = "", text4: str = "",
             text5: str = "", text6: str = "",
             text7: str = "", text8: str = "",
             text9: str = "") -> tuple[str,]:
        # 日期变量替换
        connector = replace_date_vars(connector, safe_path=False)
        # 空分隔符自动换行
        if connector == "":
            connector = "\n"

        # 收集非空输入，保留空行和前后空格
        parts = [t for t in (text1, text2, text3, text4, text5,
                             text6, text7, text8, text9) if t is not None]
        result = connector.join(parts)
        print(f"[JoinStrings_mmx] 拼接完成 → {repr(result)}")
        return (result,)


class SplitString_mmx:
    DESCRIPTION = (
        "💕 哎呀✦字符串分割节点（1→9 STRING）\n\n"
        "输入：任意字符串\n"
        "输出：9个STRING口，按换行或自定义分隔符切分，空位补\"\"\n\n"
        "分隔符：留空=换行分割"
    )
    RETURN_TYPES = tuple(["STRING"] * 9)
    RETURN_NAMES = tuple([f"string{i}" for i in range(1, 10)])
    FUNCTION = "split"
    CATEGORY = "哎呀✦MMX/text"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {"default": "", "multiline": True}),
                "separator": ("STRING", {"default": "", "multiline": False}),
            }
        }

    def split(self, text: str, separator: str) -> tuple[str, ...]:
        # 替换日期变量
        text = replace_date_vars(text, safe_path=False)
        separator = replace_date_vars(separator, safe_path=False)

        # 分割
        if separator == "":
            parts = text.splitlines()
        else:
            parts = text.split(separator)

        # 只留前 9 段，不足补空
        parts = parts[:9] + [""] * (9 - len(parts))
        result = tuple(p.strip() for p in parts)
        print(f"[SplitString_mmx] 分割完成 → {result}")
        return result


# 注册节点
register_node(JoinStrings_mmx, "JoinStrings_mmx")
register_node(SplitString_mmx, "SplitString_mmx")
