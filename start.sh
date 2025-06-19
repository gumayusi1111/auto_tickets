#!/bin/bash
# -*- coding: utf-8 -*-
"""
项目启动脚本 - 自动激活虚拟环境并进入交互模式
使用方法: ./start.sh 或 bash start.sh
"""

# 设置脚本目录为工作目录
cd "$(dirname "$0")"

echo "🎵 Weverse 自动化工具 - 精确时机控制版本"
echo "=================================================="
echo "📍 项目目录: $(pwd)"
echo ""
echo "✨ 新增优化功能:"
echo "   🎯 精确到毫秒的倒计时显示"
echo "   ⚡ 动态网络延迟测试和优化"
echo "   🔧 核心申请按钮精确定位"
echo "   🚀 简化登录流程，减少不必要延迟"
echo "   📡 优化网络请求捕获时机"
echo ""
echo "🎯 使用说明:"
echo "   1. 程序会自动进行网络延迟测试（60秒）"
echo "   2. 倒计时精确到毫秒，显示当前时间和目标时间"
echo "   3. 自动计算最佳提前点击时间"
echo "   4. 核心申请按钮优先使用精确选择器"
echo "   5. 登录流程已简化，无不必要等待"
echo ""
echo "⚠️ 重要提示:"
echo "   - 请提前登录好账号"
echo "   - 确保网络连接稳定"
echo "   - 程序会在最佳时机自动点击申请按钮"
echo ""

# 检查虚拟环境是否存在
if [ ! -d ".venv" ]; then
    echo "❌ 虚拟环境不存在，正在创建..."
    python3 -m venv .venv
    echo "✅ 虚拟环境创建完成"
fi

# 激活虚拟环境
echo "🚀 激活虚拟环境..."
source .venv/bin/activate

echo "✅ 虚拟环境已激活"
echo "📦 当前Python路径: $(which python)"
echo "📦 当前pip路径: $(which pip)"

# 检查是否需要安装依赖
if [ -f "requirements.txt" ]; then
    echo ""
    echo "📋 检查依赖..."
    
    # 检查关键依赖是否安装
    if ! python -c "import selenium, requests" 2>/dev/null; then
        echo "⚠️ 发现缺失依赖，正在安装..."
        pip install -r requirements.txt
        echo "✅ 依赖安装完成"
    else
        echo "✅ 依赖检查通过"
    fi
fi

echo ""
echo "🎯 项目已准备就绪！"
echo "📁 新的模块化目录结构："
echo "   📂 core/     - 核心功能"
echo "   📂 auth/     - 认证相关"
echo "   📂 forms/    - 表单相关" 
echo "   📂 network/  - 网络相关"
echo "   📂 vpn/      - VPN相关"
echo "   📂 archive/  - 归档功能"
echo ""
echo "🚀 启动Weverse统一自动化工具..."
echo ""

# 使用新的重构后的主程序
python -m src.weverse.core.main

echo ""
echo "📋 程序运行完成！"
echo ""
echo "💡 其他可用命令:"
echo "  🧪 API测试:        python scripts/test_api.py"
echo "  🎵 演唱会分析:      python scripts/weverse_analyzer.py"
echo "  🌐 Weverse统一工具: python -m src.weverse.core.main"
echo "  🚀 直接启动:       python weverse_auto.py"
echo ""
echo "🔧 如需重新运行: ./start.sh"
echo "🔧 退出虚拟环境: deactivate"