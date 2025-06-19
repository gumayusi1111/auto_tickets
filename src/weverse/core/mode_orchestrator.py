#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
mode_orchestrator.py
模式编排器 - 组合所有组件的主文件
"""

from typing import Dict, Any, Optional
from datetime import datetime

# 导入所有组件
from .mode_components.input_collector import InputCollector
from .mode_components.browser_manager import BrowserManager
from .mode_components.content_analyzer import ContentAnalyzer
from .mode_components.time_handler import TimeHandler
from .mode_components.application_executor import ApplicationExecutor
from .mode_components.monitoring_handler import MonitoringHandler


class ModeOrchestrator:
    """模式编排器 - 协调所有组件的主类"""
    
    def __init__(self):
        """初始化编排器"""
        # 组件实例
        self.input_collector = InputCollector()
        self.browser_manager = BrowserManager()
        self.content_analyzer = None  # 需要driver和wait，稍后初始化
        self.time_handler = TimeHandler()
        self.application_executor = None  # 需要driver和wait，稍后初始化
        self.monitoring_handler = None  # 需要driver，稍后初始化
        
        # 会话数据
        self.user_info: Dict[str, Any] = {}
        self.session_data: Dict[str, Any] = {}
    
    def run_unified_mode(self) -> bool:
        """运行统一模式 - 主入口函数"""
        try:
            print("🚀 启动 Weverse 智能申请系统")
            print("=" * 60)
            
            # 阶段1: 收集用户输入
            if not self._phase_1_collect_input():
                return False
            
            # 阶段2: 初始化浏览器和网络
            if not self._phase_2_setup_browser():
                return False
            
            # 阶段3: 导航和登录
            if not self._phase_3_navigate_and_login():
                return False
            
            # 阶段4: 分析内容和时间
            article_content, ai_time_data, analysis_result = self._phase_4_analyze_content()
            if not article_content:
                return False
            
            # 阶段5: 处理时间设置
            target_time = self._phase_5_handle_time(ai_time_data)
            if not target_time:
                return False
            
            # 阶段6: 执行申请流程
            if not self._phase_6_execute_application(target_time):
                return False
            
            # 阶段7: 清理和结束
            self._phase_7_cleanup()
            
            print("\n✅ 程序执行完成!")
            return True
            
        except KeyboardInterrupt:
            print("\n⚠️ 程序被用户中断")
            self._phase_7_cleanup()
            return False
        except Exception as e:
            print(f"\n❌ 程序执行过程中出现错误: {e}")
            import traceback
            traceback.print_exc()
            self._phase_7_cleanup()
            return False
    
    def _phase_1_collect_input(self) -> bool:
        """阶段1: 收集用户输入"""
        print("\n📝 阶段1: 收集用户输入")
        print("-" * 30)
        
        self.user_info = self.input_collector.collect_user_input()
        if not self.user_info:
            print("❌ 用户输入收集失败")
            return False
        
        print("✅ 用户输入收集完成")
        return True
    
    def _phase_2_setup_browser(self) -> bool:
        """阶段2: 设置浏览器和网络"""
        print("\n🌐 阶段2: 设置浏览器和网络")
        print("-" * 30)
        
        # 初始化浏览器
        if not self.browser_manager.initialize_browser():
            return False
        
        # 初始化网络监控
        if not self.browser_manager.initialize_network_monitor(
            self.user_info.get('enable_network_monitor', False)
        ):
            return False
        
        # 初始化依赖driver的组件
        driver = self.browser_manager.get_driver()
        wait = self.browser_manager.get_wait()
        network_monitor = self.browser_manager.get_network_monitor()
        
        self.content_analyzer = ContentAnalyzer(driver, wait)
        self.application_executor = ApplicationExecutor(driver, wait, network_monitor)
        self.monitoring_handler = MonitoringHandler(driver, network_monitor)
        
        print("✅ 浏览器和网络设置完成")
        return True
    
    def _phase_3_navigate_and_login(self) -> bool:
        """阶段3: 导航和登录"""
        print("\n🔐 阶段3: 导航和登录")
        print("-" * 30)
        
        # 导航到目标页面
        if not self.browser_manager.navigate_to_page(self.user_info['target_url']):
            return False
        
        # 处理登录流程
        if not self.browser_manager.handle_login_flow():
            return False
        
        print("✅ 导航和登录完成")
        return True
    
    def _phase_4_analyze_content(self) -> tuple:
        """阶段4: 分析内容"""
        print("\n🧠 阶段4: 分析内容")
        print("-" * 30)
        
        article_content, ai_time_data, analysis_result = self.content_analyzer.analyze_page_content()
        
        if article_content and ai_time_data:
            self.content_analyzer.print_analysis_summary(ai_time_data, analysis_result or "")
        
        return article_content, ai_time_data, analysis_result
    
    def _phase_5_handle_time(self, ai_time_data: Optional[Dict]) -> Optional[datetime]:
        """阶段5: 处理时间"""
        print("\n⏰ 阶段5: 处理时间")
        print("-" * 30)
        
        # 提取目标时间
        target_time = self.time_handler.extract_target_time(ai_time_data)
        
        # 处理时间设置
        target_time = self.time_handler.handle_time_setup(target_time)
        
        if target_time:
            print(f"✅ 目标时间确定: {target_time}")
        else:
            print("❌ 未能确定目标时间")
        
        return target_time
    
    def _phase_6_execute_application(self, target_time: datetime) -> bool:
        """阶段6: 执行申请流程"""
        print("\n🚀 阶段6: 执行申请流程")
        print("-" * 30)
        
        auto_fill_mode = self.user_info.get('auto_fill_mode', True)
        
        if auto_fill_mode:
            print("🤖 执行自动填写模式")
            success = self.application_executor.execute_countdown_and_application(
                target_time, auto_fill_mode
            )
        else:
            print("👁️ 执行监控模式")
            # 先执行倒计时和点击
            success = self.application_executor.execute_countdown_and_application(
                target_time, auto_fill_mode
            )
            
            if success:
                # 然后启动综合数据监控
                print("\n开始综合数据监控...")
                monitoring_data = self.monitoring_handler.start_comprehensive_monitoring()
                self.monitoring_handler.print_monitoring_summary(monitoring_data)
                
                # 保存监控数据
                self._save_monitoring_data(monitoring_data)
        
        return success
    
    def _phase_7_cleanup(self) -> None:
        """阶段7: 清理和结束"""
        print("\n🧹 阶段7: 清理资源")
        print("-" * 30)
        
        if self.browser_manager:
            self.browser_manager.cleanup()
        
        print("✅ 清理完成")
    
    def _save_monitoring_data(self, monitoring_data: Dict[str, Any]) -> None:
        """保存监控数据"""
        try:
            import json
            import os
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            # 确保data目录存在
            data_dir = "data"
            os.makedirs(data_dir, exist_ok=True)
            
            filename = os.path.join(data_dir, f"monitoring_session_{timestamp}.json")
            
            # 保存完整会话数据
            session_data = {
                'metadata': {
                    'timestamp': timestamp,
                    'mode': 'monitoring',
                    'target_url': self.user_info.get('target_url', ''),
                    'user_info': {
                        'birth_date': self.user_info.get('birth_date', ''),
                        'phone_number': self.user_info.get('phone_number', '')
                    }
                },
                'monitoring_data': monitoring_data
            }
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, ensure_ascii=False, indent=2)
            
            print(f"📁 监控会话数据已保存到: {filename}")
            
            # 打印数据摘要
            self._print_session_summary(session_data)
            
        except Exception as e:
            print(f"❌ 保存监控数据失败: {e}")
    
    def _print_session_summary(self, session_data: Dict[str, Any]) -> None:
        """打印会话摘要"""
        try:
            print("\n📊 会话摘要:")
            
            metadata = session_data.get('metadata', {})
            monitoring_data = session_data.get('monitoring_data', {})
            
            print(f"   📅 时间: {metadata.get('timestamp', 'N/A')}")
            print(f"   🎯 模式: {metadata.get('mode', 'N/A')}")
            print(f"   🌐 URL: {metadata.get('target_url', 'N/A')}")
            
            if monitoring_data:
                network_requests = monitoring_data.get('network_requests', [])
                elements_discovered = monitoring_data.get('elements_discovered', {})
                
                print(f"   📡 网络请求: {len(network_requests)}个")
                if elements_discovered:
                    input_count = len(elements_discovered.get('input_fields', []))
                    checkbox_count = len(elements_discovered.get('checkboxes', []))
                    button_count = len(elements_discovered.get('buttons', []))
                    print(f"   🔍 元素发现: {input_count}个输入框, {checkbox_count}个复选框, {button_count}个按钮")
                    
        except Exception as e:
            print(f"⚠️ 会话摘要显示失败: {e}")


def unified_mode():
    """统一模式入口函数 - 向后兼容"""
    orchestrator = ModeOrchestrator()
    return orchestrator.run_unified_mode() 