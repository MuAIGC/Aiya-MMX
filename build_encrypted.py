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

def fix_init_file(src_path, dst_path):
    """修复 __init__.py 的两个问题：
    1. *.py -> *.pyc
    2. [:-3] -> [:-4] (正确去掉 .pyc)
    3. 处理 __package__ 路径问题
    """
    with open(src_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 修复1: glob 模式 *.py -> *.pyc
    content = content.replace('*.py"', '*.pyc"')
    content = content.replace("*.py'", "*.pyc'")
    
    # 修复2: 关键！[:-3] 改成 [:-4] 或更安全的 splitext
    # 原代码: name = os.path.basename(f)[:-3]
    # 改为: name = os.path.splitext(os.path.basename(f))[0]
    content = content.replace(
        'name = os.path.basename(f)[:-3]',
        'name = os.path.splitext(os.path.basename(f))[0]'
    )
    
    # 修复3: 处理 __package__ 可能包含反斜杠的问题（Windows）
    # 在导入前确保使用正确的包名
    if '__import__(__package__' in content:
        # 添加包名修复逻辑
        old_import = '__import__(__package__ + "." + name, fromlist=[""])'
        new_import = '''__import__(__package__ + "." + name, fromlist=[""])'''
        # 如果包名有问题，使用硬编码或者修复
        content = content.replace(
            'for f in sorted(glob.glob',
            '''# 确保包名正确（Windows路径修复）
_package_name = __package__ if __package__ else "Aiya-MMX.nodes"
if os.path.sep in str(_package_name):
    _package_name = "Aiya-MMX.nodes"

for f in sorted(glob.glob'''
        )
        content = content.replace('__package__ + "." + name', '_package_name + "." + name')
    
    with open(dst_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("    [自动修复] __init__.py:")
    print("      - *.py -> *.pyc")
    print("      - [:-3] -> splitext (修复切片错误)")
    print("      - 包名路径修复")

# 清理和创建目录
if os.path.exists(TARGET_DIR):
    shutil.rmtree(TARGET_DIR)
os.makedirs(TARGET_DIR, exist_ok=True)

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
            fix_init_file(src, dst)
        elif f.endswith('.py'):
            try:
                result = compileall.compile_file(src, force=True, quiet=2, optimize=2)
                if result:
                    cache = os.path.join(os.path.dirname(src), '__pycache__')
                    name = f[:-3]
                    ver = f"{sys.version_info.major}{sys.version_info.minor}"
                    pyc_name = f"{name}.cpython-{ver}.opt-2.pyc"
                    pyc_path = os.path.join(cache, pyc_name)
                    
                    if os.path.exists(pyc_path):
                        dst_pyc = dst[:-3] + '.pyc'
                        shutil.copy2(pyc_path, dst_pyc)
                        print(f"[编译] {os.path.join(rel, f) if rel != '.' else f}")
                        compiled += 1
                        os.remove(pyc_path)
                        if os.path.exists(cache) and not os.listdir(cache):
                            os.rmdir(cache)
                    else:
                        shutil.copy2(src, dst)
                else:
                    shutil.copy2(src, dst)
            except:
                shutil.copy2(src, dst)
        else:
            shutil.copy2(src, dst)

print(f"\n完成: 编译 {compiled} 个文件")
print(f"输出: {TARGET_DIR}")
