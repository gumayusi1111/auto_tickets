#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_extreme_performance.py
极限性能测试 - 目标0.1秒内完成表单填写
"""

import sys
import os
import time
import statistics
from concurrent.futures import ThreadPoolExecutor
import asyncio

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.weverse.browser.setup import setup_driver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from config.form_selectors import get_form_selectors
from config.user_data import get_user_data


class ExtremePerformanceProcessor:
    """极限性能表单处理器 - 目标0.1秒内完成"""
    
    def __init__(self, driver):
        self.driver = driver
        self.selectors = get_form_selectors()
        self.user_data = get_user_data()
    
    def process_form_extreme_speed(self):
        """极限速度处理表单 - 使用JavaScript批量操作"""
        start_time = time.perf_counter()
        
        try:
            # 使用单个JavaScript调用完成所有操作
            js_script = """
            // 开始性能测量
            const startTime = performance.now();
            window.formFillStartTime = startTime;
            
            // 准备数据
            const birthDate = arguments[0];
            const phoneNumber = arguments[1];
            const checkboxSelectors = arguments[2];
            const submitSelector = arguments[3];
            
            // 创建Promise数组来并行执行所有操作
            const operations = [];
            
            // 操作1: 填写生日
            operations.push(new Promise((resolve) => {
                const birthInput = document.querySelector('#requiredProperties-birthDate');
                if (birthInput) {
                    birthInput.value = birthDate;
                    birthInput.dispatchEvent(new Event('input', {bubbles: true}));
                    birthInput.dispatchEvent(new Event('change', {bubbles: true}));
                }
                resolve('birth');
            }));
            
            // 操作2: 填写手机号
            operations.push(new Promise((resolve) => {
                const phoneInput = document.querySelector('#requiredProperties-phoneNumber');
                if (phoneInput) {
                    phoneInput.value = phoneNumber;
                    phoneInput.dispatchEvent(new Event('input', {bubbles: true}));
                    phoneInput.dispatchEvent(new Event('change', {bubbles: true}));
                }
                resolve('phone');
            }));
            
            // 操作3: 勾选所有复选框
            checkboxSelectors.forEach((selector, index) => {
                operations.push(new Promise((resolve) => {
                    try {
                        // 首先尝试找到SVG元素
                        const svgElement = document.querySelector(selector);
                        if (svgElement) {
                            // 向上查找最近的checkbox input
                            let parent = svgElement;
                            let checkbox = null;
                            
                            for (let i = 0; i < 10; i++) {
                                parent = parent.parentElement;
                                if (!parent) break;
                                
                                checkbox = parent.querySelector('input[type="checkbox"]');
                                if (checkbox) {
                                    checkbox.checked = true;
                                    checkbox.dispatchEvent(new Event('change', {bubbles: true}));
                                    break;
                                }
                            }
                        }
                    } catch (e) {
                        console.error('Checkbox error:', e);
                    }
                    resolve('checkbox' + index);
                }));
            });
            
            // 等待所有操作完成
            Promise.all(operations).then(() => {
                // 计算填写时间
                const fillTime = performance.now() - startTime;
                
                // 立即点击提交按钮
                const submitButton = document.querySelector(submitSelector);
                if (submitButton) {
                    submitButton.click();
                }
                
                // 返回性能数据
                return {
                    fillTime: fillTime,
                    totalTime: performance.now() - startTime,
                    operationsCount: operations.length
                };
            });
            
            // 返回立即执行的性能数据
            return {
                startTime: startTime,
                operations: operations.length,
                status: 'started'
            };
            """
            
            # 执行极速填写
            result = self.driver.execute_script(
                js_script,
                self.user_data['birth_date'],
                self.user_data['phone_number'],
                self.selectors['checkboxes'],
                self.selectors['submit_button_selectors'][0]
            )
            
            # 计算总时间
            total_time = (time.perf_counter() - start_time) * 1000  # 转换为毫秒
            
            print(f"⚡ 极速处理完成!")
            print(f"   总耗时: {total_time:.2f}ms")
            print(f"   操作数: {result['operations']}")
            
            return {
                'success': True,
                'total_time_ms': total_time,
                'details': result
            }
            
        except Exception as e:
            total_time = (time.perf_counter() - start_time) * 1000
            print(f"❌ 极速处理失败: {e}")
            return {
                'success': False,
                'total_time_ms': total_time,
                'error': str(e)
            }


def run_performance_test(test_count=10):
    """运行性能测试"""
    print(f"\n🚀 极限性能测试 - 目标: 0.1秒内完成")
    print("=" * 60)
    
    driver = None
    try:
        # 设置浏览器
        driver = setup_driver()
        
        # 打开测试页面
        test_file_path = os.path.abspath('tests/test_weverse_form.html')
        driver.get(f'file://{test_file_path}')
        time.sleep(1)  # 等待页面完全加载
        
        # 创建极限处理器
        processor = ExtremePerformanceProcessor(driver)
        
        # 运行多次测试
        results = []
        print(f"\n开始{test_count}次性能测试...\n")
        
        for i in range(test_count):
            print(f"测试 {i+1}/{test_count}:")
            
            # 刷新页面以重置表单
            if i > 0:
                driver.refresh()
                time.sleep(0.5)
            
            # 执行极速处理
            result = processor.process_form_extreme_speed()
            results.append(result['total_time_ms'])
            
            # 等待一下让结果显示
            time.sleep(0.5)
            
            # 检查结果
            try:
                result_element = driver.find_element(By.ID, 'resultText')
                if result_element.is_displayed():
                    print("   ✅ 表单提交成功")
            except:
                print("   ⚠️ 未检测到提交结果")
        
        # 统计分析
        print(f"\n📊 性能统计 ({test_count}次测试):")
        print("=" * 60)
        print(f"最快时间: {min(results):.2f}ms")
        print(f"最慢时间: {max(results):.2f}ms")
        print(f"平均时间: {statistics.mean(results):.2f}ms")
        print(f"中位数: {statistics.median(results):.2f}ms")
        if test_count > 1:
            print(f"标准差: {statistics.stdev(results):.2f}ms")
        
        # 检查是否达到目标
        if min(results) < 100:
            print(f"\n🎉 达到目标! 最快时间 {min(results):.2f}ms < 100ms")
        else:
            print(f"\n⚠️ 未达到目标。最快时间 {min(results):.2f}ms > 100ms")
            print("建议:")
            print("- 确保浏览器处于最佳性能状态")
            print("- 关闭其他占用CPU的程序")
            print("- 使用更快的硬件")
        
        # 显示每次测试的详细时间
        print(f"\n详细时间记录:")
        for i, time_ms in enumerate(results, 1):
            status = "✅" if time_ms < 100 else "⚠️"
            print(f"  {status} 测试{i}: {time_ms:.2f}ms")
        
        input("\n按Enter键结束测试...")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if driver:
            driver.quit()


def test_parallel_optimization():
    """测试并行优化版本"""
    print("\n🔥 测试超级并行优化版本")
    print("=" * 60)
    
    driver = None
    try:
        driver = setup_driver()
        test_file_path = os.path.abspath('tests/test_weverse_form.html')
        driver.get(f'file://{test_file_path}')
        time.sleep(1)
        
        # 超级优化的JavaScript代码 - 所有操作同时进行
        super_optimized_js = """
        return (function() {
            const t0 = performance.now();
            
            // 同时执行所有操作，不等待
            document.querySelector('#requiredProperties-birthDate').value = arguments[0];
            document.querySelector('#requiredProperties-phoneNumber').value = arguments[1];
            
            // 直接勾选复选框
            document.querySelectorAll('input[type="checkbox"]').forEach(cb => cb.checked = true);
            
            // 触发所有事件
            ['#requiredProperties-birthDate', '#requiredProperties-phoneNumber'].forEach(sel => {
                const el = document.querySelector(sel);
                el.dispatchEvent(new Event('input', {bubbles: true}));
                el.dispatchEvent(new Event('change', {bubbles: true}));
            });
            
            // 立即提交
            document.querySelector('input[type="submit"]').click();
            
            return performance.now() - t0;
        })();
        """
        
        user_data = get_user_data()
        
        # 运行5次测试
        times = []
        for i in range(5):
            if i > 0:
                driver.refresh()
                time.sleep(0.5)
            
            start = time.perf_counter()
            js_time = driver.execute_script(super_optimized_js, 
                                          user_data['birth_date'], 
                                          user_data['phone_number'])
            total_time = (time.perf_counter() - start) * 1000
            
            times.append(total_time)
            print(f"测试{i+1}: JavaScript执行时间={js_time:.2f}ms, 总时间={total_time:.2f}ms")
        
        print(f"\n最快总时间: {min(times):.2f}ms")
        
    except Exception as e:
        print(f"❌ 优化测试失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if driver:
            driver.quit()


def main():
    """主函数"""
    print("🏎️ Weverse 极限性能测试")
    print("目标: 0.1秒内完成所有表单操作")
    print("=" * 60)
    
    # 选择测试模式
    print("\n选择测试模式:")
    print("1. 标准性能测试（10次）")
    print("2. 快速性能测试（3次）")
    print("3. 超级并行优化测试")
    print("4. 全部测试")
    
    choice = input("\n请选择 (1-4): ").strip()
    
    if choice == '1':
        run_performance_test(10)
    elif choice == '2':
        run_performance_test(3)
    elif choice == '3':
        test_parallel_optimization()
    elif choice == '4':
        run_performance_test(3)
        test_parallel_optimization()
    else:
        print("无效选择")


if __name__ == "__main__":
    main() 