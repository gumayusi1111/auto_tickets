#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
网络分析测试脚本
分析抓包数据和网络延迟
"""

import sys
import os
import time
import requests

# 添加项目根目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.join(current_dir, '..')
sys.path.insert(0, project_root)

from src.weverse.operations.login_handler import measure_network_latency, analyze_captured_requests


def test_network_latency():
    """测试网络延迟"""
    print("🌐 测试网络延迟...")
    print("=" * 50)
    
    # 测试到各个服务器的延迟
    test_servers = [
        ("Weverse主站", "https://weverse.io"),
        ("Naver API", "https://global.apis.naver.com"),
        ("账户API", "https://accountapi.weverse.io"),
        ("CDN服务器", "https://cdn-v2pstatic.weverse.io"),
    ]
    
    latencies = []
    
    for name, url in test_servers:
        try:
            print(f"\n📡 测试 {name}: {url}")
            
            # 测试多次取平均值
            times = []
            for i in range(3):
                start_time = time.time()
                response = requests.head(url, timeout=5)
                latency = (time.time() - start_time) * 1000
                times.append(latency)
                print(f"   第{i+1}次: {latency:.0f}ms")
            
            avg_latency = sum(times) / len(times)
            latencies.append(avg_latency)
            print(f"   平均延迟: {avg_latency:.0f}ms")
            
        except Exception as e:
            print(f"   ❌ 测试失败: {e}")
    
    if latencies:
        overall_avg = sum(latencies) / len(latencies)
        print(f"\n📊 总体平均延迟: {overall_avg:.0f}ms")
        
        # 计算网络路径分析
        print(f"\n🛣️ 网络路径分析:")
        print(f"   上海 -> 日本VPS: ~30-50ms")
        print(f"   日本VPS -> 韩国服务器: ~20-40ms") 
        print(f"   总往返时间: ~{overall_avg:.0f}ms")
        
        # 建议的优化策略
        preclick_time = overall_avg / 1000 * 0.8
        print(f"\n⚡ 优化建议:")
        print(f"   提前点击时间: {preclick_time:.2f}秒")
        print(f"   高频检测间隔: 0.05秒")
        print(f"   超时时间设置: 15秒")
        
        return overall_avg / 1000
    
    return None


def test_captured_data_analysis():
    """分析抓包数据"""
    print("\n📊 分析抓包数据...")
    print("=" * 50)
    
    # 查找最新的抓包文件
    data_dir = "/Users/wenbai/Desktop/chajian/auto/data"
    json_files = []
    
    try:
        for filename in os.listdir(data_dir):
            if filename.endswith('.json') and 'captured_requests' in filename:
                json_files.append(os.path.join(data_dir, filename))
        
        if not json_files:
            print("❌ 未找到抓包数据文件")
            return None
        
        # 使用最新的文件
        latest_file = max(json_files, key=os.path.getmtime)
        print(f"📁 分析文件: {os.path.basename(latest_file)}")
        
        # 分析抓包数据
        analysis = analyze_captured_requests(latest_file)
        
        if analysis:
            print(f"\n📈 分析结果:")
            print(f"   POST请求总数: {analysis['total_post_requests']}")
            print(f"   需要认证: {'是' if analysis['authentication_required'] else '否'}")
            print(f"   CSRF令牌数: {len(analysis['csrf_tokens'])}")
            print(f"   会话Cookie: {len(analysis['session_cookies'])}")
            print(f"   API端点数: {len(analysis['api_endpoints'])}")
            print(f"   直接POST可行: {'是' if analysis['direct_post_feasible'] else '否'}")
            
            # 详细分析API端点
            if analysis['api_endpoints']:
                print(f"\n🔗 API端点分析:")
                for i, endpoint in enumerate(analysis['api_endpoints'], 1):
                    print(f"   {i}. {endpoint}")
                    
                    # 判断端点类型
                    if 'login' in endpoint.lower():
                        print(f"      -> 登录相关")
                    elif 'auth' in endpoint.lower():
                        print(f"      -> 认证相关")
                    elif 'api' in endpoint.lower():
                        print(f"      -> API调用")
                    elif 'submit' in endpoint.lower():
                        print(f"      -> 提交相关")
            
            return analysis
        
    except Exception as e:
        print(f"❌ 分析失败: {e}")
        return None


def test_optimization_strategy():
    """测试优化策略"""
    print("\n🚀 优化策略测试...")
    print("=" * 50)
    
    # 测试网络延迟
    avg_latency = test_network_latency()
    
    if avg_latency:
        print(f"\n💡 基于延迟的优化策略:")
        
        # 1. 智能等待策略
        check_interval = min(0.05, avg_latency / 4)  # 检测间隔不超过延迟的1/4
        print(f"   智能等待检测间隔: {check_interval:.3f}秒")
        
        # 2. 预测性点击
        preclick_time = avg_latency * 0.8
        print(f"   预测性点击提前时间: {preclick_time:.3f}秒")
        
        # 3. 超时设置
        timeout = max(10, avg_latency * 50)  # 至少10秒，或延迟的50倍
        print(f"   建议超时时间: {timeout:.1f}秒")
        
        # 4. 并发优化
        print(f"   并发请求建议: 3-5个")
        print(f"   连接池大小: 10")
        
        return {
            'avg_latency': avg_latency,
            'check_interval': check_interval,
            'preclick_time': preclick_time,
            'timeout': timeout
        }
    
    return None


def main():
    """主函数"""
    print("🔬 网络分析和优化测试")
    print("=" * 60)
    
    try:
        # 1. 测试网络延迟
        latency_result = test_network_latency()
        
        # 2. 分析抓包数据
        analysis_result = test_captured_data_analysis()
        
        # 3. 生成优化策略
        optimization_result = test_optimization_strategy()
        
        # 4. 综合建议
        print(f"\n🎯 综合优化建议:")
        print("=" * 50)
        
        if latency_result:
            print(f"✅ 网络延迟: {latency_result*1000:.0f}ms - 需要优化等待机制")
        else:
            print(f"❌ 网络延迟测试失败")
        
        if analysis_result:
            if analysis_result['direct_post_feasible']:
                print(f"✅ 直接POST: 可行 - 可以考虑绕过浏览器")
            else:
                print(f"❌ 直接POST: 困难 - 建议继续使用浏览器自动化")
        else:
            print(f"❌ 抓包数据分析失败")
        
        if optimization_result:
            print(f"✅ 优化策略: 已生成 - 可显著提升响应速度")
        else:
            print(f"❌ 优化策略生成失败")
        
        print(f"\n🚀 下一步建议:")
        print(f"   1. 应用优化后的login_handler.py")
        print(f"   2. 测试实际登录流程")
        print(f"   3. 监控性能改善情况")
        print(f"   4. 考虑是否实施直接API调用")
        
    except KeyboardInterrupt:
        print(f"\n👋 用户中断测试")
    except Exception as e:
        print(f"❌ 测试过程中出错: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 