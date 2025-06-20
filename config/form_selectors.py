#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
form_selectors.py
表单元素选择器配置
"""

# Weverse表单元素选择器
WEVERSE_FORM_SELECTORS = {
    # 输入框
    'birth_date': '#requiredProperties-birthDate',
    'phone_number': '#requiredProperties-phoneNumber',
    
    # 复选框
    'checkboxes': [
        # 第一个复选框
        '#root > div > div > div > form > section.sc-jJEKmz.hKDpP > div > div > div:nth-child(2) > div > div.sc-fWPcWZ.hNoznW > label > span.sc-khAkCZ.sc-hTZgZg.ewSqYc.fpLDWJ > svg',
        # 第二个复选框  
        '#root > div > div > div > form > section.sc-jJEKmz.hKDpP > div > div > div:nth-child(3) > div > div.sc-fWPcWZ.hNoznW > label > span.sc-khAkCZ.sc-hTZgZg.ewSqYc.fpLDWJ > svg'
    ],
    
    # 提交按钮选择器（按优先级排序）
    'submit_button_selectors': [
        '#root > div > div > div > form > div > input',  # 具体的提交按钮选择器
        'button[type="submit"]',  # 标准提交按钮
        'input[type="submit"]',  # input类型的提交按钮
        'button:contains("참여 신청")',  # 包含"参与申请"文字的按钮
        'button:contains("신청")',  # 包含"申请"文字的按钮
        'button:contains("제출")',  # 包含"提交"文字的按钮
        'button:contains("확인")',  # 包含"确认"文字的按钮
        'button:last-of-type',  # 最后一个按钮（备选）
    ]
}

def get_form_selectors():
    """获取表单选择器配置"""
    return WEVERSE_FORM_SELECTORS 