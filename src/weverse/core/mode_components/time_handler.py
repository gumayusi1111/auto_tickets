#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
time_handler.py
时间处理组件
"""

import json
import pytz
from datetime import datetime, timedelta
from typing import Dict, Optional

from config.mode_config import get_time_config, get_prompt_message, get_status_message
from ...analysis.time_processor import get_time_input


class TimeHandler:
    """时间处理器"""
    
    def __init__(self):
        self.time_config = get_time_config()
        self.china_tz = pytz.timezone(self.time_config['default_timezone'])
        self.korea_tz = pytz.timezone(self.time_config['source_timezone'])
    
    def extract_target_time(self, ai_time_data: Dict) -> Optional[datetime]:
        """从AI时间数据中提取目标时间"""
        if not ai_time_data:
            return None
        
        try:
            print(f"📅 AI提取的时间信息: {json.dumps(ai_time_data, ensure_ascii=False, indent=2)}")
            
            # 获取关键时间点
            key_times = self._collect_key_times(ai_time_data)
            
            if not key_times:
                print("⚠️ 未找到有效的时间点")
                return None
            
            # 按优先级排序并解析时间
            key_times.sort(key=lambda x: x['priority'])
            
            for time_item in key_times:
                target_time = self._parse_time_string(time_item['time'], time_item['description'])
                if target_time:
                    return target_time
            
            return None
            
        except Exception as e:
            print(f"❌ 目标时间提取失败: {e}")
            return None
    
    def _collect_key_times(self, ai_time_data: Dict) -> list:
        """收集关键时间点"""
        key_times = []
        
        # 优先使用申请开始时间
        if ai_time_data.get('申请开始时间'):
            key_times.append({
                'time': ai_time_data['申请开始时间'],
                'description': '申请开始时间',
                'priority': 1
            })
        
        # 添加申请结束时间
        if ai_time_data.get('申请结束时间'):
            key_times.append({
                'time': ai_time_data['申请结束时间'],
                'description': '申请结束时间',
                'priority': 2
            })
        
        # 添加其他重要时间点
        if ai_time_data.get('关键时间点'):
            for point in ai_time_data['关键时间点']:
                if point.get('时间') and point.get('重要性') == '高':
                    key_times.append({
                        'time': point['时间'],
                        'description': point.get('描述', '重要时间点'),
                        'priority': 3
                    })
        
        return key_times
    
    def _parse_time_string(self, time_str: str, description: str) -> Optional[datetime]:
        """解析时间字符串"""
        try:
            if time_str and time_str != 'null':
                parsed_time = datetime.strptime(time_str, "%Y-%m-%d %H:%M")
                korea_time = self.korea_tz.localize(parsed_time)
                china_time = korea_time.astimezone(self.china_tz)
                
                print(f"🇨🇳 {description}: {china_time}")
                print(get_status_message('time_set', china_time, description))
                
                return china_time
        except Exception as e:
            print(f"⚠️ 时间解析失败 {time_str}: {e}")
        
        return None
    
    def handle_time_setup(self, target_time: Optional[datetime]) -> Optional[datetime]:
        """处理时间设置"""
        # 如果没有自动检测到目标时间，询问用户
        if not target_time:
            print("\n⚠️ 未自动检测到目标时间")
            manual_input = input(get_prompt_message('manual_time_prompt')).strip().lower()
            
            if manual_input in ['y', 'yes', '是']:
                target_time = get_time_input()
                if target_time:
                    print(f"✅ 手动设置目标时间: {target_time}")
        
        # 检查时间是否过期
        if target_time:
            target_time = self._validate_and_adjust_time(target_time)
        
        return target_time
    
    def _validate_and_adjust_time(self, target_time: datetime) -> Optional[datetime]:
        """验证和调整时间"""
        current_time = datetime.now(self.china_tz)
        
        if target_time <= current_time:
            print(f"\n⚠️ 目标时间已过期!")
            print(f"   目标时间: {target_time}")
            print(f"   当前时间: {current_time}")
            
            test_choice = input(get_prompt_message('test_time_prompt')).strip().lower()
            if test_choice in ['y', 'yes', '是']:
                target_time = current_time + timedelta(seconds=self.time_config['test_time_offset'])
                print(f"✅ 已设置测试时间: {target_time}")
                return target_time
            else:
                print("❌ 取消自动报名")
                return None
        
        return target_time
    
    def get_timezone_info(self) -> Dict[str, str]:
        """获取时区信息"""
        return {
            'china_timezone': self.time_config['default_timezone'],
            'korea_timezone': self.time_config['source_timezone']
        } 