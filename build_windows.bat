@echo off
REM ================================
REM EchoLog Windows 打包脚本
REM ================================

echo.
echo ========================================
echo   EchoLog Windows 打包工具
echo ========================================
echo.

REM 激活虚拟环境
call venv\Scripts\activate

REM 检查 PyInstaller 是否安装
pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo [INFO] 正在安装 PyInstaller...
    pip install pyinstaller
)

REM 清理旧的构建文件
echo [INFO] 清理旧的构建文件...
if exist "build" rmdir /s /q build
if exist "dist" rmdir /s /q dist

REM 开始打包
echo [INFO] 开始打包 EchoLog...
echo.

pyinstaller --noconfirm echolog.spec

if errorlevel 1 (
    echo.
    echo [ERROR] 打包失败！
    pause
    exit /b 1
)

REM 复制必要文件到 dist 目录
echo.
echo [INFO] 复制配置文件...
copy .env.example dist\.env.example >nul 2>&1
copy README.md dist\README.md >nul 2>&1

REM 创建 output 目录
if not exist "dist\output" mkdir dist\output

echo.
echo ========================================
echo   打包完成！
echo ========================================
echo.
echo 可执行文件位置: dist\EchoLog.exe
echo.
echo 使用前请确保:
echo   1. 复制 .env.example 为 .env
echo   2. 在 .env 中填入 DEEPGRAM_API_KEY
echo.
pause
