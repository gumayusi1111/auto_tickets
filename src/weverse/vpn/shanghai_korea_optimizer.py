#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
shanghai_korea_optimizer.py
上海-韩国VPN延迟优化器 - 专门针对从上海通过VPN到韩国服务器的延迟优化
"""

import time
import requests
import statistics
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Tuple, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class ShanghaiKoreaOptimizer:
    """上海-韩国VPN延迟优化器"""
    
    def __init__(self):
        self.test_targets = [
            "https://weverse.io",
            "https://global.apis.naver.com",
            "https://www.naver.com",
            "https://static.weverse.io"
        ]
        self.test_duration = 30  # 30秒测试时间
        self.concurrent_tests = 5  # 并发测试数量
    
    def detect_real_latency(self) -> Dict[str, float]:
        """检测到韩国服务器的真实延迟"""
        print("🌐 检测上海→VPN→韩国的真实网络延迟...")
        print(f"⏱️ 测试时长: {self.test_duration}秒")
        print(f"🔄 并发数: {self.concurrent_tests}")
        
        all_latencies = []
        successful_tests = 0
        failed_tests = 0
        start_time = time.time()
        
        # 并发测试多个目标
        with ThreadPoolExecutor(max_workers=self.concurrent_tests) as executor:
            futures = []
            
            # 在30秒内持续提交测试任务
            while time.time() - start_time < self.test_duration:
                for target in self.test_targets:
                    future = executor.submit(self._single_latency_test, target)
                    futures.append(future)
                time.sleep(0.5)  # 每0.5秒一轮测试
            
            # 收集结果
            try:
                for future in as_completed(futures, timeout=self.test_duration + 10):
                    try:
                        result = future.result(timeout=2)  # 单个请求2秒超时
                        if result is not None:
                            all_latencies.append(result)
                            successful_tests += 1
                        else:
                            failed_tests += 1
                    except Exception as e:
                        failed_tests += 1
                        if "timeout" not in str(e).lower():
                            print(f"⚠️ 测试失败: {e}")
            except Exception as timeout_error:
                print(f"⚠️ 部分测试超时，使用已收集的数据: {len(all_latencies)}个样本")
        
        if not all_latencies:
            print("❌ 所有延迟测试都失败了")
            return self._get_fallback_latency_config()
        
        # 统计分析
        avg_latency = statistics.mean(all_latencies)
        median_latency = statistics.median(all_latencies) 
        std_dev = statistics.stdev(all_latencies) if len(all_latencies) > 1 else 0
        min_latency = min(all_latencies)
        max_latency = max(all_latencies)
        
        print(f"\n📊 延迟测试结果 ({successful_tests}次成功, {failed_tests}次失败):")
        print(f"   平均延迟: {avg_latency:.1f}ms")
        print(f"   中位数延迟: {median_latency:.1f}ms")
        print(f"   最小延迟: {min_latency:.1f}ms") 
        print(f"   最大延迟: {max_latency:.1f}ms")
        print(f"   标准差: {std_dev:.1f}ms")
        
        # 评估网络质量
        quality = self._assess_network_quality(avg_latency, std_dev)
        print(f"   网络质量: {quality}")
        
        return {
            'avg_latency_ms': avg_latency,
            'median_latency_ms': median_latency,
            'min_latency_ms': min_latency,
            'max_latency_ms': max_latency,
            'std_dev_ms': std_dev,
            'successful_tests': successful_tests,
            'failed_tests': failed_tests,
            'quality': quality,
            'all_latencies': all_latencies
        }
    
    def _single_latency_test(self, url: str) -> Optional[float]:
        """单次延迟测试 - 使用轻量HEAD请求"""
        try:
            start_time = time.perf_counter()
            # 使用HEAD请求减少数据传输，更准确测试延迟
            response = requests.head(url, timeout=3, headers={
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            }, allow_redirects=False)
            end_time = time.perf_counter()
            
            # 接受更多状态码，某些网站可能返回404但延迟仍然有效
            if response.status_code in [200, 301, 302, 404, 403]:
                latency_ms = (end_time - start_time) * 1000
                return latency_ms
            else:
                return None
                
        except Exception:
            return None
    
    def _assess_network_quality(self, avg_latency: float, std_dev: float) -> str:
        """评估网络质量 - 基于实际延迟而非地理位置推测"""
        if avg_latency <= 50 and std_dev <= 10:
            return "优秀 (低延迟高稳定)"
        elif avg_latency <= 100 and std_dev <= 20:
            return "良好 (中低延迟)"
        elif avg_latency <= 200 and std_dev <= 50:
            return "一般 (中等延迟)"
        elif avg_latency <= 500 and std_dev <= 100:
            return "较差 (高延迟)"
        elif avg_latency <= 1000 and std_dev <= 200:
            return "很差 (超高延迟)"
        else:
            return "极差 (网络异常)"
    
    def calculate_optimal_preclick_time(self, latency_data: Dict[str, float]) -> Dict[str, float]:
        """计算最优提前点击时间"""
        print("\n⚡ 计算最优提前点击时间...")
        
        avg_latency = latency_data['avg_latency_ms']
        std_dev = latency_data['std_dev_ms']
        
        # 基于统计学的优化算法
        # 使用平均延迟 + 2倍标准差作为基础，确保95%的情况下能成功
        base_preclick_ms = avg_latency + (2 * std_dev)
        
        # 添加安全边际（10-20ms）
        safety_margin_ms = max(10, min(20, avg_latency * 0.1))
        
        # 最终提前时间
        total_preclick_ms = base_preclick_ms + safety_margin_ms
        
        # 根据实际网络情况调整范围
        # 如果检测到台湾节点但延迟异常高，使用台湾的预期值
        if hasattr(self, '_is_taiwan_node') and self._is_taiwan_node and total_preclick_ms > 200:
            print(f"   🇹🇼 检测到台湾节点，使用优化的延迟预估")
            total_preclick_ms = 80  # 台湾到韩国的合理延迟
        else:
            # 限制在合理范围内（10ms - 500ms）
            total_preclick_ms = max(10, min(500, total_preclick_ms))
        
        # 转换为秒
        preclick_seconds = total_preclick_ms / 1000
        
        print(f"📊 提前点击时间计算:")
        print(f"   基础延迟: {avg_latency:.1f}ms")
        print(f"   2倍标准差: {2 * std_dev:.1f}ms")
        print(f"   安全边际: {safety_margin_ms:.1f}ms")
        print(f"   总提前时间: {total_preclick_ms:.1f}ms ({preclick_seconds:.3f}秒)")
        
        # 计算不同置信度的提前时间
        confidence_levels = {
            '50%': avg_latency / 1000,  # 中位数
            '90%': (avg_latency + 1.28 * std_dev) / 1000,  # 90%置信度
            '95%': (avg_latency + 1.96 * std_dev) / 1000,  # 95%置信度
            '99%': (avg_latency + 2.58 * std_dev) / 1000,  # 99%置信度
        }
        
        print(f"\n📈 不同置信度的提前时间:")
        for confidence, time_sec in confidence_levels.items():
            print(f"   {confidence}: {time_sec*1000:.1f}ms ({time_sec:.3f}秒)")
        
        return {
            'recommended_preclick_seconds': preclick_seconds,
            'recommended_preclick_ms': total_preclick_ms,
            'confidence_levels': confidence_levels,
            'base_latency_ms': avg_latency,
            'safety_margin_ms': safety_margin_ms
        }
    
    def get_monitoring_config(self, latency_data: Dict, preclick_data: Dict) -> Dict:
        """获取实时监控配置"""
        print("\n👁️ 生成实时监控配置...")
        
        avg_latency = latency_data['avg_latency_ms']
        quality = latency_data['quality']
        
        # 根据网络质量调整监控频率
        if avg_latency <= 50:
            check_interval_ms = 10  # 优秀网络：10ms检查一次
        elif avg_latency <= 100:
            check_interval_ms = 20  # 良好网络：20ms检查一次
        elif avg_latency <= 200:
            check_interval_ms = 50  # 一般网络：50ms检查一次
        else:
            check_interval_ms = 100  # 较差网络：100ms检查一次
        
        config = {
            'check_interval_seconds': check_interval_ms / 1000,
            'check_interval_ms': check_interval_ms,
            'preclick_time_seconds': preclick_data['recommended_preclick_seconds'],
            'timeout_seconds': 10,  # 10秒超时
            'max_retries': 3,
            'wait_after_click_ms': 200,  # 点击后等待200ms
            'network_quality': quality,
            'avg_latency_ms': avg_latency
        }
        
        print(f"📊 监控配置:")
        print(f"   检查间隔: {config['check_interval_ms']}ms")
        print(f"   提前点击: {config['preclick_time_seconds']*1000:.1f}ms")
        print(f"   超时时间: {config['timeout_seconds']}秒")
        print(f"   点击后等待: {config['wait_after_click_ms']}ms")
        print(f"   网络质量: {config['network_quality']}")
        
        return config
    
    def _get_fallback_latency_config(self) -> Dict[str, float]:
        """获取备用延迟配置（当检测失败时）"""
        print("⚠️ 使用备用延迟配置")
        return {
            'avg_latency_ms': 100.0,  # 假设100ms延迟
            'median_latency_ms': 100.0,
            'min_latency_ms': 80.0,
            'max_latency_ms': 150.0,
            'std_dev_ms': 20.0,
            'successful_tests': 0,
            'failed_tests': 0,
            'quality': '未知 (使用默认值)',
            'all_latencies': []
        }
    
    def run_complete_optimization(self) -> Dict:
        """运行完整的延迟优化流程"""
        print("🚀 上海-韩国VPN延迟优化器")
        print("=" * 50)
        print("📍 检测场景: 当前位置 → VPN → 韩国服务器")
        print("🎯 优化目标: 计算最佳提前点击时间")
        
        # 0. 检测当前IP和位置
        self._detect_current_location()
        
        # 1. 检测真实延迟
        latency_data = self.detect_real_latency()
        
        # 2. 计算最优提前点击时间
        preclick_data = self.calculate_optimal_preclick_time(latency_data)
        
        # 3. 生成监控配置
        monitoring_config = self.get_monitoring_config(latency_data, preclick_data)
        
        # 4. 综合结果
        optimization_result = {
            'timestamp': datetime.now().isoformat(),
            'location': '当前位置',
            'target': '韩国服务器',
            'latency_analysis': latency_data,
            'preclick_optimization': preclick_data,
            'monitoring_config': monitoring_config,
            'recommendations': self._generate_recommendations(latency_data, preclick_data)
        }
        
        print(f"\n✅ 延迟优化完成!")
        self._print_optimization_summary(optimization_result)
        
        return optimization_result
    
    def _generate_recommendations(self, latency_data: Dict, preclick_data: Dict) -> List[str]:
        """生成优化建议"""
        recommendations = []
        avg_latency = latency_data['avg_latency_ms']
        quality = latency_data['quality']
        
        if avg_latency <= 50:
            recommendations.append("延迟很低，当前VPN节点是最佳选择")
            recommendations.append("建议使用高频检测(10ms)获得最佳响应")
        elif avg_latency <= 100:
            recommendations.append("延迟适中，当前VPN节点表现良好")
            recommendations.append("建议使用中频检测(20ms)平衡性能")
        elif avg_latency <= 200:
            recommendations.append("延迟偏高，考虑切换到亚洲节点(香港/台湾/日本)")
            recommendations.append("建议使用低频检测(50ms)减少资源消耗")
        else:
            recommendations.append("延迟很高，强烈建议切换VPN节点")
            recommendations.append("推荐选择：香港 > 台湾 > 日本 > 新加坡")
        
        # 提前点击时间建议
        preclick_ms = preclick_data['recommended_preclick_ms']
        if preclick_ms <= 50:
            recommendations.append("提前点击时间很短，成功率很高")
        elif preclick_ms <= 150:
            recommendations.append("提前点击时间适中，成功率良好")
        else:
            recommendations.append("提前点击时间较长，建议优化网络连接")
        
        return recommendations
    
    def _print_optimization_summary(self, result: Dict) -> None:
        """打印优化总结"""
        print(f"\n📊 优化总结:")
        
        latency = result['latency_analysis']
        preclick = result['preclick_optimization']
        config = result['monitoring_config']
        
        print(f"   🌐 网络延迟: {latency['avg_latency_ms']:.1f}ms ({latency['quality']})")
        print(f"   ⚡ 提前点击: {preclick['recommended_preclick_ms']:.1f}ms")
        print(f"   👁️ 检查间隔: {config['check_interval_ms']}ms")
        print(f"   ✅ 成功测试: {latency['successful_tests']}次")
        
        print(f"\n💡 优化建议:")
        for i, rec in enumerate(result['recommendations'], 1):
            print(f"   {i}. {rec}")
    
    def _detect_current_location(self):
        """检测当前IP和地理位置"""
        try:
            print("🌍 检测当前网络位置...")
            
            # 获取公网IP
            response = requests.get('https://api.ipify.org?format=json', timeout=5)
            ip_data = response.json()
            current_ip = ip_data['ip']
            print(f"📍 当前IP: {current_ip}")
            
            # 获取地理位置
            geo_response = requests.get(f'http://ip-api.com/json/{current_ip}', timeout=5)
            geo_data = geo_response.json()
            
            if geo_data.get('status') == 'success':
                country = geo_data.get('country', '未知')
                region = geo_data.get('regionName', '未知')
                city = geo_data.get('city', '未知')
                isp = geo_data.get('isp', '未知')
                
                print(f"🌐 位置: {city}, {region}, {country}")
                print(f"🏢 ISP: {isp}")
                
                # 分析VPN节点类型
                self._analyze_vpn_node(country, region, city, isp)
            else:
                print("⚠️ 无法获取地理位置信息")
                
        except Exception as e:
            print(f"⚠️ IP检测失败: {e}")
    
    def _analyze_vpn_node(self, country: str, region: str, city: str, isp: str):
        """分析VPN节点类型"""
        print(f"🔍 VPN节点分析:")
        
        # 根据国家判断到韩国的预期延迟
        expected_latencies = {
            'Taiwan': (30, 80, '台湾节点 - 优秀选择'),
            'Hong Kong': (20, 60, '香港节点 - 最佳选择'),
            'Japan': (40, 100, '日本节点 - 良好选择'),
            'Singapore': (60, 150, '新加坡节点 - 中等选择'),
            'United States': (150, 300, '美国节点 - 较远选择'),
            'Germany': (250, 400, '德国节点 - 很远选择'),
            'Netherlands': (250, 400, '荷兰节点 - 很远选择'),
            'United Kingdom': (250, 400, '英国节点 - 很远选择')
        }
        
        if country in expected_latencies:
            min_lat, max_lat, description = expected_latencies[country]
            print(f"   {description}")
            print(f"   预期延迟范围: {min_lat}-{max_lat}ms")
            
            # 标记台湾节点
            if country == 'Taiwan':
                self._is_taiwan_node = True
        else:
            print(f"   {country}节点 - 延迟待测试")
        
        # 检查是否可能是VPN
        vpn_keywords = ['vpn', 'proxy', 'tunnel', 'private', 'virtual']
        if any(keyword in isp.lower() for keyword in vpn_keywords):
            print(f"   🔒 检测到VPN服务")
        
        print(f"   建议: 基于实际测试结果优化")

    def _get_optimized_latency_for_region(self, region: str, base_latency: float) -> float:
        """基于地理位置和实测数据优化延迟"""
        # 基于Samsung等韩国公司的实测数据优化
        optimizations = {
            'taiwan': {
                'base_network_latency': 200,  # 基于Samsung 197.5ms的实测结果
                'http_overhead': 300,         # HTTP协议额外开销
                'safety_margin': 100,         # 安全边际
                'recommended_preclick': 350   # 综合建议: 200+100+50
            },
            'shanghai': {
                'base_network_latency': 80,
                'http_overhead': 200,
                'safety_margin': 80,
                'recommended_preclick': 200
            },
            'hong_kong': {
                'base_network_latency': 150,
                'http_overhead': 250,
                'safety_margin': 100,
                'recommended_preclick': 300
            }
        }
        
        region_config = optimizations.get(region, optimizations['shanghai'])
        
        # 使用实测的基础延迟而不是HTTP延迟
        optimized_latency = region_config['base_network_latency']
        
        logger.info(f"区域 {region} 延迟优化:")
        logger.info(f"  基础网络延迟: {region_config['base_network_latency']}ms")
        logger.info(f"  HTTP协议开销: {region_config['http_overhead']}ms") 
        logger.info(f"  安全边际: {region_config['safety_margin']}ms")
        logger.info(f"  建议提前点击: {region_config['recommended_preclick']}ms")
        
        return region_config['recommended_preclick']
    
    def detect_taiwan_node(self, current_ip: str) -> Dict:
        """检测台湾VPN节点并提供基于实测数据的优化建议"""
        print(f"🔍 检测到IP: {current_ip}")
        
        # 获取IP地理信息
        ip_info = self._get_ip_geolocation(current_ip)
        
        if ip_info and '台湾' in ip_info.get('region', ''):
            print(f"✅ 确认台湾VPN节点")
            print(f"   位置: {ip_info.get('city', 'Unknown')}, {ip_info.get('region', 'Unknown')}")
            print(f"   ISP: {ip_info.get('isp', 'Unknown')}")
            
            # 使用基于Samsung实测数据的优化延迟
            recommended_preclick = self._get_optimized_latency_for_region('taiwan', 0)
            
            return {
                'is_taiwan_node': True,
                'location_info': ip_info,
                'recommended_preclick_ms': recommended_preclick,
                'confidence': 'high',
                'reason': f'Taiwan VPN node detected - using optimized {recommended_preclick}ms based on Samsung test data (197.5ms network + safety margin)'
            }
        else:
            print(f"⚠️ 非台湾节点或无法确定位置")
            print(f"   建议: 基于实际测试结果优化")
            
            return {
                'is_taiwan_node': False,
                'location_info': ip_info,
                'recommended_preclick_ms': 200,  # 提高默认值
                'confidence': 'medium',
                'reason': 'Unable to confirm Taiwan node - using conservative 200ms timing'
            }
    
    def _get_ip_geolocation(self, ip: str) -> Optional[Dict]:
        """获取IP地理位置信息"""
        try:
            response = requests.get(f'http://ip-api.com/json/{ip}', timeout=5)
            geo_data = response.json()
            
            if geo_data.get('status') == 'success':
                return {
                    'country': geo_data.get('country', '未知'),
                    'region': geo_data.get('regionName', '未知'), 
                    'city': geo_data.get('city', '未知'),
                    'isp': geo_data.get('isp', '未知')
                }
        except:
            pass
        return None


def optimize_shanghai_korea_latency() -> Dict:
    """快速调用函数 - 优化上海到韩国的延迟"""
    optimizer = ShanghaiKoreaOptimizer()
    return optimizer.run_complete_optimization()


if __name__ == "__main__":
    # 运行上海-韩国延迟优化
    result = optimize_shanghai_korea_latency()
    
    # 保存结果
    try:
        import os
        import json
        
        data_dir = "/Users/wenbai/Desktop/chajian/auto/data"
        os.makedirs(data_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        result_file = os.path.join(data_dir, f"shanghai_korea_optimization_{timestamp}.json")
        
        with open(result_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 优化结果已保存到: {result_file}")
        
    except Exception as e:
        print(f"❌ 保存结果失败: {e}")