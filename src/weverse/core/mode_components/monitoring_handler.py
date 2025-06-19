#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
monitoring_handler.py
监控处理组件 - 收集完整数据链路
从点击申请到用户提交表单的全过程数据收集
"""

import time
import json
import threading
from datetime import datetime
from typing import Dict, Any, List

from ...analysis.page_crawler import crawl_page_content


class MonitoringHandler:
    """监控处理器 - 专注于完整数据链路收集"""
    
    def __init__(self, driver: Any, network_monitor: Any = None):
        self.driver = driver
        self.network_monitor = network_monitor
        self.monitoring_start_time = None
        self.collected_data = {
            'pre_click_data': {},
            'post_click_data': {},
            'form_page_data': {},
            'network_requests': [],
            'user_actions': [],
            'final_data': {}
        }
    
    def start_comprehensive_monitoring(self) -> Dict[str, Any]:
        """启动综合监控 - 收集从点击申请到用户提交的完整数据链路"""
        print("\n👁️ 启动综合数据监控模式")
        print("=" * 60)
        print("📊 收集目标：点击申请 → 跳转页面 → 表单元素 → 网络请求 → 用户操作")
        
        self.monitoring_start_time = time.time()
        
        try:
            # 阶段1: 收集点击前的页面状态
            self._collect_pre_click_data()
            
            # 阶段2: 监控申请点击后的跳转
            self._monitor_post_click_transition()
            
            # 阶段3: 深度分析表单页面
            self._analyze_form_page_structure()
            
            # 阶段4: 持续监控用户操作和网络请求
            self._continuous_monitoring_loop()
            
            # 阶段5: 收集最终数据
            self._collect_final_data()
            
            print("\n✅ 综合监控完成！")
            return self._generate_monitoring_report()
            
        except Exception as e:
            print(f"❌ 综合监控失败: {e}")
            import traceback
            traceback.print_exc()
            return {'error': str(e), 'partial_data': self.collected_data}
    
    def _collect_pre_click_data(self) -> None:
        """收集点击申请按钮前的页面数据"""
        print("\n📋 阶段1: 收集点击前页面状态")
        
        try:
            self.collected_data['pre_click_data'] = {
                'timestamp': datetime.now().isoformat(),
                'url': self.driver.current_url,
                'title': self.driver.title,
                'page_content': crawl_page_content(self.driver),
                'cookies': self.driver.get_cookies(),
                'local_storage': self._get_local_storage(),
                'session_storage': self._get_session_storage()
            }
            print("✅ 点击前数据收集完成")
        except Exception as e:
            print(f"⚠️ 点击前数据收集失败: {e}")
    
    def _monitor_post_click_transition(self) -> None:
        """监控点击申请后的页面跳转过程"""
        print("\n🔄 阶段2: 监控申请点击后的页面跳转")
        
        try:
            # 记录点击前URL
            pre_click_url = self.driver.current_url
            
            # 等待页面可能的跳转/变化
            time.sleep(2)
            
            # 记录点击后状态
            post_click_url = self.driver.current_url
            
            self.collected_data['post_click_data'] = {
                'timestamp': datetime.now().isoformat(),
                'pre_click_url': pre_click_url,
                'post_click_url': post_click_url,
                'url_changed': pre_click_url != post_click_url,
                'title': self.driver.title,
                'transition_time': time.time() - self.monitoring_start_time
            }
            
            if pre_click_url != post_click_url:
                print(f"✅ 检测到页面跳转: {pre_click_url} → {post_click_url}")
            else:
                print("📝 页面未跳转，可能是动态表单加载")
                
        except Exception as e:
            print(f"⚠️ 页面跳转监控失败: {e}")
    
    def _analyze_form_page_structure(self) -> None:
        """深度分析表单页面结构"""
        print("\n🔍 阶段3: 深度分析表单页面结构")
        
        try:
            # 等待表单元素完全加载
            time.sleep(1)
            
            # 爬取完整页面内容
            page_content = crawl_page_content(self.driver)
            
            # 深度分析表单结构
            form_analysis = self._deep_form_analysis()
            
            self.collected_data['form_page_data'] = {
                'timestamp': datetime.now().isoformat(),
                'url': self.driver.current_url,
                'title': self.driver.title,
                'page_content': page_content,
                'form_analysis': form_analysis,
                'page_source_length': len(self.driver.page_source),
                'dom_elements_count': self._count_dom_elements()
            }
            
            # 打印表单分析结果
            self._print_form_analysis(form_analysis)
            
        except Exception as e:
            print(f"⚠️ 表单页面分析失败: {e}")
    
    def _deep_form_analysis(self) -> Dict[str, Any]:
        """深度表单分析 - 收集所有可能的表单元素"""
        try:
            analysis = {
                'input_fields': [],
                'select_fields': [],
                'checkboxes': [],
                'radio_buttons': [],
                'buttons': [],
                'form_containers': [],
                'validation_messages': [],
                'hidden_fields': []
            }
            
            # 分析所有输入框
            inputs = self.driver.find_elements("xpath", "//input")
            for inp in inputs:
                try:
                    field_data = {
                        'tag': inp.tag_name,
                        'type': inp.get_attribute('type'),
                        'name': inp.get_attribute('name'),
                        'id': inp.get_attribute('id'),
                        'class': inp.get_attribute('class'),
                        'placeholder': inp.get_attribute('placeholder'),
                        'required': inp.get_attribute('required') is not None,
                        'value': inp.get_attribute('value'),
                        'maxlength': inp.get_attribute('maxlength'),
                        'pattern': inp.get_attribute('pattern'),
                        'xpath': self._get_element_xpath(inp),
                        'css_selector': self._get_css_selector(inp),
                        'is_visible': inp.is_displayed(),
                        'is_enabled': inp.is_enabled()
                    }
                    
                    # 分类不同类型的输入框
                    input_type = field_data.get('type', 'text').lower()
                    if input_type == 'checkbox':
                        analysis['checkboxes'].append(field_data)
                    elif input_type == 'radio':
                        analysis['radio_buttons'].append(field_data)
                    elif input_type == 'hidden':
                        analysis['hidden_fields'].append(field_data)
                    else:
                        analysis['input_fields'].append(field_data)
                        
                except Exception as field_error:
                    print(f"⚠️ 分析输入框失败: {field_error}")
                    continue
            
            # 分析下拉框
            selects = self.driver.find_elements("xpath", "//select")
            for select in selects:
                try:
                    options = select.find_elements("xpath", ".//option")
                    field_data = {
                        'tag': select.tag_name,
                        'name': select.get_attribute('name'),
                        'id': select.get_attribute('id'),
                        'class': select.get_attribute('class'),
                        'options': [{'value': opt.get_attribute('value'), 'text': opt.text} for opt in options],
                        'selected_value': select.get_attribute('value'),
                        'xpath': self._get_element_xpath(select),
                        'css_selector': self._get_css_selector(select)
                    }
                    analysis['select_fields'].append(field_data)
                except Exception as field_error:
                    print(f"⚠️ 分析下拉框失败: {field_error}")
                    continue
            
            # 分析按钮
            buttons = self.driver.find_elements("xpath", "//button | //input[@type='submit'] | //input[@type='button']")
            for btn in buttons:
                try:
                    field_data = {
                        'tag': btn.tag_name,
                        'type': btn.get_attribute('type'),
                        'text': btn.text,
                        'value': btn.get_attribute('value'),
                        'class': btn.get_attribute('class'),
                        'onclick': btn.get_attribute('onclick'),
                        'xpath': self._get_element_xpath(btn),
                        'css_selector': self._get_css_selector(btn),
                        'is_visible': btn.is_displayed(),
                        'is_enabled': btn.is_enabled()
                    }
                    analysis['buttons'].append(field_data)
                except Exception as field_error:
                    print(f"⚠️ 分析按钮失败: {field_error}")
                    continue
            
            # 分析表单容器
            forms = self.driver.find_elements("xpath", "//form")
            for form in forms:
                try:
                    form_data = {
                        'tag': form.tag_name,
                        'action': form.get_attribute('action'),
                        'method': form.get_attribute('method'),
                        'id': form.get_attribute('id'),
                        'class': form.get_attribute('class'),
                        'xpath': self._get_element_xpath(form)
                    }
                    analysis['form_containers'].append(form_data)
                except Exception as field_error:
                    print(f"⚠️ 分析表单容器失败: {field_error}")
                    continue
            
            return analysis
            
        except Exception as e:
            print(f"⚠️ 深度表单分析失败: {e}")
            return {}
    
    def _continuous_monitoring_loop(self) -> None:
        """持续监控循环 - 监控用户操作和网络请求"""
        print("\n🔄 阶段4: 持续监控用户操作")
        print("=" * 60)
        print("🖱️  请您现在手动填写表单")
        print("📡 程序将实时监控所有网络请求和页面变化")
        print("⌨️  完成所有操作后，请在终端按 Enter 键结束监控")
        print("=" * 60)
        
        # 启动网络监控
        self._ensure_network_monitoring()
        
        # 记录初始状态
        last_url = self.driver.current_url
        request_count = 0
        
        # 创建停止监控的事件
        stop_monitoring = threading.Event()
        
        def input_listener():
            """监听用户输入"""
            input()  # 等待用户按回车
            stop_monitoring.set()
        
        # 启动输入监听线程
        input_thread = threading.Thread(target=input_listener)
        input_thread.daemon = True
        input_thread.start()
        
        print("🔍 开始实时监控...")
        
        # 监控循环
        while not stop_monitoring.is_set():
            try:
                # 检查页面变化
                current_url = self.driver.current_url
                if current_url != last_url:
                    print(f"📍 页面跳转: {last_url} → {current_url}")
                    self._record_page_change(last_url, current_url)
                    last_url = current_url
                
                # 检查网络请求变化
                if self.network_monitor:
                    current_requests = self.network_monitor.get_captured_requests()
                    if len(current_requests) > request_count:
                        new_requests = current_requests[request_count:]
                        for req in new_requests:
                            method = req.get('method', 'GET')
                            url = req.get('url', '')
                            status = req.get('status', 'Unknown')
                            print(f"🌐 新请求: {method} {url[:50]}... (状态: {status})")
                        request_count = len(current_requests)
                
                # 检查页面标题变化
                current_title = self.driver.title
                last_recorded_title = self.collected_data.get('post_click_data', {}).get('title', '')
                if current_title != last_recorded_title:
                    self._record_title_change(current_title)
                
                # 短暂休息避免CPU过载
                time.sleep(0.5)
                
            except Exception as e:
                print(f"⚠️ 监控循环错误: {e}")
                break
        
        print("\n✅ 用户已结束监控")
    
    def _collect_final_data(self) -> None:
        """收集最终数据"""
        print("\n📊 阶段5: 收集最终数据")
        
        try:
            # 收集最终网络请求
            if self.network_monitor:
                self.collected_data['network_requests'] = self.network_monitor.get_captured_requests()
            
            # 收集最终页面状态
            self.collected_data['final_data'] = {
                'timestamp': datetime.now().isoformat(),
                'url': self.driver.current_url,
                'title': self.driver.title,
                'final_page_content': crawl_page_content(self.driver),
                'cookies': self.driver.get_cookies(),
                'local_storage': self._get_local_storage(),
                'session_storage': self._get_session_storage(),
                'monitoring_duration': time.time() - self.monitoring_start_time
            }
            
            print(f"✅ 最终数据收集完成，总监控时长: {time.time() - self.monitoring_start_time:.1f}秒")
            
        except Exception as e:
            print(f"⚠️ 最终数据收集失败: {e}")
    
    def _generate_monitoring_report(self) -> Dict[str, Any]:
        """生成监控报告"""
        try:
            report = {
                'metadata': {
                    'monitoring_start': datetime.fromtimestamp(self.monitoring_start_time).isoformat(),
                    'monitoring_end': datetime.now().isoformat(),
                    'total_duration': time.time() - self.monitoring_start_time,
                    'mode': 'comprehensive_monitoring'
                },
                'data_collection': self.collected_data,
                'summary': {
                    'network_requests_count': len(self.collected_data.get('network_requests', [])),
                    'form_fields_discovered': len(self.collected_data.get('form_page_data', {}).get('form_analysis', {}).get('input_fields', [])),
                    'buttons_discovered': len(self.collected_data.get('form_page_data', {}).get('form_analysis', {}).get('buttons', [])),
                    'checkboxes_discovered': len(self.collected_data.get('form_page_data', {}).get('form_analysis', {}).get('checkboxes', [])),
                    'page_transitions': len([x for x in self.collected_data.get('user_actions', []) if x.get('type') == 'page_change']),
                    'data_quality': 'complete' if all(self.collected_data.values()) else 'partial'
                },
                'recommendations': self._generate_recommendations()
            }
            
            return report
            
        except Exception as e:
            print(f"⚠️ 报告生成失败: {e}")
            return {'error': str(e)}
    
    def _generate_recommendations(self) -> List[str]:
        """生成自动化建议"""
        try:
            recommendations = []
            
            form_analysis = self.collected_data.get('form_page_data', {}).get('form_analysis', {})
            input_fields = form_analysis.get('input_fields', [])
            buttons = form_analysis.get('buttons', [])
            network_requests = self.collected_data.get('network_requests', [])
            
            # 基于发现的元素生成建议
            if input_fields:
                recommendations.append(f"发现{len(input_fields)}个输入框，可用于自动填写")
                
                # 识别关键字段
                for field in input_fields:
                    name = field.get('name', '').lower()
                    placeholder = field.get('placeholder', '').lower()
                    if any(keyword in name or keyword in placeholder for keyword in ['birth', '생년월일', 'date']):
                        recommendations.append("检测到生日字段，建议使用用户提供的生日数据")
                    elif any(keyword in name or keyword in placeholder for keyword in ['phone', '전화', '연락처']):
                        recommendations.append("检测到电话字段，建议使用用户提供的电话数据")
            
            if buttons:
                submit_buttons = [btn for btn in buttons if any(keyword in btn.get('text', '').lower() for keyword in ['제출', '신청', '확인', 'submit'])]
                if submit_buttons:
                    recommendations.append(f"发现{len(submit_buttons)}个提交按钮，可用于自动提交")
            
            if network_requests:
                api_requests = [req for req in network_requests if req.get('method') in ['POST', 'PUT']]
                if api_requests:
                    recommendations.append(f"捕获到{len(api_requests)}个API提交请求，可用于验证提交成功")
            
            if not recommendations:
                recommendations.append("建议使用闪电表单处理器进行高速自动化")
            
            return recommendations
            
        except Exception as e:
            print(f"⚠️ 生成建议失败: {e}")
            return ["数据收集完成，建议人工分析"]
    
    # 辅助方法
    def _ensure_network_monitoring(self) -> None:
        """确保网络监控已启动"""
        if not self.network_monitor:
            try:
                from ...network.enhanced_monitor import EnhancedNetworkMonitor
                self.network_monitor = EnhancedNetworkMonitor(self.driver)
                self.network_monitor.start_monitoring()
                print("🌐 网络监控已启动")
            except Exception as e:
                print(f"⚠️ 网络监控启动失败: {e}")
        else:
            print("🌐 网络监控已就绪")
    
    def _get_local_storage(self) -> Dict:
        """获取本地存储"""
        try:
            return self.driver.execute_script("return window.localStorage;")
        except:
            return {}
    
    def _get_session_storage(self) -> Dict:
        """获取会话存储"""
        try:
            return self.driver.execute_script("return window.sessionStorage;")
        except:
            return {}
    
    def _count_dom_elements(self) -> int:
        """统计DOM元素数量"""
        try:
            return self.driver.execute_script("return document.getElementsByTagName('*').length;")
        except:
            return 0
    
    def _get_element_xpath(self, element) -> str:
        """获取元素的XPath"""
        try:
            return self.driver.execute_script("""
                function getElementXPath(element) {
                    if (element && element.id) {
                        return '//*[@id="' + element.id + '"]';
                    }
                    let path = '';
                    while (element) {
                        let tagName = element.tagName.toLowerCase();
                        let sibling = element;
                        let nth = 1;
                        while (sibling = sibling.previousElementSibling) {
                            if (sibling.tagName.toLowerCase() === tagName) nth++;
                        }
                        path = `/${tagName}[${nth}]${path}`;
                        element = element.parentElement;
                    }
                    return path;
                }
                return getElementXPath(arguments[0]);
            """, element)
        except:
            return ""
    
    def _get_css_selector(self, element) -> str:
        """获取元素的CSS选择器"""
        try:
            if element.get_attribute('id'):
                return f"#{element.get_attribute('id')}"
            elif element.get_attribute('name'):
                return f"[name='{element.get_attribute('name')}']"
            elif element.get_attribute('class'):
                classes = element.get_attribute('class').split()
                return f".{'.'.join(classes)}"
            else:
                return element.tag_name.lower()
        except:
            return ""
    
    def _record_page_change(self, from_url: str, to_url: str) -> None:
        """记录页面变化"""
        self.collected_data['user_actions'].append({
            'type': 'page_change',
            'timestamp': datetime.now().isoformat(),
            'from_url': from_url,
            'to_url': to_url
        })
    
    def _record_title_change(self, new_title: str) -> None:
        """记录标题变化"""
        self.collected_data['user_actions'].append({
            'type': 'title_change',
            'timestamp': datetime.now().isoformat(),
            'new_title': new_title
        })
    
    def _print_form_analysis(self, form_analysis: Dict) -> None:
        """打印表单分析结果"""
        try:
            print("📋 表单结构分析结果:")
            print(f"   📝 输入框: {len(form_analysis.get('input_fields', []))}个")
            print(f"   📋 下拉框: {len(form_analysis.get('select_fields', []))}个")
            print(f"   ☑️ 复选框: {len(form_analysis.get('checkboxes', []))}个")
            print(f"   🔘 单选框: {len(form_analysis.get('radio_buttons', []))}个")
            print(f"   🔲 按钮: {len(form_analysis.get('buttons', []))}个")
            print(f"   📦 表单容器: {len(form_analysis.get('form_containers', []))}个")
            print(f"   🔒 隐藏字段: {len(form_analysis.get('hidden_fields', []))}个")
            
            # 显示重要字段的详细信息
            print("\n   📝 重要字段详情:")
            for i, field in enumerate(form_analysis.get('input_fields', [])[:3]):  # 显示前3个字段
                field_name = field.get('name', field.get('id', f'field_{i}'))
                field_type = field.get('type', 'text')
                placeholder = field.get('placeholder', '')
                required = '(必填)' if field.get('required') else ''
                print(f"      • {field_name} ({field_type}): {placeholder} {required}")
                
        except Exception as e:
            print(f"⚠️ 表单分析显示失败: {e}")
    
    def print_monitoring_summary(self, monitoring_data: Dict[str, Any]) -> None:
        """打印监控摘要"""
        try:
            print(f"\n📊 综合监控摘要:")
            
            metadata = monitoring_data.get('metadata', {})
            summary = monitoring_data.get('summary', {})
            recommendations = monitoring_data.get('recommendations', [])
            
            print(f"   ⏱️ 监控时长: {metadata.get('total_duration', 0):.1f}秒")
            print(f"   📡 网络请求: {summary.get('network_requests_count', 0)}个")
            print(f"   📝 表单字段: {summary.get('form_fields_discovered', 0)}个")
            print(f"   🔲 按钮: {summary.get('buttons_discovered', 0)}个")
            print(f"   ☑️ 复选框: {summary.get('checkboxes_discovered', 0)}个")
            print(f"   🔄 页面跳转: {summary.get('page_transitions', 0)}次")
            print(f"   📊 数据质量: {summary.get('data_quality', '未知')}")
            
            # 显示关键网络请求
            data_collection = monitoring_data.get('data_collection', {})
            requests = data_collection.get('network_requests', [])
            
            if requests:
                print(f"\n   🌐 关键网络请求:")
                # 显示POST/PUT请求（通常是提交请求）
                submit_requests = [req for req in requests if req.get('method') in ['POST', 'PUT']]
                for req in submit_requests[-3:]:  # 显示最后3个提交请求
                    method = req.get('method', 'GET')
                    url = req.get('url', '')[:50]
                    status = req.get('status', 'Unknown')
                    print(f"      • {method} {url}... (状态: {status})")
            
            # 显示自动化建议
            if recommendations:
                print(f"\n   💡 自动化建议:")
                for rec in recommendations[:3]:  # 显示前3个建议
                    print(f"      • {rec}")
                    
        except Exception as e:
            print(f"⚠️ 监控摘要显示失败: {e}")

    # 向后兼容方法
    def start_continuous_monitoring(self) -> Dict[str, Any]:
        """向后兼容的监控方法"""
        return self.start_comprehensive_monitoring() 