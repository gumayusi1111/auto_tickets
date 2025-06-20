#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
enhanced_monitor.py
增强网络监控模块 - 捕获提交后的所有GET/POST请求
"""

import time
import json
import threading
from datetime import datetime
from typing import Dict, List, Any, Optional
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from concurrent.futures import ThreadPoolExecutor

class EnhancedNetworkMonitor:
    """增强网络监控器"""
    
    def __init__(self, driver):
        self.driver = driver
        self.captured_requests = []
        self.monitoring = False
        self.monitor_thread = None
        self.start_time = None
        
    def start_monitoring(self):
        """开始网络监控"""
        print("📡 启动增强网络监控...")
        self.captured_requests = []
        self.monitoring = True
        self.start_time = time.time()
        
        # 启动监控线程
        self.monitor_thread = threading.Thread(target=self._monitor_network)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
    
    def stop_monitoring(self) -> List[Dict[str, Any]]:
        """停止网络监控并返回捕获的请求"""
        print("📡 停止网络监控...")
        self.monitoring = False
        
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2)
        
        return self.captured_requests.copy()
    
    def get_captured_requests(self) -> List[Dict[str, Any]]:
        """获取已捕获的请求（不停止监控）"""
        return self.captured_requests.copy()
    
    def capture_post_submit_requests(self, duration: float = 10.0) -> Dict[str, Any]:
        """
        捕获提交后的所有网络请求
        
        Args:
            duration: 监控时长（秒）
        
        Returns:
            捕获结果
        """
        print(f"🌐 开始捕获提交后网络请求 ({duration}秒)...")
        capture_start = time.time()
        
        # 获取浏览器日志
        requests = self._capture_browser_logs(duration)
        
        # 分析请求类型
        analysis = self._analyze_requests(requests)
        
        capture_time = time.time() - capture_start
        
        result = {
            'capture_duration': capture_time,
            'total_requests': len(requests),
            'requests': requests,
            'analysis': analysis,
            'timestamp': datetime.now().isoformat()
        }
        
        print(f"📊 网络捕获完成:")
        print(f"   总请求数: {len(requests)}")
        print(f"   GET请求: {analysis['get_count']}")
        print(f"   POST请求: {analysis['post_count']}")
        print(f"   关键请求: {analysis['important_count']}")
        print(f"   捕获时长: {capture_time:.2f}秒")
        
        return result
    
    def _capture_browser_logs(self, duration: float) -> List[Dict[str, Any]]:
        """从浏览器日志中捕获网络请求"""
        requests = []
        end_time = time.time() + duration
        
        try:
            while time.time() < end_time:
                # 获取性能日志
                logs = self.driver.get_log('performance')
                
                for log in logs:
                    try:
                        message = json.loads(log['message'])
                        if message['message']['method'] in ['Network.responseReceived', 'Network.requestWillBeSent']:
                            request_data = self._extract_request_info(message, log['timestamp'])
                            if request_data:
                                requests.append(request_data)
                    except:
                        continue
                
                time.sleep(0.1)  # 每100ms检查一次
                
        except Exception as e:
            print(f"⚠️ 日志捕获异常: {e}")
        
        return requests
    
    def _extract_request_info(self, message: Dict, timestamp: int) -> Optional[Dict[str, Any]]:
        """提取请求信息"""
        try:
            msg = message['message']
            
            if msg['method'] == 'Network.requestWillBeSent':
                request = msg['params']['request']
                return {
                    'type': 'request',
                    'method': request['method'],
                    'url': request['url'],
                    'headers': request.get('headers', {}),
                    'postData': request.get('postData', ''),
                    'timestamp': timestamp,
                    'datetime': datetime.fromtimestamp(timestamp / 1000).isoformat()
                }
            
            elif msg['method'] == 'Network.responseReceived':
                response = msg['params']['response']
                return {
                    'type': 'response',
                    'method': response.get('requestHeaders', {}).get(':method', 'GET'),
                    'url': response['url'],
                    'status': response['status'],
                    'statusText': response['statusText'],
                    'headers': response.get('headers', {}),
                    'timestamp': timestamp,
                    'datetime': datetime.fromtimestamp(timestamp / 1000).isoformat()
                }
                
        except Exception as e:
            return None
        
        return None
    
    def _analyze_requests(self, requests: List[Dict[str, Any]]) -> Dict[str, Any]:
        """分析请求类型和重要性"""
        analysis = {
            'get_count': 0,
            'post_count': 0,
            'put_count': 0,
            'delete_count': 0,
            'important_count': 0,
            'important_requests': [],
            'api_requests': [],
            'static_requests': []
        }
        
        important_keywords = [
            'apply', 'submit', 'join', 'register', 'signup',
            '신청', '참여', '등록', '제출', '가입',
            'api', 'ajax', 'json', 'form'
        ]
        
        static_extensions = ['.css', '.js', '.png', '.jpg', '.gif', '.ico', '.woff']
        
        for req in requests:
            method = req.get('method', 'GET').upper()
            url = req.get('url', '').lower()
            
            # 统计方法类型
            if method == 'GET':
                analysis['get_count'] += 1
            elif method == 'POST':
                analysis['post_count'] += 1
            elif method == 'PUT':
                analysis['put_count'] += 1
            elif method == 'DELETE':
                analysis['delete_count'] += 1
            
            # 判断是否为重要请求
            is_important = False
            for keyword in important_keywords:
                if keyword in url:
                    is_important = True
                    break
            
            if is_important or method in ['POST', 'PUT', 'DELETE']:
                analysis['important_count'] += 1
                analysis['important_requests'].append(req)
            
            # 分类请求
            if any(ext in url for ext in static_extensions):
                analysis['static_requests'].append(req)
            elif 'api' in url or method != 'GET':
                analysis['api_requests'].append(req)
        
        return analysis
    
    def _monitor_network(self):
        """网络监控主循环"""
        while self.monitoring:
            try:
                # 获取性能日志
                logs = self.driver.get_log('performance')
                
                for log in logs:
                    try:
                        message = json.loads(log['message'])
                        if message['message']['method'] in ['Network.responseReceived', 'Network.requestWillBeSent']:
                            request_data = self._extract_request_info(message, log['timestamp'])
                            if request_data:
                                self.captured_requests.append(request_data)
                    except:
                        continue
                
                time.sleep(0.1)
            except Exception as e:
                # 静默处理错误，避免刷屏
                time.sleep(0.5)
                continue

def capture_all_post_submit_requests(driver, duration: float = 10.0) -> Dict[str, Any]:
    """
    捕获提交后的所有网络请求
    
    Args:
        driver: WebDriver实例
        duration: 监控时长
    
    Returns:
        捕获结果
    """
    monitor = EnhancedNetworkMonitor(driver)
    return monitor.capture_post_submit_requests(duration) 