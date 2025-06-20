#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_optimized_detection.py
测试优化后的0.05秒高频检测算法
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
from config.mode_config import get_button_selectors
from config.user_data import get_user_data


def test_optimized_detection_algorithm():
    """测试优化后的检测算法"""
    print("\n🚀 测试优化后的高频检测算法")
    print("=" * 80)
    print("🔧 算法特性:")
    print("   - 检测频率: 每0.05秒 (20Hz)")
    print("   - 最大等待: 3秒")
    print("   - 策略: 一发现元素立即开始填写")
    print("   - 优先级: 生日输入框 > 手机号输入框 > 提交按钮 > 任意form元素")
    
    driver = None
    try:
        # 启动浏览器
        print("\n⏳ 启动Chrome浏览器...")
        driver = setup_driver(headless=False)
        driver.set_window_size(1400, 900)
        
        # 测试1: 打开测试页面验证检测算法
        test_url = input("\n🌐 请输入测试页面URL（或按Enter使用本地测试页面）: ").strip()
        
        if not test_url:
            # 使用本地测试页面
            current_dir = os.path.dirname(os.path.abspath(__file__))
            test_file = os.path.join(current_dir, "test_weverse_form.html")
            test_url = f"file://{test_file}"
            print(f"📄 使用本地测试页面: {test_file}")
        
        print(f"\n🌐 打开测试页面: {test_url}")
        driver.get(test_url)
        
        # 等待页面加载
        time.sleep(1)
        
        # 创建申请执行器
        app_executor = ApplicationExecutor(driver)
        
        print("\n📊 配置验证:")
        form_selectors = get_form_selectors()
        button_selectors = get_button_selectors()
        user_data = get_user_data()
        
        print(f"✅ 生日输入框: {form_selectors['birth_date']}")
        print(f"✅ 手机号输入框: {form_selectors['phone_number']}")
        print(f"✅ 复选框数量: {len(form_selectors['checkboxes'])}")
        print(f"✅ 申请按钮: {button_selectors['core_application']}")
        print(f"✅ 用户数据: 生日={user_data['birth_date']}, 手机号={user_data['phone_number']}")
        
        # 测试2: 模拟申请按钮点击
        print(f"\n🎯 准备测试申请按钮点击...")
        
        # 检查申请按钮是否存在
        try:
            from selenium.webdriver.common.by import By
            apply_button = driver.find_element(By.CSS_SELECTOR, button_selectors['core_application'])
            if apply_button:
                print("✅ 找到申请按钮，准备点击...")
                
                # 询问是否继续
                if input("是否继续点击申请按钮？(y/n): ").lower() == 'y':
                    # 模拟倒计时和点击
                    target_time = datetime.now() + timedelta(seconds=5)
                    print(f"\n⏰ 5秒后执行申请 (目标时间: {target_time.strftime('%H:%M:%S')})")
                    
                    # 倒计时
                    for i in range(5, 0, -1):
                        print(f"⏳ {i}秒...")
                        time.sleep(1)
                    
                    print("🚀 开始执行申请流程...")
                    
                    # 执行优化后的检测和申请
                    success = app_executor.execute_countdown_and_application(
                        target_time=target_time,
                        auto_fill_mode=True
                    )
                    
                    print(f"\n{'🎉 申请执行成功!' if success else '❌ 申请执行失败!'}")
                    
                else:
                    print("🛑 用户取消申请按钮点击")
                    
                    # 测试3: 直接测试检测算法
                    print("\n🔄 直接测试页面跳转检测算法...")
                    detection_result = app_executor._quick_page_transition_detection()
                    print(f"检测结果: {'成功' if detection_result else '失败'}")
                    
            else:
                print("❌ 未找到申请按钮")
                
        except Exception as e:
            print(f"⚠️ 申请按钮检测失败: {e}")
            
            # 直接测试检测算法 + 自动填写
            print("\n🔄 测试完整流程: 检测 + 自动填写...")
            try:
                # 记录总体开始时间
                total_start = time.perf_counter()
                
                # 执行检测
                print("⚡ 第1步: 超高频检测...")
                detection_start = time.perf_counter()
                detection_result = app_executor._quick_page_transition_detection()
                detection_time = (time.perf_counter() - detection_start) * 1000
                
                print(f"检测结果: {'成功' if detection_result else '失败'} (耗时: {detection_time:.2f}ms)")
                
                # 如果检测成功，立即进行自动填写
                if detection_result:
                    print("\n⚡ 第2步: 闪电表单填写...")
                    fill_result = test_auto_fill_after_detection(driver)
                    
                    # 计算总体性能
                    total_time = (time.perf_counter() - total_start) * 1000
                    
                    if fill_result['success']:
                        # 计算纯执行时间（不包括Python处理开销）
                        pure_execution_time = detection_time + fill_result.get('js_execution_time_ms', 0)
                        
                        print(f"\n🎉 完整流程执行成功!")
                        print(f"📊 性能报告:")
                        print(f"   🔍 检测时间: {detection_time:.2f}ms")
                        print(f"   🚀 JS执行时间: {fill_result.get('js_execution_time_ms', 0):.2f}ms")
                        print(f"   📊 Python处理: {fill_result['processing_time_ms']:.2f}ms")
                        print(f"   ⚡ 纯执行时间: {pure_execution_time:.2f}ms")
                        print(f"   🎯 目标: <100ms ({'✅ 达标' if pure_execution_time < 100 else '❌ 超时'})")
                        print(f"   🚀 效率: 使用了目标时间的 {pure_execution_time/100*100:.1f}%")
                        
                        # 显示填写详情
                        print(f"\n📝 填写详情:")
                        print(f"   • 元素填写: {fill_result['elements_filled']}个")
                        print(f"   • 复选框勾选: {fill_result['checkboxes_checked']}个")
                        print(f"   • 表单提交: {'是' if fill_result['submitted'] else '否'}")
                        
                    else:
                        print(f"❌ 表单填写失败: {fill_result.get('error', '未知错误')}")
                        print(f"📊 检测时间: {detection_time:.2f}ms (检测成功)")
                        
                else:
                    print("❌ 检测失败，无法进行表单填写")
                    
            except Exception as detection_error:
                print(f"❌ 检测算法执行失败: {detection_error}")
                import traceback
                traceback.print_exc()
        
        # 测试4: 性能基准测试
        print(f"\n📊 性能基准测试:")
        perform_detection_benchmark(app_executor)
        
        input("\n按Enter键结束测试...")
        
    except Exception as e:
        print(f"❌ 测试过程出错: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        if driver:
            driver.quit()
            print("✅ 浏览器已关闭")


def test_auto_fill_after_detection(driver):
    """检测成功后立即测试自动填写"""
    try:
        print("⚡ 启动闪电表单填写测试...")
        
        # 获取用户数据
        user_data = get_user_data()
        
        # 创建闪电表单处理器
        processor = LightningFormProcessor(driver)
        
        # 记录开始时间
        fill_start = time.perf_counter()
        
        # 执行表单填写 - 使用已验证的闪电版本
        result = processor.process_form_lightning_fast(
            birth_date=user_data['birth_date'],
            phone_number=user_data['phone_number']
        )
        
        # 计算总时间
        fill_end = time.perf_counter()
        total_time_ms = (fill_end - fill_start) * 1000
        
        if result['success']:
            print(f"✅ 超级优化表单填写成功!")
            print(f"   🚀 JavaScript执行: {result.get('js_execution_time_ms', 0):.2f}ms")
            print(f"   📊 Python处理: {result.get('processing_time_ms', 0):.2f}ms")
            print(f"   ⏱️ 实际总时间: {total_time_ms:.2f}ms")
            print(f"   📝 填写元素: {result.get('elements_filled', 0)}个")
            print(f"   ☑️ 勾选复选框: {result.get('checkboxes_checked', 0)}个")
            print(f"   🔘 提交按钮: {'已点击' if result.get('submitted', False) else '未点击'}")
            print(f"   🎯 优化级别: {result.get('optimization_level', 'unknown')}")
            
            # 不等待，直接返回结果
            
            return {
                'success': True,
                'processing_time_ms': result.get('processing_time_ms', 0),
                'total_time_ms': total_time_ms,
                'elements_filled': result.get('elements_filled', 0),
                'checkboxes_checked': result.get('checkboxes_checked', 0),
                'submitted': result.get('submitted', False)
            }
        else:
            print(f"❌ 表单填写失败: {result.get('error', '未知错误')}")
            return {
                'success': False,
                'error': result.get('error', '未知错误'),
                'total_time_ms': total_time_ms
            }
            
    except Exception as e:
        print(f"❌ 表单填写测试失败: {e}")
        import traceback
        traceback.print_exc()
        return {
            'success': False,
            'error': str(e),
            'total_time_ms': 0
        }


def perform_detection_benchmark(app_executor):
    """执行检测性能基准测试"""
    print("🏃 执行检测性能基准测试...")
    
    # 测试检测频率
    detection_times = []
    for i in range(10):
        start_time = time.perf_counter()
        try:
            # 模拟单次检测
            result = app_executor.driver.execute_script("return document.readyState;")
        except:
            pass
        end_time = time.perf_counter()
        detection_times.append((end_time - start_time) * 1000)  # 转换为毫秒
    
    avg_detection_time = sum(detection_times) / len(detection_times)
    max_detection_time = max(detection_times)
    min_detection_time = min(detection_times)
    
    print(f"📊 检测性能指标:")
    print(f"   平均检测时间: {avg_detection_time:.2f}ms")
    print(f"   最快检测时间: {min_detection_time:.2f}ms")
    print(f"   最慢检测时间: {max_detection_time:.2f}ms")
    print(f"   理论最大频率: {1000/avg_detection_time:.1f} Hz")
    print(f"   目标频率: 20 Hz (每0.05秒)")
    
    # 计算实际可行性
    target_interval = 50  # 50ms = 0.05秒
    if avg_detection_time < target_interval:
        print(f"✅ 性能充足: 平均检测时间({avg_detection_time:.1f}ms) < 目标间隔({target_interval}ms)")
        print(f"🔥 可以支持更高频率: 最高可达 {1000/max_detection_time:.0f} Hz")
    else:
        print(f"⚠️ 性能不足: 平均检测时间({avg_detection_time:.1f}ms) > 目标间隔({target_interval}ms)")
        recommended_interval = max_detection_time * 1.2
        print(f"💡 建议间隔: {recommended_interval:.1f}ms ({1000/recommended_interval:.1f} Hz)")


def test_progressive_strategies():
    """测试渐进式策略"""
    print("\n📈 渐进式检测策略分析:")
    print("-" * 40)
    
    strategies = [
        {"name": "极速模式", "interval": 0.02, "max_wait": 1.0, "description": "50Hz检测，1秒超时"},
        {"name": "高速模式", "interval": 0.05, "max_wait": 3.0, "description": "20Hz检测，3秒超时（当前配置）"},
        {"name": "标准模式", "interval": 0.1, "max_wait": 5.0, "description": "10Hz检测，5秒超时"},
        {"name": "保守模式", "interval": 0.2, "max_wait": 10.0, "description": "5Hz检测，10秒超时"},
    ]
    
    for strategy in strategies:
        total_checks = int(strategy["max_wait"] / strategy["interval"])
        print(f"🎯 {strategy['name']}:")
        print(f"   {strategy['description']}")
        print(f"   最大检测次数: {total_checks} 次")
        print(f"   CPU使用: {'高' if strategy['interval'] < 0.05 else '中' if strategy['interval'] < 0.1 else '低'}")


if __name__ == "__main__":
    print("🚀 启动优化检测算法测试")
    
    # 测试检测算法
    test_optimized_detection_algorithm()
    
    # 分析策略
    test_progressive_strategies()
    
    print("\n🎉 测试完成！")
    print("🔥 系统已优化为0.05秒高频检测，一发现元素立即处理") 