#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_modal_element.py
测试模态框元素选择器的准确性
"""

import sys
import time
from pathlib import Path
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.weverse.browser.setup import setup_driver


def test_modal_element_selector():
    """测试模态框元素选择器"""
    print("🧪 测试模态框元素选择器")
    print("=" * 50)
    
    target_selector = "#modal > div > div.NoticeModalView_notice_wrap__fhTTz > div.NoticeModalView_floating__Mx9Cs > a"
    
    driver = setup_driver(headless=False)
    
    try:
        # 访问Weverse页面
        test_url = input("请输入要测试的URL (默认: https://weverse.io): ").strip()
        if not test_url:
            test_url = "https://weverse.io"
        
        print(f"🌐 访问页面: {test_url}")
        driver.get(test_url)
        time.sleep(3)
        
        print(f"🔍 检查目标选择器: {target_selector}")
        
        # 方法1: 直接查找元素
        print("\n📋 方法1: 直接查找元素")
        try:
            element = driver.find_element(By.CSS_SELECTOR, target_selector)
            print(f"✅ 找到元素!")
            print(f"   标签: {element.tag_name}")
            print(f"   文本: '{element.text.strip()}'")
            print(f"   href: {element.get_attribute('href')}")
            print(f"   可见: {element.is_displayed()}")
            print(f"   可点击: {element.is_enabled()}")
        except NoSuchElementException:
            print("❌ 未找到元素")
        
        # 方法2: 等待元素出现
        print("\n📋 方法2: 等待元素出现 (10秒)")
        try:
            wait = WebDriverWait(driver, 10)
            element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, target_selector)))
            print(f"✅ 等待成功找到元素!")
            print(f"   标签: {element.tag_name}")
            print(f"   文本: '{element.text.strip()}'")
            print(f"   href: {element.get_attribute('href')}")
        except TimeoutException:
            print("❌ 等待超时，未找到元素")
        
        # 方法3: 分步检查选择器
        print("\n📋 方法3: 分步检查选择器")
        selectors_to_check = [
            "#modal",
            "#modal > div",
            "#modal > div > div.NoticeModalView_notice_wrap__fhTTz",
            "#modal > div > div.NoticeModalView_notice_wrap__fhTTz > div.NoticeModalView_floating__Mx9Cs",
            target_selector
        ]
        
        for i, selector in enumerate(selectors_to_check, 1):
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    element = elements[0]
                    print(f"✅ 步骤{i}: 找到 {len(elements)} 个元素")
                    print(f"   选择器: {selector}")
                    print(f"   标签: {element.tag_name}")
                    if element.text.strip():
                        print(f"   文本: '{element.text.strip()[:50]}...'")
                else:
                    print(f"❌ 步骤{i}: 未找到元素")
                    print(f"   选择器: {selector}")
                    break
            except Exception as e:
                print(f"❌ 步骤{i}: 异常 - {e}")
                break
        
        # 方法4: 查找所有模态框相关元素
        print("\n📋 方法4: 查找所有模态框相关元素")
        modal_selectors = [
            "#modal",
            "[id*='modal']",
            "[class*='modal']",
            "[class*='Modal']",
            "[class*='notice']",
            "[class*='Notice']",
            "[class*='floating']"
        ]
        
        for selector in modal_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    print(f"✅ 找到 {len(elements)} 个元素: {selector}")
                    for i, elem in enumerate(elements[:3]):  # 只显示前3个
                        try:
                            print(f"   [{i+1}] {elem.tag_name} - '{elem.text.strip()[:30]}...'")
                        except:
                            print(f"   [{i+1}] {elem.tag_name} - (无法获取文本)")
            except:
                pass
        
        # 方法5: 查找所有a标签，看是否有类似的
        print("\n📋 方法5: 查找页面中所有链接")
        try:
            all_links = driver.find_elements(By.TAG_NAME, "a")
            print(f"📊 页面共有 {len(all_links)} 个链接")
            
            # 查找可能相关的链接
            relevant_links = []
            for link in all_links:
                try:
                    href = link.get_attribute('href') or ''
                    text = link.text.strip()
                    class_name = link.get_attribute('class') or ''
                    
                    # 检查是否可能是目标链接
                    if any(keyword in (href + text + class_name).lower() for keyword in 
                           ['notice', 'modal', 'floating', 'apply', 'submit']):
                        relevant_links.append({
                            'element': link,
                            'href': href,
                            'text': text,
                            'class': class_name
                        })
                except:
                    pass
            
            if relevant_links:
                print(f"🎯 找到 {len(relevant_links)} 个可能相关的链接:")
                for i, link_info in enumerate(relevant_links[:5]):
                    print(f"   [{i+1}] href: {link_info['href']}")
                    print(f"       text: '{link_info['text']}'")
                    print(f"       class: {link_info['class']}")
                    print()
            else:
                print("❌ 未找到相关链接")
                
        except Exception as e:
            print(f"❌ 查找链接时出错: {e}")
        
        # 让用户观察页面
        print("\n👁️ 请在浏览器中观察页面，寻找目标元素")
        print("按回车键继续...")
        input()
        
        # 最后再次尝试
        print("\n📋 最终测试: 再次查找目标元素")
        try:
            element = driver.find_element(By.CSS_SELECTOR, target_selector)
            print(f"✅ 最终测试成功!")
            print(f"   元素存在且可访问")
            
            # 尝试点击测试
            if element.is_displayed() and element.is_enabled():
                print("🖱️ 元素可点击，是否测试点击？(y/n)")
                if input().lower() == 'y':
                    element.click()
                    print("✅ 点击成功!")
                    time.sleep(3)
            
        except Exception as e:
            print(f"❌ 最终测试失败: {e}")
        
    except Exception as e:
        print(f"❌ 测试过程出错: {e}")
        
    finally:
        print("\n🔄 关闭浏览器...")
        driver.quit()
        print("✅ 测试完成")


if __name__ == "__main__":
    test_modal_element_selector() 