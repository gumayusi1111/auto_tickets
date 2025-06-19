#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_nearby_servers.py
测试附近公司/服务器的延迟，获取更准确的网络性能数据
"""

import time
import requests
import statistics
from concurrent.futures import ThreadPoolExecutor, as_completed

class NearbyServerTester:
    def __init__(self):
        # 亚洲地区的主要公司/服务器
        self.test_targets = [
            # 韩国公司
            "https://www.samsung.com",           # 三星
            "https://www.lge.com",               # LG
            "https://www.kakao.com",             # 카카오
            "https://www.nexon.com",             # 游戏公司
            
            # 日本公司（地理位置相近）
            "https://www.sony.com",              # 索尼
            "https://www.nintendo.com",          # 任天堂
            "https://www.rakuten.com",           # 乐天
            
            # 香港/台湾地区
            "https://www.hkt.com",               # 香港电讯
            "https://www.pchome.com.tw",         # 台湾PChome
            "https://www.momo.com.tw",           # 台湾momo
            
            # 中国大陆公司（对比）
            "https://www.tencent.com",           # 腾讯
            "https://www.alibaba.com",           # 阿里巴巴
            "https://www.baidu.com",             # 百度
        ]
    
    def test_server_latency(self, url: str, timeout: int = 3) -> float:
        """测试单个服务器延迟"""
        try:
            start_time = time.perf_counter()
            response = requests.head(url, timeout=timeout, headers={
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            }, allow_redirects=False)
            end_time = time.perf_counter()
            
            # 接受更多状态码
            if response.status_code in [200, 301, 302, 404, 403, 503]:
                return (end_time - start_time) * 1000
            else:
                return None
        except:
            return None
    
    def test_multiple_samples(self, url: str, samples: int = 3) -> list:
        """对单个URL进行多次采样"""
        latencies = []
        for _ in range(samples):
            latency = self.test_server_latency(url)
            if latency is not None:
                latencies.append(latency)
            time.sleep(0.1)  # 避免请求过快
        return latencies
    
    def analyze_regional_latency(self):
        """分析各地区延迟情况"""
        print("🌏 测试亚洲地区主要公司服务器延迟")
        print("=" * 60)
        
        regions = {
            '韩国': [
                "https://www.samsung.com",
                "https://www.lge.com",
                "https://www.kakao.com",
                "https://www.nexon.com"
            ],
            '日本': [
                "https://www.sony.com",
                "https://www.nintendo.com",
                "https://www.rakuten.com"
            ],
            '香港/台湾': [
                "https://www.hkt.com",
                "https://www.pchome.com.tw",
                "https://www.momo.com.tw"
            ],
            '中国大陆': [
                "https://www.tencent.com",
                "https://www.alibaba.com",
                "https://www.baidu.com"
            ]
        }
        
        regional_results = {}
        
        for region, urls in regions.items():
            print(f"\n🔍 测试 {region} 地区:")
            region_latencies = []
            
            for url in urls:
                company_name = self._extract_company_name(url)
                latencies = self.test_multiple_samples(url, 3)
                
                if latencies:
                    avg_latency = statistics.mean(latencies)
                    region_latencies.extend(latencies)
                    print(f"   {company_name:12} - {avg_latency:6.1f}ms (样本: {len(latencies)})")
                else:
                    print(f"   {company_name:12} - 连接失败")
            
            if region_latencies:
                region_avg = statistics.mean(region_latencies)
                region_min = min(region_latencies)
                region_max = max(region_latencies)
                regional_results[region] = {
                    'avg': region_avg,
                    'min': region_min,
                    'max': region_max,
                    'samples': len(region_latencies)
                }
                print(f"   📊 {region} 平均: {region_avg:.1f}ms (范围: {region_min:.1f}-{region_max:.1f}ms)")
        
        return regional_results
    
    def _extract_company_name(self, url: str) -> str:
        """从URL提取公司名称"""
        domain_to_name = {
            'samsung.com': 'Samsung',
            'lge.com': 'LG',
            'kakao.com': 'Kakao',
            'nexon.com': 'Nexon',
            'sony.com': 'Sony',
            'nintendo.com': 'Nintendo',
            'rakuten.com': 'Rakuten',
            'hkt.com': 'HKT',
            'pchome.com.tw': 'PChome',
            'momo.com.tw': 'Momo',
            'tencent.com': 'Tencent',
            'alibaba.com': 'Alibaba',
            'baidu.com': 'Baidu'
        }
        
        for domain, name in domain_to_name.items():
            if domain in url:
                return name
        return url.split('//')[1].split('/')[0]
    
    def estimate_korea_latency(self, regional_results: dict) -> dict:
        """基于测试结果估算到韩国的合理延迟"""
        print(f"\n🎯 基于测试结果估算到韩国服务器的延迟:")
        
        estimates = {}
        
        # 如果有韩国数据，直接使用
        if '韩国' in regional_results:
            korea_avg = regional_results['韩国']['avg']
            estimates['direct_korea'] = korea_avg
            print(f"   直接测试韩国: {korea_avg:.1f}ms")
        
        # 基于日本数据估算（地理位置相近）
        if '日本' in regional_results:
            japan_avg = regional_results['日本']['avg']
            # 台湾到韩国比到日本稍微远一点，+10-20ms
            estimated_korea = japan_avg + 15
            estimates['japan_based'] = estimated_korea
            print(f"   基于日本数据: {japan_avg:.1f}ms → 韩国约 {estimated_korea:.1f}ms")
        
        # 基于香港/台湾数据估算
        if '香港/台湾' in regional_results:
            hk_tw_avg = regional_results['香港/台湾']['avg']
            # 台湾内部到韩国，+20-40ms
            estimated_korea = hk_tw_avg + 30
            estimates['hk_tw_based'] = estimated_korea
            print(f"   基于香港台湾: {hk_tw_avg:.1f}ms → 韩国约 {estimated_korea:.1f}ms")
        
        # 计算最终推荐值
        if estimates:
            final_estimate = statistics.mean(estimates.values())
            print(f"   📊 综合估算: {final_estimate:.1f}ms")
            
            # 转换为VPN优化器格式
            return {
                'estimated_korea_latency': final_estimate,
                'confidence': 'high' if len(estimates) >= 2 else 'medium',
                'recommended_preclick_ms': min(final_estimate + 20, 150),  # 加安全边际，但不超过150ms
                'data_sources': list(estimates.keys())
            }
        else:
            print("   ⚠️ 无法获得可靠估算，使用默认值")
            return {
                'estimated_korea_latency': 80,
                'confidence': 'low',
                'recommended_preclick_ms': 100,
                'data_sources': ['default']
            }
    
    def run_comprehensive_test(self):
        """运行综合测试"""
        print("🚀 亚洲地区服务器延迟综合测试")
        print("📍 当前位置: 台湾")
        print("🎯 目标: 估算到韩国的真实延迟\n")
        
        # 分析各地区延迟
        regional_results = self.analyze_regional_latency()
        
        # 估算韩国延迟
        korea_estimate = self.estimate_korea_latency(regional_results)
        
        # 输出最终建议
        print(f"\n✅ 测试完成 - VPN优化建议:")
        print(f"   🇰🇷 估算韩国延迟: {korea_estimate['estimated_korea_latency']:.1f}ms")
        print(f"   ⚡ 建议提前点击: {korea_estimate['recommended_preclick_ms']:.1f}ms")
        print(f"   📊 数据可信度: {korea_estimate['confidence']}")
        print(f"   📈 数据来源: {', '.join(korea_estimate['data_sources'])}")
        
        return korea_estimate


def main():
    tester = NearbyServerTester()
    result = tester.run_comprehensive_test()
    
    # 与当前VPN优化器对比
    print(f"\n📋 对比当前VPN优化器:")
    print(f"   当前检测结果: ~900ms (异常)")
    print(f"   实际测试估算: {result['estimated_korea_latency']:.1f}ms (合理)")
    print(f"   建议使用: {result['recommended_preclick_ms']:.1f}ms 提前点击")


if __name__ == "__main__":
    main() 