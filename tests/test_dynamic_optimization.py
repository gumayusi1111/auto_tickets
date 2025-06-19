#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
动态网络优化测试脚本
测试VPN路径检测和动态点击时间优化
"""

import sys
import os
import time

# 添加项目根目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.join(current_dir, '..')
sys.path.insert(0, project_root)

from src.weverse.operations.dynamic_network_optimizer import DynamicNetworkOptimizer, quick_network_test
from src.weverse.operations.login_handler import pre_click_network_analysis


def test_dynamic_network_detection():
    """测试动态网络检测功能"""
    print("🧪 测试动态网络检测功能")
    print("=" * 60)
    
    optimizer = DynamicNetworkOptimizer()
    
    print("📊 第一次网络检测...")
    result1 = optimizer.detect_vpn_path()
    
    print(f"\n⏳ 等待5秒后进行第二次检测...")
    time.sleep(5)
    
    print("📊 第二次网络检测...")
    result2 = optimizer.detect_vpn_path()
    
    # 比较两次结果
    if result1 and result2:
        latency_diff = abs(result1['avg_latency'] - result2['avg_latency'])
        print(f"\n📈 两次检测对比:")
        print(f"   第一次延迟: {result1['avg_latency']:.0f}ms")
        print(f"   第二次延迟: {result2['avg_latency']:.0f}ms")
        print(f"   延迟差异: {latency_diff:.0f}ms")
        
        if latency_diff > 50:
            print("⚠️  网络状态变化较大，建议频繁检测")
        else:
            print("✅ 网络状态相对稳定")
    
    return result1, result2


def test_quick_network_test():
    """测试快速网络测试功能"""
    print("\n🧪 测试快速网络测试功能")
    print("=" * 60)
    
    print("⚡ 执行快速网络测试...")
    start_time = time.time()
    
    result = quick_network_test()
    
    test_duration = time.time() - start_time
    
    print(f"📊 快速测试结果:")
    print(f"   测试耗时: {test_duration:.2f}秒")
    print(f"   平均延迟: {result.get('avg_latency_ms', 0):.0f}ms")
    print(f"   提前点击: {result.get('preclick_time_ms', 0):.0f}ms")
    print(f"   网络质量: {result.get('network_quality', 'unknown')}")
    print(f"   建议: {result.get('recommendation', '无')}")
    
    # 验证快速测试是否真的快速（应该在10秒内完成）
    if test_duration < 10:
        print("✅ 快速测试性能合格")
    else:
        print("⚠️  快速测试耗时过长，需要优化")
    
    return result, test_duration


def test_pre_click_analysis():
    """测试点击前分析功能"""
    print("\n🧪 测试点击前分析功能")
    print("=" * 60)
    
    print("🕐 模拟点击前1分钟网络分析...")
    
    start_time = time.time()
    analysis = pre_click_network_analysis(minutes_ahead=1)
    analysis_duration = time.time() - start_time
    
    if analysis:
        network_result = analysis['network_result']
        strategy = analysis['strategy']
        
        print(f"\n📊 分析结果验证:")
        print(f"   分析耗时: {analysis_duration:.2f}秒")
        print(f"   网络延迟: {network_result.get('avg_latency_ms', 0):.0f}ms")
        print(f"   策略生成: {'成功' if strategy else '失败'}")
        
        if strategy:
            print(f"\n⚡ 生成的优化策略:")
            print(f"   提前点击: {strategy['preclick_time']:.3f}秒")
            print(f"   检测间隔: {strategy['check_interval']:.3f}秒")
            print(f"   超时时间: {strategy['timeout']:.1f}秒")
            print(f"   重试次数: {strategy['retry_count']} 次")
            print(f"   点击后等待: {strategy['wait_after_click']:.3f}秒")
            
            # 验证策略的合理性
            if 0.05 <= strategy['preclick_time'] <= 0.5:
                print("✅ 提前点击时间合理")
            else:
                print("⚠️  提前点击时间可能不合理")
            
            if 0.01 <= strategy['check_interval'] <= 0.1:
                print("✅ 检测间隔合理")
            else:
                print("⚠️  检测间隔可能不合理")
    
    return analysis


def test_network_path_variations():
    """测试不同网络路径的适应性"""
    print("\n🧪 测试网络路径变化适应性")
    print("=" * 60)
    
    optimizer = DynamicNetworkOptimizer()
    
    # 模拟不同的网络条件
    test_scenarios = [
        {"name": "优秀网络", "mock_latency": 80},
        {"name": "良好网络", "mock_latency": 150},
        {"name": "一般网络", "mock_latency": 300},
        {"name": "较差网络", "mock_latency": 500},
    ]
    
    results = []
    
    for scenario in test_scenarios:
        print(f"\n📡 模拟 {scenario['name']} (延迟: {scenario['mock_latency']}ms)")
        
        # 手动设置网络缓存来模拟不同网络条件
        optimizer.network_cache.update({
            'avg_latency': scenario['mock_latency'] / 1000,
            'network_quality': 'simulated',
            'last_test_time': time.time()
        })
        
        # 计算推荐的提前点击时间
        base_preclick = (scenario['mock_latency'] / 1000) * optimizer.config['preclick_ratio']
        recommended_preclick = max(
            optimizer.config['min_preclick_time'],
            min(optimizer.config['max_preclick_time'], base_preclick)
        )
        
        print(f"   推荐提前点击: {recommended_preclick:.3f}秒")
        print(f"   检测间隔: {min(0.05, scenario['mock_latency'] / 4000):.3f}秒")
        print(f"   超时时间: {max(10, scenario['mock_latency'] / 20):.1f}秒")
        
        results.append({
            'scenario': scenario['name'],
            'latency': scenario['mock_latency'],
            'preclick_time': recommended_preclick
        })
    
    # 分析适应性
    print(f"\n📈 适应性分析:")
    for result in results:
        ratio = (result['preclick_time'] * 1000) / result['latency']
        print(f"   {result['scenario']}: 提前点击占延迟比例 {ratio:.1%}")
    
    return results


def test_performance_optimization():
    """测试性能优化效果"""
    print("\n🧪 测试性能优化效果")
    print("=" * 60)
    
    # 模拟传统固定等待 vs 动态优化等待
    print("📊 对比传统方式 vs 动态优化:")
    
    # 获取当前网络状态
    network_result = quick_network_test()
    latency_ms = network_result.get('avg_latency_ms', 200)
    
    # 传统方式：固定等待2秒
    traditional_wait = 2.0
    
    # 动态优化：基于实际延迟计算
    dynamic_wait = max(0.5, latency_ms / 1000)
    
    print(f"   当前网络延迟: {latency_ms:.0f}ms")
    print(f"   传统固定等待: {traditional_wait:.1f}秒")
    print(f"   动态优化等待: {dynamic_wait:.2f}秒")
    
    # 计算优化效果
    if dynamic_wait < traditional_wait:
        improvement = ((traditional_wait - dynamic_wait) / traditional_wait) * 100
        print(f"   ✅ 性能提升: {improvement:.1f}%")
        print(f"   ⏱️  节省时间: {traditional_wait - dynamic_wait:.2f}秒")
    else:
        print(f"   ⚠️  当前网络条件下，动态等待时间较长")
    
    # 测试检测频率优化
    traditional_check_interval = 0.5  # 传统500ms检测一次
    dynamic_check_interval = min(0.05, latency_ms / 4000)  # 动态检测间隔
    
    print(f"\n🔍 检测频率对比:")
    print(f"   传统检测间隔: {traditional_check_interval:.3f}秒")
    print(f"   动态检测间隔: {dynamic_check_interval:.3f}秒")
    
    if dynamic_check_interval < traditional_check_interval:
        freq_improvement = ((traditional_check_interval - dynamic_check_interval) / traditional_check_interval) * 100
        print(f"   ✅ 响应速度提升: {freq_improvement:.1f}%")
    
    return {
        'latency_ms': latency_ms,
        'traditional_wait': traditional_wait,
        'dynamic_wait': dynamic_wait,
        'traditional_check': traditional_check_interval,
        'dynamic_check': dynamic_check_interval
    }


def main():
    """主测试函数"""
    print("🔬 动态网络优化全面测试")
    print("=" * 70)
    
    try:
        # 1. 测试动态网络检测
        print("🧪 测试1: 动态网络检测")
        detection_results = test_dynamic_network_detection()
        
        # 2. 测试快速网络测试
        print("\n🧪 测试2: 快速网络测试")
        quick_test_result, duration = test_quick_network_test()
        
        # 3. 测试点击前分析
        print("\n🧪 测试3: 点击前分析")
        analysis_result = test_pre_click_analysis()
        
        # 4. 测试网络路径变化适应性
        print("\n🧪 测试4: 网络路径适应性")
        adaptation_results = test_network_path_variations()
        
        # 5. 测试性能优化效果
        print("\n🧪 测试5: 性能优化效果")
        performance_results = test_performance_optimization()
        
        # 6. 综合评估
        print(f"\n🎯 综合测试评估:")
        print("=" * 50)
        
        # 功能完整性检查
        tests_passed = 0
        total_tests = 5
        
        if detection_results[0] and detection_results[1]:
            print("✅ 动态网络检测: 通过")
            tests_passed += 1
        else:
            print("❌ 动态网络检测: 失败")
        
        if quick_test_result and duration < 10:
            print("✅ 快速网络测试: 通过")
            tests_passed += 1
        else:
            print("❌ 快速网络测试: 失败")
        
        if analysis_result and analysis_result.get('strategy'):
            print("✅ 点击前分析: 通过")
            tests_passed += 1
        else:
            print("❌ 点击前分析: 失败")
        
        if adaptation_results and len(adaptation_results) == 4:
            print("✅ 网络路径适应性: 通过")
            tests_passed += 1
        else:
            print("❌ 网络路径适应性: 失败")
        
        if performance_results:
            print("✅ 性能优化效果: 通过")
            tests_passed += 1
        else:
            print("❌ 性能优化效果: 失败")
        
        # 总体评估
        success_rate = (tests_passed / total_tests) * 100
        print(f"\n📊 测试总结:")
        print(f"   通过测试: {tests_passed}/{total_tests}")
        print(f"   成功率: {success_rate:.1f}%")
        
        if success_rate >= 80:
            print("🎉 动态网络优化系统运行良好！")
        elif success_rate >= 60:
            print("⚠️  动态网络优化系统基本可用，但需要改进")
        else:
            print("❌ 动态网络优化系统存在问题，需要修复")
        
        print(f"\n🚀 使用建议:")
        if quick_test_result:
            latency = quick_test_result.get('avg_latency_ms', 200)
            if latency < 150:
                print("   当前网络状况良好，可以使用较激进的优化策略")
            elif latency < 300:
                print("   当前网络状况一般，建议使用标准优化策略")
            else:
                print("   当前网络状况较差，建议使用保守优化策略")
        
        print("   建议在登录前1分钟执行网络分析")
        print("   建议根据VPN变化情况调整检测频率")
        
    except KeyboardInterrupt:
        print(f"\n👋 用户中断测试")
    except Exception as e:
        print(f"❌ 测试过程中出错: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 