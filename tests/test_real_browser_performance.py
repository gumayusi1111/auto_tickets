#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_real_browser_performance.py
真实浏览器性能测试 - 模拟实际使用场景
"""

import sys
import os
import time
from datetime import datetime

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.weverse.browser.setup import setup_driver
from src.weverse.forms.lightning_form_processor import LightningFormProcessor
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from config.user_data import get_user_data


def test_real_browser_performance():
    """使用真实浏览器测试表单填写性能"""
    print("\n🌐 真实浏览器性能测试")
    print("=" * 60)
    print("📍 使用Chrome浏览器测试实际表单填写性能")
    print("🎯 目标: 0.1秒内完成所有操作")
    
    driver = None
    try:
        # 启动浏览器
        print("\n⏳ 启动Chrome浏览器...")
        driver = setup_driver(headless=False)  # 显示浏览器窗口
        driver.set_window_size(1200, 800)
        wait = WebDriverWait(driver, 10)
        
        # 打开测试页面
        test_file_path = os.path.abspath('tests/test_weverse_form.html')
        print(f"📂 打开测试页面: {test_file_path}")
        driver.get(f'file://{test_file_path}')
        
        # 等待页面加载
        time.sleep(1)
        print("✅ 页面加载完成")
        
        # 创建表单处理器
        processor = LightningFormProcessor(driver)
        user_data = get_user_data()
        
        print(f"\n📝 测试数据:")
        print(f"   生日: {user_data['birth_date']}")
        print(f"   手机号: {user_data['phone_number']}")
        
        input("\n⏸️  按Enter键开始性能测试...")
        
        # 运行3次测试
        print("\n🚀 开始性能测试（3次）\n")
        
        for i in range(3):
            if i > 0:
                # 刷新页面
                driver.refresh()
                time.sleep(1)
            
            print(f"--- 测试 {i+1}/3 ---")
            
            # 记录开始时间
            start_time = time.perf_counter()
            
            # 执行表单填写
            result = processor.process_form_lightning_fast(
                birth_date=user_data['birth_date'],
                phone_number=user_data['phone_number']
            )
            
            # 计算总时间
            total_time = (time.perf_counter() - start_time) * 1000
            
            # 显示结果
            if result['success']:
                print(f"✅ 成功!")
                print(f"   Python总耗时: {total_time:.2f}ms")
                
                if 'total_time_ms' in result:
                    print(f"   处理器耗时: {result['total_time_ms']:.2f}ms")
                
                if 'js_time_ms' in result:
                    print(f"   JavaScript耗时: {result['js_time_ms']:.2f}ms")
                
                if 'optimization' in result and result['optimization'] == 'extreme':
                    print(f"   优化模式: 极限优化 ⚡")
                
                # 检查表单提交结果
                try:
                    # 等待结果显示
                    time.sleep(0.5)
                    result_element = wait.until(
                        EC.visibility_of_element_located((By.ID, 'result'))
                    )
                    if result_element.is_displayed():
                        result_text = driver.find_element(By.ID, 'resultText').text
                        print(f"   表单提交: 成功")
                        print(f"   {result_text.split('폼 채우기 시간:')[1].strip()}")
                except:
                    print(f"   表单提交: 等待结果...")
            else:
                print(f"❌ 失败: {result.get('message', 'Unknown error')}")
            
            print()
        
        # 展示页面元素
        print("\n🔍 页面元素验证:")
        elements = {
            '生日输入框': '#requiredProperties-birthDate',
            '手机号输入框': '#requiredProperties-phoneNumber',
            '复选框': 'input[type="checkbox"]',
            '提交按钮': 'input[type="submit"]'
        }
        
        for name, selector in elements.items():
            try:
                if name == '复选框':
                    elems = driver.find_elements(By.CSS_SELECTOR, selector)
                    print(f"   {name}: ✅ 找到 {len(elems)} 个")
                else:
                    elem = driver.find_element(By.CSS_SELECTOR, selector)
                    print(f"   {name}: ✅ 找到")
            except:
                print(f"   {name}: ❌ 未找到")
        
        print("\n💡 性能优化说明:")
        print("   1. 使用极限优化模式，单次JavaScript调用")
        print("   2. 并行处理所有表单元素")
        print("   3. 直接使用CSS选择器定位")
        print("   4. 批量触发DOM事件")
        
        input("\n⏸️  按Enter键关闭浏览器...")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        input("\n按Enter键关闭...")
    
    finally:
        if driver:
            driver.quit()
            print("\n✅ 浏览器已关闭")


def test_weverse_real_site():
    """测试真实的Weverse网站（需要手动操作）"""
    print("\n🌐 Weverse真实网站测试准备")
    print("=" * 60)
    print("⚠️  注意: 这将打开真实的Weverse网站")
    print("📋 测试流程:")
    print("   1. 手动登录Weverse")
    print("   2. 导航到申请页面")
    print("   3. 程序将自动填写表单")
    
    if input("\n是否继续? (y/n): ").lower() != 'y':
        return
    
    driver = None
    try:
        # 启动浏览器
        print("\n⏳ 启动Chrome浏览器...")
        driver = setup_driver(headless=False)
        driver.set_window_size(1400, 900)
        
        # 打开Weverse
        print("🌐 打开Weverse网站...")
        driver.get("https://weverse.io")
        
        print("\n📝 请完成以下步骤:")
        print("   1. 登录您的Weverse账号")
        print("   2. 导航到要申请的活动页面")
        print("   3. 点击申请按钮，进入表单页面")
        
        input("\n⏸️  完成上述步骤后，按Enter键继续...")
        
        # 获取当前URL
        current_url = driver.current_url
        print(f"\n📍 当前页面: {current_url}")
        
        # 创建表单处理器
        processor = LightningFormProcessor(driver)
        user_data = get_user_data()
        
        print(f"\n📝 准备填写表单:")
        print(f"   生日: {user_data['birth_date']}")
        print(f"   手机号: {user_data['phone_number']}")
        
        if input("\n确认填写? (y/n): ").lower() == 'y':
            print("\n⚡ 执行极速表单填写...")
            
            # 执行填写
            result = processor.process_form_lightning_fast(
                birth_date=user_data['birth_date'],
                phone_number=user_data['phone_number']
            )
            
            if result['success']:
                print(f"✅ 填写成功! 耗时: {result.get('total_time_ms', 0):.2f}ms")
                print("\n⚠️  请检查表单是否正确填写")
                print("⚠️  如果一切正常，请手动确认提交")
            else:
                print(f"❌ 填写失败: {result.get('message', 'Unknown error')}")
        
        input("\n⏸️  按Enter键关闭浏览器...")
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        if driver:
            driver.quit()
            print("\n✅ 浏览器已关闭")


def main():
    """主函数"""
    print("🧪 Weverse 真实浏览器测试")
    print("=" * 60)
    
    print("\n选择测试模式:")
    print("1. 本地测试页面（推荐）")
    print("2. 真实Weverse网站（需要账号）")
    
    choice = input("\n请选择 (1-2): ").strip()
    
    if choice == '1':
        test_real_browser_performance()
    elif choice == '2':
        test_weverse_real_site()
    else:
        print("无效选择")


if __name__ == "__main__":
    main() 