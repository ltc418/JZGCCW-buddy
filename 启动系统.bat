@echo off
chcp 65001 >nul
title JZGCCW 建设工程财务分析系统 - 启动器

echo ========================================
echo   JZGCCW 建设工程财务分析系统
echo ========================================
echo.
echo 正在检查 Python 环境...
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未找到 Python，请先安装 Python 3.8 或更高版本
    pause
    exit /b 1
)

echo [√] Python 环境正常
python --version
echo.
echo 正在检查 Streamlit...
python -c "import streamlit" >nul 2>&1
if %errorlevel% neq 0 (
    echo [提示] Streamlit 未安装，正在自动安装...
    pip install streamlit
    if %errorlevel% neq 0 (
        echo [错误] Streamlit 安装失败
        pause
        exit /b 1
    )
)
echo [√] Streamlit 环境正常
echo.
echo ========================================
echo 正在启动 Streamlit 应用...
echo ========================================
echo.
echo 启动后浏览器会自动打开
echo 按 Ctrl+C 可以停止服务
echo.

streamlit run app_v2.py

if %errorlevel% neq 0 (
    echo.
    echo [错误] 应用启动失败
    pause
)
