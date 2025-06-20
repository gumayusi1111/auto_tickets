#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
debug_input.py
调试输入功能的简单脚本
"""

import sys
import os

def test_basic_input():
    """测试基本输入功能"""
    print("🔧 输入功能调试")
    print("=" * 40)
    
    try:
        print("📍 Python版本:", sys.version)
        print("📍 运行目录:", os.getcwd())
        print("📍 脚本路径:", __file__)
        
        print("\n测试1: 基本输入")
        test_input = input("请输入任意内容: ")
        print(f"✅ 输入成功: '{test_input}'")
        print(f"📏 输入长度: {len(test_input)}")
        print(f"🔍 输入类型: {type(test_input)}")
        
        print("\ntest2: URL输入测试")
        url_input = input("🌐 目标URL: ")
        print(f"✅ URL输入: '{url_input}'")
        
        # 验证URL
        if url_input.startswith(('http://', 'https://')):
            print("✅ URL格式正确")
        else:
            print("❌ URL格式不正确")
            
        print(f"\n🎯 测试完成！")
        
    except KeyboardInterrupt:
        print("\n⚠️ 用户中断测试")
    except Exception as e:
        print(f"\n❌ 测试出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_basic_input() 