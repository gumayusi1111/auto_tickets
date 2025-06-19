#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
vpn模块 - VPN延迟优化功能
"""

from .shanghai_korea_optimizer import (
    ShanghaiKoreaOptimizer,
    optimize_shanghai_korea_latency
)

__all__ = [
    'ShanghaiKoreaOptimizer',
    'optimize_shanghai_korea_latency'
]
