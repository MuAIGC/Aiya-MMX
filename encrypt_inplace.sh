#!/bin/bash
# 原地加密脚本：将 Aiya-MMX/nodes 下的 .py 编译为 .so 并直接替换（保留 __init__.py）
# 用法: sudo ./encrypt_inplace.sh [插件名，默认 Aiya-MMX]

set -e

# 配置
COMFYUI_DIR="/MMXTools/ComfyUI/custom_nodes"
PLUGIN_NAME="${1:-Aiya-MMX}"  # 默认 Aiya-MMX，可传参指定其他
TARGET_DIR="${COMFYUI_DIR}/${PLUGIN_NAME}"
NODES_DIR="${TARGET_DIR}/nodes"

# 颜色
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log() { echo -e "${GREEN}[加密]${NC} $1"; }
warn() { echo -e "${YELLOW}[警告]${NC} $1"; }
err() { echo -e "${RED}[错误]${NC} $1"; }

# 检查
if [ ! -d "$NODES_DIR" ]; then
    err "未找到目录: $NODES_DIR"
    err "请确保插件已部署到 ${COMFYUI_DIR}/${PLUGIN_NAME}"
    exit 1
fi

if ! python -c "import nuitka" 2>/dev/null; then
    log "安装 Nuitka..."
    pip install nuitka -q
fi

# 检查 __init__.py 是否支持 .so
if ! grep -q "\.so" "${NODES_DIR}/__init__.py" 2>/dev/null; then
    warn "nodes/__init__.py 可能不支持 .so 加载！"
    warn "请确保已修改为同时加载 *.py 和 *.so 的版本"
    read -p "按回车强制继续，或 Ctrl+C 取消..."
fi

cd "$NODES_DIR"
log "工作目录: $(pwd)"
log "开始编译并替换..."

COMPILED=0
FAILED=0

# 遍历所有 py 文件
for py_file in *.py; do
    [ -e "$py_file" ] || continue
    
    # 跳过 __init__.py（必须保留源码）
    if [[ "$py_file" == "__init__.py" ]]; then
        log "保留: $py_file"
        continue
    fi
    
    module_name="${py_file%.py}"
    echo -n "  编译 $py_file -> ${module_name}.so ... "
    
    # 编译到当前目录（原地）
    if python -m nuitka --module \
        --output-dir=. \
        --remove-output \
        --quiet \
        --no-pyi-file \
        "$py_file" 2>/dev/null; then
        
        # 找到生成的 .so（带 cpython 版本后缀）
        generated_so=$(ls "${module_name}.cpython-"*.so 2>/dev/null | head -1)
        
        if [ -f "$generated_so" ]; then
            # 重命名为标准名称
            mv "$generated_so" "${module_name}.so"
            # 删除原 py 文件（完成替换）
            rm -f "$py_file"
            echo -e "${GREEN}成功${NC}"
            COMPILED=$((COMPILED + 1))
        else
            echo -e "${RED}失败(未找到输出)${NC}"
            FAILED=$((FAILED + 1))
        fi
    else
        echo -e "${RED}失败${NC}"
        FAILED=$((FAILED + 1))
    fi
done

# 清理临时目录
rm -rf build __pycache__

log "完成！编译: $COMPILED, 失败: $FAILED"
log "已原地替换 ${NODES_DIR} 下的 .py 为 .so（__init__.py 保留）"
log "请重启 ComfyUI 生效"
