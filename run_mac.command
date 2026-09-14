#!/bin/bash
# -------------------------------------------------------------
# 双击即可在 macOS 上启动 Hello Kitty 桌面互动宠物
# -------------------------------------------------------------
cd "$(dirname "$0")"

echo "========================================="
echo "   🎀 Hello Kitty 桌面宠物启动中..."
echo "========================================="

# 1. 检测 Python3
if ! command -v python3 &> /dev/null; then
    echo "⚠️ 未检测到 Python3 环境。"
    echo "请打开终端输入 xcode-select --install 安装开发者工具，"
    echo "或前往 https://www.python.org/ 下载安装官方 Python 3。"
    echo ""
    read -p "按回车键退出..."
    exit 1
fi

# 2. 初始化 Mac 专属运行环境（仅首次需要，约需 10~30 秒）
if [ ! -d ".venv_mac" ]; then
    echo "正在为你首次初始化环境（下载极简依赖，请稍候）..."
    python3 -m venv .venv_mac
    ./.venv_mac/bin/pip install --upgrade pip -q -i https://pypi.tuna.tsinghua.edu.cn/simple
    
    # 优先安装 PyQt5，若 Apple Silicon (M1/M2/M3) 架构缺少轮子则自动安装官方支持的 PyQt6
    echo "正在安装界面引擎..."
    if ! ./.venv_mac/bin/pip install PyQt5 -q -i https://pypi.tuna.tsinghua.edu.cn/simple 2>/dev/null; then
        echo "检测到 Apple Silicon 芯片，正在安装适配版 PyQt6..."
        ./.venv_mac/bin/pip install PyQt6 -q -i https://pypi.tuna.tsinghua.edu.cn/simple
    fi
    echo "✅ 环境准备完成！"
fi

# 3. 启动 Hello Kitty
echo "💖 正在唤醒你的 Hello Kitty..."
nohup ./.venv_mac/bin/python3 main.py >/dev/null 2>&1 &

echo "🎉 启动成功！Kitty 已经出现在你的桌面上了！"
echo "（你可以关闭这个黑色小窗口了）"
sleep 2
exit 0
