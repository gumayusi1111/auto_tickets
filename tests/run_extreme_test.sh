#!/bin/bash
# 运行极限性能测试脚本

echo "🏎️ Weverse 极限性能测试启动器"
echo "================================"

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "❌ 未找到 Python3"
    exit 1
fi

# 进入项目根目录
cd "$(dirname "$0")/.." || exit

# 激活虚拟环境（如果存在）
if [ -f "venv/bin/activate" ]; then
    echo "🔄 激活虚拟环境..."
    source venv/bin/activate
elif [ -f ".venv/bin/activate" ]; then
    echo "🔄 激活虚拟环境..."
    source .venv/bin/activate
fi

# 检查测试HTML文件是否存在
if [ ! -f "tests/test_weverse_form.html" ]; then
    echo "❌ 测试HTML文件不存在: tests/test_weverse_form.html"
    exit 1
fi

echo "✅ 环境准备完成"
echo ""

# 运行极限性能测试
python3 tests/test_extreme_performance.py

echo ""
echo "✅ 测试完成" 