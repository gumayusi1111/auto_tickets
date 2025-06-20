#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
time_processor.py
时间处理模块 - 优化版本
"""

import re
import time
from datetime import datetime, timedelta
import pytz
from typing import Dict, List, Optional, Any, Tuple
import statistics
import requests
from concurrent.futures import ThreadPoolExecutor

# 导入延迟配置
try:
    from config.latency_config import get_latency_config, get_optimized_preclick_ms
    LATENCY_CONFIG_AVAILABLE = True
except ImportError:
    LATENCY_CONFIG_AVAILABLE = False
    print("⚠️ 延迟配置文件不可用，使用默认值")

# 导入新的VPN优化器
try:
    from ..vpn.shanghai_korea_optimizer import ShanghaiKoreaOptimizer
    VPN_OPTIMIZER_AVAILABLE = True
except ImportError:
    VPN_OPTIMIZER_AVAILABLE = False
    print("⚠️ VPN优化器不可用，将使用传统延迟检测")


def extract_time_info(content):
    """从内容中提取时间信息"""
    time_patterns = [
        r'(\d{4})년\s*(\d{1,2})월\s*(\d{1,2})일\s*(\d{1,2})시\s*(\d{1,2})분',  # 韩文时间格式
        r'(\d{4})-(\d{1,2})-(\d{1,2})\s+(\d{1,2}):(\d{1,2})',  # 标准时间格式
        r'(\d{1,2})월\s*(\d{1,2})일\s*(\d{1,2})시\s*(\d{1,2})분',  # 简化韩文格式
        r'(\d{1,2})/(\d{1,2})\s+(\d{1,2}):(\d{1,2})',  # 简化格式
        r'(\d{1,2}):(\d{2})\s*(?:KST|한국시간|韩国时间)',  # 韩国时间
        r'(\d{1,2}):(\d{2})\s*(?:CST|中国时间|北京时间)',  # 中国时间
    ]
    
    extracted_times = []
    
    for pattern in time_patterns:
        matches = re.findall(pattern, content)
        for match in matches:
            extracted_times.append(match)
    
    return extracted_times


def convert_to_china_time(korean_time_str):
    """将韩国时间转换为中国时间"""
    try:
        # 韩国时区
        korea_tz = pytz.timezone('Asia/Seoul')
        # 中国时区
        china_tz = pytz.timezone('Asia/Shanghai')
        
        # 解析韩国时间（假设是当前年份）
        current_year = datetime.now().year
        
        # 尝试不同的时间格式解析
        if len(korean_time_str) == 5:  # (月, 日, 时, 分)
            month, day, hour, minute = map(int, korean_time_str)
            korea_time = korea_tz.localize(datetime(current_year, month, day, hour, minute))
        elif len(korean_time_str) == 6:  # (年, 月, 日, 时, 分)
            year, month, day, hour, minute = map(int, korean_time_str)
            korea_time = korea_tz.localize(datetime(year, month, day, hour, minute))
        elif len(korean_time_str) == 2:  # (时, 分)
            hour, minute = map(int, korean_time_str)
            today = datetime.now().date()
            korea_time = korea_tz.localize(datetime.combine(today, datetime.min.time().replace(hour=hour, minute=minute)))
        else:
            return None
        
        # 转换为中国时间
        china_time = korea_time.astimezone(china_tz)
        return china_time
    except Exception as e:
        print(f"时间转换失败: {e}")
        return None


def calculate_time_difference(target_time):
    """计算距离目标时间的差值"""
    if not target_time:
        return None
    
    china_tz = pytz.timezone('Asia/Shanghai')
    current_time = datetime.now(china_tz)
    
    if target_time > current_time:
        diff = target_time - current_time
        return diff
    else:
        return timedelta(0)  # 已过期


def test_real_network_latency(duration: int = 30, test_url: str = "https://www.weverse.io") -> Dict[str, float]:
    """
    真实网络延迟动态检测
    
    Args:
        duration: 测试时长（秒）
        test_url: 测试URL
    
    Returns:
        真实延迟统计信息
    """
    print(f"🌐 开始 {duration} 秒真实网络延迟检测...")
    print(f"🎯 测试目标: {test_url}")
    
    latencies = []
    start_time = time.time()
    test_count = 0
    
    def single_latency_test():
        """单次延迟测试"""
        try:
            test_start = time.perf_counter()
            response = requests.head(test_url, timeout=5, allow_redirects=False)
            test_end = time.perf_counter()
            latency = test_end - test_start
            return latency * 1000  # 转换为毫秒
        except:
            return None
    
    # 并行测试提高准确性
    with ThreadPoolExecutor(max_workers=3) as executor:
        while time.time() - start_time < duration:
            # 提交多个并行测试
            futures = [executor.submit(single_latency_test) for _ in range(3)]
            
            for future in futures:
                try:
                    latency_ms = future.result(timeout=2)
                    if latency_ms is not None:
                        latencies.append(latency_ms)
                        test_count += 1
                        
                        # 实时显示
                        if test_count % 5 == 0:
                            current_avg = sum(latencies[-10:]) / min(10, len(latencies))
                            print(f"\r📊 已测试 {test_count} 次, 近期平均: {current_avg:.1f}ms", end="", flush=True)
                except:
                    pass
            
            time.sleep(0.1)  # 避免过于频繁的请求
    
    print()  # 换行
    
    if not latencies or len(latencies) < 5:
        print("⚠️ 延迟测试数据不足，使用默认值")
        return {
            'avg_ms': 200,
            'min_ms': 100, 
            'max_ms': 500,
            'std_ms': 50,
            'recommended_advance_ms': 300,
            'confidence': 'low'
        }
    
    # 过滤异常值（去掉最高和最低10%）
    latencies.sort()
    filtered_count = max(5, int(len(latencies) * 0.8))
    start_idx = (len(latencies) - filtered_count) // 2
    filtered_latencies = latencies[start_idx:start_idx + filtered_count]
    
    stats = {
        'avg_ms': statistics.mean(filtered_latencies),
        'min_ms': min(filtered_latencies),
        'max_ms': max(filtered_latencies),
        'std_ms': statistics.stdev(filtered_latencies) if len(filtered_latencies) > 1 else 0,
        'test_count': len(latencies),
        'confidence': 'high' if len(latencies) >= 20 else 'medium'
    }
    
    # 计算推荐的提前时间（毫秒）
    # 基于平均延迟 + 2倍标准差 + 安全边距
    safety_margin = 50  # 50ms安全边距
    recommended_advance_ms = stats['avg_ms'] + 2 * stats['std_ms'] + safety_margin
    
    # 限制在合理范围内（100ms-1000ms）
    stats['recommended_advance_ms'] = max(100, min(1000, recommended_advance_ms))
    
    print(f"📊 真实网络延迟检测结果:")
    print(f"   测试次数: {stats['test_count']}")
    print(f"   平均延迟: {stats['avg_ms']:.1f}ms")
    print(f"   最小延迟: {stats['min_ms']:.1f}ms")
    print(f"   最大延迟: {stats['max_ms']:.1f}ms")
    print(f"   标准差: {stats['std_ms']:.1f}ms")
    print(f"   推荐提前: {stats['recommended_advance_ms']:.1f}ms")
    print(f"   置信度: {stats['confidence']}")
    
    return stats


def show_countdown_with_dynamic_timing(target_time: datetime, enable_latency_test: bool = True) -> Optional[float]:
    """
    显示动态倒计时，使用上海-韩国VPN优化的真实延迟检测
    
    Args:
        target_time: 目标时间
        enable_latency_test: 是否启用真实延迟测试
    
    Returns:
        推荐的提前点击时间（秒）
    """
    current_time = datetime.now(target_time.tzinfo)
    time_diff = (target_time - current_time).total_seconds()
    
    # 动态延迟检测
    recommended_advance_ms = 300  # 默认300ms
    
    if time_diff > 35 and enable_latency_test:
        # 获取延迟配置
        if LATENCY_CONFIG_AVAILABLE:
            latency_config = get_latency_config()
            scenario = latency_config.get('scenario', 'internal')
            
            # 根据场景选择基础延迟
            if scenario == 'external':
                base_latency_ms = latency_config['external_request']['base_latency_ms']
                scenario_desc = "外部请求（Postman场景）"
            else:
                base_latency_ms = latency_config['internal_navigation']['base_latency_ms']
                scenario_desc = "页面内跳转（推荐）"
                
            browser_overhead_ms = latency_config['browser_overhead_ms']
            safety_margin_ms = latency_config['safety_margin_ms']
            dynamic_adjustment = latency_config['dynamic_adjustment']
        else:
            base_latency_ms = 300  # 默认使用页面内跳转值
            browser_overhead_ms = 80
            safety_margin_ms = 100
            scenario_desc = "页面内跳转（默认）"
            dynamic_adjustment = {'enabled': True, 'weight_measured': 0.7, 'weight_realtime': 0.3, 'max_deviation_ms': 200}
        
        # 新增：基于用户Postman测试数据的优化计算
        print("🎯 开始优化延迟计算...")
        print(f"📊 场景: {scenario_desc}")
        print("💡 说明: 页面内跳转通常比外部请求快，因为：")
        print("   - 复用已有的TCP/HTTPS连接")
        print("   - 可能使用浏览器缓存")
        print("   - 无需重新进行DNS解析")
        print(f"\n📈 延迟计算参数：")
        print(f"   - 基础网络延迟: {base_latency_ms}ms")
        print(f"   - 浏览器额外开销: {browser_overhead_ms}ms")
        
        # 计算总延迟
        total_latency_ms = base_latency_ms + browser_overhead_ms + safety_margin_ms
        
        print(f"\n📊 延迟计算明细：")
        print(f"   基础网络延迟: {base_latency_ms}ms ({scenario_desc})")
        print(f"   浏览器开销: {browser_overhead_ms}ms")
        print(f"   安全边际: {safety_margin_ms}ms")
        print(f"   总提前时间: {total_latency_ms}ms")
        
        # 如果启用了动态检测，进行补充验证
        if VPN_OPTIMIZER_AVAILABLE and dynamic_adjustment['enabled']:
            try:
                print("\n🔄 进行实时网络验证...")
                optimizer = ShanghaiKoreaOptimizer()
                optimizer.test_duration = min(10, int(time_diff - 5))  # 快速验证
                
                # 快速检测当前延迟
                latency_data = optimizer.detect_real_latency()
                current_avg_ms = latency_data['avg_latency_ms']
                
                print(f"✅ 实时检测延迟: {current_avg_ms:.1f}ms")
                
                # 如果实时检测值与预设值差异较大，进行调整
                if abs(current_avg_ms - base_latency_ms) > dynamic_adjustment['max_deviation_ms']:
                    print(f"⚠️ 检测到网络波动较大，动态调整...")
                    # 使用加权平均
                    adjusted_latency = (base_latency_ms * dynamic_adjustment['weight_measured'] + 
                                      current_avg_ms * dynamic_adjustment['weight_realtime'])
                    total_latency_ms = adjusted_latency + browser_overhead_ms + safety_margin_ms
                    print(f"📊 调整后提前时间: {total_latency_ms:.0f}ms")
                
            except Exception as e:
                print(f"⚠️ 实时验证失败，使用预设值: {e}")
        
        # 确保在合理范围内
        if LATENCY_CONFIG_AVAILABLE:
            limits = latency_config['limits']
            recommended_advance_ms = max(limits['min_ms'], min(limits['max_ms'], total_latency_ms))
        else:
            recommended_advance_ms = max(500, min(1200, total_latency_ms))
        
        print(f"\n✅ 最终提前时间: {recommended_advance_ms:.0f}ms")
        print("💡 说明: 基于实测延迟 + 浏览器开销 + 安全边际")
        
    else:
        # 时间太短，使用固定的优化值
        if LATENCY_CONFIG_AVAILABLE:
            recommended_advance_ms = get_optimized_preclick_ms('internal')  # 使用页面内跳转场景
        else:
            recommended_advance_ms = 480  # 300 + 80 + 100（页面内跳转）
        print(f"⏰ 使用优化预设值: {recommended_advance_ms}ms (页面内跳转场景)")
    
    recommended_advance_s = recommended_advance_ms / 1000.0
    
    print(f"\n⏰ 动态精确倒计时开始")
    print(f"⚡ 动态提前时间: {recommended_advance_ms:.0f}ms ({recommended_advance_s:.3f}秒)")
    print("=" * 70)
    
    try:
        while True:
            current_time = datetime.now(target_time.tzinfo)
            time_diff = (target_time - current_time).total_seconds()
            
            if time_diff <= 0:
                print(f"\r🎉 目标时间已到！立即执行！        ")
                return 0
            
            # 检查是否到达动态提前点击时间
            if time_diff <= recommended_advance_s:
                print(f"\r⚡ 动态提前时间到！立即点击！剩余: {time_diff:.3f}秒        ")
                return recommended_advance_s
            
            # 显示精确倒计时
            hours = int(time_diff // 3600)
            minutes = int((time_diff % 3600) // 60)
            seconds = time_diff % 60
            
            if hours > 0:
                countdown_str = f"⏳ 倒计时: {hours:02d}:{minutes:02d}:{seconds:06.3f}"
            else:
                countdown_str = f"⏳ 倒计时: {minutes:02d}:{seconds:06.3f}"
            
            current_str = f"🕐 当前: {current_time.strftime('%H:%M:%S.%f')[:-3]}"
            target_str = f"🎯 目标: {target_time.strftime('%H:%M:%S.%f')[:-3]}"
            advance_str = f"⚡ 提前: {recommended_advance_ms:.0f}ms"
            
            print(f"\r{countdown_str} | {current_str} | {target_str} | {advance_str}", end="", flush=True)
            
            # 精确控制更新频率
            if time_diff > 10:
                time.sleep(0.1)
            elif time_diff > 1:
                time.sleep(0.01)
            else:
                time.sleep(0.001)
                
    except KeyboardInterrupt:
        print(f"\n⏹️ 倒计时被用户中断")
        return None
    
    return recommended_advance_s


# 保持原有的show_countdown函数作为兼容性接口
def show_countdown(target_time: datetime) -> None:
    """兼容性接口：显示倒计时"""
    show_countdown_with_dynamic_timing(target_time, enable_latency_test=False)


def get_time_input():
    """获取用户输入的目标时间"""
    print("\n⏰ 请输入目标时间")
    print("格式示例: 14:30 (表示今天14:30)")
    print("或者: 2024-03-15 14:30 (表示具体日期时间)")
    
    time_input = input("目标时间: ").strip()
    
    try:
        if ":" in time_input and "-" not in time_input:
            # 只有时间，默认为今天
            hour, minute = map(int, time_input.split(":"))
            today = datetime.now().date()
            target_time = datetime.combine(today, datetime.min.time().replace(hour=hour, minute=minute))
            
            # 如果时间已过，设为明天
            if target_time <= datetime.now():
                target_time += timedelta(days=1)
        else:
            # 完整日期时间
            target_time = datetime.strptime(time_input, "%Y-%m-%d %H:%M")
        
        # 转换为中国时区
        china_tz = pytz.timezone('Asia/Shanghai')
        target_time = china_tz.localize(target_time)
        
        return target_time
    except ValueError:
        print("❌ 时间格式错误")
        return None