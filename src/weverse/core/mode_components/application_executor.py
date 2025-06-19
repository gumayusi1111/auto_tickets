#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
application_executor.py
申请执行组件
"""

import time
from datetime import datetime
from typing import Dict, Any

from config.mode_config import get_button_selectors, get_status_message, get_time_config
from ...analysis.time_processor import show_countdown_with_dynamic_timing
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC


class ApplicationExecutor:
    """申请执行器"""
    
    def __init__(self, driver: Any, wait: Any, network_monitor: Any = None):
        self.driver = driver
        self.wait = wait
        self.network_monitor = network_monitor
        self.button_config = get_button_selectors()
        self.time_config = get_time_config()
    
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
        """执行自动填写模式"""
        print(get_status_message('application_start'))
        print(f"⚡ 使用动态计算的提前时间: {advance_time:.3f}秒")
        
        # 执行原有的智能申请流程
        return self._execute_intelligent_application()
    
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
    
    def _click_core_button_instantly(self, core_selector: str, fallback_text: str) -> Dict[str, Any]:
        """立即点击核心按钮（无延迟）"""
        try:
            click_start = time.perf_counter()
            
            # 优先尝试核心选择器
            try:
                element = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, core_selector)))
                element.click()
                click_time = (time.perf_counter() - click_start) * 1000
                print(f"✅ 核心按钮点击成功 ({click_time:.1f}ms): {core_selector}")
                return {
                    'success': True,
                    'method': f"核心选择器: {core_selector}",
                    'click_time_ms': click_time
                }
            except Exception as e:
                print(f"⚠️ 核心选择器失败: {e}")
                
                # 备选文字查找
                try:
                    xpath = f"//a[contains(text(), '{fallback_text}')]"
                    element = self.wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
                    element.click()
                    click_time = (time.perf_counter() - click_start) * 1000
                    print(f"✅ 备选按钮点击成功 ({click_time:.1f}ms): {fallback_text}")
                    return {
                        'success': True,
                        'method': f"文字查找: {xpath}",
                        'click_time_ms': click_time
                    }
                except Exception as e2:
                    print(f"❌ 所有按钮点击方法都失败: {e2}")
                    return {
                        'success': False,
                        'error': f"核心选择器失败: {e}, 备选方法失败: {e2}"
                    }
            
        except Exception as e:
            print(f"❌ 按钮点击过程失败: {e}")
            return {'success': False, 'error': str(e)}
    
    def _execute_intelligent_application(self) -> Dict[str, Any]:
        """执行智能申请流程（处理未知表单）"""
        application_start = time.time()
        
        try:
            # 准备核心按钮选择器和数据
            core_selector = self.button_config.get('core_application')
            fallback_text = self.button_config['fallback_texts'][0]
            
            print(f"🎯 核心申请按钮: {core_selector}")
            
            # 步骤1: 点击核心申请按钮
            click_result = self._click_core_button_instantly(core_selector, fallback_text)
            if not click_result.get('success'):
                return {'success': False, 'error': '核心按钮点击失败'}
            
            # 步骤2: 智能表单处理（使用闪电表单处理器）
            print("🤖 启动智能表单处理...")
            form_result = self._intelligent_form_handling()
            
            # 合并所有结果
            total_time = (time.time() - application_start) * 1000
            
            results = {
                'success': True,
                'total_time_ms': total_time,
                'click_result': click_result,
                'intelligent_form_result': form_result,
                'timestamp': datetime.now().isoformat(),
                'performance': {
                    'target_form_fill_time': 500,  # 目标500ms
                    'actual_form_fill_time': form_result.get('total_time_ms', 0),
                    'total_application_time': total_time
                }
            }
            
            print(f"🎉 智能申请流程完成!")
            print(f"   总耗时: {total_time:.1f}ms")
            print(f"   表单处理: {form_result.get('total_time_ms', 0):.1f}ms")
            
            return results
            
        except Exception as e:
            print(f"❌ 智能申请流程失败: {e}")
            return {'success': False, 'error': str(e)}
    
    def _intelligent_form_handling(self) -> Dict[str, Any]:
        """智能表单处理（使用闪电表单处理器）"""
        try:
            # 使用闪电表单处理器
            from ...forms.lightning_form_processor import capture_and_process_complete_flow
            result = capture_and_process_complete_flow(
                driver=self.driver,
                network_monitor=self.network_monitor,
                birth_date='19900101'  # 使用默认生日
            )
            
            return result
            
        except Exception as e:
            print(f"❌ 智能表单处理失败: {e}")
            return {
                'success': False,
                'error': str(e),
                'total_time_ms': 0
            }