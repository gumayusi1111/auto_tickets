#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
config_ai.py
AI分析配置文件 - 存储API密钥和模型配置
"""

import os
from typing import Dict, Any

# =============================================================================
# AI模型配置
# =============================================================================

# DeepSeek配置
DEEPSEEK_CONFIG = {
    'api_key': os.getenv('DEEPSEEK_API_KEY', 'sk-d246fe03fd164cf3abf49f45d0220d21'),  # 从环境变量获取，默认使用提供的密钥
    'base_url': 'https://api.deepseek.com',
    'model_name': 'deepseek-reasoner',  # 使用推理模型
    'chat_model': 'deepseek-chat',  # 聊天模型
    'max_tokens': 2000,
    'temperature': 0.1,  # 降低温度提高准确性
    'timeout': 60  # 推理模型需要更长时间
}

# OpenAI配置
OPENAI_CONFIG = {
    'api_key': os.getenv('OPENAI_API_KEY', ''),  # 从环境变量获取
    'base_url': 'https://api.openai.com',  # 可以修改为中转服务地址
    'model_name': 'gpt-3.5-turbo',  # 或 'gpt-4'
    'max_tokens': 2000,
    'temperature': 0.7,
    'timeout': 30
}

# 中转服务配置示例（如果使用中转服务）
# OPENAI_CONFIG['base_url'] = 'https://your-proxy-service.com'  # 替换为你的中转服务地址

# =============================================================================
# 演唱会信息提取配置
# =============================================================================

# 默认选择器配置
DEFAULT_SELECTORS = {
    'weverse_notice': {
        'primary': "#modal > div > div.NoticeModalView_notice_wrap__fhTTz > div.NoticeModalView_detail__t4JWo.NoticeModalView_-show_button__r9Yi5 > div > p:nth-child(1)",
        'fallback': [
            "#modal p",
            ".NoticeModalView_detail__t4JWo p",
            "[class*='notice'] p",
            "[class*='detail'] p"
        ]
    },
    'general': {
        'primary': "p",
        'fallback': [
            "div",
            "span",
            "article",
            "section"
        ]
    }
}

# 时间格式配置
TIME_PATTERNS = {
    'korean_formats': [
        r'(\d{4})년\s*(\d{1,2})월\s*(\d{1,2})일\s*\(([^)]+)\)\s*(\d{1,2}):(\d{2})',  # 2024년 1월 15일 (월) 19:00
        r'(\d{4})\.(\d{1,2})\.(\d{1,2})\s*\(([^)]+)\)\s*(\d{1,2}):(\d{2})',      # 2024.01.15 (월) 19:00
        r'(\d{1,2})월\s*(\d{1,2})일\s*\(([^)]+)\)\s*(\d{1,2}):(\d{2})',         # 1월 15일 (월) 19:00
        r'(\d{1,2})/(\d{1,2})\s*\(([^)]+)\)\s*(\d{1,2}):(\d{2})',             # 1/15 (월) 19:00
    ],
    'international_formats': [
        r'(\d{4})-(\d{1,2})-(\d{1,2})\s+(\d{1,2}):(\d{2})',                   # 2024-01-15 19:00
        r'(\d{1,2})/(\d{1,2})/(\d{4})\s+(\d{1,2}):(\d{2})',                   # 01/15/2024 19:00
        r'(\d{4})\.(\d{1,2})\.(\d{1,2})\s+(\d{1,2}):(\d{2})',                 # 2024.01.15 19:00
    ]
}

# =============================================================================
# 浏览器配置
# =============================================================================

BROWSER_CONFIG = {
    'headless': False,  # 默认显示浏览器
    'window_size': (1920, 1080),
    'user_agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'page_load_timeout': 30,
    'implicit_wait': 10,
    'explicit_wait': 15
}

# =============================================================================
# 显示配置
# =============================================================================

DISPLAY_CONFIG = {
    'update_interval': 1,  # 实时显示更新间隔（秒）
    'max_text_length': 500,  # 显示文本的最大长度
    'max_analysis_length': 1000,  # 显示AI分析的最大长度
    'clear_screen': True,  # 是否清屏
    'show_timestamps': True,  # 是否显示时间戳
    'show_ai_model': True  # 是否显示AI模型信息
}

# =============================================================================
# 提示词模板
# =============================================================================

PROMPT_TEMPLATES = {
    'concert_analysis': """
