#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import shutil
import compileall

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(SCRIPT_DIR)
SOURCE_DIR = os.path.join(PARENT_DIR, "Aiya-MMX")
TARGET_DIR = os.path.join(PARENT_DIR, "Aiya-MMX-B")

print(f"Python {sys.version_info.major}.{sys.version_info.minor}")
print(f"源: {SOURCE_DIR}")
print(f"目标: {TARGET_DIR}")
print("-" * 40)

def process_init_file(src_path, dst_path):
    """处理 __init__.py：把 *.py 改为 *.pyc"""
    with open(src_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 替换 glob 模式：*.py -> *.pyc
    # 但要避免重复替换（如果已经是 *.pyc 就不再改）
    original = content
    content = content.replace('*.py"', '*.pyc"')
    content = content.replace("*.py'", "*.pyc'")
    content = content.replace('*.py)', '*.pyc)')
    
    if content != original:
        print(f"    [自动修复] *.py -> *.pyc")
    
    with open(dst_path, 'w', encoding='utf-8') as f:
        f.write(content)

# 清理
if os.path.exists(TARGET_DIR):
    shutil.rmtree(TARGET_DIR)
os.makedirs(TARGET_DIR)

compiled = 0

for root, dirs, files in os.walk(SOURCE_DIR):
    dirs[:] = [d for d in dirs if d not in ['__pycache__', '.git', 'dist', 'release', 'Aiya-MMX-B']]
    
    rel = os.path.relpath(root, SOURCE_DIR)
    dst_root = os.path.join(TARGET_DIR, rel) if rel != '.' else TARGET_DIR
    os.makedirs(dst_root, exist_ok=True)
    
    for f in files:
        if f.startswith('.') or f.endswith('.pyc'):
            continue
            
        src = os.path.join(root, f)
        dst = os.path.join(dst_root, f)
        
        # __init__.py 特殊处理：替换 *.py 为 *.pyc
        if f == '__init__.py':
            process_init_file(src, dst)
            print(f"[修复] {os.path.join(rel, f) if rel != '.' else f}")
            continue
        
        # .py 文件编译为 .pyc
        if f.endswith('.py'):
            try:
                result = compileall.compile_file(src, force=True, quiet=2, optimize=2)
                
                if result:
                    # 查找 pyc 文件
                    cache = os.path.join(os.path.dirname(src), '__pycache__')
                    name = f[:-3]
                    ver = f"{sys.version_info.major}{sys.version_info.minor}"
                    
                    # 尝试多种可能的文件名
                    pyc_names = [
                        f"{name}.cpython-{ver}.opt-2.pyc",
                        f"{name}.cpython-{ver}.pyc",
                    ]
                    
                    pyc_file = None
                    for pname in pyc_names:
                        ppath = os.path.join(cache, pname)
                        if os.path.exists(ppath):
                            pyc_file = ppath
                            break
                    
                    if pyc_file:
                        # 目标改为 .pyc
                        dst_pyc = dst[:-3] + '.pyc'
                        shutil.copy2(pyc_file, dst_pyc)
                        print(f"[编译] {os.path.join(rel, f) if rel != '.' else f}")
                        compiled += 1
                        
                        # 清理缓存
                        os.remove(pyc_file)
                        try:
                            if os.path.exists(cache) and not os.listdir(cache):
                                os.rmdir(cache)
                        except:
                            pass
                    else:
                        raise Exception("pyc not found")
                else:
                    raise Exception("compile failed")
                    
            except Exception as e:
                shutil.copy2(src, dst)
                print(f"[复制] {os.path.join(rel, f) if rel != '.' else f} (失败)")
        else:
            # 其他文件直接复制
            shutil.copy2(src, dst)

print("-" * 40)
print(f"编译完成: {compiled} 个文件")
print(f"\n重要修改:")
print("  - __init__.py 中的 *.py 已自动替换为 *.pyc")
print(f"\n位置: {TARGET_DIR}")
print("现在可以重命名原目录并测试")
