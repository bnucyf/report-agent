@echo off
chcp 65001 >nul
echo ========================================
echo   智能报表机器人 - 一键安装 (Windows)
echo ========================================
echo.

REM 检查 Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到 Python，请先安装 Python 3.10+
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [1/5] 创建虚拟环境...
if not exist .venv (
    python -m venv .venv
    echo 虚拟环境已创建。
) else (
    echo 虚拟环境已存在，跳过。
)

echo [2/5] 激活虚拟环境...
call .venv\Scripts\activate.bat

echo [3/5] 安装依赖...
pip install -r requirements.txt -q
if errorlevel 1 (
    echo [错误] 依赖安装失败，请检查网络连接。
    pause
    exit /b 1
)
echo 依赖安装完成。

echo [4/5] 复制配置文件...
if not exist .env (
    copy .env.example .env >nul
    echo .env 已从模板创建，请编辑填写凭证。
) else (
    echo .env 已存在，跳过。
)

if not exist config\bot_keywords.json (
    echo {} > config\bot_keywords.json
)

echo [5/5] 创建输出目录...
if not exist outputs\snapshots mkdir outputs\snapshots
if not exist outputs\reports mkdir outputs\reports

echo.
echo ========================================
echo   安装完成！
echo ========================================
echo.
echo 下一步:
echo   1. 用记事本编辑 .env，填入钉钉凭证和数据库信息
echo   2. 运行 start_bot_windows.bat 启动机器人
echo.
pause
