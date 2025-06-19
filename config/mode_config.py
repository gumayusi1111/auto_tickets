#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
mode_config.py
模式处理配置文件 - 统一管理模式相关的配置项
"""

import os
from typing import Dict, Any, List

# =============================================================================
# 默认配置常量
# =============================================================================

# 默认用户信息
DEFAULT_USER_INFO = {
    'birth_date': '1990-01-01',
    'phone_number': '13800138000',
    'name': '김민수',
    'email': 'test@example.com'
}

# 按钮选择器配置
BUTTON_SELECTORS = {
    'primary': "#root > div.fixed_bottom_layer.FixedBottomLayerView_fixed_wrap__J2yYZ > div.UserJoinInduceLayerView_container__8AjD7 > div > button",
    'core_application': '#modal > div > div.NoticeModalView_notice_wrap__fhTTz > div.NoticeModalView_floating__Mx9Cs > a',  # 核心申请按钮
    'fallback_texts': ['참여 신청', '신청하기', '참여하기', 'Apply', 'Join'],
    'login_button': 'button[data-testid="login"], .login-button, [class*="login"]',
    'confirm_login': 'button[data-testid="confirm"], .confirm-button, [class*="confirm"]'
}

# =============================================================================
# 模式配置
# =============================================================================

# 统一模式配置
UNIFIED_MODE_CONFIG = {
    'name': '统一自动化模式',
    'description': 'Weverse 统一自动化模式：分析+报名',
    'features': [
        'AI内容分析',
        '时间自动提取',
        '倒计时功能',
        '自动报名',
        '网络监控',
        '表单填写'
    ],
    'default_enable_network_monitor': False,
    'default_enable_ai_analysis': True,
    'default_enable_auto_fill': True
}

# 时间处理配置
TIME_CONFIG = {
    'default_timezone': 'Asia/Shanghai',
    'source_timezone': 'Asia/Seoul',
    'test_time_offset': 5,  # 测试模式下的时间偏移（秒）
    'countdown_update_interval': 1,  # 倒计时更新间隔（秒）
    'countdown_precision': 'milliseconds',  # 新增：倒计时精度
    'pre_click_offset': 0.3,  # 新增：提前点击时间（秒）
    'dynamic_latency_test': True,  # 新增：启用动态延迟测试
    'latency_test_duration': 60,  # 新增：延迟测试时长（秒）
    'min_advance_time': 0.1,  # 新增：最小提前时间
    'max_advance_time': 1.0,   # 新增：最大提前时间
    'time_format': '%Y-%m-%d %H:%M:%S %Z'
}

# 网络监控配置
NETWORK_MONITOR_CONFIG = {
    'capture_duration_before': 2,  # 点击前捕获持续时间（秒）
    'capture_duration_after': 3,   # 点击后捕获持续时间（秒）
    'enable_by_default': False,
    'save_requests': True,
    'print_summary': True
}

# 表单填写配置
FORM_CONFIG = {
    'fill_timeout': 10,  # 填写超时时间（秒）
    'submit_timeout': 15,  # 提交超时时间（秒）
    'retry_count': 3,    # 重试次数
    'wait_between_fills': 0.5,  # 填写间隔（秒）
}

# 浏览器操作配置
BROWSER_OPERATION_CONFIG = {
    'page_load_wait': 20,  # 页面加载等待时间（秒）
    'element_wait': 10,    # 元素等待时间（秒）
    'click_wait': 5,       # 点击等待时间（秒）
    'manual_login_wait': 30,  # 手动登录等待时间（秒）
}

# =============================================================================
# 用户交互配置
# =============================================================================

# 提示信息配置
PROMPT_MESSAGES = {
    'welcome': "🎯 Weverse 统一自动化模式",
    'separator': "=" * 40,
    'input_info': "📝 请输入以下信息：",
    'url_prompt': "🌐 目标URL: ",
    'network_monitor_prompt': "🔍 是否启用网络请求监控功能？(yes/no，默认no): ",
    'birth_date_prompt': "🎂 生日 (格式: 1990-01-01): ",
    'phone_prompt': "📱 手机号: ",
    'manual_time_prompt': "是否手动设置目标时间？(y/n): ",
    'test_time_prompt': "🧪 是否设置为测试时间（当前时间+5秒）？(y/n): ",
    'continue_prompt': "按回车键继续...",
    'close_prompt': "按回车键关闭浏览器..."
}

# 状态消息配置
STATUS_MESSAGES = {
    'page_loading': "🌐 正在访问: {}",
    'page_loaded': "✅ 页面加载完成",
    'page_load_timeout': "⚠️ 页面加载超时，继续执行",
    'login_start': "🔐 开始登录流程...",
    'login_success': "✅ 登录页面响应完成",
    'content_extracting': "📄 正在提取文章内容...",
    'content_extracted': "✅ 成功提取文章内容 ({} 字符)",
    'ai_analyzing': "🤖 正在进行AI分析...",
    'ai_time_analyzing': "⏰ 正在使用AI分析时间信息...",
    'time_set': "🎯 自动设置目标时间: {} ({})",
    'countdown_start': "🚀 启动倒计时模式，目标时间: {}",
    'countdown_stop': "⏹️ 倒计时已停止",
    'application_start': "🎯 开始自动报名流程...",
    'application_success': "✅ 并行处理流程完成!",
    'application_failed': "❌ 并行处理流程失败",
    'network_monitor_start': "📡 网络监控已开始",
    'network_monitor_stop': "📡 正在保存网络监控数据...",
    'cleanup_start': "🧹 清理临时数据...",
    'program_end': "🔚 程序结束，浏览器将保持打开状态",
    'program_interrupted': "⚠️ 程序被用户中断",
    'program_error': "❌ 程序执行出错: {}"
}

# =============================================================================
# 工具函数
# =============================================================================

def get_default_user_info() -> Dict[str, str]:
    """获取默认用户信息"""
    return DEFAULT_USER_INFO.copy()

def get_button_selectors() -> Dict[str, Any]:
    """获取按钮选择器配置"""
    return BUTTON_SELECTORS.copy()

def get_mode_config(mode_name: str = 'unified') -> Dict[str, Any]:
    """
    获取指定模式的配置
    
    Args:
        mode_name: 模式名称
    
    Returns:
        模式配置字典
    """
    configs = {
        'unified': UNIFIED_MODE_CONFIG
    }
    return configs.get(mode_name, {})

def get_time_config() -> Dict[str, Any]:
    """获取时间处理配置"""
    return TIME_CONFIG.copy()

def get_network_monitor_config() -> Dict[str, Any]:
    """获取网络监控配置"""
    return NETWORK_MONITOR_CONFIG.copy()

def get_form_config() -> Dict[str, Any]:
    """获取表单配置"""
    return FORM_CONFIG.copy()

def get_browser_config() -> Dict[str, Any]:
    """获取浏览器操作配置"""
    return BROWSER_OPERATION_CONFIG.copy()

def get_prompt_message(key: str, *args) -> str:
    """
    获取提示信息
    
    Args:
        key: 消息键
        *args: 格式化参数
    
    Returns:
        格式化后的消息
    """
    message = PROMPT_MESSAGES.get(key, key)
    if args:
        try:
            return message.format(*args)
        except:
            return message
    return message

def get_status_message(key: str, *args) -> str:
    """
    获取状态消息
    
    Args:
        key: 消息键
        *args: 格式化参数
    
    Returns:
        格式化后的消息
    """
    message = STATUS_MESSAGES.get(key, key)
    if args:
        try:
            return message.format(*args)
        except:
            return message
    return message

def update_user_info(updates: Dict[str, str]) -> Dict[str, str]:
    """
    更新用户信息
    
    Args:
        updates: 要更新的信息
    
    Returns:
        更新后的用户信息
    """
    user_info = get_default_user_info()
    user_info.update(updates)
    return user_info

def validate_user_input(input_type: str, value: str) -> bool:
    """
    验证用户输入
    
    Args:
        input_type: 输入类型 ('url', 'birth_date', 'phone', 'email')
        value: 输入值
    
    Returns:
        是否有效
    """
    if not value or not isinstance(value, str):
        return False
    
    value = value.strip()
    
    if input_type == 'url':
        return value.startswith(('http://', 'https://'))
    elif input_type == 'birth_date':
        import re
        return bool(re.match(r'^\d{4}-\d{2}-\d{2}$', value))
    elif input_type == 'phone':
        return len(value) >= 10
    elif input_type == 'email':
        import re
        return bool(re.match(r'^[^@]+@[^@]+\.[^@]+$', value))
    
    return True

# =============================================================================
# 环境变量和配置检查
# =============================================================================

def check_environment() -> Dict[str, bool]:
    """
    检查环境配置
    
    Returns:
        环境检查结果
    """
    checks = {
        'ai_config_exists': os.path.exists('config/ai_config.py'),
        'data_dir_exists': os.path.exists('data'),
        'src_dir_exists': os.path.exists('src'),
        'has_deepseek_key': bool(os.getenv('DEEPSEEK_API_KEY')),
        'has_openai_key': bool(os.getenv('OPENAI_API_KEY'))
    }
    
    return checks

if __name__ == "__main__":
    print("🔧 模式配置文件")
    print("=" * 50)
    
    # 显示配置信息
    print(f"统一模式: {UNIFIED_MODE_CONFIG['name']}")
    print(f"功能: {', '.join(UNIFIED_MODE_CONFIG['features'])}")
    
    # 环境检查
    env_checks = check_environment()
    print("\n环境检查:")
    for check, result in env_checks.items():
        status = "✅" if result else "❌"
        print(f"{status} {check}: {result}") 