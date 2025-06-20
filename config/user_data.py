#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
user_data.py
用户数据配置
"""

# 默认用户数据
DEFAULT_USER_DATA = {
    'birth_date': '19900101',  # 生日格式：YYYYMMDD
    'phone_number': '01012345678',  # 韩国手机号格式
}

def get_user_data():
    """获取用户数据"""
    return DEFAULT_USER_DATA

def update_user_data(birth_date=None, phone_number=None):
    """更新用户数据"""
    data = DEFAULT_USER_DATA.copy()
    if birth_date:
        data['birth_date'] = birth_date
    if phone_number:
        data['phone_number'] = phone_number
    return data 