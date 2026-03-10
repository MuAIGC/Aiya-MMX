"""
💕 哎呀✦MMX 节点自动装载机
按文件名升序批量导入，避免手动维护（支持 .py 和 .so 加密文件）
"""
from __future__ import annotations
import glob
import os
import shutil
import sys

# ═══════════════════════════════════════════════════════════════════
# 批量导入（静默模式）- 同时支持 .py 源码和 .so 加密文件
# ═══════════════════════════════════════════════════════════════════

class _SilentWriter:
    """用于临时抑制 stdout 的虚拟输出流"""
    def write(self, x): pass
    def flush(self): pass

loaded_modules = []
_original_stdout = sys.stdout

# 关键修改：同时搜索 .py 和 .so 文件
_module_files = sorted(
    glob.glob(os.path.join(os.path.dirname(__file__), "*.py")) +
    glob.glob(os.path.join(os.path.dirname(__file__), "*.so"))
)

for f in _module_files:
    # 关键修改：用 splitext 正确处理 .py 和 .so 扩展名
    name = os.path.splitext(os.path.basename(f))[0]
    
    # 跳过 __init__ 和已处理的模块（防止 .py 和 .so 重复导入）
    if name == "__init__" or name in loaded_modules:
        continue
        
    try:
        # 导入期间抑制 stdout，拦截 "✅ 已注册节点" 等打印
        sys.stdout = _SilentWriter()
        __import__(__package__ + "." + name, fromlist=[""])
        loaded_modules.append(name)
    except Exception as e:
        # 错误时恢复 stdout 以便显示报错信息
        sys.stdout = _original_stdout
        print(f"[哎呀✦MMX] 加载 {name} 失败: {e}")
    finally:
        sys.stdout = _original_stdout

# ═══════════════════════════════════════════════════════════════════
# 环境检查 + 华丽 LOGO
# ═══════════════════════════════════════════════════════════════════

def _print_logo():
    logo = r"""
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║     ✦  *  ✦                                                      ║
║       █████╗ ██╗██╗   ██╗ █████╗      ███╗   ███╗██╗  ██╗██╗  ██╗║
║      ██╔══██╗██║╚██╗ ██╔╝██╔══██╗     ████╗ ████║╚██╗██╔╝╚██╗██╔╝║
║      ███████║██║ ╚████╔╝ ███████║     ██╔████╔██║ ╚███╔╝  ╚███╔╝ ║
║      ██╔══██║██║  ╚██╔╝  ██╔══██║     ██║╚██╔╝██║ ██╔██╗  ██╔██╗ ║
║      ██║  ██║██║   ██║   ██║  ██║     ██║ ╚═╝ ██║██╔╝ ██╗██╔╝ ██╗║
║      ╚═╝  ╚═╝╚═╝   ╚═╝   ╚═╝  ╚═╝     ╚═╝     ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝║
║              💕 Aiya MMX 好可爱呀 💕                             ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝"""
    print(logo)
    
    # 仅显示模块数量，不罗列详细列表
    if loaded_modules:
        print(f"   📦 已装载节点模块: {len(loaded_modules)} 个")
    
    # FFmpeg 状态检测
    if shutil.which("ffmpeg"):
        print("   🔊 FFmpeg 已就绪")
    else:
        print("   🔇 FFmpeg 未检测到，将回退到 OpenCV")
        print("   💡 安装提示: https://www.gyan.dev/ffmpeg/builds/ ")
    
    print()  # 底部空行，保持间距

_print_logo()
