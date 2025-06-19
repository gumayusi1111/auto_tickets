#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
browser_manager.py
浏览器管理组件
"""

from typing import Optional, Any
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from config.mode_config import get_browser_config, get_network_monitor_config, get_status_message
from ...browser.setup import setup_driver, create_wait
from ...auth.login_handler import click_login_button_only, click_confirm_login_button, wait_for_manual_login


class BrowserManager:
    """浏览器管理器"""
    
    def __init__(self):
        self.driver: Optional[Any] = None
        self.wait: Optional[Any] = None
        self.network_monitor: Optional[Any] = None
        self.browser_config = get_browser_config()
        self.network_config = get_network_monitor_config()
    
    def initialize_browser(self) -> bool:
        """初始化浏览器"""
        try:
            self.driver = setup_driver()
            self.wait = create_wait(self.driver, self.browser_config['page_load_wait'])
            print("✅ 浏览器初始化成功")
            return True
        except Exception as e:
            print(f"❌ 浏览器初始化失败: {e}")
            return False
    
    def initialize_network_monitor(self, enable_monitor: bool = False) -> bool:
        """初始化网络监控（如果启用）"""
        if not enable_monitor:
            print("ℹ️ 网络监控未启用")
            return True
        
        try:
            from ...network.enhanced_monitor import EnhancedNetworkMonitor
            self.network_monitor = EnhancedNetworkMonitor(self.driver)
            self.network_monitor.start_monitoring()
            print(get_status_message('network_monitor_start'))
            return True
        except Exception as e:
            print(f"❌ 网络监控初始化失败: {e}")
            return False
    
    def navigate_to_page(self, url: str) -> bool:
        """导航到指定页面"""
        try:
            print(get_status_message('page_loading', url))
            self.driver.get(url)
            self._wait_for_page_load()
            return True
        except Exception as e:
            print(f"❌ 页面导航失败: {e}")
            return False
    
    def handle_login_flow(self) -> bool:
        """处理登录流程"""
        try:
            print(get_status_message('login_start'))
            
            # 简化的登录流程 - 移除不必要的延迟
            if click_login_button_only(self.driver, self.wait):
                print(get_status_message('login_success'))
                click_confirm_login_button(self.driver, self.wait)
            
            # 直接等待手动登录，无额外延迟
            wait_for_manual_login()
            return True
            
        except Exception as e:
            print(f"❌ 登录流程失败: {e}")
            return False
    
    def _wait_for_page_load(self) -> None:
        """等待页面加载完成"""
        try:
            self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            print(get_status_message('page_loaded'))
        except TimeoutException:
            print(get_status_message('page_load_timeout'))
        
        try:
            self.wait.until(lambda d: d.execute_script("return document.readyState") == "complete")
            print("✅ 页面完全加载完成")
        except TimeoutException:
            print("⚠️ 页面完全加载超时，继续执行")
    
    def cleanup(self) -> None:
        """清理资源"""
        try:
            if self.network_monitor:
                # 停止网络监控
                print("🔄 停止网络监控...")
            
            if self.driver:
                print("🔄 关闭浏览器...")
                self.driver.quit()
                print("✅ 浏览器已关闭")
        except Exception as e:
            print(f"⚠️ 清理过程中出现错误: {e}")
    
    def get_driver(self) -> Optional[Any]:
        """获取WebDriver实例"""
        return self.driver
    
    def get_wait(self) -> Optional[Any]:
        """获取WebDriverWait实例"""
        return self.wait
    
    def get_network_monitor(self) -> Optional[Any]:
        """获取网络监控实例"""
        return self.network_monitor 