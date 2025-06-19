#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
mode_handler.py
模式处理器主类 - 智能版本
"""

import time
import json
import pytz
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# 导入配置和工具函数
from config.mode_config import (
    get_default_user_info, get_button_selectors, get_browser_config,
    get_time_config, get_network_monitor_config, get_prompt_message,
    get_status_message, validate_user_input
)
from ..browser.setup import setup_driver, create_wait
from ..auth.login_handler import click_login_button_only, click_confirm_login_button, wait_for_manual_login
from ..analysis.content_extractor import extract_article_content
from ..analysis.time_processor import (
    extract_time_info, convert_to_china_time, calculate_time_difference,
    show_countdown, get_time_input, show_countdown_with_dynamic_timing
)
from ..ai.analyzer import analyze_with_ai, extract_time_with_ai
from ..analysis.data_saver import save_analysis
from ..analysis.page_crawler import crawl_page_content


class ModeHandler:
    """智能模式处理器主类"""
    
    def __init__(self):
        """初始化模式处理器"""
        self.user_info = {}
        self.browser_config = get_browser_config()
        self.time_config = get_time_config()
        self.network_config = get_network_monitor_config()
        self.button_config = get_button_selectors()
        
        # 时区设置
        self.china_tz = pytz.timezone(self.time_config['default_timezone'])
        self.korea_tz = pytz.timezone(self.time_config['source_timezone'])
        
        # 组件初始化
        self.driver = None
        self.wait = None
        self.network_monitor = None
    
    def collect_user_input(self) -> bool:
        """收集用户输入信息"""
        try:
            print(get_prompt_message('welcome'))
            print(get_prompt_message('separator'))
            print(get_prompt_message('input_info'))
            
            # 获取目标URL
            target_url = input(get_prompt_message('url_prompt')).strip()
            if not target_url or not validate_user_input('url', target_url):
                print("❌ URL不能为空或格式不正确")
                return False
            
            # 选择运行模式
            print("\n🎯 请选择运行模式:")
            print("1. 自动填写模式 - 程序自动填写表单")
            print("2. 监控模式 - 只点击申请按钮，用户手动填写，程序监控请求")
            mode_choice = input("请选择模式 (1/2): ").strip()
            
            auto_fill_mode = mode_choice == "1"
            if auto_fill_mode:
                print("✅ 已选择: 自动填写模式")
            else:
                print("✅ 已选择: 监控模式 (手动填写)")
            
            # 询问是否启用网络监控
            network_monitor_input = input(get_prompt_message('network_monitor_prompt')).strip().lower()
            enable_network_monitor = network_monitor_input in ['yes', 'y', '是']
            
            # 获取生日信息
            default_info = get_default_user_info()
            birth_date = input(get_prompt_message('birth_date_prompt')).strip()
            if not birth_date:
                birth_date = default_info['birth_date']
                print(f"使用默认生日: {birth_date}")
            elif not validate_user_input('birth_date', birth_date):
                print("⚠️ 生日格式不正确，使用默认值")
                birth_date = default_info['birth_date']
            
            # 获取手机号
            phone_number = input(get_prompt_message('phone_prompt')).strip()
            if not phone_number:
                phone_number = default_info['phone_number']
                print(f"使用默认手机号: {phone_number}")
            
            # 保存用户信息
            self.user_info = {
                'target_url': target_url,
                'auto_fill_mode': auto_fill_mode,
                'enable_network_monitor': enable_network_monitor,
                'birth_date': birth_date,
                'phone_number': phone_number,
                'name': default_info['name'],
                'email': default_info['email']
            }
            
            print("\n⏰ 目标时间将通过AI分析自动获取")
            return True
            
        except Exception as e:
            print(f"❌ 用户输入收集失败: {e}")
            return False
    
    def initialize_browser(self) -> bool:
        """初始化浏览器"""
        try:
            self.driver = setup_driver()
            self.wait = create_wait(self.driver, self.browser_config['page_load_wait'])
            return True
        except Exception as e:
            print(f"❌ 浏览器初始化失败: {e}")
            return False
    
    def initialize_network_monitor(self) -> bool:
        """初始化网络监控（如果启用）"""
        if not self.user_info.get('enable_network_monitor', False):
            return True
        
        try:
            from ..network.enhanced_monitor import EnhancedNetworkMonitor
            self.network_monitor = EnhancedNetworkMonitor(self.driver)
            self.network_monitor.start_monitoring()
            print(get_status_message('network_monitor_start'))
            return True
        except Exception as e:
            print(f"❌ 网络监控初始化失败: {e}")
            return False
    
    def navigate_and_login(self) -> bool:
        """导航到页面并处理登录"""
        try:
            # 访问目标页面
            target_url = self.user_info['target_url']
            print(get_status_message('page_loading', target_url))
            self.driver.get(target_url)
            
            # 等待页面加载
            self._wait_for_page_load()
            
            # 处理登录流程
            return self._handle_login_flow()
            
        except Exception as e:
            print(f"❌ 页面导航或登录失败: {e}")
            return False
    
    def _wait_for_page_load(self) -> None:
        """等待页面加载完成"""
        try:
            self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            print(get_status_message('page_loaded'))
        except TimeoutException:
            print(get_status_message('page_load_timeout'))
        
        try:
            self.wait.until(lambda d: d.execute_script("return document.readyState") == "complete")
            print("✅ 页面完全加载完成")
        except TimeoutException:
            print("⚠️ 页面完全加载超时，继续执行")
    
    def _handle_login_flow(self) -> bool:
        """处理登录流程（简化版本）"""
        try:
            print(get_status_message('login_start'))
            
            # 简化的登录流程 - 移除不必要的延迟
            if click_login_button_only(self.driver, self.wait):
                print(get_status_message('login_success'))
                click_confirm_login_button(self.driver, self.wait)
            
            # 直接等待手动登录，无额外延迟
            wait_for_manual_login()
            return True
            
        except Exception as e:
            print(f"❌ 登录流程失败: {e}")
            return False
    
    def analyze_content(self) -> Tuple[Optional[str], Optional[Dict], Optional[str]]:
        """分析页面内容"""
        try:
            # 提取文章内容
            print(get_status_message('content_extracting'))
            article_content = extract_article_content(self.driver, self.wait)
            
            if not article_content:
                print("❌ 未能提取到文章内容")
                return None, None, None
            
            print(get_status_message('content_extracted', len(article_content)))
            
            # 使用AI提取时间信息
            print(get_status_message('ai_time_analyzing'))
            ai_time_data = extract_time_with_ai(article_content)
            
            # 备用方案：传统时间提取
            time_info = None
            if not ai_time_data:
                print("⚠️ AI时间提取失败，使用传统正则表达式方法...")
                time_info = extract_time_info(article_content)
            
            # AI分析
            print(get_status_message('ai_analyzing'))
            analysis_result = analyze_with_ai(article_content, time_info)
            
            if analysis_result:
                print("\n📊 AI分析结果:")
                print(analysis_result)
                save_analysis(article_content, analysis_result, time_info, {})
                print("\n💾 分析结果已保存")
            
            return article_content, ai_time_data or time_info, analysis_result
            
        except Exception as e:
            print(f"❌ 内容分析失败: {e}")
            return None, None, None
    
    def extract_target_time(self, ai_time_data: Dict) -> Optional[datetime]:
        """从AI时间数据中提取目标时间"""
        if not ai_time_data:
            return None
        
        try:
            print(f"📅 AI提取的时间信息: {json.dumps(ai_time_data, ensure_ascii=False, indent=2)}")
            
            # 获取关键时间点
            key_times = []
            
            # 优先使用申请开始时间
            if ai_time_data.get('申请开始时间'):
                key_times.append({
                    'time': ai_time_data['申请开始时间'],
                    'description': '申请开始时间',
                    'priority': 1
                })
            
            # 添加申请结束时间
            if ai_time_data.get('申请结束时间'):
                key_times.append({
                    'time': ai_time_data['申请结束时间'],
                    'description': '申请结束时间',
                    'priority': 2
                })
            
            # 添加其他重要时间点
            if ai_time_data.get('关键时间点'):
                for point in ai_time_data['关键时间点']:
                    if point.get('时间') and point.get('重要性') == '高':
                        key_times.append({
                            'time': point['时间'],
                            'description': point.get('描述', '重要时间点'),
                            'priority': 3
                        })
            
            # 按优先级排序并解析时间
            key_times.sort(key=lambda x: x['priority'])
            
            for time_item in key_times:
                try:
                    time_str = time_item['time']
                    if time_str and time_str != 'null':
                        parsed_time = datetime.strptime(time_str, "%Y-%m-%d %H:%M")
                        korea_time = self.korea_tz.localize(parsed_time)
                        china_time = korea_time.astimezone(self.china_tz)
                        
                        print(f"🇨🇳 {time_item['description']}: {china_time}")
                        print(get_status_message('time_set', china_time, time_item['description']))
                        
                        return china_time
                        
                except Exception as e:
                    print(f"⚠️ 时间解析失败 {time_item['time']}: {e}")
                    continue
            
            return None
            
        except Exception as e:
            print(f"❌ 目标时间提取失败: {e}")
            return None
    
    def handle_time_setup(self, target_time: Optional[datetime]) -> Optional[datetime]:
        """处理时间设置"""
        # 如果没有自动检测到目标时间，询问用户
        if not target_time:
            print("\n⚠️ 未自动检测到目标时间")
            manual_input = input(get_prompt_message('manual_time_prompt')).strip().lower()
            
            if manual_input in ['y', 'yes', '是']:
                target_time = get_time_input()
                if target_time:
                    print(f"✅ 手动设置目标时间: {target_time}")
        
        # 检查时间是否过期
        if target_time:
            current_time = datetime.now(self.china_tz)
            
            if target_time <= current_time:
                print(f"\n⚠️ 目标时间已过期!")
                print(f"   目标时间: {target_time}")
                print(f"   当前时间: {current_time}")
                
                test_choice = input(get_prompt_message('test_time_prompt')).strip().lower()
                if test_choice in ['y', 'yes', '是']:
                    target_time = current_time + timedelta(seconds=self.time_config['test_time_offset'])
                    print(f"✅ 已设置测试时间: {target_time}")
                else:
                    print("❌ 取消自动报名")
                    target_time = None
        
        return target_time
    
    def execute_countdown_and_application(self, target_time: datetime) -> bool:
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
            if self.user_info.get('auto_fill_mode', True):
                print("🤖 执行自动填写模式...")
                results = self._execute_auto_fill_mode(advance_time)
            else:
                print("👁️ 执行监控模式...")
                results = self._execute_monitoring_mode(advance_time)
            
            # 处理结果
            self._handle_application_results(results)
            return True
            
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
        """执行监控模式 - 只点击申请按钮，然后持续监控"""
        print(f"⚡ 使用动态计算的提前时间: {advance_time:.3f}秒")
        print("🔘 点击申请按钮后，请您手动填写表单...")
        
        application_start = time.time()
        
        try:
            # 1. 点击申请按钮
            core_selector = self.button_config.get('core_application')
            fallback_text = self.button_config['fallback_texts'][0]
            
            click_result = self._click_core_button_instantly(core_selector, fallback_text)
            if not click_result.get('success'):
                return {'success': False, 'error': '申请按钮点击失败'}
            
            print("✅ 申请按钮点击成功!")
            print("📱 表单页面已打开，请您手动填写...")
            
            # 2. 开始持续监控
            monitoring_result = self._start_continuous_monitoring()
            
            total_time = (time.time() - application_start) * 1000
            
            return {
                'success': True,
                'mode': 'monitoring',
                'total_time_ms': total_time,
                'click_result': click_result,
                'monitoring_result': monitoring_result,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"❌ 监控模式执行失败: {e}")
            return {'success': False, 'error': str(e)}
    
    def _start_continuous_monitoring(self) -> Dict[str, Any]:
        """开始持续监控 - 捕获页面元素和网络请求"""
        print("\n👁️ 开始持续监控...")
        print("📄 正在捕获表单页面元素...")
        
        try:
            # 等待页面加载
            time.sleep(1)
            
            # 1. 捕获表单页面内容
            page_data = crawl_page_content(self.driver)
            print("✅ 表单页面元素捕获完成")
            
            # 2. 启动网络监控
            if self.network_monitor:
                print("🌐 网络监控已启动...")
            else:
                # 如果没有网络监控，创建一个简单的监控
                from ..network.enhanced_monitor import EnhancedNetworkMonitor
                self.network_monitor = EnhancedNetworkMonitor(self.driver)
                self.network_monitor.start_monitoring()
                print("🌐 启动网络监控...")
            
            # 3. 等待用户手动操作并持续监控
            print("\n" + "="*60)
            print("🖱️  请您现在手动填写表单并提交")
            print("📡 程序将持续监控所有网络请求")
            print("⌨️  完成后请在终端按 Enter 键结束监控")
            print("="*60)
            
            # 等待用户按回车键结束
            input("👆 按 Enter 键结束监控...")
            
            # 4. 获取监控结果
            network_data = []
            if self.network_monitor:
                network_data = self.network_monitor.get_captured_requests()
                print(f"📡 捕获到 {len(network_data)} 个网络请求")
            
            # 5. 再次捕获页面状态（可能已跳转）
            final_page_data = crawl_page_content(self.driver)
            print("✅ 最终页面状态捕获完成")
            
            # 6. 保存完整监控数据
            monitoring_data = {
                'initial_page_data': page_data,
                'final_page_data': final_page_data,
                'network_requests': network_data,
                'monitoring_duration': time.time(),
                'elements_discovered': self._analyze_discovered_elements(page_data)
            }
            
            self._save_monitoring_data(monitoring_data)
            
            print("✅ 监控完成！数据已保存")
            return monitoring_data
            
        except Exception as e:
            print(f"❌ 持续监控失败: {e}")
            return {'error': str(e)}
    
    def _analyze_discovered_elements(self, page_data: Dict) -> Dict[str, Any]:
        """分析发现的元素，为下次自动填写做准备"""
        try:
            form_elements = page_data.get('form_elements', {})
            
            analysis = {
                'input_fields': [],
                'checkboxes': [],
                'buttons': [],
                'recommendations': []
            }
            
            # 分析输入框
            for inp in form_elements.get('input_fields', []):
                field_analysis = {
                    'selector': f"input[name='{inp.get('name')}']" if inp.get('name') else f"input[id='{inp.get('id')}']",
                    'type': inp.get('type'),
                    'placeholder': inp.get('placeholder'),
                    'likely_purpose': self._guess_field_purpose(inp)
                }
                analysis['input_fields'].append(field_analysis)
            
            # 分析复选框
            for cb in form_elements.get('checkboxes', []):
                checkbox_analysis = {
                    'selector': f"input[name='{cb.get('name')}']" if cb.get('name') else f"input[id='{cb.get('id')}']",
                    'text': cb.get('text', ''),
                    'likely_purpose': '同意条款' if '동의' in cb.get('text', '') else '选择项'
                }
                analysis['checkboxes'].append(checkbox_analysis)
            
            # 分析按钮
            for btn in form_elements.get('buttons', []):
                button_analysis = {
                    'selector': f"button[type='{btn.get('type')}']" if btn.get('type') else 'button',
                    'text': btn.get('text', ''),
                    'likely_purpose': '提交按钮' if any(keyword in btn.get('text', '') for keyword in ['제출', '신청', '확인']) else '其他按钮'
                }
                analysis['buttons'].append(button_analysis)
            
            # 生成建议
            analysis['recommendations'] = [
                f"发现 {len(analysis['input_fields'])} 个输入框",
                f"发现 {len(analysis['checkboxes'])} 个复选框", 
                f"发现 {len(analysis['buttons'])} 个按钮",
                "这些信息可用于下次自动填写"
            ]
            
            return analysis
            
        except Exception as e:
            print(f"⚠️ 元素分析失败: {e}")
            return {}
    
    def _guess_field_purpose(self, field: Dict) -> str:
        """猜测字段用途"""
        placeholder = field.get('placeholder', '').lower()
        name = field.get('name', '').lower()
        
        if '생년월일' in placeholder or 'birth' in name:
            return '生日字段'
        elif '전화' in placeholder or '연락처' in placeholder or 'phone' in name:
            return '手机号字段'  
        elif '이름' in placeholder or 'name' in name:
            return '姓名字段'
        elif 'email' in placeholder or 'email' in name:
            return '邮箱字段'
        else:
            return '未知字段'
    
    def _save_monitoring_data(self, monitoring_data: Dict[str, Any]) -> None:
        """保存监控数据"""
        try:
            import os
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            # 确保data目录存在
            data_dir = "data"
            os.makedirs(data_dir, exist_ok=True)
            
            filename = os.path.join(data_dir, f"monitoring_data_{timestamp}.json")
            
            # 添加元数据
            save_data = {
                'metadata': {
                    'timestamp': timestamp,
                    'mode': 'monitoring',
                    'target_url': self.user_info['target_url'],
                    'user_info': {
                        'birth_date': self.user_info['birth_date'],
                        'phone_number': self.user_info['phone_number']
                    }
                },
                'monitoring_data': monitoring_data
            }
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, ensure_ascii=False, indent=2)
            
            print(f"📁 监控数据已保存到: {filename}")
            
        except Exception as e:
            print(f"❌ 保存监控数据失败: {e}")

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
            
            # 步骤2: 智能表单处理（包含完整的网络监控和页面爬取）
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
            
            # 保存单一数据文件（解决重复保存问题）
            self._save_unified_application_data(results)
            
            return results
            
        except Exception as e:
            print(f"❌ 智能申请流程失败: {e}")
            return {'success': False, 'error': str(e)}
    
    def _click_core_button_instantly(self, core_selector: str, fallback_text: str) -> Dict[str, Any]:
        """立即点击核心按钮（无延迟）"""
        try:
            click_start = time.perf_counter()
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support import expected_conditions as EC
            
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
    
    def _intelligent_form_handling(self) -> Dict[str, Any]:
        """智能表单处理（包含页面爬取和网络监控）"""
        try:
            # 准备填写数据
            fill_data = {
                'name': self.user_info.get('name', 'Test User'),
                'phone': self.user_info['phone_number'],
                'email': self.user_info.get('email', 'test@example.com'),
                'birthday': self.user_info['birth_date'],
                'default': 'Test Input'
            }
            
            # 使用闪电表单处理器
            from ..forms.lightning_form_processor import capture_and_process_complete_flow
            result = capture_and_process_complete_flow(
                driver=self.driver,
                network_monitor=self.network_monitor,
                birth_date=fill_data['birthday']
            )
            
            return result
            
        except Exception as e:
            print(f"❌ 智能表单处理失败: {e}")
            return {
                'success': False,
                'error': str(e),
                'total_time_ms': 0
            }
    
    def _save_unified_application_data(self, results: Dict[str, Any]) -> None:
        """保存统一的申请数据（解决重复保存问题）"""
        try:
            # 创建统一的数据结构
            unified_data = {
                'application_metadata': {
                    'target_url': self.user_info['target_url'],
                    'timestamp': datetime.now().isoformat(),
                    'user_info': {
                        'birth_date': self.user_info['birth_date'],
                        'phone_number': self.user_info['phone_number'],
                        'name': self.user_info.get('name', 'Test User'),
                        'email': self.user_info.get('email', 'test@example.com')
                    }
                },
                'performance_metrics': results.get('performance', {}),
                'click_results': results.get('click_result', {}),
                'intelligent_form_results': results.get('intelligent_form_result', {}),
                'page_crawling': {
                    'initial_page': results.get('intelligent_form_result', {}).get('initial_page_data', {}),
                    'final_page': results.get('intelligent_form_result', {}).get('final_page_data', {})
                },
                'network_monitoring': results.get('intelligent_form_result', {}).get('network_monitoring', {}),
                'form_discovery': results.get('intelligent_form_result', {}).get('form_discovery_results', {}),
                'submit_results': results.get('intelligent_form_result', {}).get('submit_results', {})
            }
            
            # 保存到单一文件
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"unified_weverse_application_{timestamp}.json"
            
            import os
            
            # 确保data目录存在
            data_dir = "data"
            if not os.path.exists(data_dir):
                os.makedirs(data_dir)
            
            # 保存数据
            filepath = os.path.join(data_dir, filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(unified_data, f, ensure_ascii=False, indent=2)
            
            print(f"💾 统一数据已保存: {filepath}")
            
            # 打印数据摘要
            self._print_data_summary(unified_data)
            
        except Exception as e:
            print(f"❌ 数据保存失败: {e}")
    
    def _print_data_summary(self, data: Dict[str, Any]) -> None:
        """打印数据摘要"""
        try:
            print("\n📊 申请数据摘要:")
            
            # 性能指标
            performance = data.get('performance_metrics', {})
            if performance:
                print(f"   ⏱️ 总耗时: {performance.get('total_application_time', 0):.1f}ms")
                print(f"   📝 表单处理: {performance.get('actual_form_fill_time', 0):.1f}ms")
            
            # 页面爬取结果
            page_data = data.get('page_crawling', {})
            initial_elements = page_data.get('initial_page', {}).get('page_elements', {})
            final_elements = page_data.get('final_page', {}).get('page_elements', {})
            
            if initial_elements:
                total_initial = sum(len(v) if isinstance(v, list) else 0 for v in initial_elements.values())
                print(f"   🔍 初始页面元素: {total_initial}个")
            
            if final_elements:
                total_final = sum(len(v) if isinstance(v, list) else 0 for v in final_elements.values())
                print(f"   🔍 最终页面元素: {total_final}个")
            
            # 网络监控结果
            network = data.get('network_monitoring', {})
            if network:
                total_requests = network.get('total_requests', 0)
                analysis = network.get('analysis', {})
                print(f"   📡 网络请求: 总计{total_requests}个")
                print(f"       GET: {analysis.get('get_count', 0)}个, POST: {analysis.get('post_count', 0)}个")
                print(f"       重要请求: {len(analysis.get('important_requests', []))}个")
            
            # 表单处理结果
            form_results = data.get('form_discovery', {})
            if form_results:
                print(f"   📝 表单填写: 输入框{form_results.get('inputs_filled', 0)}个, "
                      f"复选框{form_results.get('checkboxes_checked', 0)}个")
            
            # 提交结果
            submit = data.get('submit_results', {})
            if submit:
                status = '成功' if submit.get('success') else '失败'
                method = submit.get('method', '未知')
                print(f"   🎯 表单提交: {status} (方法: {method})")
            
            print("✅ 完整的申请流程数据已保存\n")
            
        except Exception as e:
            print(f"⚠️ 数据摘要打印失败: {e}")
    
    def _handle_application_results(self, results: Dict[str, Any]) -> None:
        """处理申请结果"""
        if results and results.get('success'):
            print(get_status_message('application_success'))
        else:
            print(get_status_message('application_failed'))
    
    def cleanup_and_finish(self) -> None:
        """清理和结束程序"""
        try:
            if self.network_monitor:
                print("🔧 停止网络监控...")
                self.network_monitor.stop_monitoring()
            
            if self.driver:
                print("🔧 关闭浏览器...")
                self.driver.quit()
            
            print("✅ 清理完成")
            
        except Exception as e:
            print(f"⚠️ 清理过程异常: {e}")


def unified_mode():
    """统一模式主函数"""
    handler = ModeHandler()
    
    try:
        # 步骤1: 收集用户输入
        if not handler.collect_user_input():
            return
        
        # 步骤2: 初始化浏览器
        if not handler.initialize_browser():
            return
        
        # 步骤3: 初始化网络监控
        if not handler.initialize_network_monitor():
            return
        
        # 步骤4: 导航和登录
        if not handler.navigate_and_login():
            return
        
        # 步骤5: 分析内容
        article_content, ai_time_data, analysis_result = handler.analyze_content()
        if not article_content:
            print("❌ 内容分析失败，无法继续")
            return
        
        # 步骤6: 提取目标时间
        target_time = handler.extract_target_time(ai_time_data)
        
        # 步骤7: 处理时间设置
        target_time = handler.handle_time_setup(target_time)
        if not target_time:
            print("❌ 未设置目标时间，程序结束")
            return
        
        # 步骤8: 执行倒计时和申请
        success = handler.execute_countdown_and_application(target_time)
        
        if success:
            print("🎉 程序执行成功！")
        else:
            print("❌ 程序执行失败")
    
    except Exception as e:
        print(f"❌ 程序执行异常: {e}")
    
    finally:
        # 步骤9: 清理和结束
        handler.cleanup_and_finish()


if __name__ == "__main__":
    unified_mode() 