请分析以下演唱会信息，并提供详细的分析结果：

原始信息：
{raw_text}

提取的时间信息：
{time_info}

页面URL: {url}
提取时间: {extracted_at}

请从以下角度进行分析：

1. **演唱会基本信息**：
   - 艺人/团体名称
   - 演唱会名称或主题
   - 举办地点
   - 演出时间（请确认时区转换是否正确）

2. **时间分析**：
   - 验证提取的时间信息是否准确
   - 时区转换是否正确（韩国时间转中国时间）
   - 是否有多个时间点（如多场演出）

3. **重要提醒**：
   - 距离演出还有多长时间
   - 是否需要特别关注的时间节点
   - 购票或报名的重要时间

4. **建议行动**：
   - 用户应该在什么时候开始准备
   - 需要设置哪些提醒
   - 其他注意事项

请用中文回答，格式清晰，重点突出。如果发现时间信息有误或不完整，请指出并给出建议。
""",
    
    'page_content_analysis': """
请分析以下网页内容，提取所有有用的信息：

页面标题: {title}
页面URL: {url}

页面内容:
{content}

请提供以下分析：
1. 页面主要内容概述
2. 重要时间信息（如有）
3. 关键信息提取
4. 用户可能关心的要点
5. 建议的后续行动

请用中文回答，条理清晰。
"""
}

# =============================================================================
# 工具函数
# =============================================================================

def get_config(config_type: str) -> Dict[str, Any]:
    """
    获取指定类型的配置
    
    Args:
        config_type: 配置类型 ('deepseek', 'openai', 'browser', 'display')
    
    Returns:
        配置字典
    """
    configs = {
        'deepseek': DEEPSEEK_CONFIG,
        'openai': OPENAI_CONFIG,
        'browser': BROWSER_CONFIG,
        'display': DISPLAY_CONFIG
    }
    
    return configs.get(config_type, {})

def update_config(config_type: str, updates: Dict[str, Any]) -> bool:
    """
    更新配置
    
    Args:
        config_type: 配置类型
        updates: 要更新的配置项
    
    Returns:
        是否更新成功
    """
    try:
        config = get_config(config_type)
        if config:
            config.update(updates)
            return True
        return False
    except Exception:
        return False

def validate_api_key(api_key: str, model_type: str) -> bool:
    """
    验证API密钥格式
    
    Args:
        api_key: API密钥
        model_type: 模型类型
    
    Returns:
        是否有效
    """
    if not api_key or not isinstance(api_key, str):
        return False
    
    # 基本长度检查
    if len(api_key.strip()) < 10:
        return False
    
    # 模型特定检查
    if model_type == 'deepseek':
        # DeepSeek API密钥通常以sk-开头
        return api_key.strip().startswith('sk-')
    elif model_type == 'openai':
        # OpenAI API密钥通常以sk-开头
        return api_key.strip().startswith('sk-')
    
    return True

# =============================================================================
# 环境变量设置说明
# =============================================================================

ENV_SETUP_INSTRUCTIONS = """
环境变量设置说明：

1. DeepSeek API密钥：
   export DEEPSEEK_API_KEY="your_deepseek_api_key_here"

2. OpenAI API密钥：
   export OPENAI_API_KEY="your_openai_api_key_here"

3. 永久设置（添加到 ~/.bashrc 或 ~/.zshrc）：
   echo 'export DEEPSEEK_API_KEY="your_key"' >> ~/.bashrc
   echo 'export OPENAI_API_KEY="your_key"' >> ~/.bashrc
   source ~/.bashrc

4. 临时设置（仅当前会话有效）：
   export DEEPSEEK_API_KEY="your_key"

注意：请将 "your_key" 替换为你的实际API密钥
"""

if __name__ == "__main__":
    print("🔧 AI分析配置文件")
    print("=" * 50)
    print(ENV_SETUP_INSTRUCTIONS)