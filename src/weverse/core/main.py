# -*- coding: utf-8 -*-
"""
main.py
Weverse 自动化工具主入口 - 重构版本
"""

import sys
import os

# 添加项目根目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.join(current_dir, '..', '..', '..')
sys.path.insert(0, project_root)

# 导入模块化功能
try:
    from .mode_orchestrator import unified_mode
except ImportError:
    # 如果相对导入失败，使用绝对导入
    from src.weverse.core.mode_orchestrator import unified_mode


def main():
    """主函数"""
    print("🎵 Weverse 自动化工具 - 重构版本")
    print("=" * 50)
    print("🎯 启动统一模式 (分析+报名)")
    
    unified_mode()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit("\n👋 用户中断脚本。")
    except Exception as e:
        print(f"❌ 程序运行出错: {e}")
        import traceback
        traceback.print_exc()