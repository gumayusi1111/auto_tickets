#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
page_crawler.py
页面爬取模块
"""

import json
import time
import os
from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from typing import Dict, Any, Optional


class PageCrawler:
    """页面内容爬取器"""
    
    def __init__(self, driver):
        self.driver = driver
        self.page_data = {
            'timestamp': datetime.now().isoformat(),
            'crawl_timestamp': datetime.now().isoformat(),
            'url': '',
            'page_title': '',
            'html_content': '',
            'page_crawl_success': False,
            'form_elements': {
                'input_fields': [],
                'checkboxes': [],
                'radio_buttons': [],
                'select_dropdowns': [],
                'textareas': [],
                'buttons': []
            }
        }
    
    def crawl_page_content(self, timeout=10):
        """爬取当前页面的所有内容
        
        包含:
        1. 完整的HTML源码
        2. 页面标题和URL
        3. 所有表单元素（输入框、复选框、按钮等）
        4. 使用多种方法确保元素获取完整
        """
        print("\n📄 开始爬取跳转后页面的完整内容...")
        
        try:
            # 智能等待页面完全加载
            from selenium.webdriver.support import expected_conditions as EC
            from selenium.webdriver.common.by import By
            from selenium.common.exceptions import TimeoutException
            
            try:
                # 等待页面DOM加载完成
                WebDriverWait(self.driver, 5).until(
                    lambda d: d.execute_script("return document.readyState") == "complete"
                )
                print("✅ 页面DOM加载完成")
            except TimeoutException:
                print("⚠️ 页面DOM加载超时，继续执行")
                time.sleep(1)  # 备用等待
            
            # 获取基本页面信息
            self.page_data['url'] = self.driver.current_url
            self.page_data['page_title'] = self.driver.title
            print(f"📍 页面URL: {self.page_data['url']}")
            print(f"📄 页面标题: {self.page_data['page_title']}")
            
            # 获取完整的HTML源码
            print("🕷️ 获取完整HTML内容...")
            self.page_data['html_content'] = self.driver.page_source
            html_size = len(self.page_data['html_content'])
            print(f"📏 HTML内容大小: {html_size} 字符")
            
            # 爬取所有表单元素
            print("🔍 开始爬取表单元素...")
            self._crawl_form_elements()
            
            # 统计爬取结果
            form_elements = self.page_data['form_elements']
            total_elements = (
                len(form_elements['input_fields']) +
                len(form_elements['checkboxes']) +
                len(form_elements['radio_buttons']) +
                len(form_elements['select_dropdowns']) +
                len(form_elements['textareas']) +
                len(form_elements['buttons'])
            )
            
            print(f"📊 表单元素统计:")
            print(f"   📝 输入框: {len(form_elements['input_fields'])} 个")
            print(f"   ☑️ 复选框: {len(form_elements['checkboxes'])} 个")
            print(f"   🔘 单选框: {len(form_elements['radio_buttons'])} 个")
            print(f"   📋 下拉框: {len(form_elements['select_dropdowns'])} 个")
            print(f"   📄 文本域: {len(form_elements['textareas'])} 个")
            print(f"   🔲 按钮: {len(form_elements['buttons'])} 个")
            print(f"   📊 总计: {total_elements} 个表单元素")
            
            # 标记爬取成功
            self.page_data['page_crawl_success'] = True
            
            print("✅ 页面内容爬取完成")
            return self.page_data
            
        except Exception as e:
            print(f"❌ 爬取页面内容失败: {e}")
            self.page_data['page_crawl_success'] = False
            return self.page_data
    
    def _crawl_form_elements(self):
        """爬取所有表单元素"""
        print("🔍 正在爬取表单元素...")
        
        # 方法1: 通过标签名查找
        self._crawl_by_tag_names()
        
        # 方法2: 通过常见的CSS选择器查找
        self._crawl_by_css_selectors()
        
        # 方法3: 通过XPath查找
        self._crawl_by_xpath()
        
        # 去重和整理数据
        self._deduplicate_elements()
    
    def _crawl_by_tag_names(self):
        """方法1: 通过HTML标签名爬取元素"""
        try:
            # 输入框
            inputs = self.driver.find_elements(By.TAG_NAME, "input")
            for input_elem in inputs:
                element_data = self._extract_element_data(input_elem)
                if element_data['type'] == 'checkbox':
                    self.page_data['form_elements']['checkboxes'].append(element_data)
                elif element_data['type'] == 'radio':
                    self.page_data['form_elements']['radio_buttons'].append(element_data)
                else:
                    self.page_data['form_elements']['input_fields'].append(element_data)
            
            # 下拉选择框
            selects = self.driver.find_elements(By.TAG_NAME, "select")
            for select_elem in selects:
                element_data = self._extract_element_data(select_elem)
                self.page_data['form_elements']['select_dropdowns'].append(element_data)
            
            # 文本域
            textareas = self.driver.find_elements(By.TAG_NAME, "textarea")
            for textarea_elem in textareas:
                element_data = self._extract_element_data(textarea_elem)
                self.page_data['form_elements']['textareas'].append(element_data)
            
            # 按钮
            buttons = self.driver.find_elements(By.TAG_NAME, "button")
            for button_elem in buttons:
                element_data = self._extract_element_data(button_elem)
                self.page_data['form_elements']['buttons'].append(element_data)
                
        except Exception as e:
            print(f"⚠️ 标签名方法爬取失败: {e}")
    
    def _crawl_by_css_selectors(self):
        """方法2: 通过CSS选择器爬取元素"""
        try:
            # 常见的表单选择器
            selectors = [
                'input[type="text"]',
                'input[type="email"]',
                'input[type="tel"]',
                'input[type="date"]',
                'input[type="number"]',
                'input[type="password"]',
                'input[type="checkbox"]',
                'input[type="radio"]',
                'input[type="submit"]',
                'input[type="button"]',
                'button[type="submit"]',
                'button[class*="submit"]',
                'button[class*="confirm"]',
                '.form-control',
                '.form-input',
                '.checkbox',
                '.radio'
            ]
            
            for selector in selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for elem in elements:
                        element_data = self._extract_element_data(elem)
                        element_data['found_by'] = f'css: {selector}'
                        
                        # 根据类型分类
                        if 'checkbox' in selector or element_data['type'] == 'checkbox':
                            self.page_data['form_elements']['checkboxes'].append(element_data)
                        elif 'radio' in selector or element_data['type'] == 'radio':
                            self.page_data['form_elements']['radio_buttons'].append(element_data)
                        elif 'submit' in selector or 'button' in selector:
                            self.page_data['form_elements']['buttons'].append(element_data)
                        else:
                            self.page_data['form_elements']['input_fields'].append(element_data)
                            
                except Exception:
                    continue
                    
        except Exception as e:
            print(f"⚠️ CSS选择器方法爬取失败: {e}")
    
    def _crawl_by_xpath(self):
        """方法3: 通过XPath爬取元素"""
        try:
            # 常见的XPath表达式
            xpaths = [
                "//input[@type='text' or @type='email' or @type='tel' or @type='date']",
                "//input[@type='checkbox']",
                "//input[@type='radio']",
                "//button[contains(text(), '제출') or contains(text(), '확인') or contains(text(), '신청')]",
                "//button[contains(@class, 'submit') or contains(@class, 'confirm')]",
                "//input[contains(@placeholder, '생년월일') or contains(@placeholder, '전화번호')]",
                "//input[contains(@name, 'birth') or contains(@name, 'phone') or contains(@name, 'mobile')]",
                "//textarea",
                "//select"
            ]
            
            for xpath in xpaths:
                try:
                    elements = self.driver.find_elements(By.XPATH, xpath)
                    for elem in elements:
                        element_data = self._extract_element_data(elem)
                        element_data['found_by'] = f'xpath: {xpath}'
                        
                        # 根据XPath特征分类
                        if 'checkbox' in xpath:
                            self.page_data['form_elements']['checkboxes'].append(element_data)
                        elif 'radio' in xpath:
                            self.page_data['form_elements']['radio_buttons'].append(element_data)
                        elif 'button' in xpath:
                            self.page_data['form_elements']['buttons'].append(element_data)
                        elif 'textarea' in xpath:
                            self.page_data['form_elements']['textareas'].append(element_data)
                        elif 'select' in xpath:
                            self.page_data['form_elements']['select_dropdowns'].append(element_data)
                        else:
                            self.page_data['form_elements']['input_fields'].append(element_data)
                            
                except Exception:
                    continue
                    
        except Exception as e:
            print(f"⚠️ XPath方法爬取失败: {e}")
    
    def _extract_element_data(self, element):
        """提取元素的详细信息"""
        try:
            return {
                'tag_name': element.tag_name,
                'type': element.get_attribute('type') or '',
                'name': element.get_attribute('name') or '',
                'id': element.get_attribute('id') or '',
                'class': element.get_attribute('class') or '',
                'placeholder': element.get_attribute('placeholder') or '',
                'value': element.get_attribute('value') or '',
                'text': element.text or '',
                'required': element.get_attribute('required') is not None,
                'disabled': element.get_attribute('disabled') is not None,
                'visible': element.is_displayed(),
                'enabled': element.is_enabled(),
                'location': element.location,
                'size': element.size,
                'found_by': 'tag_name'
            }
        except Exception as e:
            return {
                'error': str(e),
                'tag_name': 'unknown',
                'found_by': 'error'
            }
    
    def _deduplicate_elements(self):
        """去除重复的元素"""
        for category in self.page_data['form_elements']:
            elements = self.page_data['form_elements'][category]
            unique_elements = []
            seen_elements = set()
            
            for elem in elements:
                # 创建唯一标识符
                identifier = f"{elem.get('tag_name', '')}_{elem.get('type', '')}_{elem.get('name', '')}_{elem.get('id', '')}"
                if identifier not in seen_elements:
                    seen_elements.add(identifier)
                    unique_elements.append(elem)
            
            self.page_data['form_elements'][category] = unique_elements
    
    def save_page_data(self, filename=None):
        """保存页面数据到文件"""
        try:
            if not filename:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"page_crawl_{timestamp}.json"
            
            # 确保data目录存在
            data_dir = "/Users/wenbai/Desktop/chajian/auto/data"
            os.makedirs(data_dir, exist_ok=True)
            
            filepath = os.path.join(data_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self.page_data, f, ensure_ascii=False, indent=2)
            
            print(f"📁 页面数据已保存到: {filepath}")
            return filepath
            
        except Exception as e:
            print(f"❌ 保存页面数据失败: {e}")
            return None
    
    def print_summary(self):
        """打印爬取结果摘要"""
        print("\n📊 页面爬取结果摘要:")
        print(f"📍 URL: {self.page_data['url']}")
        
        for category, elements in self.page_data['form_elements'].items():
            if elements:
                print(f"🔹 {category}: {len(elements)} 个")
                for elem in elements[:3]:  # 只显示前3个
                    name = elem.get('name', '') or elem.get('id', '') or elem.get('placeholder', '')
                    print(f"   - {elem.get('tag_name', 'unknown')} ({elem.get('type', 'unknown')}): {name}")
                if len(elements) > 3:
                    print(f"   ... 还有 {len(elements) - 3} 个")

def crawl_page_content(driver) -> Dict[str, Any]:
    """
    爬取页面内容
    
    Args:
        driver: WebDriver实例
    
    Returns:
        页面内容数据
    """
    try:
        # 获取基本页面信息
        page_data = {
            'html_content': driver.page_source,
            'page_crawl_success': True,
            'crawl_timestamp': datetime.now().isoformat(),
            'page_title': driver.title,
            'page_url': driver.current_url
        }
        
        # 获取HTML内容大小
        html_size = len(page_data['html_content'])
        print(f"📏 HTML内容大小: {html_size} 字符")
        
        return page_data
        
    except Exception as e:
        print(f"❌ 页面内容爬取失败: {e}")
        return {
            'html_content': '',
            'page_crawl_success': False,
            'crawl_timestamp': datetime.now().isoformat(),
            'page_title': '',
            'page_url': driver.current_url,
            'error': str(e)
        }