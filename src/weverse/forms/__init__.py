#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
forms模块 - 表单处理相关功能
"""

from .lightning_form_processor import (
    LightningFormProcessor,
    process_form_lightning_fast,
    capture_and_process_complete_flow
)

# korean_form_handler已被lightning_form_processor替代

__all__ = [
    'LightningFormProcessor',
    'process_form_lightning_fast', 
    'capture_and_process_complete_flow'
]
