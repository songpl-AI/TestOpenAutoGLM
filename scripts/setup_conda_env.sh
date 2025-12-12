#!/bin/bash

# Open-AutoGLM Conda 环境创建脚本
# 创建名为 PythonAgent 的 conda 环境，Python 版本 3.10（推荐）

set -e  # 遇到错误立即退出

echo "=========================================="
echo "创建 PythonAgent Conda 环境"
echo "=========================================="

# 检查 conda 是否安装
if ! command -v conda &> /dev/null; then
    echo "❌ Conda 未安装或未在 PATH 中"
    echo ""
    echo "请先安装 conda："
    echo "  方式 1: brew install miniconda"
    echo "  方式 2: 访问 https://docs.conda.io/en/latest/miniconda.html"
    echo ""
    echo "安装后，运行以下命令初始化："
    echo "  conda init zsh  # 或 conda init bash"
    echo "  source ~/.zshrc  # 或 source ~/.bashrc"
    exit 1
fi

echo "✓ Conda 已安装: $(conda --version)"
echo ""

# 初始化 conda（如果需要）
if ! conda info --envs &> /dev/null; then
    echo "初始化 conda..."
    eval "$(conda shell.bash hook)"
fi

# 检查环境是否已存在
if conda env list | grep -q "^PythonAgent"; then
    echo "⚠️  环境 PythonAgent 已存在"
    read -p "是否删除并重新创建？(y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "删除现有环境..."
        conda env remove -n PythonAgent -y
    else
        echo "使用现有环境"
        echo ""
        echo "激活环境："
        echo "  conda activate PythonAgent"
        exit 0
    fi
fi

# 创建环境（如果失败，可能是服务条款问题）
echo "创建环境 PythonAgent (Python 3.10)..."
create_output=$(conda create -n PythonAgent python=3.10 -y 2>&1)
create_status=$?

if [ $create_status -ne 0 ]; then
    # 检查是否是服务条款问题
    if echo "$create_output" | grep -q "Terms of Service"; then
        echo ""
        echo "⚠️  需要接受 Anaconda 服务条款"
        echo "正在自动接受..."
        conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/main 2>/dev/null || true
        conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/r 2>/dev/null || true
        echo "重新创建环境..."
        conda create -n PythonAgent python=3.10 -y
    else
        echo "❌ 环境创建失败："
        echo "$create_output"
        exit 1
    fi
fi

# 激活环境
echo "激活环境..."
eval "$(conda shell.bash hook)"
conda activate PythonAgent

# 验证 Python 版本
echo ""
echo "验证 Python 版本..."
python_version=$(python --version)
echo "✓ $python_version"

# 检查项目目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [ -f "$SCRIPT_DIR/requirements.txt" ]; then
    echo ""
    echo "安装项目依赖..."
    cd "$SCRIPT_DIR"
    pip install -r requirements.txt
    pip install -e .
    echo "✓ 依赖安装完成"
else
    echo "⚠️  未找到 requirements.txt，跳过依赖安装"
fi

echo ""
echo "=========================================="
echo "✅ 环境创建完成！"
echo "=========================================="
echo ""
echo "使用以下命令激活环境："
echo "  conda activate PythonAgent"
echo ""
echo "验证安装："
echo "  python --version"
echo "  pip list"
echo ""
echo "运行项目："
echo "  cd $SCRIPT_DIR"
echo "  python main.py '打开微信'"
echo ""

