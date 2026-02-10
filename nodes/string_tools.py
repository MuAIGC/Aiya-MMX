# ~/ComfyUI/custom_nodes/Aiya_mmx/nodes/string_tools.py
from __future__ import annotations
import os
from pathlib import Path
import folder_paths
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

class Strings2List_mmx:
    DESCRIPTION = (
        "💕 哎呀✦字符串分割→LIST<STRING>\n"
        "输入一段多行文本（或自定义分隔符）\n"
        "输出：LIST<STRING> + List<STRING>，空行自动跳过"
    )
    RETURN_TYPES = ("LIST", "STRING")
    RETURN_NAMES = ("string_list", "strings")
    FUNCTION = "split_to_list"
    CATEGORY = "哎呀✦MMX/text"
    OUTPUT_IS_LIST = [False, True]

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {"multiline": True, "default": ""}),
                "separator": ("STRING", {"default": "", "multiline": False}),
            }
        }

    def split_to_list(self, text: str, separator: str):
        # 日期变量替换
        text = replace_date_vars(text, safe_path=False)
        sep = replace_date_vars(separator, safe_path=False)

        # 分割并去空白、跳过空行
        parts = text.splitlines() if sep == "" else text.split(sep)
        items = [p.strip() for p in parts if p.strip()]

        print(f"[Strings2List_mmx] 分割完成 → {len(items)} 条字符串")
        return (items, items)

class StrReplace_mmx:
    DESCRIPTION = "💕 哎呀✦字符串查找替换（支持 \\n 转义）"
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("text",)
    FUNCTION = "apply"
    CATEGORY = "哎呀✦MMX/text"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text":    ("STRING", {"default": "", "multiline": True}),
                "find":    ("STRING", {"default": "", "multiline": False}),
                "replace": ("STRING", {"default": "", "multiline": False}),
            }
        }

    def apply(self, text: str, find: str, replace: str) -> tuple[str,]:
        # 让用户用 \n 字面量就能插入换行
        replace = replace.replace("\\n", "\n")
        find    = find.replace("\\n", "\n")
        out = text.replace(find, replace)
        print(f"[StrReplace_mmx] 替换完成")
        return (out,)


# 统一缓存目录，与 LoadImageFromPath_mmx 同级
CACHE_DIR = Path(folder_paths.get_output_directory()) / "Aiya/Aiya_path"

class SaveText_mmx:
    DESCRIPTION = "💕 哎呀✦字符串保存 *.txt，前缀里用 / 分目录，支持 %Aiya:xxx% 日期变量"

    def __init__(self):
        self.base_dir = folder_paths.get_output_directory()

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {"default": "", "multiline": True}),
                "filename_prefix": ("STRING", {"default": "Aiya/%Aiya:yyyyMMdd%/%Aiya:yyyyMMdd%_txt"}),
                "cache_name": ("STRING", {"default": "default", "multiline": False}),  # 新增：与LoadText配对
            },
            "hidden": {"prompt": "PROMPT", "extra_pnginfo": "EXTRA_PNGINFO", "unique_id": "UNIQUE_ID"},
        }

    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("txt_path", "text")
    FUNCTION = "save_text"
    OUTPUT_NODE = True
    CATEGORY = "哎呀✦MMX/text"

    def save_text(self, text, filename_prefix, cache_name,  # 新增 cache_name 参数
                  prompt=None, extra_pnginfo=None, unique_id=None):
        # 1. 替换日期变量
        prefix = replace_date_vars(filename_prefix, safe_path=True)
        # 2. 拆目录 & 文件前缀
        *folder_parts, name_prefix = prefix.split("/")
        out_dir = Path(self.base_dir).joinpath(*folder_parts)
        out_dir.mkdir(parents=True, exist_ok=True)

        # 3. 把节点 ID 拼到前缀里，保证多节点不撞车
        if unique_id:
            name_prefix = f"{name_prefix}_{unique_id}"

        # 4. 让 ComfyUI 帮你递增序号
        _, filename, counter, _, _ = folder_paths.get_save_image_path(
            name_prefix, str(out_dir), 1, 1)
        file_name = f"{filename}_{counter:05}.txt"
        save_path = out_dir / file_name

        # 5. 写文件 & 缓存
        save_path.write_text(text, encoding="utf-8")
        
        # 修复：使用输入的 cache_name，而不是不存在的 self.cache_name
        cache_name = (cache_name or "default").strip()
        cache_file = CACHE_DIR / f"{cache_name}.txtpath"
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        cache_file.write_text(str(save_path), encoding="utf-8")
        
        print(f"[SaveText_mmx] 文件保存至: {save_path}")
        print(f"[SaveText_mmx] 缓存写入: {cache_file} → {save_path}")

        return (str(save_path), text)


class LoadTextFromPath_mmx:
    DESCRIPTION = "💕 哎呀✦从 *.txt 路径读取字符串，空输入自动读缓存"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "path": ("STRING", {"default": "", "multiline": False}),
                "cache_name": ("STRING", {"default": "default", "multiline": False}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("text",)
    FUNCTION = "load_text"
    CATEGORY = "哎呀✦MMX/text"

    def load_text(self, path, cache_name):
        path = path.strip()
        cache_name = cache_name.strip() or "default"
        cache_file = CACHE_DIR / f"{cache_name}.txtpath"
        
        print(f"[LoadTextFromPath_mmx] 输入path: '{path}' | cache_name: '{cache_name}'")
        print(f"[LoadTextFromPath_mmx] 缓存文件位置: {cache_file}")

        # 空输入 → 读缓存
        if not path:
            if cache_file.exists():
                cached_path = cache_file.read_text(encoding="utf-8").strip()
                print(f"[LoadTextFromPath_mmx] 从缓存读取路径: '{cached_path}'")
                path = cached_path
            else:
                raise RuntimeError(f"LoadTextFromPath_mmx: 缓存「{cache_name}」不存在！缓存文件: {cache_file}")
        
        if not path:
            raise RuntimeError(f"LoadTextFromPath_mmx: 缓存「{cache_name}」内容为空！请先用SaveText保存，或手动输入路径。")

        # 非空输入（且不是从缓存读的）→ 写缓存（可选，这里不做，保持只读语义清晰）
        
        path = Path(path).expanduser().resolve()
        print(f"[LoadTextFromPath_mmx] 最终解析路径: {path}")
        
        if not path.exists():
            raise FileNotFoundError(f"LoadTextFromPath_mmx: 文件不存在 → {path}\n"
                                  f"（若使用缓存，请检查 {cache_file} 内容是否正确）")

        text = path.read_text(encoding="utf-8")
        return (text,)


# 注册节点
register_node(JoinStrings_mmx, "JoinStrings_mmx")
register_node(SplitString_mmx, "SplitString_mmx")
register_node(Strings2List_mmx, "Strings2List_mmx")
register_node(StrReplace_mmx, "StrReplace_mmx")
register_node(SaveText_mmx, "SaveText_mmx")
register_node(LoadTextFromPath_mmx, "LoadTextFromPath_mmx")
