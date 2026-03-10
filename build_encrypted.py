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

def fix_init(src, dst):
    with open(src, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 修复1: glob 模式 *.py -> *.pyc
    content = content.replace('*.py"', '*.pyc"').replace("*.py'", "*.pyc'")
    
    # 修复2: 切片 [:-3] -> [:-4] (正确处理 .pyc)
    content = content.replace('os.path.basename(f)[:-3]', 
                             'os.path.splitext(os.path.basename(f))[0]')
    
    # 修复3: 关键！__package__ -> __name__
    # 在 __init__.py 中，__name__ 就是当前包名（Aiya-MMX.nodes）
    content = content.replace('__package__', '__name__')
    
    with open(dst, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("    [修复] *.py->*.pyc | [:-3]->splitext | __package__->__name__")

# 清理
if os.path.exists(TARGET_DIR):
    shutil.rmtree(TARGET_DIR)

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
        
        if f == '__init__.py':
            fix_init(src, dst)
        elif f.endswith('.py'):
            try:
                if compileall.compile_file(src, force=True, quiet=2, optimize=2):
                    cache = os.path.join(os.path.dirname(src), '__pycache__')
                    name = f[:-3]
                    ver = f"{sys.version_info.major}{sys.version_info.minor}"
                    pyc = os.path.join(cache, f"{name}.cpython-{ver}.opt-2.pyc")
                    
                    if os.path.exists(pyc):
                        shutil.copy2(pyc, dst[:-3] + '.pyc')
                        compiled += 1
                        os.remove(pyc)
                        if not os.listdir(cache):
                            os.rmdir(cache)
                    else:
                        shutil.copy2(src, dst)
                else:
                    shutil.copy2(src, dst)
            except:
                shutil.copy2(src, dst)
        else:
            shutil.copy2(src, dst)

print(f"完成！编译 {compiled} 个文件")
