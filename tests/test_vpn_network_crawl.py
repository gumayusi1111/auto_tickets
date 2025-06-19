#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_vpn_network_crawl.py
VPN网络延迟检测、页面爬取和请求监控综合测试
"""

import sys
import os
import json
import time
import requests
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
import statistics
from concurrent.futures import ThreadPoolExecutor, as_completed

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.weverse.browser.setup import setup_driver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities


def test_vpn_network_latency(duration: int = 15) -> Dict[str, Any]:
    """
    优化的VPN网络延迟检测 - 专门针对韩国Weverse服务器
    """
    print(f"🌐 开始 {duration} 秒VPN网络延迟检测...")
    
    # 测试目标：使用同一地理位置的多个端点
    test_endpoints = [
        "https://www.weverse.io",
        "https://weverse.io",
        "https://api.weverse.io",
        "https://static.weverse.io"
    ]
    
    latencies = []
    successful_tests = 0
    failed_tests = 0
    start_time = time.time()
    
    def single_latency_test(url: str) -> Optional[float]:
        """单次延迟测试"""
        try:
            test_start = time.perf_counter()
            response = requests.head(
                url, 
                timeout=3, 
                allow_redirects=False,
                headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'}
            )
            test_end = time.perf_counter()
            latency = (test_end - test_start) * 1000  # 转换为毫秒
            return latency
        except:
            return None
    
    print("🎯 测试端点:", ", ".join(test_endpoints))
    
    with ThreadPoolExecutor(max_workers=4) as executor:
        while time.time() - start_time < duration:
            # 对每个端点并行测试
            futures = {
                executor.submit(single_latency_test, url): url 
                for url in test_endpoints
            }
            
            for future in as_completed(futures, timeout=5):
                url = futures[future]
                try:
                    latency_ms = future.result()
                    if latency_ms is not None:
                        latencies.append(latency_ms)
                        successful_tests += 1
                        
                        # 实时显示最新结果
                        if successful_tests % 8 == 0:
                            recent_avg = sum(latencies[-8:]) / min(8, len(latencies))
                            print(f"\r📊 成功测试 {successful_tests} 次, 最近平均: {recent_avg:.1f}ms", end="", flush=True)
                    else:
                        failed_tests += 1
                except:
                    failed_tests += 1
            
            time.sleep(0.2)  # 适当间隔
    
    print()  # 换行
    
    if not latencies or len(latencies) < 5:
        print("⚠️ VPN延迟测试数据不足")
        return {
            'avg_ms': 300,
            'min_ms': 150, 
            'max_ms': 800,
            'std_ms': 100,
            'recommended_advance_ms': 400,
            'confidence': 'low',
            'test_count': 0
        }
    
    # 数据处理：去除异常值
    latencies.sort()
    # 去掉最高和最低20%的异常值
    trim_count = max(1, int(len(latencies) * 0.2))
    trimmed_latencies = latencies[trim_count:-trim_count] if len(latencies) > 5 else latencies
    
    stats = {
        'avg_ms': statistics.mean(trimmed_latencies),
        'min_ms': min(trimmed_latencies),
        'max_ms': max(trimmed_latencies),
        'std_ms': statistics.stdev(trimmed_latencies) if len(trimmed_latencies) > 1 else 0,
        'p95_ms': trimmed_latencies[int(len(trimmed_latencies) * 0.95)] if len(trimmed_latencies) > 10 else max(trimmed_latencies),
        'test_count': len(latencies),
        'success_rate': successful_tests / (successful_tests + failed_tests) * 100,
        'confidence': 'high' if len(latencies) >= 20 else 'medium' if len(latencies) >= 10 else 'low'
    }
    
    # 基于你提供的实际数据优化计算
    # 你的数据显示：36ms-1.32s，我们需要更保守的策略
    base_advance = stats['avg_ms']
    std_buffer = 2 * stats['std_ms']
    safety_margin = 100  # 增加安全边距到100ms
    
    # 考虑p95延迟，确保95%的情况下都能成功
    p95_buffer = stats['p95_ms'] - stats['avg_ms']
    
    recommended_advance_ms = base_advance + max(std_buffer, p95_buffer) + safety_margin
    
    # 根据你的实际数据，限制在200ms-2000ms范围内
    stats['recommended_advance_ms'] = max(200, min(2000, recommended_advance_ms))
    
    print(f"📊 VPN网络延迟检测结果:")
    print(f"   ✅ 成功测试: {stats['test_count']} 次")
    print(f"   📈 成功率: {stats['success_rate']:.1f}%")
    print(f"   ⚡ 平均延迟: {stats['avg_ms']:.1f}ms")
    print(f"   🚀 最快延迟: {stats['min_ms']:.1f}ms")
    print(f"   🐌 最慢延迟: {stats['max_ms']:.1f}ms")
    print(f"   📊 95%延迟: {stats['p95_ms']:.1f}ms")
    print(f"   📏 标准差: {stats['std_ms']:.1f}ms")
    print(f"   ⚡ 推荐提前: {stats['recommended_advance_ms']:.1f}ms")
    print(f"   🎯 置信度: {stats['confidence']}")
    
    return stats


def setup_browser_with_network_monitoring():
    """设置带网络监控的浏览器"""
    print("🌐 设置浏览器网络监控...")
    
    # 启用性能日志记录
    caps = DesiredCapabilities.CHROME
    caps['goog:loggingPrefs'] = {'performance': 'ALL'}
    
    driver = setup_driver(headless=False)
    
    # 启用网络域
    driver.execute_cdp_cmd('Network.enable', {})
    driver.execute_cdp_cmd('Page.enable', {})
    
    print("✅ 浏览器网络监控已启用")
    return driver


def capture_network_requests(driver, duration: int = 30) -> List[Dict]:
    """捕获网络请求"""
    print(f"🕷️ 开始捕获网络请求 ({duration}秒)...")
    
    requests_data = []
    start_time = time.time()
    
    try:
        while time.time() - start_time < duration:
            # 获取性能日志
            logs = driver.get_log('performance')
            
            for log in logs:
                message = json.loads(log['message'])
                if message['message']['method'] == 'Network.responseReceived':
                    response = message['message']['params']['response']
                    request_data = {
                        'url': response['url'],
                        'status': response['status'],
                        'method': response.get('method', 'unknown'),
                        'headers': response.get('headers', {}),
                        'timing': response.get('timing', {}),
                        'timestamp': datetime.now().isoformat()
                    }
                    requests_data.append(request_data)
                    
                    # 实时显示捕获的请求
                    if len(requests_data) % 10 == 0:
                        print(f"\r📡 已捕获 {len(requests_data)} 个网络请求", end="", flush=True)
            
            time.sleep(0.1)
            
    except Exception as e:
        print(f"⚠️ 网络监控异常: {e}")
    
    print(f"\n✅ 网络请求捕获完成，共 {len(requests_data)} 个请求")
    return requests_data


def crawl_page_content(driver, url: str) -> Dict[str, Any]:
    """爬取页面内容"""
    print(f"🕷️ 开始爬取页面: {url}")
    
    try:
        # 访问页面
        driver.get(url)
        time.sleep(3)  # 等待页面加载
        
        page_data = {
            'url': url,
            'title': driver.title,
            'current_url': driver.current_url,
            'page_source_length': len(driver.page_source),
            'timestamp': datetime.now().isoformat()
        }
        
        # 尝试获取特定元素
        try:
            # 查找登录相关元素
            wait = WebDriverWait(driver, 5)
            login_elements = driver.find_elements(By.XPATH, "//*[contains(text(), '로그인') or contains(text(), '登录') or contains(text(), 'Login')]")
            page_data['login_elements_count'] = len(login_elements)
            
            # 查找申请/报名相关元素
            apply_elements = driver.find_elements(By.XPATH, "//*[contains(text(), '신청') or contains(text(), '申请') or contains(text(), 'Apply')]")
            page_data['apply_elements_count'] = len(apply_elements)
            
            # 获取所有链接
            links = driver.find_elements(By.TAG_NAME, 'a')
            page_data['total_links'] = len(links)
            
            # 获取所有按钮
            buttons = driver.find_elements(By.TAG_NAME, 'button')
            page_data['total_buttons'] = len(buttons)
            
        except TimeoutException:
            page_data['elements_error'] = "页面元素加载超时"
        
        print(f"✅ 页面爬取完成:")
        print(f"   📄 标题: {page_data['title']}")
        print(f"   🔗 链接数: {page_data.get('total_links', 0)}")
        print(f"   🖱️ 按钮数: {page_data.get('total_buttons', 0)}")
        print(f"   🔐 登录元素: {page_data.get('login_elements_count', 0)}")
        print(f"   📝 申请元素: {page_data.get('apply_elements_count', 0)}")
        
        return page_data
        
    except Exception as e:
        print(f"❌ 页面爬取失败: {e}")
        return {'url': url, 'error': str(e), 'timestamp': datetime.now().isoformat()}


def save_crawl_data(data: Dict[str, Any], filename: str = None):
    """保存爬取数据到文件"""
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"crawl_data_{timestamp}.json"
    
    filepath = project_root / "data" / filename
    filepath.parent.mkdir(exist_ok=True)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"💾 数据已保存到: {filepath}")
    return filepath


def main():
    """主测试函数"""
    print("🧪 VPN网络延迟、页面爬取和请求监控综合测试")
    print("=" * 70)
    
    # 1. VPN网络延迟检测
    print("\n📡 第1阶段: VPN网络延迟检测")
    print("-" * 40)
    latency_stats = test_vpn_network_latency(duration=15)
    
    # 2. 设置浏览器
    print("\n🌐 第2阶段: 启动浏览器")
    print("-" * 40)
    driver = None
    
    try:
        driver = setup_browser_with_network_monitoring()
        
        # 3. 页面爬取测试
        print("\n🕷️ 第3阶段: 页面爬取测试")
        print("-" * 40)
        
        test_urls = [
            "https://www.weverse.io",
            "https://weverse.io/nct127/notice"
        ]
        
        crawl_results = []
        for url in test_urls:
            page_data = crawl_page_content(driver, url)
            crawl_results.append(page_data)
        
        # 4. 网络请求监控
        print("\n📡 第4阶段: 网络请求监控")
        print("-" * 40)
        print("🔄 访问Weverse主页进行网络监控...")
        
        # 访问页面并监控网络请求
        driver.get("https://www.weverse.io")
        network_requests = capture_network_requests(driver, duration=20)
        
        # 5. 整合所有数据
        print("\n💾 第5阶段: 数据整合保存")
        print("-" * 40)
        
        comprehensive_data = {
            'test_info': {
                'timestamp': datetime.now().isoformat(),
                'test_duration_seconds': 60,
                'vpn_status': 'active'
            },
            'network_latency': latency_stats,
            'page_crawl_results': crawl_results,
            'network_requests': network_requests,
            'summary': {
                'total_pages_crawled': len(crawl_results),
                'total_network_requests': len(network_requests),
                'avg_latency_ms': latency_stats['avg_ms'],
                'recommended_advance_ms': latency_stats['recommended_advance_ms']
            }
        }
        
        # 保存数据
        saved_file = save_crawl_data(comprehensive_data)
        
        # 6. 结果分析
        print("\n📊 测试结果总结")
        print("=" * 50)
        print(f"✅ VPN延迟检测: 平均 {latency_stats['avg_ms']:.1f}ms")
        print(f"✅ 页面爬取: {len(crawl_results)} 个页面")
        print(f"✅ 网络请求: {len(network_requests)} 个请求")
        print(f"✅ 推荐提前时间: {latency_stats['recommended_advance_ms']:.1f}ms")
        print(f"📁 数据文件: {saved_file.name}")
        
        # 分析你提供的延迟数据
        print(f"\n🔍 基于你的实际数据分析:")
        print(f"   - 你的延迟范围: 36ms - 1.32s")
        print(f"   - 检测到的延迟: {latency_stats['min_ms']:.0f}ms - {latency_stats['max_ms']:.0f}ms")
        if latency_stats['max_ms'] > 1000:
            print(f"   ⚠️  检测到高延迟，建议提前时间: {latency_stats['recommended_advance_ms']:.0f}ms")
        else:
            print(f"   ✅ 网络状况良好，提前时间: {latency_stats['recommended_advance_ms']:.0f}ms")
        
        print("\n🎊 所有测试完成!")
        print("📋 现在你可以查看保存的数据文件了解详细信息")
        
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}")
        
    finally:
        if driver:
            print("\n🔄 关闭浏览器...")
            driver.quit()
            print("✅ 浏览器已关闭")


if __name__ == "__main__":
    main() 