#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API连通性测试脚本
测试DeepSeek API是否正常工作
"""

import sys
import os
import requests
import json
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config.ai_config import DEEPSEEK_CONFIG

def test_deepseek_api():
    """
    测试DeepSeek API连通性
    """
    print("🔍 正在测试DeepSeek API连通性...")
    print(f"📡 API地址: {DEEPSEEK_CONFIG['base_url']}")
    print(f"🤖 模型: {DEEPSEEK_CONFIG['model_name']}")
    
    # 检查API密钥
    api_key = DEEPSEEK_CONFIG['api_key']
    if not api_key:
        print("❌ 错误: 未找到API密钥")
        return False
    
    print(f"🔑 API密钥: {api_key[:10]}...{api_key[-4:]}")
    
    # 准备请求
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    data = {
        'model': DEEPSEEK_CONFIG['model_name'],
        'messages': [
            {
                'role': 'user',
                'content': '你好，请回复"API连接成功"'
            }
        ],
        'max_tokens': 50,
        'temperature': 0.1
    }
    
    try:
        # 发送请求
        print("📤 发送测试请求...")
        response = requests.post(
            f"{DEEPSEEK_CONFIG['base_url']}/chat/completions",
            headers=headers,
            json=data,
            timeout=DEEPSEEK_CONFIG['timeout']
        )
        
        print(f"📥 响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            if 'choices' in result and len(result['choices']) > 0:
                reply = result['choices'][0]['message']['content']
                print(f"✅ API连接成功!")
                print(f"🤖 AI回复: {reply}")
                return True
            else:
                print("❌ 响应格式异常")
                print(f"响应内容: {result}")
                return False
        else:
            print(f"❌ API请求失败")
            print(f"错误信息: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ 请求超时")
        return False
    except requests.exceptions.ConnectionError:
        print("❌ 连接错误，请检查网络")
        return False
    except Exception as e:
        print(f"❌ 未知错误: {str(e)}")
        return False

def main():
    """
    主函数
    """
    print("=" * 50)
    print("🧪 DeepSeek API 连通性测试")
    print("=" * 50)
    
    success = test_deepseek_api()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 测试完成: API连接正常")
        print("✨ 您可以正常使用AI分析功能")
    else:
        print("💥 测试失败: API连接异常")
        print("🔧 请检查:")
        print("   1. API密钥是否正确")
        print("   2. 网络连接是否正常")
        print("   3. API服务是否可用")
    print("=" * 50)
    
    return success

if __name__ == "__main__":
    main()