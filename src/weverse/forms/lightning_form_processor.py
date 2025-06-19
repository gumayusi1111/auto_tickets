#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
lightning_form_processor.py
闪电表单处理器 - 0.5秒内完成表单填写
"""

import time
import json
import os
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.keys import Keys
from typing import Dict, List, Any, Optional, Tuple


class LightningFormProcessor:
    """闪电表单处理器 - 专为0.5秒内完成表单填写而设计"""
    
    def __init__(self, driver, network_monitor=None):
        self.driver = driver
        self.network_monitor = network_monitor
        self.start_time = None
        self.form_data = {
            'birth_date': '19900101',  # 默认生日
            'phone': '',  # 手机号可能预填
            'checkboxes_to_check': 2,  # 需要勾选的复选框数量
        }
    
    def process_form_lightning_fast(self, birth_date='19900101') -> Dict[str, Any]:
        """闪电般快速处理表单 - 目标0.5秒内完成"""
        self.start_time = time.time()
        print(f"\n⚡ 开始闪电表单处理 - 目标0.5秒内完成")
        
        try:
            # 更新表单数据
            self.form_data['birth_date'] = birth_date
            
            # 阶段1: 快速元素识别 (0.1秒内)
            elements = self._rapid_element_detection()
            detection_time = time.time() - self.start_time
            print(f"🔍 元素识别完成: {detection_time:.3f}秒")
            
            if not elements:
                return self._create_result(False, "未找到表单元素")
            
            # 阶段2: 并行填写 (0.3秒内)
            fill_success = self._parallel_form_filling(elements)
            fill_time = time.time() - self.start_time
            print(f"📝 表单填写完成: {fill_time:.3f}秒")
            
            # 阶段3: 提交表单 (0.1秒内)
            submit_success = self._instant_submit(elements.get('submit_button'))
            submit_time = time.time() - self.start_time
            print(f"🚀 表单提交完成: {submit_time:.3f}秒")
            
            total_time = time.time() - self.start_time
            success = fill_success and submit_success
            
            print(f"⚡ 闪电处理完成! 总耗时: {total_time:.3f}秒")
            
            return self._create_result(success, f"处理完成，耗时{total_time:.3f}秒", {
                'detection_time': detection_time,
                'fill_time': fill_time,
                'submit_time': submit_time,
                'total_time': total_time,
                'elements_found': elements
            })
            
        except Exception as e:
            total_time = time.time() - self.start_time
            print(f"❌ 闪电处理失败: {e}, 耗时: {total_time:.3f}秒")
            return self._create_result(False, f"处理失败: {e}")
    
    def _rapid_element_detection(self) -> Dict[str, Any]:
        """快速元素检测 - 0.1秒内完成"""
        elements = {}
        
        try:
            # 使用JavaScript快速获取所有可能的元素
            js_script = """
            return {
                inputs: Array.from(document.querySelectorAll('input')).map((el, index) => ({
                    index: index,
                    tag: el.tagName,
                    type: el.type,
                    name: el.name,
                    id: el.id,
                    className: el.className,
                    placeholder: el.placeholder,
                    value: el.value,
                    checked: el.checked
                })),
                buttons: Array.from(document.querySelectorAll('button')).map((el, index) => ({
                    index: index,
                    tag: el.tagName,
                    type: el.type,
                    className: el.className,
                    text: el.textContent.trim()
                }))
            };
            """
            
            # 执行JavaScript获取元素信息
            js_elements = self.driver.execute_script(js_script)
            
            # 快速识别生日输入框
            birth_input = self._find_birth_input(js_elements['inputs'])
            if birth_input:
                elements['birth_input'] = self._get_element_by_index('input', birth_input['index'])
            
            # 快速识别复选框
            checkboxes = self._find_checkboxes(js_elements['inputs'])
            if checkboxes:
                elements['checkboxes'] = [self._get_element_by_index('input', cb['index']) for cb in checkboxes]
            
            # 快速识别提交按钮
            submit_button = self._find_submit_button(js_elements['buttons'])
            if submit_button:
                elements['submit_button'] = self._get_element_by_index('button', submit_button['index'])
            
            return elements
            
        except Exception as e:
            print(f"⚠️ JavaScript检测失败，使用备用方法: {e}")
            return self._fallback_element_detection()
    
    def _find_birth_input(self, inputs: List[Dict]) -> Optional[Dict]:
        """识别生日输入框"""
        for inp in inputs:
            if inp['type'] in ['text', 'date', 'tel']:
                # 检查placeholder或name中是否包含生日相关关键词
                text_to_check = f"{inp.get('placeholder', '')} {inp.get('name', '')}".lower()
                if any(keyword in text_to_check for keyword in ['생년월일', 'birth', 'birthday', 'date']):
                    return inp
                # 如果是空的text输入框，也可能是生日输入框
                if inp['type'] == 'text' and not inp.get('value'):
                    return inp
        return None
    
    def _find_checkboxes(self, inputs: List[Dict]) -> List[Dict]:
        """识别复选框"""
        checkboxes = []
        for inp in inputs:
            if inp['type'] == 'checkbox':
                checkboxes.append(inp)
        return checkboxes[:2]  # 只取前两个
    
    def _find_submit_button(self, buttons: List[Dict]) -> Optional[Dict]:
        """识别提交按钮"""
        for btn in buttons:
            text = btn.get('text', '').strip()
            if any(keyword in text for keyword in ['참여 신청', '제출', '확인', '신청']):
                return btn
        # 如果没找到特定文本，返回最后一个按钮
        return buttons[-1] if buttons else None
    
    def _get_element_by_index(self, tag_name: str, index: int) -> Any:
        """根据标签名和索引获取元素"""
        try:
            elements = self.driver.find_elements(By.TAG_NAME, tag_name)
            return elements[index] if index < len(elements) else None
        except:
            return None
    
    def _fallback_element_detection(self) -> Dict[str, Any]:
        """备用元素检测方法"""
        elements = {}
        
        try:
            # 查找生日输入框
            birth_selectors = [
                'input[placeholder*="생년월일"]',
                'input[name*="birth"]',
                'input[type="date"]',
                'input[type="text"]:not([value])',
            ]
            
            for selector in birth_selectors:
                try:
                    element = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if element.is_displayed():
                        elements['birth_input'] = element
                        break
                except:
                    continue
            
            # 查找复选框
            try:
                checkbox_elements = self.driver.find_elements(By.CSS_SELECTOR, 'input[type="checkbox"]')
                checkboxes = [cb for cb in checkbox_elements if cb.is_displayed()]
                if checkboxes:
                    elements['checkboxes'] = checkboxes[:2]
            except:
                pass
            
            # 查找提交按钮
            submit_selectors = [
                'button[type="submit"]',
                'button:contains("참여 신청")',
                'button:contains("제출")',
                'input[type="submit"]',
                'button:last-of-type',
            ]
            
            for selector in submit_selectors:
                try:
                    element = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if element.is_displayed():
                        elements['submit_button'] = element
                        break
                except:
                    continue
            
            return elements
            
        except Exception as e:
            print(f"❌ 备用检测失败: {e}")
            return {}
    
    def _parallel_form_filling(self, elements: Dict[str, Any]) -> bool:
        """并行表单填写"""
        try:
            tasks = []
            
            with ThreadPoolExecutor(max_workers=4) as executor:
                # 任务1: 填写生日
                if elements.get('birth_input'):
                    tasks.append(executor.submit(self._fill_birth_input, elements['birth_input']))
                
                # 任务2: 勾选复选框
                if elements.get('checkboxes'):
                    tasks.append(executor.submit(self._check_all_checkboxes, elements['checkboxes']))
                
                # 等待所有任务完成
                success_count = 0
                for future in as_completed(tasks, timeout=0.3):
                    try:
                        if future.result():
                            success_count += 1
                    except Exception as e:
                        print(f"⚠️ 并行任务失败: {e}")
                
                return success_count > 0
                
        except Exception as e:
            print(f"❌ 并行填写失败: {e}")
            return False
    
    def _fill_birth_input(self, element) -> bool:
        """填写生日输入框"""
        try:
            # 使用JavaScript直接设置值，最快
            self.driver.execute_script(f"arguments[0].value = '{self.form_data['birth_date']}';", element)
            # 触发change事件
            self.driver.execute_script("arguments[0].dispatchEvent(new Event('change'));", element)
            print(f"✅ 生日填写完成: {self.form_data['birth_date']}")
            return True
        except Exception as e:
            print(f"❌ 生日填写失败: {e}")
            return False
    
    def _check_all_checkboxes(self, checkboxes: List) -> bool:
        """勾选所有复选框"""
        try:
            success_count = 0
            for i, checkbox in enumerate(checkboxes):
                try:
                    if not checkbox.is_selected():
                        # 使用JavaScript点击，最快
                        self.driver.execute_script("arguments[0].click();", checkbox)
                        success_count += 1
                        print(f"✅ 复选框{i+1}勾选完成")
                except Exception as e:
                    print(f"⚠️ 复选框{i+1}勾选失败: {e}")
            
            return success_count > 0
            
        except Exception as e:
            print(f"❌ 复选框处理失败: {e}")
            return False
    
    def _instant_submit(self, submit_button) -> bool:
        """瞬间提交表单"""
        try:
            if not submit_button:
                print("❌ 未找到提交按钮")
                return False
            
            # 开始网络监控
            if self.network_monitor:
                self.network_monitor.start_monitoring()
            
            # 使用JavaScript点击提交按钮，最快
            self.driver.execute_script("arguments[0].click();", submit_button)
            print("🚀 表单提交完成")
            
            # 短暂等待网络请求
            time.sleep(0.1)
            
            return True
            
        except Exception as e:
            print(f"❌ 表单提交失败: {e}")
            return False
    
    def _create_result(self, success: bool, message: str, extra_data: Dict = None) -> Dict[str, Any]:
        """创建结果对象"""
        result = {
            'success': success,
            'message': message,
            'timestamp': datetime.now().isoformat(),
            'processing_time': time.time() - self.start_time if self.start_time else 0,
        }
        
        if extra_data:
            result.update(extra_data)
        
        return result
    
    def capture_page_and_network_data(self) -> Dict[str, Any]:
        """捕获页面和网络数据"""
        try:
            data = {
                'timestamp': datetime.now().isoformat(),
                'url': self.driver.current_url,
                'title': self.driver.title,
                'html_content': self.driver.page_source,
                'network_requests': []
            }
            
            # 获取网络请求数据
            if self.network_monitor:
                data['network_requests'] = self.network_monitor.get_captured_requests()
            
            # 保存数据
            self._save_data(data)
            
            return data
            
        except Exception as e:
            print(f"❌ 数据捕获失败: {e}")
            return {}
    
    def _save_data(self, data: Dict[str, Any]):
        """保存数据到文件"""
        try:
            data_dir = "/Users/wenbai/Desktop/chajian/auto/data"
            os.makedirs(data_dir, exist_ok=True)
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = os.path.join(data_dir, f"lightning_form_data_{timestamp}.json")
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            print(f"📁 数据已保存到: {filename}")
            
        except Exception as e:
            print(f"❌ 数据保存失败: {e}")


def process_form_lightning_fast(driver, network_monitor=None, birth_date='19900101') -> Dict[str, Any]:
    """
    闪电表单处理函数
    
    Args:
        driver: WebDriver实例
        network_monitor: 网络监控器
        birth_date: 生日数据
    
    Returns:
        处理结果
    """
    processor = LightningFormProcessor(driver, network_monitor)
    return processor.process_form_lightning_fast(birth_date)


def capture_and_process_complete_flow(driver, network_monitor=None, birth_date='19900101'):
    """
    完整流程：捕获页面 → 处理表单 → 获取网络数据
    """
    processor = LightningFormProcessor(driver, network_monitor)
    
    print("\n🔄 开始完整流程处理...")
    
    # 1. 处理表单
    result = processor.process_form_lightning_fast(birth_date)
    
    # 2. 捕获数据
    data = processor.capture_page_and_network_data()
    
    # 3. 返回完整结果
    return {
        'form_processing': result,
        'captured_data': data,
        'total_success': result.get('success', False) and bool(data)
    }