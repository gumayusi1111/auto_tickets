# -*- coding: utf-8 -*-
"""
content_extractor.py
内容提取模块
"""

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC


def extract_article_content(driver, wait):
    """提取文章内容"""
    content_selectors = [
        "#root > div.App > div > div.body > div > div > div > div > div.NoticeDetailView_content__30Pm8 > div > p:nth-child(1)",
        "[class*='NoticeDetailView_content']",
        "[class*='notice'] [class*='detail']",
        "[class*='content']",
        "[class*='article']",
        "[class*='post']",
        "main",
        "article"
    ]
    
    try:
        print("🔍 提取文章内容...")
        
        for selector in content_selectors:
            try:
                content_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
                content = content_element.text.strip()
                if content and len(content) > 10:
                    print(f"✅ 成功提取内容（{len(content)}字符）")
                    return content
            except:
                continue
        
        # 如果指定选择器没有内容，尝试获取整个页面的文本
        print("⚠️  指定选择器内容为空，尝试获取整个页面内容...")
        content = driver.find_element(By.TAG_NAME, "body").text
        print(f"✅ 获取到页面内容（{len(content)}字符）")
        return content
        
    except Exception as e:
        print(f"❌ 提取内容失败: {e}")
        return None