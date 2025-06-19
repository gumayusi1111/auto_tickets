#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_correct_click_crawl.py
正确的点击后爬取测试 - 只在点击按钮后监控请求
"""

import sys
import os
import json
import time
import requests
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
import threading

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.weverse.browser.setup import setup_driver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities


def calculate_optimized_advance_time(ping_latency_ms: float) -> float:
    """
    基于实际ping延迟优化计算提前时间
    
    Args:
        ping_latency_ms: 实际ping延迟(毫秒)
    
    Returns:
        优化后的提前时间(毫秒)
    """
    print(f"🎯 基于你的ping延迟优化计算: {ping_latency_ms}ms")
    
    # 理论最低延迟 = ping延迟
    base_latency = ping_latency_ms
    
    # 浏览器处理开销 (点击->发送请求)
    browser_overhead = 50  # 50ms是合理的浏览器处理时间
    
    # 网络波动缓冲 (保守估计)
    network_buffer = ping_latency_ms * 0.1  # ping延迟的10%作为波动缓冲
    
    # 安全边距 (最小50ms)
    safety_margin = max(50, ping_latency_ms * 0.05)  # ping延迟的5%或50ms
    
    # 计算总提前时间
    total_advance = base_latency + browser_overhead + network_buffer + safety_margin
    
    print(f"📊 延迟分解:")
    print(f"   🌐 基础网络延迟: {base_latency:.1f}ms")
    print(f"   🖥️ 浏览器处理开销: {browser_overhead:.1f}ms")  
    print(f"   📊 网络波动缓冲: {network_buffer:.1f}ms")
    print(f"   🛡️ 安全边距: {safety_margin:.1f}ms")
    print(f"   ⚡ 总计提前时间: {total_advance:.1f}ms")
    
    return total_advance


def test_real_ping_latency() -> float:
    """测试真实的HTTP延迟（模拟ping）"""
    print("🌐 测试真实HTTP延迟...")
    
    latencies = []
    test_count = 10
    
    for i in range(test_count):
        try:
            start_time = time.perf_counter()
            response = requests.head(
                "https://weverse.io", 
                timeout=5,
                headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'}
            )
            end_time = time.perf_counter()
            
            latency_ms = (end_time - start_time) * 1000
            latencies.append(latency_ms)
            
            print(f"\r📡 测试 {i+1}/{test_count}: {latency_ms:.1f}ms", end="", flush=True)
            time.sleep(0.5)
            
        except Exception as e:
            print(f"\n❌ 测试失败: {e}")
    
    if latencies:
        avg_latency = sum(latencies) / len(latencies)
        min_latency = min(latencies)
        max_latency = max(latencies)
        
        print(f"\n📊 HTTP延迟测试结果:")
        print(f"   平均: {avg_latency:.1f}ms")
        print(f"   最快: {min_latency:.1f}ms") 
        print(f"   最慢: {max_latency:.1f}ms")
        
        return avg_latency
    else:
        print("\n⚠️ HTTP延迟测试失败，使用你提供的770ms")
        return 770.0


class ClickThenCrawlMonitor:
    """点击后爬取监控器"""
    
    def __init__(self, driver):
        self.driver = driver
        self.monitoring = False
        self.requests_data = []
        self.monitor_thread = None
        
    def start_monitoring(self):
        """开始监控网络请求"""
        print("🚀 开始监控网络请求...")
        self.monitoring = True
        self.requests_data = []
        
        # 启动监控线程
        self.monitor_thread = threading.Thread(target=self._monitor_requests)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
        
    def _monitor_requests(self):
        """监控网络请求的线程函数"""
        while self.monitoring:
            try:
                # 获取性能日志
                logs = self.driver.get_log('performance')
                
                for log in logs:
                    message = json.loads(log['message'])
                    
                    # 捕获网络响应
                    if message['message']['method'] == 'Network.responseReceived':
                        response = message['message']['params']['response']
                        request_data = {
                            'url': response['url'],
                            'status': response['status'],
                            'method': response.get('method', 'GET'),
                            'headers': dict(response.get('headers', {})),
                            'timestamp': datetime.now().isoformat(),
                            'timing': response.get('timing', {})
                        }
                        self.requests_data.append(request_data)
                        
                        # 实时显示重要请求
                        if any(keyword in response['url'].lower() for keyword in ['apply', 'submit', 'post', 'api']):
                            print(f"🎯 重要请求: {response['status']} {response['url'][:80]}...")
                
                time.sleep(0.1)  # 100ms检查间隔
                
            except Exception as e:
                if self.monitoring:  # 只在还在监控时报错
                    print(f"⚠️ 监控异常: {e}")
                break
    
    def stop_monitoring(self):
        """停止监控"""
        print(f"🛑 停止监控，共捕获 {len(self.requests_data)} 个请求")
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2)
        
        return self.requests_data


def test_click_then_crawl():
    """测试点击按钮后的爬取功能"""
    print("🧪 测试点击后爬取功能")
    print("=" * 50)
    
    # 1. 测试延迟并优化计算
    if input("是否使用你的770ms ping延迟？(y/n, 默认y): ").lower() != 'n':
        ping_latency = 770.0
    else:
        ping_latency = test_real_ping_latency()
    
    # 2. 计算优化的提前时间
    optimized_advance = calculate_optimized_advance_time(ping_latency)
    
    # 3. 设置浏览器
    print("\n🌐 启动浏览器...")
    caps = DesiredCapabilities.CHROME
    caps['goog:loggingPrefs'] = {'performance': 'ALL'}
    
    driver = setup_driver(headless=False)
    driver.execute_cdp_cmd('Network.enable', {})
    
    # 4. 创建监控器
    monitor = ClickThenCrawlMonitor(driver)
    
    try:
        # 5. 访问测试页面
        test_url = input("请输入要测试的URL (默认: https://weverse.io): ").strip()
        if not test_url:
            test_url = "https://weverse.io"
        
        print(f"🌐 访问页面: {test_url}")
        driver.get(test_url)
        time.sleep(3)
        
        # 6. 查找可点击的按钮
        print("🔍 查找可点击的按钮...")
        buttons = driver.find_elements(By.TAG_NAME, 'button')
        links = driver.find_elements(By.TAG_NAME, 'a')
        
        clickable_elements = []
        for i, btn in enumerate(buttons[:5]):  # 只显示前5个按钮
            try:
                if btn.is_displayed() and btn.is_enabled():
                    text = btn.text.strip()[:30] or f"按钮{i+1}"
                    clickable_elements.append((btn, f"按钮: {text}"))
            except:
                pass
        
        for i, link in enumerate(links[:3]):  # 只显示前3个链接
            try:
                if link.is_displayed():
                    text = link.text.strip()[:30] or f"链接{i+1}"
                    clickable_elements.append((link, f"链接: {text}"))
            except:
                pass
        
        if not clickable_elements:
            print("❌ 未找到可点击的元素")
            return
        
        # 7. 显示可点击元素供选择
        print("\n🖱️ 可点击的元素:")
        for i, (element, desc) in enumerate(clickable_elements):
            print(f"   {i+1}. {desc}")
        
        # 8. 用户选择要点击的元素
        try:
            choice = int(input(f"请选择要点击的元素 (1-{len(clickable_elements)}): ")) - 1
            if 0 <= choice < len(clickable_elements):
                target_element, target_desc = clickable_elements[choice]
            else:
                print("❌ 选择无效")
                return
        except ValueError:
            print("❌ 输入无效")
            return
        
        # 9. 倒计时并点击
        print(f"\n⏰ 将在5秒后点击: {target_desc}")
        print(f"⚡ 使用优化的提前时间: {optimized_advance:.1f}ms")
        
        for i in range(5, 0, -1):
            print(f"\r倒计时: {i}秒", end="", flush=True)
            time.sleep(1)
        
        print(f"\n🎯 开始监控...")
        
        # 10. 点击前开始监控
        monitor.start_monitoring()
        
        # 11. 点击元素
        print(f"🖱️ 点击: {target_desc}")
        click_time = datetime.now()
        target_element.click()
        
        # 12. 持续监控
        print("📡 正在监控网络请求...")
        print("按 Ctrl+C 或等待30秒结束监控")
        
        try:
            time.sleep(30)  # 监控30秒
        except KeyboardInterrupt:
            print("\n⏹️ 用户中断监控")
        
        # 13. 停止监控并保存数据
        captured_requests = monitor.stop_monitoring()
        
        # 14. 分析和保存结果
        result_data = {
            'test_info': {
                'timestamp': datetime.now().isoformat(),
                'target_url': test_url,
                'clicked_element': target_desc,
                'click_time': click_time.isoformat(),
                'ping_latency_ms': ping_latency,
                'optimized_advance_ms': optimized_advance
            },
            'captured_requests': captured_requests,
            'summary': {
                'total_requests': len(captured_requests),
                'important_requests': [
                    req for req in captured_requests 
                    if any(keyword in req['url'].lower() for keyword in ['apply', 'submit', 'post', 'api'])
                ]
            }
        }
        
        # 15. 保存数据
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"click_crawl_data_{timestamp}.json"
        filepath = project_root / "data" / filename
        filepath.parent.mkdir(exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(result_data, f, ensure_ascii=False, indent=2)
        
        print(f"\n📊 测试结果:")
        print(f"   🖱️ 点击时间: {click_time.strftime('%H:%M:%S.%f')[:-3]}")
        print(f"   📡 捕获请求: {len(captured_requests)} 个")
        print(f"   🎯 重要请求: {len(result_data['summary']['important_requests'])} 个")
        print(f"   💾 数据文件: {filename}")
        
        # 显示重要请求
        if result_data['summary']['important_requests']:
            print(f"\n🎯 重要请求列表:")
            for req in result_data['summary']['important_requests'][:5]:
                print(f"   {req['status']} {req['method']} {req['url'][:80]}...")
        
    except Exception as e:
        print(f"❌ 测试过程出错: {e}")
        
    finally:
        monitor.stop_monitoring()
        driver.quit()
        print("✅ 浏览器已关闭")


if __name__ == "__main__":
    test_click_then_crawl() 