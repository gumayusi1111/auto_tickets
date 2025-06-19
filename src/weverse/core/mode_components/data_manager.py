#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
data_manager.py
数据管理组件
"""

import json
import os
from datetime import datetime
from typing import Dict, Any, Optional


class DataManager:
    """数据管理器"""
    
    def __init__(self):
        self.data_dir = "data"
        self._ensure_data_directory()
    
    def _ensure_data_directory(self) -> None:
        """确保数据目录存在"""
        os.makedirs(self.data_dir, exist_ok=True)
    
    def save_monitoring_data(self, monitoring_data: Dict[str, Any], user_info: Dict[str, Any]) -> str:
        """保存监控数据"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = os.path.join(self.data_dir, f"monitoring_data_{timestamp}.json")
            
            # 添加元数据
            save_data = {
                'metadata': {
                    'timestamp': timestamp,
                    'mode': 'monitoring',
                    'target_url': user_info.get('target_url', ''),
                    'user_info': {
                        'birth_date': user_info.get('birth_date', ''),
                        'phone_number': user_info.get('phone_number', '')
                    }
                },
                'monitoring_data': monitoring_data
            }
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, ensure_ascii=False, indent=2)
            
            print(f"📁 监控数据已保存到: {filename}")
            return filename
            
        except Exception as e:
            print(f"❌ 保存监控数据失败: {e}")
            return ""
    
    def save_application_data(self, application_results: Dict[str, Any], user_info: Dict[str, Any]) -> str:
        """保存申请数据"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = os.path.join(self.data_dir, f"application_data_{timestamp}.json")
            
            # 创建统一的数据结构
            unified_data = {
                'application_metadata': {
                    'target_url': user_info.get('target_url', ''),
                    'timestamp': datetime.now().isoformat(),
                    'mode': 'auto_fill' if user_info.get('auto_fill_mode') else 'monitoring',
                    'user_info': {
                        'birth_date': user_info.get('birth_date', ''),
                        'phone_number': user_info.get('phone_number', ''),
                        'name': user_info.get('name', ''),
                        'email': user_info.get('email', '')
                    }
                },
                'application_results': application_results
            }
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(unified_data, f, ensure_ascii=False, indent=2)
            
            print(f"📁 申请数据已保存到: {filename}")
            return filename
            
        except Exception as e:
            print(f"❌ 保存申请数据失败: {e}")
            return ""
    
    def save_unified_session_data(self, session_data: Dict[str, Any]) -> str:
        """保存统一的会话数据"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = os.path.join(self.data_dir, f"unified_session_{timestamp}.json")
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, ensure_ascii=False, indent=2)
            
            print(f"📁 会话数据已保存到: {filename}")
            return filename
            
        except Exception as e:
            print(f"❌ 保存会话数据失败: {e}")
            return ""
    
    def print_data_summary(self, data: Dict[str, Any]) -> None:
        """打印数据摘要"""
        try:
            print("\n📊 数据摘要:")
            
            # 基本信息
            metadata = data.get('metadata', {}) or data.get('application_metadata', {})
            if metadata:
                print(f"   📅 时间戳: {metadata.get('timestamp', 'N/A')}")
                print(f"   🎯 模式: {metadata.get('mode', 'N/A')}")
                print(f"   🌐 目标URL: {metadata.get('target_url', 'N/A')}")
            
            # 监控数据摘要
            if 'monitoring_data' in data:
                monitoring_data = data['monitoring_data']
                network_requests = monitoring_data.get('network_requests', [])
                elements_discovered = monitoring_data.get('elements_discovered', {})
                
                print(f"   📡 网络请求: {len(network_requests)}个")
                print(f"   🔍 元素发现: {len(elements_discovered.get('input_fields', []))}个输入框, {len(elements_discovered.get('checkboxes', []))}个复选框")
            
            # 申请结果摘要
            if 'application_results' in data:
                app_results = data['application_results']
                print(f"   ✅ 申请成功: {'是' if app_results.get('success') else '否'}")
                if 'total_time_ms' in app_results:
                    print(f"   ⏱️ 总时长: {app_results['total_time_ms']:.1f}ms")
            
            # 文件大小
            try:
                data_size = len(json.dumps(data, ensure_ascii=False))
                print(f"   📏 数据大小: {data_size} 字符")
            except:
                pass
                
        except Exception as e:
            print(f"⚠️ 数据摘要显示失败: {e}")
    
    def load_latest_data(self, data_type: str = "all") -> Optional[Dict[str, Any]]:
        """加载最新的数据文件"""
        try:
            # 获取数据目录中的所有文件
            files = []
            for filename in os.listdir(self.data_dir):
                if filename.endswith('.json'):
                    if data_type == "all" or data_type in filename:
                        filepath = os.path.join(self.data_dir, filename)
                        files.append((filepath, os.path.getmtime(filepath)))
            
            if not files:
                print(f"⚠️ 未找到{data_type}类型的数据文件")
                return None
            
            # 按修改时间排序，获取最新的文件
            latest_file = max(files, key=lambda x: x[1])[0]
            
            with open(latest_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            print(f"📁 已加载最新数据: {latest_file}")
            return data
            
        except Exception as e:
            print(f"❌ 加载数据失败: {e}")
            return None
    
    def get_data_directory(self) -> str:
        """获取数据目录路径"""
        return os.path.abspath(self.data_dir)
    
    def list_data_files(self) -> list:
        """列出所有数据文件"""
        try:
            files = []
            for filename in os.listdir(self.data_dir):
                if filename.endswith('.json'):
                    filepath = os.path.join(self.data_dir, filename)
                    size = os.path.getsize(filepath)
                    mtime = datetime.fromtimestamp(os.path.getmtime(filepath))
                    files.append({
                        'filename': filename,
                        'filepath': filepath,
                        'size': size,
                        'modified_time': mtime.isoformat()
                    })
            
            # 按修改时间倒序排列
            files.sort(key=lambda x: x['modified_time'], reverse=True)
            return files
            
        except Exception as e:
            print(f"❌ 列出数据文件失败: {e}")
            return []