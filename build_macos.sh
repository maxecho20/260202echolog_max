#!/bin/bash
# ================================
# EchoLog macOS 打包脚本
# ================================

echo ""
echo "========================================"
echo "  EchoLog macOS 打包工具"
echo "========================================"
echo ""

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

# 激活虚拟环境
if [ -d "venv" ]; then
    source venv/bin/activate
elif [ -d ".venv" ]; then
    source .venv/bin/activate
else
    echo "[ERROR] 未找到虚拟环境，请先运行: python3 -m venv venv"
    exit 1
fi

# 检查 PyInstaller 是否安装
if ! pip show pyinstaller > /dev/null 2>&1; then
    echo "[INFO] 正在安装 PyInstaller..."
    pip install pyinstaller
fi

# 清理旧的构建文件
echo "[INFO] 清理旧的构建文件..."
rm -rf build dist

# 开始打包
echo "[INFO] 开始打包 EchoLog..."
echo ""

pyinstaller --noconfirm \
    --name "EchoLog" \
    --windowed \
    --onefile \
    --add-data ".env.example:." \
    --add-data "README.md:." \
    --hidden-import customtkinter \
    --hidden-import websockets \
    --hidden-import sounddevice \
    --hidden-import numpy \
    --hidden-import dotenv \
    platforms/macos/main_gui_macos.py

if [ $? -ne 0 ]; then
    echo ""
    echo "[ERROR] 打包失败！"
    exit 1
fi

# 复制必要文件
echo ""
echo "[INFO] 复制配置文件..."
cp .env.example dist/.env.example 2>/dev/null || true
cp README.md dist/README.md 2>/dev/null || true
mkdir -p dist/output

echo ""
echo "========================================"
echo "  打包完成！"
echo "========================================"
echo ""
echo "可执行文件位置: dist/EchoLog"
echo ""
echo "使用前请确保:"
echo "  1. 复制 .env.example 为 .env"
echo "  2. 在 .env 中填入 DEEPGRAM_API_KEY"
echo ""
