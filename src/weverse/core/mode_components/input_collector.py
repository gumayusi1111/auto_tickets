#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
input_collector.py
用户输入收集组件
"""

from typing import Dict, Optional
from config.mode_config import (
    get_default_user_info, get_prompt_message,
    validate_user_input
)


class InputCollector:
    """用户输入收集器"""
    
    def __init__(self):
        self.user_info: Dict = {}
    
    def collect_user_input(self) -> Dict[str, any]:
        """收集用户输入信息"""
        try:
            print(get_prompt_message('welcome'))
            print(get_prompt_message('separator'))
            print(get_prompt_message('input_info'))
            
            # 获取目标URL
            target_url = self._get_target_url()
            if not target_url:
                return {}
            
            # 选择运行模式
            auto_fill_mode = self._get_mode_selection()
            
            # 询问是否启用网络监控
            enable_network_monitor = self._get_network_monitor_preference()
            
            # 获取生日信息
            birth_date = self._get_birth_date()
            
            # 获取手机号
            phone_number = self._get_phone_number()
            
            # 获取默认信息
            default_info = get_default_user_info()
            
            # 组装用户信息
            self.user_info = {
                'target_url': target_url,
                'auto_fill_mode': auto_fill_mode,
                'enable_network_monitor': enable_network_monitor,
                'birth_date': birth_date,
                'phone_number': phone_number,
                'name': default_info['name'],
                'email': default_info['email']
            }
            
            print("\n⏰ 目标时间将通过AI分析自动获取")
            return self.user_info
            
        except Exception as e:
            print(f"❌ 用户输入收集失败: {e}")
            return {}
    
    def _get_target_url(self) -> Optional[str]:
        """获取目标URL"""
        target_url = input(get_prompt_message('url_prompt')).strip()
        if not target_url or not validate_user_input('url', target_url):
            print("❌ URL不能为空或格式不正确")
            return None
        return target_url
    
    def _get_mode_selection(self) -> bool:
        """获取模式选择"""
        print("\n🎯 请选择运行模式:")
        print("1. 自动填写模式 - 程序自动填写表单")
        print("2. 监控模式 - 只点击申请按钮，用户手动填写，程序监控请求")
        mode_choice = input("请选择模式 (1/2): ").strip()
        
        auto_fill_mode = mode_choice == "1"
        if auto_fill_mode:
            print("✅ 已选择: 自动填写模式")
        else:
            print("✅ 已选择: 监控模式 (手动填写)")
        
        return auto_fill_mode
    
    def _get_network_monitor_preference(self) -> bool:
        """获取网络监控偏好"""
        network_monitor_input = input(get_prompt_message('network_monitor_prompt')).strip().lower()
        return network_monitor_input in ['yes', 'y', '是']
    
    def _get_birth_date(self) -> str:
        """获取生日信息"""
        default_info = get_default_user_info()
        birth_date = input(get_prompt_message('birth_date_prompt')).strip()
        
        if not birth_date:
            birth_date = default_info['birth_date']
            print(f"使用默认生日: {birth_date}")
        elif not validate_user_input('birth_date', birth_date):
            print("⚠️ 生日格式不正确，使用默认值")
            birth_date = default_info['birth_date']
        
        return birth_date
    
    def _get_phone_number(self) -> str:
        """获取手机号"""
        default_info = get_default_user_info()
        phone_number = input(get_prompt_message('phone_prompt')).strip()
        
        if not phone_number:
            phone_number = default_info['phone_number']
            print(f"使用默认手机号: {phone_number}")
        
        return phone_number
    
    def get_user_info(self) -> Dict[str, any]:
        """获取收集的用户信息"""
        return self.user_info 