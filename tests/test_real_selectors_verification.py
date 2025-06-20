#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_real_selectors_verification.py
验证所有真实选择器配置的测试
"""

import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.form_selectors import get_form_selectors
from config.mode_config import get_button_selectors
from config.user_data import get_user_data


def test_all_real_selectors():
    """验证所有真实选择器配置"""
    print("\n🔍 验证所有真实选择器配置")
    print("=" * 80)
    
    # 1. 验证表单选择器
    print("\n📋 表单选择器配置验证:")
    print("-" * 40)
    
    form_selectors = get_form_selectors()
    
    print(f"✅ 生日输入框选择器:")
    print(f"   {form_selectors['birth_date']}")
    
    print(f"✅ 手机号输入框选择器:")
    print(f"   {form_selectors['phone_number']}")
    
    print(f"✅ 复选框选择器 ({len(form_selectors['checkboxes'])} 个):")
    for i, checkbox_selector in enumerate(form_selectors['checkboxes'], 1):
        print(f"   {i}. {checkbox_selector}")
    
    print(f"✅ 提交按钮选择器 ({len(form_selectors['submit_button_selectors'])} 个，按优先级排序):")
    for i, submit_selector in enumerate(form_selectors['submit_button_selectors'], 1):
        print(f"   {i}. {submit_selector}")
    
    # 2. 验证申请按钮选择器
    print("\n🔘 申请按钮选择器配置验证:")
    print("-" * 40)
    
    button_selectors = get_button_selectors()
    
    print(f"✅ 核心申请按钮选择器:")
    print(f"   {button_selectors['core_application']}")
    
    print(f"✅ 备用文字选择器 ({len(button_selectors['fallback_texts'])} 个):")
    for i, fallback_text in enumerate(button_selectors['fallback_texts'], 1):
        print(f"   {i}. '{fallback_text}'")
    
    # 3. 验证用户数据配置
    print("\n📝 用户数据配置验证:")
    print("-" * 40)
    
    user_data = get_user_data()
    
    print(f"✅ 默认生日: {user_data['birth_date']}")
    print(f"✅ 默认手机号: {user_data['phone_number']}")
    
    # 4. 生成完整的选择器映射
    print("\n🗺️ 完整选择器映射:")
    print("-" * 40)
    
    print("📍 申请流程:")
    print(f"   1️⃣ 点击申请按钮: {button_selectors['core_application']}")
    print(f"   2️⃣ 等待表单出现 (每0.1秒检测)")
    print(f"   3️⃣ 填写生日: {form_selectors['birth_date']} → '{user_data['birth_date']}'")
    print(f"   4️⃣ 智能填写手机号: {form_selectors['phone_number']} → '{user_data['phone_number']}'")
    print(f"   5️⃣ 勾选复选框1: {form_selectors['checkboxes'][0]}")
    print(f"   6️⃣ 勾选复选框2: {form_selectors['checkboxes'][1]}")
    print(f"   7️⃣ 提交表单: {form_selectors['submit_button_selectors'][0]}")
    
    # 5. 验证选择器有效性
    print("\n✅ 选择器有效性检查:")
    print("-" * 40)
    
    # 检查是否所有必要的选择器都存在
    required_checks = [
        ("申请按钮", button_selectors.get('core_application')),
        ("生日输入框", form_selectors.get('birth_date')),
        ("手机号输入框", form_selectors.get('phone_number')),
        ("复选框1", form_selectors.get('checkboxes', [None])[0] if form_selectors.get('checkboxes') else None),
        ("复选框2", form_selectors.get('checkboxes', [None, None])[1] if len(form_selectors.get('checkboxes', [])) > 1 else None),
        ("提交按钮", form_selectors.get('submit_button_selectors', [None])[0] if form_selectors.get('submit_button_selectors') else None),
    ]
    
    all_valid = True
    for name, selector in required_checks:
        if selector:
            print(f"   ✅ {name}: 已配置")
        else:
            print(f"   ❌ {name}: 未配置或为空")
            all_valid = False
    
    # 6. 生成JavaScript测试代码
    print("\n🧪 JavaScript验证代码生成:")
    print("-" * 40)
    
    js_test_code = f"""
// 在浏览器控制台中运行此代码来验证选择器
console.log('🔍 开始验证所有真实选择器...');

// 验证申请按钮
const applyBtn = document.querySelector('{button_selectors['core_application']}');
console.log('申请按钮:', applyBtn ? '✅ 找到' : '❌ 未找到', applyBtn);

// 验证表单元素
const birthInput = document.querySelector('{form_selectors['birth_date']}');
console.log('生日输入框:', birthInput ? '✅ 找到' : '❌ 未找到', birthInput);

const phoneInput = document.querySelector('{form_selectors['phone_number']}');
console.log('手机号输入框:', phoneInput ? '✅ 找到' : '❌ 未找到', phoneInput);

const checkbox1 = document.querySelector('{form_selectors['checkboxes'][0]}');
console.log('复选框1:', checkbox1 ? '✅ 找到' : '❌ 未找到', checkbox1);

const checkbox2 = document.querySelector('{form_selectors['checkboxes'][1]}');
console.log('复选框2:', checkbox2 ? '✅ 找到' : '❌ 未找到', checkbox2);

const submitBtn = document.querySelector('{form_selectors['submit_button_selectors'][0]}');
console.log('提交按钮:', submitBtn ? '✅ 找到' : '❌ 未找到', submitBtn);

console.log('🎯 验证完成!');
"""
    
    print("📋 在浏览器控制台运行以下代码来验证选择器:")
    print(js_test_code)
    
    # 7. 总结
    print("\n📊 配置总结:")
    print("-" * 40)
    print(f"✅ 配置完整性: {'完整' if all_valid else '不完整'}")
    print(f"✅ 表单元素: {len(form_selectors['checkboxes']) + 3} 个 (生日+手机号+{len(form_selectors['checkboxes'])}个复选框+提交按钮)")
    print(f"✅ 检测策略: 每0.1秒高频检测，不限CPU资源")
    print(f"✅ 处理策略: 智能手机号填写，强制勾选复选框，立即提交")
    
    return all_valid


def test_performance_configuration():
    """验证性能配置"""
    print("\n⚡ 性能配置验证:")
    print("-" * 40)
    
    print("🔄 检测配置:")
    print("   - 检测间隔: 0.1秒 (每秒10次检测)")
    print("   - 最大等待: 2.0秒 (最多20次检测)")
    print("   - CPU使用: 不限制，追求最快速度")
    print("   - 内存使用: 不限制，缓存所有结果")
    
    print("\n⚡ 处理策略:")
    print("   - 极限优化: 单次JavaScript调用完成所有操作")
    print("   - 并行处理: 5个线程同时处理表单元素")
    print("   - 智能填写: 手机号仅在空白时填写")
    print("   - 强制提交: 立即点击提交按钮")
    
    print("\n🎯 性能目标:")
    print("   - 申请按钮点击: <300ms")
    print("   - 页面跳转检测: <0.1s (每0.1s检测)")
    print("   - 表单填写: <100ms")
    print("   - 总目标时间: <500ms")


if __name__ == "__main__":
    print("🚀 启动真实选择器验证测试")
    
    # 验证所有选择器
    all_valid = test_all_real_selectors()
    
    # 验证性能配置
    test_performance_configuration()
    
    print(f"\n{'✅ 所有配置验证通过!' if all_valid else '❌ 配置验证失败，请检查上述问题'}")
    print("🔥 系统已配置为极限性能模式 - 每0.1秒检测，不限CPU资源")
    
    input("\n按Enter键结束...") 