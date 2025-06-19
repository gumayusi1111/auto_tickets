# -*- coding: utf-8 -*-
"""
data_saver.py
数据保存模块
"""

import json
from datetime import datetime
from pathlib import Path


def save_analysis(content, analysis, extracted_times, time_analysis):
    """保存分析结果"""
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"weverse_analysis_{timestamp}.json"
        
        # 获取项目根目录
        current_file = Path(__file__)
        project_root = current_file.parent.parent.parent
        output_path = project_root / "data" / filename
        output_path.parent.mkdir(exist_ok=True)
        
        data = {
            "timestamp": timestamp,
            "original_content": content,
            "extracted_times": extracted_times,
            "time_analysis": time_analysis,
            "ai_analysis": analysis
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2, default=str)
        
        print(f"✅ 分析结果已保存到: {output_path}")
        return str(output_path)
    except Exception as e:
        print(f"❌ 保存失败: {e}")
        return None