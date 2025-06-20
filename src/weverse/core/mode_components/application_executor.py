#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
application_executor.py
申请执行组件
"""

import time
from datetime import datetime
from typing import Dict, Any

from config.mode_config import get_time_config, get_button_selectors, get_status_message
from config.latency_config import get_optimized_preclick_ms
from ...analysis.time_processor import show_countdown_with_dynamic_timing
from config.user_data import get_user_data
from ...browser.setup import click_element_with_fallback


class ApplicationExecutor:
    """申请执行器"""
    
    def __init__(self, driver):
        self.driver = driver
        self.time_config = get_time_config()
        self.button_config = get_button_selectors()
    
    def execute_countdown_and_application(self, target_time: datetime, auto_fill_mode: bool) -> bool:
        """执行动态倒计时和申请流程（根据模式选择）"""
        try:
            print(get_status_message('countdown_start', target_time))
            print("按 Ctrl+C 可以停止倒计时")
            
            # 启动动态精确倒计时（使用真实网络延迟检测）
            advance_time = show_countdown_with_dynamic_timing(
                target_time, 
                enable_latency_test=self.time_config.get('dynamic_latency_test', True)
            )
            
            if advance_time is None:
                print("❌ 倒计时被中断")
                return False
            
            # 根据模式选择执行不同流程
            if auto_fill_mode:
                print("🤖 执行自动填写模式...")
                results = self._execute_auto_fill_mode(advance_time)
            else:
                print("👁️ 执行监控模式...")
                results = self._execute_monitoring_mode(advance_time)
            
            return results.get('success', False)
            
        except KeyboardInterrupt:
            print(get_status_message('countdown_stop'))
            return False
        except Exception as e:
            print(f"❌ 动态倒计时和申请执行失败: {e}")
            return False
    
    def _execute_auto_fill_mode(self, advance_time: float) -> Dict[str, Any]:
        """执行自动填写模式 - 纯粹的表单填写，不捕获任何数据"""
        print(get_status_message('application_start'))
        print(f"⚡ 使用动态计算的提前时间: {advance_time:.3f}秒")
        print("🎯 全自动填写模式 - 专注于任务完成，不捕获数据")
        
        application_start = time.time()
        
        try:
            # 步骤1: 点击申请按钮
            core_selector = self.button_config.get('core_application')
            fallback_text = self.button_config['fallback_texts'][0]
            
            click_result = self._click_core_button_instantly(core_selector, fallback_text)
            if not click_result.get('success'):
                return {'success': False, 'error': '申请按钮点击失败'}
            
            # 步骤2: 快速检测页面跳转（最多等待0.5秒）
            page_ready = self._quick_page_transition_detection()
            if not page_ready:
                print("⚠️ 页面跳转检测超时，直接尝试表单填写")
            
            # 步骤3: 纯粹的表单填写（不捕获数据）
            print("⚡ 启动闪电表单填写...")
            form_result = self._pure_form_filling()
            
            total_time = (time.time() - application_start) * 1000
            
            results = {
                'success': form_result.get('success', False),
                'mode': 'auto_fill_pure',
                'total_time_ms': total_time,
                'click_result': click_result,
                'form_result': form_result,
                'timestamp': datetime.now().isoformat(),
                'performance': {
                    'target_time': 500,  # 目标500ms
                    'actual_time': total_time,
                    'button_click_time': click_result.get('click_time_ms', 0),
                    'form_fill_time': form_result.get('processing_time', 0) * 1000
                }
            }
            
            print(f"🎉 自动填写模式完成!")
            print(f"   总耗时: {total_time:.1f}ms")
            print(f"   表单处理: {form_result.get('processing_time', 0) * 1000:.1f}ms")
            print(f"   目标达成: {'✅ 是' if total_time <= 500 else '❌ 否'}")
            
            return results
            
        except Exception as e:
            print(f"❌ 自动填写模式执行失败: {e}")
            return {'success': False, 'error': str(e)}
    
    def _pure_form_filling(self) -> Dict[str, Any]:
        """纯粹的表单填写（不捕获数据）"""
        try:
            # 获取用户数据
            user_data = get_user_data()
            
            # 使用闪电表单处理器进行纯粹的表单填写
            from ...forms.lightning_form_processor import LightningFormProcessor
            processor = LightningFormProcessor(self.driver)
            
            # 直接进行表单填写，不捕获页面数据或网络数据
            result = processor.process_form_lightning_fast(
                birth_date=user_data['birth_date'],
                phone_number=user_data['phone_number']
            )
            
            return result
            
        except Exception as e:
            print(f"❌ 纯粹表单填写失败: {e}")
            return {
                'success': False,
                'error': str(e),
                'processing_time': 0
            }
    
    def _execute_monitoring_mode(self, advance_time: float) -> Dict[str, Any]:
        """执行监控模式 - 只点击申请按钮，然后返回让监控处理器处理"""
        print(f"⚡ 使用动态计算的提前时间: {advance_time:.3f}秒")
        print("🔘 点击申请按钮...")
        
        application_start = time.time()
        
        try:
            # 点击申请按钮
            core_selector = self.button_config.get('core_application')
            fallback_text = self.button_config['fallback_texts'][0]
            
            click_result = self._click_core_button_instantly(core_selector, fallback_text)
            if not click_result.get('success'):
                return {'success': False, 'error': '申请按钮点击失败'}
            
            print("✅ 申请按钮点击成功!")
            print("📱 表单页面已打开")
            
            total_time = (time.time() - application_start) * 1000
            
            return {
                'success': True,
                'mode': 'monitoring',
                'total_time_ms': total_time,
                'click_result': click_result,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"❌ 监控模式执行失败: {e}")
            return {'success': False, 'error': str(e)}
    
    def _click_core_button_instantly(self, selector: str, fallback_text: str) -> Dict[str, Any]:
        """瞬间点击核心按钮"""
        click_start = time.time()
        
        try:
            success = click_element_with_fallback(
                self.driver,
                selector,
                fallback_text=fallback_text,
                timeout=5
            )
            
            click_time = (time.time() - click_start) * 1000  # 毫秒
            
            return {
                'success': success,
                'click_time_ms': click_time,
                'selector_used': selector,
                'fallback_text': fallback_text
            }
            
        except Exception as e:
            click_time = (time.time() - click_start) * 1000
            print(f"❌ 按钮点击失败: {e}")
            return {
                'success': False,
                'error': str(e),
                'click_time_ms': click_time
            }
    
    def _quick_page_transition_detection(self) -> bool:
        """超高频智能页面跳转检测 - 0.05秒检测，一发现元素立即开始填写"""
        print("🔄 启动超高频智能检测 - 0.05秒间隔，一发现元素立即填写...")
        
        start_time = time.time()
        max_wait = 3.0  # 最多等待3秒（应对网络延迟）
        check_interval = 0.05  # 每0.05秒检测一次（更快响应）
        
        # 导入真实的表单选择器
        from config.form_selectors import get_form_selectors
        selectors = get_form_selectors()
        
        try:
            # 记录初始URL
            initial_url = self.driver.current_url
            print(f"📍 初始URL: {initial_url}")
            print(f"🎯 主要目标: 生日输入框 {selectors['birth_date']}")
            print(f"🚀 策略: 一发现任何表单元素立即开始填写")
            
            check_count = 0
            elements_found = False
            
            # 超高频检测循环 - 专注于快速发现元素
            while time.time() - start_time < max_wait:
                check_count += 1
                current_time = time.time() - start_time
                current_url = self.driver.current_url
                
                # 每20次检测显示一次进度（约1秒）
                if check_count % 20 == 0:
                    print(f"🔍 检测中... {current_time:.1f}s (第{check_count}次检测，频率:{1/check_interval:.0f}Hz)")
                
                # 1. 检测URL变化（可能的页面跳转）
                if current_url != initial_url:
                    print(f"✅ URL变化: {initial_url} → {current_url}")
                    # URL变化后，给DOM一点时间加载，然后立即检测元素
                    time.sleep(0.02)  # 20ms等待DOM更新
                
                # 2. 核心策略：优先检测最重要的元素（生日输入框）
                try:
                    birth_input = self.driver.find_element("css selector", selectors['birth_date'])
                    if birth_input and birth_input.is_displayed() and birth_input.is_enabled():
                        print(f"🎉 关键元素已出现! 生日输入框 (第{check_count}次检测，{current_time:.1f}s)")
                        print(f"⚡ 立即启动表单填写，无需等待其他元素...")
                        elements_found = True
                        break
                except:
                    pass
                
                # 3. 备选检测：如果生日输入框没找到，检测其他表单元素
                if not elements_found:
                    # 检测手机号输入框（备选触发器）
                    try:
                        phone_input = self.driver.find_element("css selector", selectors['phone_number'])
                        if phone_input and phone_input.is_displayed() and phone_input.is_enabled():
                            print(f"🎉 备选元素已出现! 手机号输入框 (第{check_count}次检测，{current_time:.1f}s)")
                            print(f"⚡ 立即启动表单填写...")
                            elements_found = True
                            break
                    except:
                        pass
                    
                    # 检测提交按钮（最后的触发器）
                    try:
                        submit_btn = self.driver.find_element("css selector", selectors['submit_button_selectors'][0])
                        if submit_btn and submit_btn.is_displayed() and submit_btn.is_enabled():
                            print(f"🎉 提交按钮已出现! (第{check_count}次检测，{current_time:.1f}s)")
                            print(f"⚡ 立即启动表单填写...")
                            elements_found = True
                            break
                    except:
                        pass
                
                # 4. 超激进模式：检测到任何form元素都尝试开始
                if check_count > 10 and not elements_found:  # 检测10次后启用激进模式
                    try:
                        # 检测是否有任何form元素出现
                        form_element = self.driver.find_element("tag name", "form")
                        if form_element and form_element.is_displayed():
                            print(f"🔥 激进模式: 检测到form元素! (第{check_count}次检测，{current_time:.1f}s)")
                            print(f"⚡ 尝试启动表单填写...")
                            elements_found = True
                            break
                    except:
                        pass
                
                # 等待很短时间后继续检测（极速响应网络延迟）
                time.sleep(check_interval)
            
            if elements_found:
                print(f"🎉 检测成功! 总检测次数: {check_count}, 耗时: {time.time() - start_time:.2f}s")
                print(f"📊 检测频率: {check_count/(time.time() - start_time):.1f} 次/秒")
                return True
            else:
                print(f"⚠️ 检测超时 ({max_wait}秒，共检测{check_count}次)")
                print("🔥 强制启动表单填写（可能元素已存在但检测失败）...")
                return False
            
        except Exception as e:
            print(f"❌ 检测过程异常: {e}")
            print("🔥 发生异常，强制启动表单填写...")
            import traceback
            traceback.print_exc()
            return False