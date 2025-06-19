#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_form_speed.py
完整流程测试：表单填写 + 网络请求捕获 + 页面元素爬取
"""

import time
import os
import json
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

class NetworkCapture:
    """网络请求捕获器"""
    
    def __init__(self, driver):
        self.driver = driver
        self.requests = []
        self.monitoring = False
    
    def start_monitoring(self):
        """开始监控网络请求"""
        print("📡 启动网络请求监控...")
        
        # 启用Chrome DevTools Protocol
        self.driver.execute_cdp_cmd('Network.enable', {})
        self.monitoring = True
        
        # 注入更强力的JavaScript拦截器
        js_code = """
        window.capturedRequests = [];
        window.networkLogs = [];
        
        // 记录所有网络活动
        function logRequest(method, url, data, type) {
            const request = {
                method: method,
                url: url,
                data: data,
                timestamp: new Date().toISOString(),
                type: type
            };
            window.capturedRequests.push(request);
            window.networkLogs.push(`${method} ${url} [${type}]`);
            console.log('Network Request:', request);
        }
        
        // 拦截XMLHttpRequest
        const originalXHR = window.XMLHttpRequest;
        window.XMLHttpRequest = function() {
            const xhr = new originalXHR();
            const originalOpen = xhr.open;
            const originalSend = xhr.send;
            
            xhr.open = function(method, url, ...args) {
                this._method = method;
                this._url = url;
                return originalOpen.apply(this, [method, url, ...args]);
            };
            
            xhr.send = function(data) {
                logRequest(this._method, this._url, data, 'xhr');
                return originalSend.apply(this, [data]);
            };
            
            return xhr;
        };
        
        // 拦截fetch请求
        const originalFetch = window.fetch;
        window.fetch = function(url, options = {}) {
            const method = options.method || 'GET';
            logRequest(method, url, options.body, 'fetch');
            return originalFetch.apply(this, arguments);
        };
        
        // 拦截表单提交
        const forms = document.querySelectorAll('form');
        forms.forEach(form => {
            form.addEventListener('submit', function(e) {
                const formData = new FormData(form);
                const data = {};
                for (let [key, value] of formData.entries()) {
                    data[key] = value;
                }
                logRequest('POST', form.action || '/api/submit', JSON.stringify(data), 'form-submit');
            });
        });
        
        // 监听所有点击事件
        document.addEventListener('click', function(e) {
            if (e.target.type === 'submit' || e.target.tagName === 'BUTTON') {
                logRequest('CLICK', window.location.href, 'button-click', 'user-action');
            }
        });
        """
        
        self.driver.execute_script(js_code)
        print("✅ 增强网络拦截器已注入")
    
    def capture_requests(self, duration=3):
        """捕获指定时间内的网络请求"""
        print(f"🔍 捕获网络请求（{duration}秒）...")
        
        start_time = time.time()
        captured = []
        
        while time.time() - start_time < duration:
            try:
                # 方法1：获取JavaScript捕获的请求
                js_requests = self.driver.execute_script("return window.capturedRequests || [];")
                
                for req in js_requests:
                    if req not in captured:
                        captured.append(req)
                        print(f"📤 JS捕获: {req['method']} {req['url']} [{req['type']}]")
                
                # 方法2：通过CDP获取网络日志
                try:
                    logs = self.driver.get_log('performance')
                    for log in logs:
                        message = log.get('message', {})
                        if isinstance(message, str):
                            import json
                            try:
                                message = json.loads(message)
                            except:
                                continue
                        
                        method = message.get('message', {}).get('method', '')
                        params = message.get('message', {}).get('params', {})
                        
                        if method == 'Network.requestWillBeSent':
                            request = params.get('request', {})
                            network_req = {
                                'method': request.get('method', 'UNKNOWN'),
                                'url': request.get('url', ''),
                                'data': request.get('postData', ''),
                                'timestamp': time.time(),
                                'type': 'cdp-network'
                            }
                            if network_req not in captured:
                                captured.append(network_req)
                                print(f"📤 CDP捕获: {network_req['method']} {network_req['url']}")
                
                except Exception as cdp_error:
                    # CDP方法失败时不报错，继续使用JS方法
                    pass
                
                time.sleep(0.1)
                
            except Exception as e:
                print(f"⚠️ 捕获请求时出错: {e}")
        
        self.requests.extend(captured)
        
        # 获取网络日志用于调试
        try:
            network_logs = self.driver.execute_script("return window.networkLogs || [];")
            if network_logs:
                print(f"🔍 网络日志: {network_logs}")
        except:
            pass
        
        # 清空JavaScript缓存
        self.driver.execute_script("window.capturedRequests = []; window.networkLogs = [];")
        
        return captured

class PageElementCrawler:
    """页面元素爬取器"""
    
    def __init__(self, driver):
        self.driver = driver
    
    def crawl_page_elements(self):
        """爬取页面所有表单元素"""
        print("🕷️ 开始爬取页面元素...")
        
        elements_data = {
            'timestamp': datetime.now().isoformat(),
            'url': self.driver.current_url,
            'title': self.driver.title,
            'input_fields': [],
            'buttons': [],
            'checkboxes': [],
            'select_fields': [],
            'textareas': [],
            'links': []
        }
        
        try:
            # 爬取输入框
            inputs = self.driver.find_elements(By.TAG_NAME, 'input')
            for inp in inputs:
                try:
                    input_data = {
                        'tag': 'input',
                        'type': inp.get_attribute('type'),
                        'name': inp.get_attribute('name'),
                        'id': inp.get_attribute('id'),
                        'placeholder': inp.get_attribute('placeholder'),
                        'value': inp.get_attribute('value'),
                        'required': inp.get_attribute('required'),
                        'visible': inp.is_displayed(),
                        'enabled': inp.is_enabled()
                    }
                    elements_data['input_fields'].append(input_data)
                except:
                    continue
            
            # 爬取按钮
            buttons = self.driver.find_elements(By.TAG_NAME, 'button')
            for btn in buttons:
                try:
                    button_data = {
                        'tag': 'button',
                        'type': btn.get_attribute('type'),
                        'text': btn.text,
                        'id': btn.get_attribute('id'),
                        'class': btn.get_attribute('class'),
                        'onclick': btn.get_attribute('onclick'),
                        'visible': btn.is_displayed(),
                        'enabled': btn.is_enabled()
                    }
                    elements_data['buttons'].append(button_data)
                except:
                    continue
            
            # 爬取复选框
            checkboxes = self.driver.find_elements(By.CSS_SELECTOR, 'input[type="checkbox"]')
            for cb in checkboxes:
                try:
                    checkbox_data = {
                        'tag': 'input',
                        'type': 'checkbox',
                        'name': cb.get_attribute('name'),
                        'id': cb.get_attribute('id'),
                        'checked': cb.is_selected(),
                        'visible': cb.is_displayed(),
                        'enabled': cb.is_enabled()
                    }
                    elements_data['checkboxes'].append(checkbox_data)
                except:
                    continue
            
            # 爬取下拉框
            selects = self.driver.find_elements(By.TAG_NAME, 'select')
            for sel in selects:
                try:
                    select_data = {
                        'tag': 'select',
                        'name': sel.get_attribute('name'),
                        'id': sel.get_attribute('id'),
                        'multiple': sel.get_attribute('multiple'),
                        'options': [opt.text for opt in sel.find_elements(By.TAG_NAME, 'option')],
                        'visible': sel.is_displayed(),
                        'enabled': sel.is_enabled()
                    }
                    elements_data['select_fields'].append(select_data)
                except:
                    continue
            
            # 爬取文本域
            textareas = self.driver.find_elements(By.TAG_NAME, 'textarea')
            for ta in textareas:
                try:
                    textarea_data = {
                        'tag': 'textarea',
                        'name': ta.get_attribute('name'),
                        'id': ta.get_attribute('id'),
                        'placeholder': ta.get_attribute('placeholder'),
                        'value': ta.get_attribute('value'),
                        'visible': ta.is_displayed(),
                        'enabled': ta.is_enabled()
                    }
                    elements_data['textareas'].append(textarea_data)
                except:
                    continue
            
            # 爬取链接
            links = self.driver.find_elements(By.TAG_NAME, 'a')
            for link in links:
                try:
                    link_data = {
                        'tag': 'a',
                        'href': link.get_attribute('href'),
                        'text': link.text,
                        'id': link.get_attribute('id'),
                        'class': link.get_attribute('class'),
                        'visible': link.is_displayed()
                    }
                    elements_data['links'].append(link_data)
                except:
                    continue
            
            # 统计信息
            total_elements = (len(elements_data['input_fields']) + 
                            len(elements_data['buttons']) + 
                            len(elements_data['checkboxes']) + 
                            len(elements_data['select_fields']) + 
                            len(elements_data['textareas']) + 
                            len(elements_data['links']))
            
            print(f"✅ 爬取完成，共发现 {total_elements} 个元素:")
            print(f"   📝 输入框: {len(elements_data['input_fields'])} 个")
            print(f"   🔘 按钮: {len(elements_data['buttons'])} 个") 
            print(f"   ☑️ 复选框: {len(elements_data['checkboxes'])} 个")
            print(f"   📋 下拉框: {len(elements_data['select_fields'])} 个")
            print(f"   📄 文本域: {len(elements_data['textareas'])} 个")
            print(f"   🔗 链接: {len(elements_data['links'])} 个")
            
            return elements_data
            
        except Exception as e:
            print(f"❌ 页面元素爬取失败: {e}")
            return None

def setup_fast_chrome():
    """设置Chrome驱动（支持网络监控）"""
    print("🔧 设置Chrome驱动（支持网络监控）...")
    
    chrome_options = Options()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--disable-images')  # 禁用图片加载
    chrome_options.add_argument('--disable-plugins')
    chrome_options.add_argument('--disable-extensions')
    
    # 启用性能日志
    chrome_options.set_capability('goog:loggingPrefs', {
        'performance': 'ALL',
        'browser': 'ALL'
    })
    
    # 使用webdriver-manager自动管理驱动
    print("✅ 使用webdriver-manager自动管理驱动")
    service = Service(ChromeDriverManager().install())
    
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.set_page_load_timeout(5)  # 5秒页面加载超时
    
    return driver

def complete_flow_test():
    """完整流程测试：填写表单 + 捕获请求 + 爬取元素"""
    print("🧪 完整流程测试")
    print("🎯 目标：表单填写 + 网络捕获 + 元素爬取")
    print("=" * 50)
    
    driver = None
    try:
        # 启动浏览器
        driver = setup_fast_chrome()
        wait = WebDriverWait(driver, 5)
        
        # 获取测试文件路径
        test_file = os.path.join(os.path.dirname(__file__), 'test_form.html')
        file_url = f"file://{os.path.abspath(test_file)}"
        
        print(f"📄 打开测试页面: {file_url}")
        
        # 记录总开始时间
        total_start = time.time()
        
        # 加载页面
        driver.get(file_url)
        print("✅ 页面加载完成")
        
        # 启动网络监控
        network_capture = NetworkCapture(driver)
        network_capture.start_monitoring()
        
        # 第一次爬取页面元素（填写前）
        print("\n🕷️ 第一次页面元素爬取（填写前）...")
        page_crawler = PageElementCrawler(driver)
        elements_before = page_crawler.crawl_page_elements()
        
        # 表单填写
        print("\n🚀 开始表单填写...")
        fill_start = time.time()
        
        form_data = {
            'name': '김민수',
            'birthday': '1995-03-15', 
            'phone': '010-1234-5678',
            'email': 'test@example.com'
        }
        
        fields_filled = 0
        
        # 填写所有字段
        for field_id, value in form_data.items():
            try:
                if field_id == 'birthday':
                    element = driver.find_element(By.ID, field_id)
                else:
                    element = driver.find_element(By.ID, field_id)
                element.clear()
                element.send_keys(value)
                fields_filled += 1
                print(f"✅ {field_id}: {value}")
            except Exception as e:
                print(f"❌ {field_id} 填写失败: {e}")
        
        # 勾选复选框
        checkboxes_checked = 0
        for checkbox_id in ['agree1', 'agree2', 'agree3']:
            try:
                checkbox = driver.find_element(By.ID, checkbox_id)
                if not checkbox.is_selected():
                    checkbox.click()
                    checkboxes_checked += 1
                    print(f"✅ 复选框: {checkbox_id}")
            except Exception as e:
                print(f"❌ 复选框 {checkbox_id} 失败: {e}")
        
        fill_end = time.time()
        fill_time = fill_end - fill_start
        
        print(f"\n📊 表单填写完成:")
        print(f"   📝 成功填写字段: {fields_filled}/4")
        print(f"   ☑️ 成功勾选复选框: {checkboxes_checked}/3")
        print(f"   ⚡ 填写时间: {fill_time:.3f}秒")
        
        # 点击提交按钮并捕获网络请求
        print("\n🖱️ 点击提交按钮...")
        submit_start = time.time()
        
        try:
            submit_button = driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
            submit_button.click()
            print("✅ 提交按钮点击成功")
            
            # 捕获网络请求
            captured_requests = network_capture.capture_requests(duration=2)
            
            submit_end = time.time()
            submit_time = submit_end - submit_start
            
            print(f"📡 网络请求捕获完成:")
            print(f"   🌐 捕获到请求: {len(captured_requests)} 个")
            print(f"   ⚡ 捕获时间: {submit_time:.3f}秒")
            
            # 分析请求类型
            get_requests = [r for r in captured_requests if r['method'] == 'GET']
            post_requests = [r for r in captured_requests if r['method'] == 'POST']
            
            print(f"   📥 GET请求: {len(get_requests)} 个")
            print(f"   📤 POST请求: {len(post_requests)} 个")
            
            # 显示POST请求详情
            for req in post_requests:
                print(f"   📤 POST: {req['url']} ({req['type']})")
            
        except Exception as e:
            print(f"❌ 提交按钮点击失败: {e}")
            captured_requests = []
        
        # 第二次爬取页面元素（提交后）
        print("\n🕷️ 第二次页面元素爬取（提交后）...")
        elements_after = page_crawler.crawl_page_elements()
        
        # 保存完整数据
        complete_data = {
            'test_timestamp': datetime.now().isoformat(),
            'test_url': file_url,
            'form_fill_results': {
                'fields_filled': fields_filled,
                'checkboxes_checked': checkboxes_checked,
                'fill_time': fill_time,
                'success_rate': (fields_filled + checkboxes_checked) / 7
            },
            'network_requests': captured_requests,
            'get_requests': get_requests,
            'post_requests': post_requests,
            'page_elements_before': elements_before,
            'page_elements_after': elements_after,
            'total_time': time.time() - total_start
        }
        
        # 保存到文件
        data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
        os.makedirs(data_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"complete_flow_test_{timestamp}.json"
        filepath = os.path.join(data_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(complete_data, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 完整数据已保存: {filepath}")
        
        # 总结报告
        total_time = time.time() - total_start
        
        print(f"\n🎯 完整流程测试报告:")
        print(f"   ⏱️ 总耗时: {total_time:.3f}秒")
        print(f"   📝 表单填写: {fill_time:.3f}秒")
        print(f"   📡 网络捕获: {len(captured_requests)} 个请求")
        print(f"   🕷️ 元素爬取: {len(elements_before['input_fields']) if elements_before else 0} 个输入框")
        print(f"   📈 整体成功率: {((fields_filled + checkboxes_checked)/7 + (1 if captured_requests else 0) + (1 if elements_before else 0))/3*100:.1f}%")
        
        # 成功条件
        is_success = (
            fill_time <= 2.0 and  # 填写时间<=2秒
            len(captured_requests) > 0 and  # 捕获到网络请求
            elements_before is not None  # 成功爬取元素
        )
        
        if is_success:
            print("\n🎉 完整流程测试通过！")
        else:
            print("\n⚠️ 完整流程测试未完全通过")
        
        return is_success
        
    except Exception as e:
        print(f"❌ 测试过程出错: {e}")
        return False
        
    finally:
        if driver:
            driver.quit()
            print("\n🔚 浏览器已关闭")

if __name__ == "__main__":
    print("🧪 完整流程测试")
    print("🎯 目标：表单填写 + 网络请求捕获 + 页面元素爬取")
    print("=" * 50)
    
    success = complete_flow_test()
    
    if success:
        print("\n✅ 测试完成!")
    else:
        print("\n❌ 测试失败!") 