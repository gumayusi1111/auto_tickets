#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_auto_form_fill.py
测试全自动模式的表单填写功能
"""

import sys
import os
import time
from datetime import datetime, timedelta

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.weverse.browser.setup import setup_driver
from src.weverse.core.mode_components.application_executor import ApplicationExecutor
from src.weverse.forms.lightning_form_processor import LightningFormProcessor
from selenium.webdriver.support.ui import WebDriverWait
from config.form_selectors import get_form_selectors
from config.user_data import get_user_data


def test_form_selectors():
    """测试表单选择器配置"""
    print("\n📋 测试表单选择器配置")
    print("=" * 60)
    
    selectors = get_form_selectors()
    print("✅ 生日输入框选择器:", selectors['birth_date'])
    print("✅ 手机号输入框选择器:", selectors['phone_number'])
    print("✅ 复选框选择器数量:", len(selectors['checkboxes']))
    print("✅ 提交按钮选择器数量:", len(selectors['submit_button_selectors']))
    
    user_data = get_user_data()
    print("\n📝 用户数据配置:")
    print("✅ 生日:", user_data['birth_date'])
    print("✅ 手机号:", user_data['phone_number'])


def test_form_fill_process():
    """测试表单填写流程"""
    print("\n🚀 测试全自动表单填写流程")
    print("=" * 60)
    
    driver = None
    try:
        # 设置浏览器
        driver = setup_driver()
        wait = WebDriverWait(driver, 10)
        
        # 创建表单处理器
        form_processor = LightningFormProcessor(driver)
        
        # 打开测试页面（这里需要一个实际的表单页面URL）
        test_url = input("请输入表单页面URL（按Enter跳过）: ").strip()
        
        if test_url:
            print(f"📍 导航到: {test_url}")
            driver.get(test_url)
            time.sleep(2)
            
            # 测试表单元素检测
            print("\n🔍 开始检测表单元素...")
            elements = form_processor._rapid_element_detection_with_selectors()
            
            print(f"\n📊 检测结果:")
            print(f"   生日输入框: {'✅ 找到' if elements.get('birth_input') else '❌ 未找到'}")
            print(f"   手机号输入框: {'✅ 找到' if elements.get('phone_input') else '❌ 未找到'}")
            print(f"   复选框数量: {len(elements.get('checkboxes', []))}")
            print(f"   提交按钮: {'✅ 找到' if elements.get('submit_button') else '❌ 未找到'}")
            
            # 询问是否继续填写
            if input("\n是否测试表单填写？(y/n): ").lower() == 'y':
                user_data = get_user_data()
                
                # 可以自定义数据
                custom_birth = input(f"输入生日 (默认: {user_data['birth_date']}): ").strip()
                custom_phone = input(f"输入手机号 (默认: {user_data['phone_number']}): ").strip()
                
                if custom_birth:
                    user_data['birth_date'] = custom_birth
                if custom_phone:
                    user_data['phone_number'] = custom_phone
                
                # 执行表单填写
                print("\n⚡ 开始闪电表单填写...")
                result = form_processor.process_form_lightning_fast(
                    birth_date=user_data['birth_date'],
                    phone_number=user_data['phone_number']
                )
                
                print(f"\n📊 填写结果:")
                print(f"   成功: {result['success']}")
                print(f"   耗时: {result.get('processing_time', 0):.3f}秒")
                print(f"   消息: {result['message']}")
                
                if result.get('detection_time'):
                    print(f"\n⏱️ 性能分析:")
                    print(f"   元素检测: {result['detection_time']:.3f}秒")
                    print(f"   表单填写: {result['fill_time'] - result['detection_time']:.3f}秒")
                    print(f"   表单提交: {result['submit_time'] - result['fill_time']:.3f}秒")
                    print(f"   总耗时: {result['total_time']:.3f}秒")
        
        else:
            print("⚠️ 未提供URL，仅测试配置")
            
            # 模拟倒计时和申请流程
            if input("\n是否测试倒计时申请流程？(y/n): ").lower() == 'y':
                # 创建申请执行器
                app_executor = ApplicationExecutor(driver, wait)
                
                # 设置目标时间（10秒后）
                target_time = datetime.now() + timedelta(seconds=10)
                
                print(f"\n⏰ 目标时间: {target_time.strftime('%H:%M:%S')}")
                print("🚀 开始倒计时...")
                
                # 执行倒计时和申请（自动填写模式）
                success = app_executor.execute_countdown_and_application(
                    target_time=target_time,
                    auto_fill_mode=True
                )
                
                print(f"\n{'✅ 申请成功!' if success else '❌ 申请失败!'}")
        
        input("\n按Enter键结束测试...")
        
    except Exception as e:
        print(f"❌ 测试过程出错: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        if driver:
            driver.quit()
            print("✅ 浏览器已关闭")


def main():
    """主函数"""
    print("🧪 Weverse 全自动表单填写测试")
    print("=" * 60)
    
    # 测试配置
    test_form_selectors()
    
    # 测试表单填写
    test_form_fill_process()
    
    print("\n✅ 测试完成!")


if __name__ == "__main__":
    main() 