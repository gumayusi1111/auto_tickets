# -*- coding: utf-8 -*-
"""
latency_config.py
延迟优化配置文件 - 基于实测数据的精准配置
"""

# 网络延迟配置（基于Postman实测）
NETWORK_LATENCY_CONFIG = {
    # 外部请求延迟（Postman GET请求）
    'external_request': {
        'base_latency_ms': 730,  # Postman GET请求实测值
        'description': '从外部直接请求服务器（新建连接）'
    },
    
    # 页面内跳转延迟（预估值）
    'internal_navigation': {
        'base_latency_ms': 300,  # 页面内跳转通常更快
        'description': '页面内跳转（复用连接、可能有缓存）'
    },
    
    # 浏览器额外开销（毫秒）
    'browser_overhead_ms': 80,  # 包括DOM渲染、JavaScript执行等
    
    # 安全边际（毫秒）
    'safety_margin_ms': 100,  # 确保不会提前点击
    
    # 总提前时间（毫秒）- 默认使用页面内跳转值
    'total_preclick_ms': 480,  # 300 + 80 + 100（页面内跳转场景）
    
    # 场景选择
    'scenario': 'internal',  # 'external' 或 'internal'
    
    # 动态调整参数
    'dynamic_adjustment': {
        'enabled': True,  # 是否启用动态调整
        'weight_measured': 0.7,  # 实测值权重
        'weight_realtime': 0.3,  # 实时检测权重
        'max_deviation_ms': 200,  # 触发调整的最大偏差
    },
    
    # 延迟范围限制
    'limits': {
        'min_ms': 300,  # 最小提前时间（降低到300ms）
        'max_ms': 1200,  # 最大提前时间
    }
}

# 监控配置
MONITORING_CONFIG = {
    # 监控间隔（毫秒）
    'check_interval_ms': 500,  # 每0.5秒检查一次
    
    # 数据快照间隔（秒）
    'snapshot_interval_s': 10,  # 每10秒保存一次快照
    
    # 请求详细记录
    'detailed_request_logging': {
        'enabled': True,
        'methods': ['POST', 'PUT'],  # 详细记录的方法
        'keywords': ['api', 'submit', 'form'],  # URL关键词
    },
    
    # 用户操作追踪
    'user_action_tracking': {
        'enabled': True,
        'track_clicks': True,
        'track_inputs': True,
        'track_form_submits': True,
        'track_checkbox_changes': True,
    }
}

# 性能优化配置
PERFORMANCE_CONFIG = {
    # 表单处理目标时间（毫秒）
    'form_fill_target_ms': 500,  # 0.5秒内完成
    
    # 并行处理
    'parallel_processing': {
        'enabled': True,
        'max_workers': 4,
    },
    
    # JavaScript执行优化
    'js_optimization': {
        'use_direct_js': True,  # 使用JavaScript直接操作DOM
        'batch_operations': True,  # 批量执行操作
    }
}

def get_optimized_preclick_ms(scenario='internal'):
    """
    获取优化的提前点击时间（毫秒）
    
    Args:
        scenario: 'external' (外部请求) 或 'internal' (页面内跳转)
    """
    if scenario == 'external':
        # 外部请求：730 + 80 + 100 = 910ms
        base = NETWORK_LATENCY_CONFIG['external_request']['base_latency_ms']
    else:
        # 页面内跳转：300 + 80 + 100 = 480ms
        base = NETWORK_LATENCY_CONFIG['internal_navigation']['base_latency_ms']
    
    overhead = NETWORK_LATENCY_CONFIG['browser_overhead_ms']
    margin = NETWORK_LATENCY_CONFIG['safety_margin_ms']
    
    return base + overhead + margin

def get_latency_config():
    """获取完整的延迟配置"""
    return NETWORK_LATENCY_CONFIG

def get_monitoring_config():
    """获取监控配置"""
    return MONITORING_CONFIG

def get_performance_config():
    """获取性能配置"""
    return PERFORMANCE_CONFIG 