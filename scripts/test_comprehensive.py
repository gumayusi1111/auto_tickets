#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
综合测试脚本
测试API连通性、浏览器功能和元素分析
"""

import sys
import os
import time
import requests
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config.ai_config import DEEPSEEK_CONFIG
from src.core.browser_setup import setup_driver, create_wait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException

def test_api_connectivity():
    """
    测试DeepSeek API连通性
    """
    print("\n" + "=" * 60)
    print("🧪 测试 1: API连通性测试")
    print("=" * 60)
    
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
                'content': '请简单回复"API测试成功"，并分析这是一个测试请求。'
            }
        ],
        'max_tokens': 100,
        'temperature': 0.1
    }
    
    try:
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

def test_browser_setup():
    """
    测试浏览器设置和反检测功能
    """
    print("\n" + "=" * 60)
    print("🌐 测试 2: 浏览器设置测试")
    print("=" * 60)
    
    driver = None
    try:
        print("🚀 初始化浏览器驱动...")
        driver = setup_driver(headless=False, stealth_mode=True)
        
        print("🔍 测试反检测功能...")
        
        # 访问检测网站
        test_url = "https://bot.sannysoft.com/"
        print(f"📍 访问检测网站: {test_url}")
        
        driver.get(test_url)
        time.sleep(5)  # 等待页面加载
        
        # 检查页面标题
        title = driver.title
        print(f"📄 页面标题: {title}")
        
        # 检查是否被检测为机器人
        try:
            # 查找可能的检测结果
            wait = create_wait(driver, 10)
            
            # 检查webdriver属性
            webdriver_result = driver.execute_script("return navigator.webdriver")
            print(f"🔍 webdriver属性: {webdriver_result}")
            
            # 检查plugins
            plugins_length = driver.execute_script("return navigator.plugins.length")
            print(f"🔌 插件数量: {plugins_length}")
            
            # 检查languages
            languages = driver.execute_script("return navigator.languages")
            print(f"🌍 语言设置: {languages}")
            
            # 检查用户代理
            user_agent = driver.execute_script("return navigator.userAgent")
            print(f"🤖 用户代理: {user_agent[:100]}...")
            
            print("✅ 浏览器反检测测试完成")
            return True
            
        except TimeoutException:
            print("⚠️ 页面加载超时，但浏览器初始化成功")
            return True
            
    except WebDriverException as e:
        print(f"❌ 浏览器驱动错误: {e}")
        return False
    except Exception as e:
        print(f"❌ 浏览器测试失败: {e}")
        return False
    finally:
        if driver:
            print("🔄 关闭浏览器...")
            driver.quit()

def test_element_analysis():
    """
    测试元素分析功能
    """
    print("\n" + "=" * 60)
    print("🎯 测试 3: 元素分析测试")
    print("=" * 60)
    
    driver = None
    try:
        print("🚀 初始化浏览器驱动...")
        driver = setup_driver(headless=False, stealth_mode=True)
        
        # 访问一个简单的测试页面
        test_url = "https://httpbin.org/html"
        print(f"📍 访问测试页面: {test_url}")
        
        driver.get(test_url)
        time.sleep(3)
        
        # 分析页面元素
        print("🔍 分析页面元素...")
        
        # 获取页面标题
        title = driver.title
        print(f"📄 页面标题: {title}")
        
        # 查找所有链接
        links = driver.find_elements(By.TAG_NAME, "a")
        print(f"🔗 找到 {len(links)} 个链接")
        
        # 查找所有段落
        paragraphs = driver.find_elements(By.TAG_NAME, "p")
        print(f"📝 找到 {len(paragraphs)} 个段落")
        
        # 获取页面文本内容
        body_text = driver.find_element(By.TAG_NAME, "body").text
        print(f"📄 页面文本长度: {len(body_text)} 字符")
        print(f"📄 页面文本预览: {body_text[:200]}...")
        
        # 测试等待功能
        wait = create_wait(driver, 10)
        body_element = wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        print(f"⏱️ 等待功能测试成功")
        
        print("✅ 元素分析测试完成")
        return True
        
    except Exception as e:
        print(f"❌ 元素分析测试失败: {e}")
        return False
    finally:
        if driver:
            print("🔄 关闭浏览器...")
            driver.quit()

def main():
    """
    主测试函数
    """
    print("🎵 演唱会自动化工具 - 综合测试")
    print("=" * 80)
    
    results = []
    
    # 测试1: API连通性
    api_result = test_api_connectivity()
    results.append(("API连通性", api_result))
    
    # 测试2: 浏览器设置
    browser_result = test_browser_setup()
    results.append(("浏览器设置", browser_result))
    
    # 测试3: 元素分析
    element_result = test_element_analysis()
    results.append(("元素分析", element_result))
    
    # 显示测试结果
    print("\n" + "=" * 80)
    print("📊 测试结果汇总")
    print("=" * 80)
    
    all_passed = True
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"  {test_name:<15} {status}")
        if not result:
            all_passed = False
    
    print("\n" + "=" * 80)
    if all_passed:
        print("🎉 所有测试通过！系统已准备就绪")
        print("✨ 您可以开始使用演唱会自动化功能")
    else:
        print("💥 部分测试失败，请检查相关配置")
        print("🔧 建议:")
        print("   1. 检查网络连接")
        print("   2. 确认API密钥正确")
        print("   3. 更新Chrome浏览器")
        print("   4. 检查依赖安装")
    print("=" * 80)
    
    return all_passed

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️ 测试被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n💥 测试过程中发生错误: {e}")
        sys.exit(1)