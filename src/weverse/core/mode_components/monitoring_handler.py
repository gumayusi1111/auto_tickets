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
        print("🔍 监控内容包括：")
        print("   - 所有网络请求（GET/POST/PUT等）")
        print("   - 页面跳转和DOM变化")
        print("   - 用户交互的元素（输入框、按钮、复选框等）")
        print("   - 表单提交和响应数据")
        print("⌨️  完成所有操作后，请在终端按 Enter 键结束监控")
        print("=" * 60)
        
        # 启动网络监控
        self._ensure_network_monitoring()
        
        # 记录初始状态
        last_url = self.driver.current_url
        last_page_source_hash = hash(self.driver.page_source)
        request_count = 0
        tracked_elements = set()  # 跟踪用户交互过的元素
        
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
        
        # 注入JavaScript监听器来跟踪用户操作
        self._inject_user_action_tracker()
        
        print("🔍 开始实时监控...")
        
        # 监控循环
        monitor_count = 0
        while not stop_monitoring.is_set():
            try:
                monitor_count += 1
                
                # 检查页面URL变化
                current_url = self.driver.current_url
                if current_url != last_url:
                    print(f"📍 页面跳转: {last_url} → {current_url}")
                    self._record_page_change(last_url, current_url)
                    last_url = current_url
                    
                    # 页面跳转后重新注入用户操作跟踪器
                    time.sleep(0.5)  # 等待页面加载
                    self._inject_user_action_tracker()
                    print(f"🔄 重新注入跟踪器（新页面: {current_url}）")
                
                # 检查DOM变化
                current_page_source_hash = hash(self.driver.page_source)
                if current_page_source_hash != last_page_source_hash:
                    print(f"📄 DOM内容已更新")
                    last_page_source_hash = current_page_source_hash
                
                # 获取用户操作的元素
                user_actions = self._get_user_actions()
                for action in user_actions:
                    if action['element_id'] not in tracked_elements:
                        tracked_elements.add(action['element_id'])
                        self._record_user_action(action)
                        print(f"👆 用户操作: {action['type']} - {action['description']}")
                
                # 检查网络请求变化
                if self.network_monitor:
                    current_requests = self.network_monitor.get_captured_requests()
                    if len(current_requests) > request_count:
                        new_requests = current_requests[request_count:]
                        for req in new_requests:
                            method = req.get('method', 'GET')
                            url = req.get('url', '')
                            status = req.get('status', 'Unknown')
                            
                            # 详细记录重要请求
                            if method in ['POST', 'PUT'] or 'api' in url.lower():
                                print(f"🌐 重要请求: {method} {url[:80]}...")
                                print(f"   状态: {status}")
                                if req.get('request_body'):
                                    print(f"   请求数据: {str(req['request_body'])[:100]}...")
                                if req.get('response_body'):
                                    print(f"   响应数据: {str(req['response_body'])[:100]}...")
                            else:
                                print(f"🌐 新请求: {method} {url[:50]}... (状态: {status})")
                        
                        request_count = len(current_requests)
                
                # 定期保存监控数据快照
                if monitor_count % 20 == 0:  # 每10秒保存一次
                    self._save_monitoring_snapshot()
                
                # 短暂休息避免CPU过载
                time.sleep(0.5)
                
            except Exception as e:
                print(f"⚠️ 监控循环错误: {e}")
                import traceback
                traceback.print_exc()
                # 继续监控，不要中断
                time.sleep(1)  # 出错时等待更长时间
                continue
        
        print("\n✅ 用户已结束监控")
        print(f"📊 监控统计：")
        print(f"   - 监控循环次数: {monitor_count}")
        print(f"   - 捕获网络请求: {request_count}个")
        print(f"   - 用户操作元素: {len(tracked_elements)}个")
    
    def _inject_user_action_tracker(self) -> None:
        """注入JavaScript来跟踪用户操作"""
        try:
            # 检查当前域名
            current_domain = self.driver.execute_script("return window.location.hostname;")
            current_url = self.driver.execute_script("return window.location.href;")
            print(f"🌐 在域名 {current_domain} 注入跟踪器")
            print(f"📍 当前URL: {current_url}")
            
            # 首先检查页面是否支持JavaScript
            try:
                js_enabled = self.driver.execute_script("return typeof window !== 'undefined';")
                print(f"🔧 JavaScript可用性: {js_enabled}")
            except Exception as js_check_error:
                print(f"❌ JavaScript检查失败: {js_check_error}")
                return False
            
            tracker_script = """
            // 清除控制台并开始跟踪
            console.clear();
            console.log('🚀 开始注入用户操作跟踪器...');
            
            // 确保全局变量存在
            window.userActions = window.userActions || [];
            window.actionId = window.actionId || 0;
            window.trackingActive = true;
            window.injectionTime = new Date().toISOString();
            
            console.log('=== 用户操作跟踪器启动 ===');
            console.log('当前页面:', window.location.href);
            console.log('注入时间:', window.injectionTime);
            
            // 移除现有监听器（如果有）
            if (window.clickHandler) {
                document.removeEventListener('click', window.clickHandler, true);
                console.log('🗑️ 移除旧的点击监听器');
            }
            if (window.inputHandler) {
                document.removeEventListener('input', window.inputHandler, true);
                console.log('🗑️ 移除旧的输入监听器');
            }
            
            // 测试函数
            window.testTracker = function() {
                console.log('🧪 跟踪器测试 - 当前操作数:', window.userActions.length);
                console.log('🧪 跟踪器状态:', window.trackingActive);
                return {
                    active: window.trackingActive,
                    actionCount: window.userActions.length,
                    injectionTime: window.injectionTime
                };
            };
            
            // 定义点击处理器 - 简化版本先测试
            window.clickHandler = function(e) {
                console.log('🎯 点击事件触发!', e.target);
                
                if (!window.trackingActive) {
                    console.log('⚠️ 跟踪器未激活');
                    return;
                }
                
                try {
                    window.actionId++;
                    const action = {
                        id: window.actionId,
                        type: 'click',
                        timestamp: new Date().toISOString(),
                        pageUrl: window.location.href,
                        pageDomain: window.location.hostname,
                        element: e.target.tagName || 'UNKNOWN',
                        elementId: e.target.id || '',
                        elementClass: e.target.className || '',
                        elementText: (e.target.textContent || e.target.innerText || '').substring(0, 100),
                        elementValue: e.target.value || '',
                        elementType: e.target.type || '',
                        elementHref: e.target.href || '',
                        xpath: getXPath(e.target),
                        cssSelector: getCSSSelector(e.target),
                        clientX: e.clientX || 0,
                        clientY: e.clientY || 0
                    };
                    
                    window.userActions.push(action);
                    console.log('✅ 点击捕获成功:', action);
                    console.log('📊 当前总操作数:', window.userActions.length);
                    
                    // 立即保存到sessionStorage作为备份
                    try {
                        sessionStorage.setItem('userActions', JSON.stringify(window.userActions));
                        console.log('💾 操作已备份到sessionStorage');
                    } catch(storage_error) {
                        console.log('⚠️ sessionStorage备份失败:', storage_error);
                    }
                    
                } catch(error) {
                    console.error('❌ 点击处理错误:', error);
                }
            };
            
            // 定义输入处理器
            window.inputHandler = function(e) {
                console.log('⌨️ 输入事件触发!', e.target);
                
                if (!window.trackingActive) return;
                
                try {
                    window.actionId++;
                    const action = {
                        id: window.actionId,
                        type: 'input',
                        timestamp: new Date().toISOString(),
                        pageUrl: window.location.href,
                        pageDomain: window.location.hostname,
                        element: e.target.tagName || 'UNKNOWN',
                        elementId: e.target.id || '',
                        elementClass: e.target.className || '',
                        elementName: e.target.name || '',
                        elementType: e.target.type || '',
                        placeholder: e.target.placeholder || '',
                        value: e.target.type === 'password' ? '[PASSWORD]' : (e.target.value || '').substring(0, 50),
                        xpath: getXPath(e.target),
                        cssSelector: getCSSSelector(e.target)
                    };
                    
                    window.userActions.push(action);
                    console.log('✅ 输入捕获成功:', action);
                    
                    // 备份到sessionStorage
                    try {
                        sessionStorage.setItem('userActions', JSON.stringify(window.userActions));
                    } catch(storage_error) {
                        console.log('⚠️ sessionStorage备份失败:', storage_error);
                    }
                    
                } catch(error) {
                    console.error('❌ 输入处理错误:', error);
                }
            };
            
            // 添加事件监听器 - 使用多种方式确保捕获
            try {
                document.addEventListener('click', window.clickHandler, true);
                console.log('✅ 点击监听器已添加 (capture=true)');
            } catch(e1) {
                console.error('❌ 点击监听器添加失败 (capture=true):', e1);
                try {
                    document.addEventListener('click', window.clickHandler, false);
                    console.log('✅ 点击监听器已添加 (capture=false)');
                } catch(e2) {
                    console.error('❌ 点击监听器添加完全失败:', e2);
                }
            }
            
            try {
                document.addEventListener('input', window.inputHandler, true);
                console.log('✅ 输入监听器已添加');
            } catch(e3) {
                console.error('❌ 输入监听器添加失败:', e3);
            }
            
            // 添加mousedown事件作为备选
            document.addEventListener('mousedown', function(e) {
                console.log('🖱️ mousedown事件:', e.target.tagName);
            }, true);
            
            // 添加touchstart事件（移动端）
            document.addEventListener('touchstart', function(e) {
                console.log('👆 touchstart事件:', e.target.tagName);
            }, true);
            
            // 获取元素XPath的简化版本
            function getXPath(element) {
                if (!element) return '';
                if (element.id) return '//*[@id="' + element.id + '"]';
                
                try {
                    let path = '';
                    let current = element;
                    
                    while (current && current.nodeType === 1 && current !== document.body) {
                        let selector = current.tagName.toLowerCase();
                        let index = 1;
                        let sibling = current.previousElementSibling;
                        while (sibling) {
                            if (sibling.tagName === current.tagName) index++;
                            sibling = sibling.previousElementSibling;
                        }
                        path = '/' + selector + '[' + index + ']' + path;
                        current = current.parentNode;
                        
                        if (path.length > 200) break; // 防止过长
                    }
                    return path || '/unknown';
                } catch(xpath_error) {
                    console.log('⚠️ XPath生成错误:', xpath_error);
                    return '/error';
                }
            }
            
            // 获取CSS选择器的简化版本
            function getCSSSelector(element) {
                if (!element) return '';
                if (element.id) return '#' + element.id;
                
                try {
                    if (element.className && typeof element.className === 'string') {
                        return element.tagName.toLowerCase() + '.' + element.className.trim().split(/\\s+/).join('.');
                    }
                    return element.tagName.toLowerCase();
                } catch(css_error) {
                    console.log('⚠️ CSS选择器生成错误:', css_error);
                    return element.tagName.toLowerCase() || 'unknown';
                }
            }
            
            // 页面可见性变化监听
            document.addEventListener('visibilitychange', function() {
                if (document.visibilityState === 'visible') {
                    console.log('📖 页面变为可见');
                } else {
                    console.log('📕 页面变为隐藏');
                }
            });
            
            // 定期检查跟踪器状态
            window.trackerHealthCheck = setInterval(function() {
                console.log('💓 跟踪器心跳检查 - 操作数:', window.userActions.length);
            }, 10000); // 每10秒检查一次
            
            console.log('✅ 用户操作跟踪器注入完成');
            console.log('📊 初始操作记录数:', window.userActions.length);
            console.log('🧪 可通过 window.testTracker() 测试跟踪器');
            
            // 返回成功标志
            return true;
            """
            
            # 执行注入脚本
            injection_result = self.driver.execute_script(tracker_script)
            
            # 验证注入是否成功
            time.sleep(0.5)  # 等待脚本执行
            
            verification_result = self.driver.execute_script("""
                return {
                    trackingActive: window.trackingActive || false,
                    userActionsExists: typeof window.userActions !== 'undefined',
                    clickHandlerExists: typeof window.clickHandler === 'function',
                    testTrackerExists: typeof window.testTracker === 'function',
                    currentActionCount: (window.userActions || []).length,
                    injectionTime: window.injectionTime || 'unknown'
                };
            """)
            
            print(f"🔍 跟踪器验证结果:")
            print(f"   - 跟踪激活: {verification_result.get('trackingActive')}")
            print(f"   - userActions存在: {verification_result.get('userActionsExists')}")
            print(f"   - 点击处理器存在: {verification_result.get('clickHandlerExists')}")
            print(f"   - 测试函数存在: {verification_result.get('testTrackerExists')}")
            print(f"   - 当前操作数: {verification_result.get('currentActionCount')}")
            print(f"   - 注入时间: {verification_result.get('injectionTime')}")
            
            if verification_result.get('trackingActive') and verification_result.get('clickHandlerExists'):
                print(f"✅ 用户操作跟踪器在 {current_domain} 注入并验证成功")
                
                # 执行一次测试点击
                test_result = self.driver.execute_script("""
                    // 模拟一次测试点击
                    if (window.clickHandler) {
                        try {
                            var testEvent = {
                                target: document.body,
                                clientX: 100,
                                clientY: 100
                            };
                            window.clickHandler(testEvent);
                            return 'test_click_executed';
                        } catch(e) {
                            return 'test_click_failed: ' + e.message;
                        }
                    }
                    return 'no_click_handler';
                """)
                print(f"🧪 测试点击结果: {test_result}")
                
                return True
            else:
                print(f"❌ 跟踪器注入失败或验证失败")
                return False
            
        except Exception as e:
            print(f"⚠️ 注入跟踪器失败: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _get_user_actions(self) -> List[Dict]:
        """获取用户操作记录"""
        try:
            # 检查driver是否还有效
            if not self.driver:
                print("⚠️ WebDriver不可用")
                return []
            
            # 检查页面是否已加载
            try:
                ready_state = self.driver.execute_script("return document.readyState;")
                print(f"📄 页面状态: {ready_state}")
            except Exception:
                print("⚠️ 页面未准备好，跳过用户操作检测")
                return []
            
            # 检查跟踪器状态
            try:
                tracker_status = self.driver.execute_script("""
                    return {
                        trackingActive: window.trackingActive || false,
                        userActionsCount: (window.userActions || []).length,
                        hasClickHandler: typeof window.clickHandler === 'function',
                        hasTestTracker: typeof window.testTracker === 'function'
                    };
                """)
                print(f"🔍 跟踪器状态检查:")
                print(f"   - 激活状态: {tracker_status.get('trackingActive')}")
                print(f"   - 操作记录数: {tracker_status.get('userActionsCount')}")
                print(f"   - 点击处理器: {tracker_status.get('hasClickHandler')}")
                print(f"   - 测试函数: {tracker_status.get('hasTestTracker')}")
            except Exception as status_error:
                print(f"⚠️ 跟踪器状态检查失败: {status_error}")
            
            # 获取JavaScript中的用户操作记录
            js_actions = []
            try:
                js_actions = self.driver.execute_script("""
                    var actions = window.userActions || [];
                    console.log('📊 获取操作记录，当前数量:', actions.length);
                    
                    // 不清空数组，保留记录用于调试
                    return actions;
                """)
                print(f"📋 从JavaScript获取到 {len(js_actions)} 个操作记录")
                
                if js_actions:
                    print(f"   最新操作预览:")
                    for i, action in enumerate(js_actions[-3:]):  # 显示最后3个操作
                        action_type = action.get('type', 'unknown')
                        element = action.get('element', 'unknown')
                        text = action.get('elementText', '')[:30]
                        timestamp = action.get('timestamp', '')
                        print(f"     {i+1}. [{timestamp}] {action_type} {element}: {text}")
                
            except Exception as js_error:
                print(f"⚠️ JavaScript操作记录获取失败: {js_error}")
            
            # 从sessionStorage获取备份数据
            backup_actions = []
            try:
                backup_data = self.driver.execute_script("""
                    var backupData = sessionStorage.getItem('userActions');
                    if (backupData) {
                        try {
                            return JSON.parse(backupData);
                        } catch(e) {
                            console.log('⚠️ 备份数据解析失败:', e);
                            return [];
                        }
                    }
                    return [];
                """)
                
                if backup_data:
                    backup_actions = backup_data
                    print(f"💾 从sessionStorage获取到 {len(backup_actions)} 个备份操作记录")
                else:
                    print("💾 sessionStorage中无备份数据")
                    
            except Exception as backup_error:
                print(f"⚠️ sessionStorage备份数据获取失败: {backup_error}")
            
            # 合并数据源，优先使用JavaScript数据，备份数据作为补充
            all_actions = js_actions if js_actions else backup_actions
            
            if not all_actions:
                print("❌ 所有数据源都无操作记录")
                
                # 尝试手动测试跟踪器
                try:
                    manual_test_result = self.driver.execute_script("""
                        if (window.testTracker) {
                            return window.testTracker();
                        }
                        return null;
                    """)
                    if manual_test_result:
                        print(f"🧪 手动测试结果: {manual_test_result}")
                    else:
                        print("🧪 测试函数不可用")
                except Exception as test_error:
                    print(f"🧪 手动测试失败: {test_error}")
                
                return []
            
            # 处理每个操作
            processed_actions = []
            print(f"🔄 处理 {len(all_actions)} 个操作记录")
            
            for i, action in enumerate(all_actions):
                if action and isinstance(action, dict):
                    try:
                        processed_action = {
                            'element_id': f"{action.get('type', 'unknown')}_{action.get('id', i)}",
                            'type': action.get('type', 'unknown'),
                            'description': self._format_action_description(action),
                            'raw_data': action
                        }
                        processed_actions.append(processed_action)
                        
                        # 详细记录重要操作
                        if action.get('type') == 'click':
                            element_text = action.get('elementText', '').strip()
                            element = action.get('element', 'unknown')
                            print(f"   ✅ 处理点击操作 {i+1}: {element} - '{element_text[:30]}...'")
                        
                    except Exception as process_error:
                        print(f"⚠️ 处理操作 {i+1} 失败: {process_error}")
                        continue
            
            print(f"✅ 成功处理 {len(processed_actions)} 个操作记录")
            return processed_actions
            
        except Exception as e:
            print(f"❌ 获取用户操作失败: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def _format_action_description(self, action: Dict) -> str:
        """格式化操作描述"""
        action_type = action.get('type')
        
        if action_type == 'click':
            element_text = action.get('elementText', '').strip()
            if element_text:
                return f"点击 {action.get('element')} 元素: '{element_text[:30]}...'"
            else:
                return f"点击 {action.get('element')} 元素 (ID: {action.get('elementId')})"
        
        elif action_type == 'input':
            return f"输入 {action.get('elementType')} 字段 ({action.get('placeholder') or action.get('elementId')})"
        
        elif action_type == 'change':
            if action.get('elementType') == 'checkbox':
                return f"{'勾选' if action.get('checked') else '取消勾选'}复选框 (ID: {action.get('elementId')})"
            elif action.get('elementType') == 'radio':
                return f"选择单选框 (值: {action.get('value')})"
        
        elif action_type == 'submit':
            return f"提交表单 ({action.get('formMethod')} {action.get('formAction')})"
        
        return f"{action_type} 操作"
    
    def _record_user_action(self, action: Dict) -> None:
        """记录用户操作"""
        self.collected_data['user_actions'].append({
            'timestamp': datetime.now().isoformat(),
            'action': action
        })
    
    def _save_monitoring_snapshot(self) -> None:
        """保存监控数据快照"""
        try:
            snapshot_data = {
                'timestamp': datetime.now().isoformat(),
                'url': self.driver.current_url,
                'network_requests_count': len(self.collected_data.get('network_requests', [])),
                'user_actions_count': len(self.collected_data.get('user_actions', []))
            }
            print(f"💾 保存监控快照: {snapshot_data['network_requests_count']}个请求, {snapshot_data['user_actions_count']}个操作")
        except Exception as e:
            print(f"⚠️ 保存快照失败: {e}")
    
    def _collect_final_data(self) -> None:
        """收集最终数据"""
        print("\n📊 阶段5: 收集最终数据")
        
        try:
            # 收集最终用户操作
            final_user_actions = self._get_user_actions()
            for action in final_user_actions:
                self._record_user_action(action)
            
            # 从JavaScript中收集所有剩余的操作记录
            try:
                all_js_actions = self.driver.execute_script("""
                    return window.userActions || [];
                """)
                print(f"📋 从JavaScript收集到 {len(all_js_actions)} 个操作记录")
                
                # 将JavaScript中的操作记录也保存到collected_data中
                if all_js_actions:
                    for js_action in all_js_actions:
                        processed_action = {
                            'element_id': f"{js_action.get('type', 'unknown')}_{js_action.get('id', 0)}",
                            'type': js_action.get('type', 'unknown'),
                            'description': self._format_action_description(js_action),
                            'raw_data': js_action
                        }
                        self._record_user_action(processed_action)
                        
            except Exception as js_error:
                print(f"⚠️ 收集JavaScript操作记录失败: {js_error}")
            
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
            
            # 显示详细的用户操作汇总
            self._print_user_actions_summary()
            
            # 停用JavaScript跟踪器
            self._disable_user_action_tracker()
            
            print(f"✅ 最终数据收集完成，总监控时长: {time.time() - self.monitoring_start_time:.1f}秒")
            
        except Exception as e:
            print(f"⚠️ 最终数据收集失败: {e}")
            import traceback
            traceback.print_exc()
    
    def _print_user_actions_summary(self) -> None:
        """打印用户操作详细汇总"""
        try:
            user_actions = self.collected_data.get('user_actions', [])
            
            if not user_actions:
                print("\n❌ 未捕获到任何用户操作")
                return
            
            print(f"\n🎯 用户操作汇总 (共 {len(user_actions)} 个操作):")
            print("=" * 80)
            
            # 按页面分组显示操作
            actions_by_page = {}
            click_count = 0
            input_count = 0
            other_count = 0
            
            for action_wrapper in user_actions:
                action = action_wrapper.get('action', {})
                raw_data = action.get('raw_data', {})
                
                page_url = raw_data.get('pageUrl', '未知页面')
                page_domain = raw_data.get('pageDomain', '未知域名')
                
                if page_url not in actions_by_page:
                    actions_by_page[page_url] = []
                
                actions_by_page[page_url].append(action)
                
                # 统计操作类型
                action_type = raw_data.get('type', 'unknown')
                if action_type == 'click':
                    click_count += 1
                elif action_type == 'input':
                    input_count += 1
                else:
                    other_count += 1
            
            # 显示统计信息
            print(f"📊 操作统计: 点击 {click_count} 次 | 输入 {input_count} 次 | 其他 {other_count} 次")
            print(f"🌐 涉及页面: {len(actions_by_page)} 个")
            print()
            
            # 按页面显示详细操作
            for page_idx, (page_url, page_actions) in enumerate(actions_by_page.items(), 1):
                print(f"📄 页面 {page_idx}: {page_url}")
                print("-" * 60)
                
                for action_idx, action in enumerate(page_actions, 1):
                    raw_data = action.get('raw_data', {})
                    timestamp = raw_data.get('timestamp', '未知时间')
                    action_type = raw_data.get('type', 'unknown')
                    element = raw_data.get('element', '未知元素')
                    element_text = raw_data.get('elementText', '').strip()
                    css_selector = raw_data.get('cssSelector', '')
                    
                    # 格式化时间
                    try:
                        from datetime import datetime as dt
                        dt_obj = dt.fromisoformat(timestamp.replace('Z', '+00:00'))
                        time_str = dt_obj.strftime('%H:%M:%S')
                    except:
                        time_str = timestamp
                    
                    # 显示操作详情
                    if action_type == 'click':
                        if element_text:
                            print(f"   👆 {action_idx}. [{time_str}] 点击 {element}: '{element_text[:50]}{'...' if len(element_text) > 50 else ''}'")
                        else:
                            print(f"   👆 {action_idx}. [{time_str}] 点击 {element} (选择器: {css_selector})")
                    
                    elif action_type == 'input':
                        input_value = raw_data.get('value', '')
                        placeholder = raw_data.get('placeholder', '')
                        if placeholder:
                            print(f"   ⌨️ {action_idx}. [{time_str}] 输入 {element} ({placeholder}): '{input_value}'")
                        else:
                            print(f"   ⌨️ {action_idx}. [{time_str}] 输入 {element}: '{input_value}'")
                    
                    elif action_type == 'change':
                        element_type = raw_data.get('elementType', '')
                        if element_type in ['checkbox', 'radio']:
                            checked = raw_data.get('checked', False)
                            print(f"   ☑️ {action_idx}. [{time_str}] {'勾选' if checked else '取消勾选'} {element_type}")
                    
                    else:
                        print(f"   🔄 {action_idx}. [{time_str}] {action_type} {element}")
                    
                    # 显示CSS选择器（重要操作）
                    if action_type == 'click' and css_selector:
                        print(f"      📍 CSS选择器: {css_selector}")
                
                print()  # 页面间空行
            
            print("=" * 80)
            print("✅ 用户操作汇总完成")
            
        except Exception as e:
            print(f"⚠️ 用户操作汇总失败: {e}")
            import traceback
            traceback.print_exc()
    
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

    def _disable_user_action_tracker(self) -> None:
        """停用JavaScript跟踪器"""
        try:
            self.driver.execute_script("""
                window.trackingActive = false;
                console.log('=== 用户操作跟踪器停用 ===');
            """)
            print("✅ 用户操作跟踪器已停用")
        except Exception as e:
            print(f"⚠️ 停用跟踪器失败: {e}")
            import traceback
            traceback.print_exc() 