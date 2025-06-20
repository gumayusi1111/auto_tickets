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

# 导入表单选择器配置
from config.form_selectors import get_form_selectors


class LightningFormProcessor:
    """闪电表单处理器 - 专为0.5秒内完成表单填写而设计"""
    
    def __init__(self, driver, network_monitor=None):
        self.driver = driver
        self.network_monitor = network_monitor
        self.start_time = None
        self.form_selectors = get_form_selectors()  # 获取表单选择器配置
        self.form_data = {
            'birth_date': '19900101',  # 默认生日
            'phone': '01012345678',  # 默认手机号
            'checkboxes_to_check': 2,  # 需要勾选的复选框数量
        }
    
    def process_form_lightning_fast(self, birth_date='19900101', phone_number='01012345678') -> Dict[str, Any]:
        """闪电般快速处理表单 - 优化版：边检测边处理，无等待"""
        self.start_time = time.time()
        print(f"\n⚡ 开始闪电表单处理 - 边检测边处理策略")
        
        try:
            # 更新表单数据
            self.form_data['birth_date'] = birth_date
            self.form_data['phone'] = phone_number
            
            # 策略1: 极限优化 - 一次JavaScript调用（如果页面完全加载）
            if self._quick_element_check():
                print("🚀 页面已完全加载，使用极限优化策略...")
                extreme_result = self._process_form_extreme_speed()
                if extreme_result and extreme_result.get('success'):
                    return extreme_result
            
            # 策略2: 智能渐进式处理 - 边发现边处理
            print("🔄 使用智能渐进式处理策略...")
            progressive_result = self._progressive_form_processing()
            if progressive_result:
                return progressive_result
            
            # 策略3: 传统备用方案
            print("🔄 使用传统备用处理方案...")
            return self._fallback_form_processing()
            
        except Exception as e:
            total_time = time.time() - self.start_time
            print(f"❌ 所有策略都失败: {e}, 耗时: {total_time:.3f}秒")
            return self._create_result(False, f"处理失败: {e}")
    
    def _quick_element_check(self) -> bool:
        """快速检查页面是否完全加载"""
        try:
            # 检查关键元素是否都存在且可用
            birth_exists = bool(self.driver.find_elements("css selector", self.form_selectors['birth_date']))
            phone_exists = bool(self.driver.find_elements("css selector", self.form_selectors['phone_number']))
            submit_exists = bool(self.driver.find_elements("css selector", self.form_selectors['submit_button_selectors'][0]))
            
            return birth_exists and phone_exists and submit_exists
        except:
            return False
    
    def _progressive_form_processing(self) -> Dict[str, Any]:
        """渐进式表单处理 - 边发现元素边处理，无需等待全部加载"""
        print("🔄 启动渐进式处理 - 发现一个处理一个...")
        
        processing_results = {
            'birth_filled': False,
            'phone_handled': False,
            'checkboxes_checked': 0,
            'submitted': False
        }
        
        max_attempts = 60  # 最多尝试60次（约3秒，每次0.05秒）
        attempt_interval = 0.05
        
        for attempt in range(max_attempts):
            current_time = time.time() - self.start_time
            
            try:
                # 1. 优先处理生日输入框（最重要）
                if not processing_results['birth_filled']:
                    try:
                        birth_input = self.driver.find_element("css selector", self.form_selectors['birth_date'])
                        if birth_input and birth_input.is_displayed() and birth_input.is_enabled():
                            birth_input.clear()
                            birth_input.send_keys(self.form_data['birth_date'])
                            processing_results['birth_filled'] = True
                            print(f"✅ 生日填写完成 ({current_time:.2f}s)")
                    except:
                        pass
                
                # 2. 智能处理手机号
                if not processing_results['phone_handled']:
                    try:
                        phone_input = self.driver.find_element("css selector", self.form_selectors['phone_number'])
                        if phone_input and phone_input.is_displayed() and phone_input.is_enabled():
                            current_value = phone_input.get_attribute('value').strip()
                            if not current_value:  # 只在空白时填写
                                phone_input.send_keys(self.form_data['phone'])
                                print(f"✅ 手机号填写完成 ({current_time:.2f}s)")
                            else:
                                print(f"⏭️ 手机号已预填 ({current_value}) - 跳过 ({current_time:.2f}s)")
                            processing_results['phone_handled'] = True
                    except:
                        pass
                
                # 3. 处理复选框（尽快勾选）
                if processing_results['checkboxes_checked'] < 2:
                    for i, checkbox_selector in enumerate(self.form_selectors['checkboxes']):
                        if processing_results['checkboxes_checked'] <= i:
                            try:
                                checkbox = self.driver.find_element("css selector", checkbox_selector)
                                if checkbox and checkbox.is_displayed():
                                    checkbox.click()
                                    processing_results['checkboxes_checked'] += 1
                                    print(f"✅ 复选框{i+1}勾选完成 ({current_time:.2f}s)")
                            except:
                                pass
                
                # 4. 一旦关键元素处理完毕，立即尝试提交
                if (processing_results['birth_filled'] and 
                    processing_results['phone_handled'] and 
                    not processing_results['submitted']):
                    
                    for submit_selector in self.form_selectors['submit_button_selectors']:
                        try:
                            submit_btn = self.driver.find_element("css selector", submit_selector)
                            if submit_btn and submit_btn.is_displayed() and submit_btn.is_enabled():
                                submit_btn.click()
                                processing_results['submitted'] = True
                                print(f"🚀 表单提交完成 ({current_time:.2f}s)")
                                break
                        except:
                            continue
                    
                    if processing_results['submitted']:
                        break
                
                # 检查是否所有关键任务都完成
                if (processing_results['birth_filled'] and 
                    processing_results['phone_handled'] and 
                    processing_results['submitted']):
                    break
                
                # 短暂等待后继续尝试
                time.sleep(attempt_interval)
                
            except Exception as e:
                print(f"⚠️ 渐进处理第{attempt+1}次尝试失败: {e}")
                time.sleep(attempt_interval)
                continue
        
        total_time = time.time() - self.start_time
        success = processing_results['birth_filled'] and processing_results['submitted']
        
        if success:
            print(f"🎉 渐进式处理成功! 总耗时: {total_time:.3f}秒")
            print(f"   处理详情: 生日✅ 手机号✅ 复选框{processing_results['checkboxes_checked']}/2 提交✅")
        else:
            print(f"⚠️ 渐进式处理部分完成: 总耗时: {total_time:.3f}秒")
            print(f"   处理状态: 生日{'✅' if processing_results['birth_filled'] else '❌'} "
                  f"手机号{'✅' if processing_results['phone_handled'] else '❌'} "
                  f"复选框{processing_results['checkboxes_checked']}/2 "
                  f"提交{'✅' if processing_results['submitted'] else '❌'}")
        
        return self._create_result(success, f"渐进式处理完成，耗时{total_time:.3f}秒", {
            'processing_results': processing_results,
            'total_time': total_time,
            'attempts_used': min(attempt + 1, max_attempts)
        })
    
    def _fallback_form_processing(self) -> Dict[str, Any]:
        """传统备用处理方案"""
        print("🔄 启动传统备用处理...")
        
        try:
            # 阶段1: 快速元素识别
            elements = self._rapid_element_detection_with_selectors()
            detection_time = time.time() - self.start_time
            print(f"🔍 元素识别完成: {detection_time:.3f}秒")
            
            if not elements:
                return self._create_result(False, "未找到表单元素")
            
            # 阶段2: 并行填写
            fill_success = self._parallel_form_filling(elements)
            fill_time = time.time() - self.start_time
            print(f"📝 表单填写完成: {fill_time:.3f}秒")
            
            # 阶段3: 提交表单
            submit_success = self._instant_submit(elements.get('submit_button'))
            submit_time = time.time() - self.start_time
            print(f"🚀 表单提交完成: {submit_time:.3f}秒")
            
            total_time = time.time() - self.start_time
            success = fill_success and submit_success
            
            return self._create_result(success, f"备用处理完成，耗时{total_time:.3f}秒", {
                'detection_time': detection_time,
                'fill_time': fill_time,
                'submit_time': submit_time,
                'total_time': total_time
            })
            
        except Exception as e:
            total_time = time.time() - self.start_time
            return self._create_result(False, f"备用处理失败: {e}")
    
    def _use_extreme_optimization(self) -> bool:
        """判断是否使用极限优化"""
        # 如果有具体的选择器，使用极限优化
        return bool(self.form_selectors.get('birth_date') and 
                   self.form_selectors.get('submit_button_selectors'))
    
    def _process_form_extreme_speed(self) -> Dict[str, Any]:
        """极限速度处理 - 单次JavaScript调用完成所有操作"""
        try:
            # 极限优化的JavaScript代码 - 直接使用选择器和数据
            extreme_js = f"""
            return (function() {{
                const t0 = performance.now();
                const results = {{success: true, operations: [], details: {{}}}};
                
                try {{
                    // 设置生日输入框
                    const birthInput = document.querySelector('{self.form_selectors['birth_date']}');
                    if (birthInput) {{
                        birthInput.value = '{self.form_data['birth_date']}';
                        birthInput.dispatchEvent(new Event('input', {{bubbles: true}}));
                        birthInput.dispatchEvent(new Event('change', {{bubbles: true}}));
                        results.operations.push('birth');
                        results.details.birth_value = birthInput.value;
                    }} else {{
                        results.details.birth_error = 'Birth input not found';
                    }}
                    
                    // 智能处理手机号输入框 - 仅在为空时填写
                    const phoneInput = document.querySelector('{self.form_selectors['phone_number']}');
                    if (phoneInput) {{
                        const currentPhoneValue = phoneInput.value.trim();
                        if (currentPhoneValue === '' || currentPhoneValue.length === 0) {{
                            phoneInput.value = '{self.form_data['phone']}';
                            phoneInput.dispatchEvent(new Event('input', {{bubbles: true}}));
                            phoneInput.dispatchEvent(new Event('change', {{bubbles: true}}));
                            results.operations.push('phone_filled');
                            results.details.phone_value = phoneInput.value;
                            results.details.phone_action = 'filled_empty_field';
                        }} else {{
                            results.operations.push('phone_skipped');
                            results.details.phone_value = currentPhoneValue;
                            results.details.phone_action = 'skipped_prefilled';
                        }}
                    }} else {{
                        results.details.phone_error = 'Phone input not found';
                    }}
                    
                    // 勾选具体的复选框 - 使用用户提供的选择器
                    let checkboxCount = 0;
                    const checkboxSelectors = {self.form_selectors['checkboxes']};
                    checkboxSelectors.forEach((selector, i) => {{
                        try {{
                            // 先尝试直接点击SVG元素
                            const svgElement = document.querySelector(selector);
                            if (svgElement) {{
                                svgElement.click();
                                checkboxCount++;
                                results.operations.push('checkbox' + (i + 1) + '_svg');
                            }} else {{
                                // 如果SVG不存在，尝试查找父级的checkbox input
                                const checkboxInput = document.querySelector(`input[type="checkbox"]:nth-of-type(${{i + 1}})`);
                                if (checkboxInput && !checkboxInput.checked) {{
                                    checkboxInput.checked = true;
                                    checkboxInput.dispatchEvent(new Event('change', {{bubbles: true}}));
                                    checkboxCount++;
                                    results.operations.push('checkbox' + (i + 1) + '_input');
                                }}
                            }}
                        }} catch (cbError) {{
                            console.log('复选框', i + 1, '点击失败:', cbError);
                        }}
                    }});
                    results.details.checkboxes_count = checkboxCount;
                    
                    // 立即提交 - 使用配置中的选择器
                    const submitBtn = document.querySelector('{self.form_selectors['submit_button_selectors'][0]}') || 
                                    document.querySelector('input[type="submit"]') || 
                                    document.querySelector('button[type="submit"]');
                    
                    if (submitBtn) {{
                        submitBtn.click();
                        results.operations.push('submit');
                        results.details.submit_button = submitBtn.tagName;
                    }} else {{
                        results.details.submit_error = 'Submit button not found';
                    }}
                    
                    results.jsTime = performance.now() - t0;
                    return results;
                    
                }} catch (e) {{
                    return {{success: false, error: e.toString(), jsTime: performance.now() - t0}};
                }}
            }})();
            """
            
            # 执行极速处理
            start_perf = time.perf_counter()
            result = self.driver.execute_script(extreme_js)
            
            total_time = (time.perf_counter() - start_perf) * 1000  # 毫秒
            
            if result['success']:
                print(f"🚀 极限处理成功!")
                print(f"   JavaScript执行: {result['jsTime']:.2f}ms")
                print(f"   Python总耗时: {total_time:.2f}ms")
                print(f"   完成操作: {', '.join(result['operations'])}")
                
                # 显示详细信息
                details = result.get('details', {})
                if 'birth_value' in details:
                    print(f"   ✅ 生日输入: {details['birth_value']}")
                if 'phone_value' in details:
                    phone_action = details.get('phone_action', 'unknown')
                    if phone_action == 'filled_empty_field':
                        print(f"   ✅ 手机号填写: {details['phone_value']}")
                    elif phone_action == 'skipped_prefilled':
                        print(f"   📱 手机号已预填: {details['phone_value']} (跳过)")
                    else:
                        print(f"   ✅ 手机号处理: {details['phone_value']}")
                if 'checkboxes_count' in details:
                    print(f"   ✅ 复选框: {details['checkboxes_count']}个已勾选")
                if 'submit_button' in details:
                    print(f"   ✅ 提交按钮: {details['submit_button']}已点击")
                
                # 显示错误信息
                if 'birth_error' in details:
                    print(f"   ❌ 生日错误: {details['birth_error']}")
                if 'phone_error' in details:
                    print(f"   ❌ 手机错误: {details['phone_error']}")
                if 'submit_error' in details:
                    print(f"   ❌ 提交错误: {details['submit_error']}")
                
                return self._create_result(True, f"极限处理完成，耗时{total_time:.2f}ms", {
                    'total_time_ms': total_time,
                    'js_time_ms': result['jsTime'],
                    'operations': result['operations'],
                    'details': details,
                    'optimization': 'extreme'
                })
            else:
                raise Exception(result.get('error', 'Unknown error'))
                
        except Exception as e:
            print(f"⚠️ 极限优化失败，使用备用方案: {e}")
            # 失败时返回None，让主函数使用传统方法
            return None
    
    def _rapid_element_detection_with_selectors(self) -> Dict[str, Any]:
        """使用具体选择器快速检测元素 - 0.1秒内完成"""
        elements = {}
        
        try:
            # 并行查找所有元素
            with ThreadPoolExecutor(max_workers=5) as executor:
                futures = {}
                
                # 提交查找任务
                futures['birth_input'] = executor.submit(self._find_element_by_selector, 
                                                        self.form_selectors['birth_date'], 
                                                        '生日输入框')
                futures['phone_input'] = executor.submit(self._find_element_by_selector, 
                                                        self.form_selectors['phone_number'], 
                                                        '手机号输入框')
                futures['submit_button'] = executor.submit(self._find_submit_button_fast)
                
                # 查找复选框
                for i, selector in enumerate(self.form_selectors['checkboxes']):
                    futures[f'checkbox_{i}'] = executor.submit(self._find_checkbox_parent, 
                                                             selector, 
                                                             f'复选框{i+1}')
                
                # 收集结果
                checkboxes = []
                for key, future in futures.items():
                    try:
                        result = future.result(timeout=0.1)
                        if result:
                            if 'checkbox' in key:
                                checkboxes.append(result)
                            else:
                                elements[key] = result
                    except Exception as e:
                        print(f"⚠️ {key} 查找失败: {e}")
                
                if checkboxes:
                    elements['checkboxes'] = checkboxes
            
            return elements
            
        except Exception as e:
            print(f"⚠️ 选择器检测失败，使用备用方法: {e}")
            return self._rapid_element_detection()
    
    def _find_element_by_selector(self, selector: str, element_name: str) -> Optional[Any]:
        """通过选择器查找元素"""
        try:
            element = self.driver.find_element(By.CSS_SELECTOR, selector)
            if element and element.is_displayed():
                print(f"✅ 找到{element_name}: {selector}")
                return element
        except Exception as e:
            print(f"❌ {element_name}未找到: {e}")
        return None
    
    def _find_checkbox_parent(self, svg_selector: str, checkbox_name: str) -> Optional[Any]:
        """通过SVG选择器找到复选框的可点击父元素"""
        try:
            # 首先找到SVG元素
            svg_element = self.driver.find_element(By.CSS_SELECTOR, svg_selector)
            
            # 找到最近的可点击父元素（通常是label或包含的div）
            parent = svg_element
            for _ in range(5):  # 最多向上查找5层
                parent = parent.find_element(By.XPATH, '..')
                tag_name = parent.tag_name.lower()
                if tag_name in ['label', 'div', 'span']:
                    # 检查是否有关联的checkbox input
                    try:
                        checkbox_input = parent.find_element(By.CSS_SELECTOR, 'input[type="checkbox"]')
                        if checkbox_input:
                            print(f"✅ 找到{checkbox_name}的input元素")
                            return checkbox_input
                    except:
                        pass
                    
                    # 如果没有找到input，返回可点击的父元素
                    if parent.is_displayed() and parent.is_enabled():
                        print(f"✅ 找到{checkbox_name}的可点击元素: {tag_name}")
                        return parent
            
            print(f"⚠️ {checkbox_name}未找到可点击的父元素，使用SVG元素")
            return svg_element
            
        except Exception as e:
            print(f"❌ {checkbox_name}查找失败: {e}")
            return None
    
    def _find_submit_button_fast(self) -> Optional[Any]:
        """快速查找提交按钮"""
        try:
            # 使用JavaScript一次性查找所有可能的按钮（包括button和input）
            js_script = """
            const selectors = arguments[0];
            for (let selector of selectors) {
                try {
                    // 处理contains选择器
                    if (selector.includes(':contains')) {
                        const text = selector.match(/:contains\("(.+?)"\)/)[1];
                        const buttons = Array.from(document.querySelectorAll('button'));
                        const found = buttons.find(btn => btn.textContent.includes(text));
                        if (found) return found;
                    } else {
                        const element = document.querySelector(selector);
                        if (element) return element;
                    }
                } catch (e) {
                    continue;
                }
            }
            return null;
            """
            
            button = self.driver.execute_script(js_script, self.form_selectors['submit_button_selectors'])
            if button:
                element_type = button.tag_name.lower()
                print(f"✅ 找到提交按钮 ({element_type})")
                return button
            
        except Exception as e:
            print(f"⚠️ JavaScript查找按钮失败: {e}")
        
        # 备用方法：查找button或input[type="submit"]
        try:
            # 先查找input[type="submit"]
            submit_inputs = self.driver.find_elements(By.CSS_SELECTOR, 'input[type="submit"]')
            if submit_inputs:
                print(f"✅ 找到input类型的提交按钮")
                return submit_inputs[0]
            
            # 再查找button
            buttons = self.driver.find_elements(By.TAG_NAME, 'button')
            if buttons:
                last_button = buttons[-1]
                print(f"✅ 使用最后一个button作为提交按钮")
                return last_button
        except:
            pass
        
        return None
    
    def _rapid_element_detection(self) -> Dict[str, Any]:
        """通用快速元素检测 - 作为备用方法"""
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
            birth_input = self._find_birth_input_generic(js_elements['inputs'])
            if birth_input:
                elements['birth_input'] = self._get_element_by_index('input', birth_input['index'])
            
            # 快速识别手机号输入框
            phone_input = self._find_phone_input_generic(js_elements['inputs'])
            if phone_input:
                elements['phone_input'] = self._get_element_by_index('input', phone_input['index'])
            
            # 快速识别复选框
            checkboxes = self._find_checkboxes_generic(js_elements['inputs'])
            if checkboxes:
                elements['checkboxes'] = [self._get_element_by_index('input', cb['index']) for cb in checkboxes]
            
            # 快速识别提交按钮
            submit_button = self._find_submit_button_generic(js_elements['buttons'])
            if submit_button:
                elements['submit_button'] = self._get_element_by_index('button', submit_button['index'])
            
            return elements
            
        except Exception as e:
            print(f"⚠️ 通用JavaScript检测失败: {e}")
            return {}
    
    def _find_birth_input_generic(self, inputs: List[Dict]) -> Optional[Dict]:
        """通用方法识别生日输入框"""
        for inp in inputs:
            if inp['type'] in ['text', 'date', 'tel']:
                # 检查placeholder或name中是否包含生日相关关键词
                text_to_check = f"{inp.get('placeholder', '')} {inp.get('name', '')} {inp.get('id', '')}".lower()
                if any(keyword in text_to_check for keyword in ['생년월일', 'birth', 'birthday', 'date']):
                    return inp
        return None
    
    def _find_phone_input_generic(self, inputs: List[Dict]) -> Optional[Dict]:
        """通用方法识别手机号输入框"""
        for inp in inputs:
            if inp['type'] in ['text', 'tel', 'number']:
                # 检查placeholder或name中是否包含手机号相关关键词
                text_to_check = f"{inp.get('placeholder', '')} {inp.get('name', '')} {inp.get('id', '')}".lower()
                if any(keyword in text_to_check for keyword in ['phone', '전화', '연락처', '휴대폰']):
                    return inp
        return None
    
    def _find_checkboxes_generic(self, inputs: List[Dict]) -> List[Dict]:
        """通用方法识别复选框"""
        checkboxes = []
        for inp in inputs:
            if inp['type'] == 'checkbox':
                checkboxes.append(inp)
        return checkboxes[:2]  # 只取前两个
    
    def _find_submit_button_generic(self, buttons: List[Dict]) -> Optional[Dict]:
        """通用方法识别提交按钮"""
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
    
    def _parallel_form_filling(self, elements: Dict[str, Any]) -> bool:
        """并行表单填写"""
        try:
            tasks = []
            
            with ThreadPoolExecutor(max_workers=5) as executor:
                # 任务1: 填写生日
                if elements.get('birth_input'):
                    tasks.append(executor.submit(self._fill_birth_input, elements['birth_input']))
                
                # 任务2: 填写手机号
                if elements.get('phone_input'):
                    tasks.append(executor.submit(self._fill_phone_input, elements['phone_input']))
                
                # 任务3: 勾选复选框
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
            # 触发change和input事件
            self.driver.execute_script("""
                arguments[0].dispatchEvent(new Event('change', {bubbles: true}));
                arguments[0].dispatchEvent(new Event('input', {bubbles: true}));
            """, element)
            print(f"✅ 生日填写完成: {self.form_data['birth_date']}")
            return True
        except Exception as e:
            print(f"❌ 生日填写失败: {e}")
            return False
    
    def _fill_phone_input(self, element) -> bool:
        """智能填写手机号输入框 - 仅在为空时填写"""
        try:
            # 检查当前值是否为空
            current_value = element.get_attribute('value')
            if current_value and current_value.strip():
                print(f"📱 手机号已预填，跳过填写: {current_value}")
                return True
            
            # 为空时才填写
            self.driver.execute_script(f"arguments[0].value = '{self.form_data['phone']}';", element)
            # 触发change和input事件
            self.driver.execute_script("""
                arguments[0].dispatchEvent(new Event('change', {bubbles: true}));
                arguments[0].dispatchEvent(new Event('input', {bubbles: true}));
            """, element)
            print(f"✅ 手机号填写完成: {self.form_data['phone']}")
            return True
        except Exception as e:
            print(f"❌ 手机号处理失败: {e}")
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

    def process_form_ultra_fast(self, birth_date: str, phone_number: str) -> Dict[str, Any]:
        """
        超级优化表单处理 - 目标0.5ms以下
        专为极限速度优化，减少所有不必要的操作
        """
        process_start = time.perf_counter()
        
        try:
            # 获取选择器配置
            selectors = get_form_selectors()
            
            # 超级优化JavaScript - 单次执行，无冗余操作
            ultra_fast_script = f"""
            (function() {{
                const start = performance.now();
                
                // 直接操作，不进行任何检查
                const birth = document.querySelector('{selectors['birth_date']}');
                const phone = document.querySelector('{selectors['phone_number']}');
                const submit = document.querySelector('{selectors['submit_button_selectors'][0]}');
                
                // 超速填写（无事件触发）
                if (birth) birth.value = '{birth_date}';
                if (phone && !phone.value) phone.value = '{phone_number}';
                
                // 超速复选框勾选（兼容SVG元素）
                const cb1 = document.querySelector('{selectors['checkboxes'][0]}');
                const cb2 = document.querySelector('{selectors['checkboxes'][1]}');
                let cb1_clicked = false, cb2_clicked = false;
                
                if (cb1) {{
                    try {{
                        if (cb1.tagName === 'SVG' || cb1.click === undefined) {{
                            cb1.dispatchEvent(new MouseEvent('click', {{bubbles: true}}));
                        }} else {{
                            cb1.click();
                        }}
                        cb1_clicked = true;
                    }} catch(e) {{
                        // 尝试点击父元素
                        if (cb1.parentElement) {{
                            cb1.parentElement.click();
                            cb1_clicked = true;
                        }}
                    }}
                }}
                
                if (cb2) {{
                    try {{
                        if (cb2.tagName === 'SVG' || cb2.click === undefined) {{
                            cb2.dispatchEvent(new MouseEvent('click', {{bubbles: true}}));
                        }} else {{
                            cb2.click();
                        }}
                        cb2_clicked = true;
                    }} catch(e) {{
                        // 尝试点击父元素
                        if (cb2.parentElement) {{
                            cb2.parentElement.click();
                            cb2_clicked = true;
                        }}
                    }}
                }}
                
                // 超速提交
                if (submit) submit.click();
                
                return {{
                    success: true,
                    birth_filled: !!birth,
                    phone_filled: !!phone,
                    checkboxes_clicked: (cb1_clicked ? 1 : 0) + (cb2_clicked ? 1 : 0),
                    submitted: !!submit,
                    js_time: performance.now() - start
                }};
            }})();
            """
            
            # 执行超级优化脚本
            js_start = time.perf_counter()
            result = self.driver.execute_script(ultra_fast_script)
            js_time = (time.perf_counter() - js_start) * 1000
            
            total_time = (time.perf_counter() - process_start) * 1000
            
            if result and result.get('success'):
                print(f"🚀 超级优化成功! JavaScript: {result['js_time']:.2f}ms, 总耗时: {total_time:.2f}ms")
                
                return {
                    'success': True,
                    'processing_time_ms': total_time,
                    'js_execution_time_ms': result['js_time'],
                    'elements_filled': (1 if result['birth_filled'] else 0) + (1 if result['phone_filled'] else 0),
                    'checkboxes_checked': result['checkboxes_clicked'],
                    'submitted': result['submitted'],
                    'optimization_level': 'ultra_fast'
                }
            else:
                return {'success': False, 'error': 'JavaScript执行失败', 'processing_time_ms': total_time}
                
        except Exception as e:
            total_time = (time.perf_counter() - process_start) * 1000
            print(f"❌ 超级优化失败: {e}")
            return {'success': False, 'error': str(e), 'processing_time_ms': total_time}


def process_form_lightning_fast(driver, network_monitor=None, birth_date='19900101', phone_number='01012345678') -> Dict[str, Any]:
    """
    闪电表单处理函数
    
    Args:
        driver: WebDriver实例
        network_monitor: 网络监控器
        birth_date: 生日数据
        phone_number: 手机号数据
    
    Returns:
        处理结果
    """
    processor = LightningFormProcessor(driver, network_monitor)
    return processor.process_form_lightning_fast(birth_date, phone_number)


def capture_and_process_complete_flow(driver, network_monitor=None, birth_date='19900101', phone_number='01012345678'):
    """
    完整流程：捕获页面 → 处理表单 → 获取网络数据
    """
    processor = LightningFormProcessor(driver, network_monitor)
    
    print("\n🔄 开始完整流程处理...")
    
    # 1. 处理表单
    result = processor.process_form_lightning_fast(birth_date, phone_number)
    
    # 2. 捕获数据
    data = processor.capture_page_and_network_data()
    
    # 3. 返回完整结果
    return {
        'form_processing': result,
        'captured_data': data,
        'total_success': result.get('success', False) and bool(data)
    }