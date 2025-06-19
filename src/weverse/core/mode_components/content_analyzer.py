#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
content_analyzer.py
内容分析组件
"""

import json
from typing import Dict, Optional, Tuple, Any

from config.mode_config import get_status_message
from ...analysis.content_extractor import extract_article_content
from ...analysis.time_processor import extract_time_info
from ...ai.analyzer import analyze_with_ai, extract_time_with_ai
from ...analysis.data_saver import save_analysis


class ContentAnalyzer:
    """内容分析器"""
    
    def __init__(self, driver: Any, wait: Any):
        self.driver = driver
        self.wait = wait
    
    def analyze_page_content(self) -> Tuple[Optional[str], Optional[Dict], Optional[str]]:
        """分析页面内容"""
        try:
            # 提取文章内容
            print(get_status_message('content_extracting'))
            article_content = extract_article_content(self.driver, self.wait)
            
            if not article_content:
                print("❌ 未能提取到文章内容")
                return None, None, None
            
            print(get_status_message('content_extracted', len(article_content)))
            
            # 使用AI提取时间信息
            print(get_status_message('ai_time_analyzing'))
            ai_time_data = extract_time_with_ai(article_content)
            
            # 备用方案：传统时间提取
            time_info = None
            if not ai_time_data:
                print("⚠️ AI时间提取失败，使用传统正则表达式方法...")
                time_info = extract_time_info(article_content)
            
            # AI分析
            print(get_status_message('ai_analyzing'))
            analysis_result = analyze_with_ai(article_content, time_info)
            
            if analysis_result:
                print("\n📊 AI分析结果:")
                print(analysis_result)
                self._save_analysis_data(article_content, analysis_result, ai_time_data or time_info)
                print("\n💾 分析结果已保存")
            
            return article_content, ai_time_data or time_info, analysis_result
            
        except Exception as e:
            print(f"❌ 内容分析失败: {e}")
            return None, None, None
    
    def _save_analysis_data(self, article_content: str, analysis_result: str, time_info: Optional[Dict]) -> None:
        """保存分析数据"""
        try:
            save_analysis(article_content, analysis_result, time_info, {})
        except Exception as e:
            print(f"⚠️ 分析数据保存失败: {e}")
    
    def print_analysis_summary(self, ai_time_data: Dict, analysis_result: str) -> None:
        """打印分析摘要"""
        try:
            print("\n📊 分析摘要:")
            
            if ai_time_data:
                print(f"📅 AI提取的时间信息:")
                print(f"   {json.dumps(ai_time_data, ensure_ascii=False, indent=4)}")
            
            if analysis_result:
                print(f"🤖 AI分析结果:")
                # 只显示前200个字符的摘要
                summary = analysis_result[:200] + "..." if len(analysis_result) > 200 else analysis_result
                print(f"   {summary}")
                
        except Exception as e:
            print(f"⚠️ 分析摘要显示失败: {e}") 