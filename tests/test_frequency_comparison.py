#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_frequency_comparison.py
多频率性能对比测试 - 5Hz到100Hz全面测试
"""

import os
import sys
import time
import psutil
import threading
from datetime import datetime, timedelta

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.weverse.browser.setup import setup_driver
from src.weverse.forms.lightning_form_processor import LightningFormProcessor
from config.form_selectors import get_form_selectors
from config.user_data import get_user_data


class FrequencyTester:
    """多频率检测性能测试器"""
    
    def __init__(self, driver):
        self.driver = driver
        self.selectors = get_form_selectors()
        self.user_data = get_user_data()
        self.cpu_usage = []
        self.memory_usage = []
        
    def test_detection_frequency(self, frequency_hz: float, test_duration: float = 3.0) -> dict:
        """
        测试指定频率的检测性能
        
        Args:
            frequency_hz: 检测频率（Hz）
            test_duration: 测试持续时间（秒）
        """
        interval = 1.0 / frequency_hz
        max_checks = int(test_duration / interval)
        
        print(f"\n🔍 测试频率: {frequency_hz}Hz (间隔: {interval*1000:.1f}ms)")
        print(f"📊 测试设置: {test_duration}秒内最多检测{max_checks}次")
        
        # 重置CPU和内存监控
        self.cpu_usage.clear()
        self.memory_usage.clear()
        
        # 启动系统监控
        monitor_stop = threading.Event()
        monitor_thread = threading.Thread(
            target=self._monitor_system_resources, 
            args=(monitor_stop, 0.1)
        )
        monitor_thread.start()
        
        # 执行检测测试
        start_time = time.perf_counter()
        detection_times = []
        successful_detections = 0
        check_count = 0
        
        try:
            while time.perf_counter() - start_time < test_duration and check_count < max_checks:
                check_start = time.perf_counter()
                
                # 执行单次检测
                try:
                    birth_input = self.driver.find_element("css selector", self.selectors['birth_date'])
                    if birth_input and birth_input.is_displayed() and birth_input.is_enabled():
                        successful_detections += 1
                        detection_time = (time.perf_counter() - check_start) * 1000
                        detection_times.append(detection_time)
                except:
                    detection_time = (time.perf_counter() - check_start) * 1000
                    detection_times.append(detection_time)
                
                check_count += 1
                
                # 等待到下一个检测时机
                elapsed = time.perf_counter() - check_start
                if elapsed < interval:
                    time.sleep(interval - elapsed)
                    
        except KeyboardInterrupt:
            print("⚠️ 测试被用户中断")
        
        # 停止监控
        monitor_stop.set()
        monitor_thread.join()
        
        actual_duration = time.perf_counter() - start_time
        actual_frequency = check_count / actual_duration if actual_duration > 0 else 0
        
        # 计算统计数据
        avg_cpu = sum(self.cpu_usage) / len(self.cpu_usage) if self.cpu_usage else 0
        max_cpu = max(self.cpu_usage) if self.cpu_usage else 0
        avg_memory_mb = sum(self.memory_usage) / len(self.memory_usage) if self.memory_usage else 0
        max_memory_mb = max(self.memory_usage) if self.memory_usage else 0
        
        avg_detection_time = sum(detection_times) / len(detection_times) if detection_times else 0
        min_detection_time = min(detection_times) if detection_times else 0
        max_detection_time = max(detection_times) if detection_times else 0
        
        return {
            'target_frequency': frequency_hz,
            'actual_frequency': actual_frequency,
            'frequency_accuracy': (actual_frequency / frequency_hz * 100) if frequency_hz > 0 else 0,
            'total_checks': check_count,
            'successful_detections': successful_detections,
            'detection_success_rate': (successful_detections / check_count * 100) if check_count > 0 else 0,
            'test_duration': actual_duration,
            'avg_detection_time_ms': avg_detection_time,
            'min_detection_time_ms': min_detection_time,
            'max_detection_time_ms': max_detection_time,
            'avg_cpu_percent': avg_cpu,
            'max_cpu_percent': max_cpu,
            'avg_memory_mb': avg_memory_mb,
            'max_memory_mb': max_memory_mb,
            'is_stable': max_detection_time < interval * 1000 * 0.8,  # 检测时间不超过间隔的80%
            'performance_rating': self._calculate_performance_rating(
                actual_frequency, frequency_hz, avg_cpu, avg_detection_time, interval * 1000
            )
        }
    
    def _monitor_system_resources(self, stop_event: threading.Event, monitor_interval: float):
        """监控系统资源使用"""
        process = psutil.Process()
        
        while not stop_event.is_set():
            try:
                cpu_percent = process.cpu_percent()
                memory_mb = process.memory_info().rss / 1024 / 1024
                
                self.cpu_usage.append(cpu_percent)
                self.memory_usage.append(memory_mb)
                
                time.sleep(monitor_interval)
            except:
                break
    
    def _calculate_performance_rating(self, actual_freq, target_freq, cpu_usage, detection_time, target_interval):
        """计算性能评级"""
        freq_score = min(actual_freq / target_freq, 1.0) * 40  # 频率准确性 40分
        cpu_score = max(0, (100 - cpu_usage) / 100) * 30  # CPU使用率 30分
        speed_score = max(0, (target_interval - detection_time) / target_interval) * 30  # 检测速度 30分
        
        total_score = freq_score + cpu_score + speed_score
        
        if total_score >= 90:
            return "🔥 极佳"
        elif total_score >= 80:
            return "✅ 优秀"
        elif total_score >= 70:
            return "👍 良好"
        elif total_score >= 60:
            return "⚠️ 一般"
        else:
            return "❌ 较差"
    
    def test_auto_fill_with_frequency(self, frequency_hz: float) -> dict:
        """测试指定频率下的自动填写性能"""
        print(f"\n⚡ 测试{frequency_hz}Hz下的自动填写...")
        
        processor = LightningFormProcessor(self.driver)
        
        # 执行多次填写测试
        fill_times = []
        success_count = 0
        
        for i in range(5):  # 测试5次
            try:
                start_time = time.perf_counter()
                result = processor.process_form_lightning_fast(
                    birth_date=self.user_data['birth_date'],
                    phone_number=self.user_data['phone_number']
                )
                fill_time = (time.perf_counter() - start_time) * 1000
                
                if result.get('success'):
                    fill_times.append(fill_time)
                    success_count += 1
                    
                # 重置页面
                self.driver.refresh()
                time.sleep(0.5)  # 等待页面重新加载
                
            except Exception as e:
                print(f"⚠️ 第{i+1}次填写测试失败: {e}")
        
        avg_fill_time = sum(fill_times) / len(fill_times) if fill_times else 0
        
        return {
            'frequency': frequency_hz,
            'fill_attempts': 5,
            'fill_successes': success_count,
            'fill_success_rate': success_count / 5 * 100,
            'avg_fill_time_ms': avg_fill_time,
            'min_fill_time_ms': min(fill_times) if fill_times else 0,
            'max_fill_time_ms': max(fill_times) if fill_times else 0
        }


def run_comprehensive_frequency_test():
    """运行综合频率测试"""
    print("🚀 启动多频率性能对比测试")
    print("=" * 80)
    
    # 测试频率列表
    test_frequencies = [5, 10, 20, 50, 100]
    print(f"🎯 测试频率: {test_frequencies} Hz")
    print(f"📊 每个频率测试3秒，监控CPU和内存使用")
    
    driver = None
    try:
        # 启动浏览器
        print("\n⏳ 启动Chrome浏览器...")
        driver = setup_driver(headless=False)
        driver.set_window_size(1400, 900)
        
        # 打开测试页面
        current_dir = os.path.dirname(os.path.abspath(__file__))
        test_file = os.path.join(current_dir, "test_weverse_form.html")
        test_url = f"file://{test_file}"
        
        print(f"🌐 打开测试页面: {test_url}")
        driver.get(test_url)
        time.sleep(1)
        
        # 创建测试器
        tester = FrequencyTester(driver)
        
        # 存储所有测试结果
        detection_results = []
        fill_results = []
        
        print("\n" + "="*80)
        print("📊 开始检测频率性能测试")
        print("="*80)
        
        # 测试各个频率的检测性能
        for freq in test_frequencies:
            result = tester.test_detection_frequency(freq, test_duration=3.0)
            detection_results.append(result)
            
            # 显示实时结果
            print(f"✅ {freq}Hz测试完成:")
            print(f"   实际频率: {result['actual_frequency']:.1f}Hz ({result['frequency_accuracy']:.1f}%)")
            print(f"   检测成功率: {result['detection_success_rate']:.1f}%")
            print(f"   平均检测时间: {result['avg_detection_time_ms']:.2f}ms")
            print(f"   CPU使用: {result['avg_cpu_percent']:.1f}% (最高: {result['max_cpu_percent']:.1f}%)")
            print(f"   内存使用: {result['avg_memory_mb']:.1f}MB")
            print(f"   稳定性: {'✅ 稳定' if result['is_stable'] else '⚠️ 不稳定'}")
            print(f"   性能评级: {result['performance_rating']}")
            
            time.sleep(1)  # 间隔1秒
        
        print("\n" + "="*80)
        print("⚡ 开始自动填写性能测试")
        print("="*80)
        
        # 测试自动填写性能
        for freq in [20, 50, 100]:  # 只测试高频率的填写性能
            result = tester.test_auto_fill_with_frequency(freq)
            fill_results.append(result)
            
            print(f"✅ {freq}Hz填写测试完成:")
            print(f"   成功率: {result['fill_success_rate']:.1f}%")
            print(f"   平均时间: {result['avg_fill_time_ms']:.2f}ms")
            print(f"   时间范围: {result['min_fill_time_ms']:.2f}-{result['max_fill_time_ms']:.2f}ms")
        
        # 生成综合报告
        print("\n" + "="*80)
        print("📈 综合性能报告")
        print("="*80)
        
        generate_comparison_report(detection_results, fill_results)
        
        # 推荐最佳频率
        recommend_optimal_frequency(detection_results)
        
    except Exception as e:
        print(f"❌ 测试过程出错: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        if driver:
            driver.quit()
            print("✅ 浏览器已关闭")


def generate_comparison_report(detection_results: list, fill_results: list):
    """生成对比报告"""
    print("📊 检测性能对比:")
    print("-" * 60)
    print(f"{'频率':<8} {'实际Hz':<10} {'检测时间':<12} {'CPU使用':<10} {'稳定性':<8} {'评级':<8}")
    print("-" * 60)
    
    for result in detection_results:
        freq = result['target_frequency']
        actual = result['actual_frequency']
        detection_time = result['avg_detection_time_ms']
        cpu = result['avg_cpu_percent']
        stable = "✅" if result['is_stable'] else "⚠️"
        rating = result['performance_rating']
        
        print(f"{freq:<8} {actual:<10.1f} {detection_time:<12.2f} {cpu:<10.1f} {stable:<8} {rating:<8}")
    
    if fill_results:
        print("\n⚡ 填写性能对比:")
        print("-" * 50)
        print(f"{'频率':<8} {'成功率':<10} {'平均时间':<12} {'时间范围':<15}")
        print("-" * 50)
        
        for result in fill_results:
            freq = result['frequency']
            success_rate = result['fill_success_rate']
            avg_time = result['avg_fill_time_ms']
            time_range = f"{result['min_fill_time_ms']:.1f}-{result['max_fill_time_ms']:.1f}"
            
            print(f"{freq:<8} {success_rate:<10.1f}% {avg_time:<12.2f}ms {time_range:<15}ms")


def recommend_optimal_frequency(detection_results: list):
    """推荐最佳频率"""
    print("\n💡 最佳频率推荐:")
    print("-" * 40)
    
    # 按性能评级排序
    sorted_results = sorted(detection_results, 
                          key=lambda x: (x['frequency_accuracy'], -x['avg_cpu_percent']), 
                          reverse=True)
    
    best_result = sorted_results[0]
    
    print(f"🔥 推荐频率: {best_result['target_frequency']}Hz")
    print(f"   理由: {best_result['performance_rating']}")
    print(f"   实际频率: {best_result['actual_frequency']:.1f}Hz")
    print(f"   CPU使用: {best_result['avg_cpu_percent']:.1f}%")
    print(f"   检测时间: {best_result['avg_detection_time_ms']:.2f}ms")
    
    # 显示其他可选方案
    print(f"\n📋 其他方案:")
    for i, result in enumerate(sorted_results[1:3], 1):
        print(f"   {i+1}. {result['target_frequency']}Hz - {result['performance_rating']} "
              f"(CPU: {result['avg_cpu_percent']:.1f}%)")


if __name__ == "__main__":
    run_comprehensive_frequency_test() 