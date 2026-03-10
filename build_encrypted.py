#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import shutil
import compileall
import py_compile

SOURCE_NAME = "Aiya-MMX"
TARGET_NAME = "Aiya-MMX-B"

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(SCRIPT_DIR)
SOURCE_DIR = os.path.join(PARENT_DIR, SOURCE_NAME)
TARGET_DIR = os.path.join(PARENT_DIR, TARGET_NAME)

def log(msg):
    print(f">>> {msg}")

def find_pyc(py_path):
    """查找编译后的 pyc 文件"""
    base = os.path.dirname(py_path)
    name = os.path.basename(py_path)[:-3]  # 去掉 .py
    
    # Python 3.13 可能的路径
    candidates = [
        os.path.join(base, "__pycache__", f"{name}.cpython-313.opt-2.pyc"),
        os.path.join(base, "__pycache__", f"{name}.cpython-313.pyc"),
        os.path.join(base, "__pycache__", f"{name}.opt-2.pyc"),
        py_path + 'c',
    ]
    
    for c in candidates:
        if os.path.exists(c):
            return c
    return None

def build():
    log(f"开始构建: {SOURCE_NAME} -> {TARGET_NAME}")
    
    if not os.path.exists(SOURCE_DIR):
        log(f"错误: 找不到 {SOURCE_DIR}")
        return False
    
    # 清理
    if os.path.exists(TARGET_DIR):
        shutil.rmtree(TARGET_DIR)
    os.makedirs(TARGET_DIR, exist_ok=True)
    
    compiled = 0
    copied = 0
    
    for root, dirs, files in os.walk(SOURCE_DIR):
        dirs[:] = [d for d in dirs if d not in ['__pycache__', '.git', 'dist', 'release', TARGET_NAME]]
        
        rel = os.path.relpath(root, SOURCE_DIR)
        if rel == '.':
            rel = ''
        
        dst_root = os.path.join(TARGET_DIR, rel)
        
        for f in files:
            if f.startswith('.') or f.endswith('.pyc'):
                continue
            
            src = os.path.join(root, f)
            display = os.path.join(rel, f) if rel else f
            is_root_init = (rel == '' and f == "__init__.py")
            
            if f.endswith('.py') and not is_root_init:
                os.makedirs(dst_root, exist_ok=True)
                
                try:
                    # 关键修复：使用 optimize=2（不是 optimization=2）
                    success = compileall.compile_file(src, force=True, quiet=2, optimize=2)
                    
                    if success:
                        pyc = find_pyc(src)
                        if pyc:
                            dst_pyc = os.path.join(dst_root, f[:-3] + '.pyc')
                            shutil.copy2(pyc, dst_pyc)
                            compiled += 1
                            print(f"  [编译] {display}")
                            
                            # 清理缓存
                            try:
                                os.remove(pyc)
                                cache = os.path.dirname(pyc)
                                if os.path.exists(cache) and not os.listdir(cache):
                                    os.rmdir(cache)
                            except:
                                pass
                        else:
                            raise Exception("pyc not found")
                    else:
                        raise Exception("compile returned False")
                        
                except Exception as e:
                    print(f"  [复制] {display} ({str(e)[:20]})")
                    shutil.copy2(src, os.path.join(dst_root, f))
                    copied += 1
            
            else:
                os.makedirs(dst_root, exist_ok=True)
                shutil.copy2(src, os.path.join(dst_root, f))
                if is_root_init:
                    print(f"  [保留] {f} (ComfyUI入口)")
                else:
                    copied += 1
    
    log(f"完成: 编译 {compiled}, 复制 {copied}")
    return compiled > 0

if __name__ == "__main__":
    print("="*50)
    print("ComfyUI 插件编译加密工具 (修正版)")
    print("="*50)
    
    if build():
        print("\n" + "="*50)
        print(f"✅ 成功生成: {TARGET_NAME}")
        print(f"位置: {TARGET_DIR}")
        print("="*50)
    else:
        print("\n[!] 构建失败")