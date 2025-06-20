# -*- coding: utf-8 -*-
"""
main.py
Weverse 自动化工具主入口 - 优化版本
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


def print_banner():
    """打印程序横幅"""
    print("\n" + "=" * 70)
    print("🎵 Weverse 自动化工具 - 优化版本")
    print("=" * 70)
    print("✨ 功能特性:")
    print("   📊 智能延迟计算：页面内跳转480ms，外部请求910ms")
    print("   ⚡ 0.5秒内完成表单填写")
    print("   🔍 全方位监控用户操作和网络请求")
    print("   🤖 AI智能分析和策略建议")
    print("=" * 70)


def main():
    """主函数"""
    print_banner()
    
    print("\n🎯 系统优化说明:")
    print("   1. 延迟计算已优化：")
    print("      - 页面内跳转: 300ms(网络) + 80ms(浏览器) + 100ms(安全) = 480ms")
    print("      - 外部请求: 730ms(网络) + 80ms(浏览器) + 100ms(安全) = 910ms")
    print("   2. 默认使用页面内跳转场景（更快更准确）")
    print("   3. 监控功能增强：实时追踪所有用户操作和网络请求")
    print("   4. 数据收集完善：自动保存完整的操作链路数据")
    
    print("\n🚀 启动统一模式 (分析+报名+监控)")
    print("-" * 50)
    
    try:
        unified_mode()
    except Exception as e:
        print(f"\n❌ 程序执行失败: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    print("\n✅ 程序执行完成!")
    print("📁 请查看 data/ 目录获取详细的监控数据")
    return 0


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        sys.exit("\n👋 用户中断脚本。")
    except Exception as e:
        print(f"❌ 程序运行出错: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)