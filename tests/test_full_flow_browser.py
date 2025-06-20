#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_full_flow_browser.py
完整流程浏览器测试 - 包含申请按钮点击
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
from config.form_selectors import get_form_selectors


def test_full_flow():
    """测试完整流程：点击申请按钮 -> 填写表单 -> 提交"""
    print("\n🌐 完整流程浏览器测试")
    print("=" * 60)
    print("📍 测试流程：")
    print("   1. 打开页面")
    print("   2. 点击'참여 신청하기'按钮")
    print("   3. 等待表单加载")
    print("   4. 极速填写表单")
    print("   5. 提交申请")
    
    driver = None
    try:
        # 启动浏览器
        print("\n⏳ 启动Chrome浏览器...")
        driver = setup_driver(headless=False)
        driver.set_window_size(1200, 800)
        wait = WebDriverWait(driver, 10)
        
        # 使用test_lightning_form.html而不是test_weverse_form.html
        test_file_path = os.path.abspath('tests/test_lightning_form.html')
        print(f"📂 打开测试页面: {test_file_path}")
        driver.get(f'file://{test_file_path}')
        
        # 等待页面加载
        time.sleep(1)
        print("✅ 主页加载完成")
        
        # 步骤1: 点击申请按钮
        print("\n📍 步骤1: 点击申请按钮")
        apply_button = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, '.main-button'))
        )
        print("   找到申请按钮：'참여 신청하기'")
        
        # 记录点击时间
        click_start = time.perf_counter()
        apply_button.click()
        
        # 等待表单页面加载
        print("   等待表单页面加载...")
        try:
            # 等待表单元素出现
            wait.until(
                EC.presence_of_element_located((By.ID, 'birth'))
            )
            form_load_time = (time.perf_counter() - click_start) * 1000
            print(f"✅ 表单页面加载完成 (耗时: {form_load_time:.2f}ms)")
        except:
            print("❌ 表单页面加载失败")
            return
        
        # 步骤2: 极速填写表单
        print("\n📍 步骤2: 极速填写表单")
        
        # 使用配置的选择器（但由于测试页面不同，需要适配）
        # 创建自定义的表单处理器
        processor = LightningFormProcessor(driver)
        user_data = get_user_data()
        
        print(f"📝 填写数据:")
        print(f"   生日: {user_data['birth_date']}")
        print(f"   手机号: {user_data['phone_number']}")
        
        # 由于测试页面的选择器不同，我们需要直接使用JavaScript
        fill_start = time.perf_counter()
        
        # 使用极速JavaScript填写
        fill_script = """
        return (function() {
            const t0 = performance.now();
            const results = {success: true, operations: []};
            
            try {
                // 填写生日
                const birthInput = document.querySelector('#birth');
                if (birthInput) {
                    birthInput.value = arguments[0];
                    birthInput.dispatchEvent(new Event('input', {bubbles: true}));
                    birthInput.dispatchEvent(new Event('change', {bubbles: true}));
                    results.operations.push('birth');
                }
                
                // 手机号通常是预填的，但可以尝试修改
                const phoneInput = document.querySelector('#phone');
                if (phoneInput && !phoneInput.readOnly) {
                    phoneInput.value = arguments[1];
                    phoneInput.dispatchEvent(new Event('input', {bubbles: true}));
                    phoneInput.dispatchEvent(new Event('change', {bubbles: true}));
                    results.operations.push('phone');
                }
                
                // 勾选所有复选框
                const checkboxes = document.querySelectorAll('input[type="checkbox"]');
                checkboxes.forEach((cb, i) => {
                    cb.checked = true;
                    cb.dispatchEvent(new Event('change', {bubbles: true}));
                    results.operations.push('checkbox' + i);
                });
                
                results.jsTime = performance.now() - t0;
                return results;
                
            } catch (e) {
                return {success: false, error: e.toString(), jsTime: performance.now() - t0};
            }
        })();
        """
        
        # 执行填写
        fill_result = driver.execute_script(
            fill_script,
            user_data['birth_date'],
            user_data['phone_number']
        )
        
        fill_time = (time.perf_counter() - fill_start) * 1000
        
        if fill_result['success']:
            print(f"✅ 表单填写成功!")
            print(f"   JavaScript执行: {fill_result['jsTime']:.2f}ms")
            print(f"   Python总耗时: {fill_time:.2f}ms")
            print(f"   完成操作: {', '.join(fill_result['operations'])}")
        else:
            print(f"❌ 表单填写失败: {fill_result.get('error', 'Unknown')}")
            return
        
        # 步骤3: 提交表单
        print("\n📍 步骤3: 提交表单")
        
        # 查找提交按钮
        submit_button = driver.find_element(By.CSS_SELECTOR, '.submit-button')
        
        # 点击提交
        submit_start = time.perf_counter()
        submit_button.click()
        submit_time = (time.perf_counter() - submit_start) * 1000
        
        print(f"✅ 表单提交完成 (耗时: {submit_time:.2f}ms)")
        
        # 等待结果显示
        try:
            wait.until(
                EC.visibility_of_element_located((By.ID, 'result-page'))
            )
            print("\n🎉 申请成功！已跳转到结果页面")
            
            # 获取提交的数据
            result_text = driver.find_element(By.ID, 'form-data').text
            print("\n📊 提交的数据:")
            print(result_text)
            
        except:
            print("⚠️ 等待结果页面...")
        
        # 总计时间
        total_time = form_load_time + fill_time + submit_time
        print(f"\n⏱️ 性能总结:")
        print(f"   表单加载: {form_load_time:.2f}ms")
        print(f"   表单填写: {fill_time:.2f}ms")
        print(f"   表单提交: {submit_time:.2f}ms")
        print(f"   总耗时: {total_time:.2f}ms")
        
        if fill_time < 100:
            print(f"\n🎉 达到极速目标! 填写时间 {fill_time:.2f}ms < 100ms")
        
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


def main():
    """主函数"""
    test_full_flow()


if __name__ == "__main__":
    main() 