#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
weverse_complete_auto.py

手动运行版本：
1. 用户手动运行脚本并登录到报名页面
2. 脚本显示倒计时，等待到指定时间
3. 时间到了自动点击报名按钮
4. 爬取表单页面所有元素并保存到文件
5. 跳转后自动填写表单并提交
"""

from __future__ import annotations

import datetime as _dt
import sys
import time
import json
import os
import re

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

# =============== 配置区域 ===============
TARGET_URL = "https://weverse.io/nct127/notice/27902"

# 个人信息
BIRTH_DATE = "20050125"      # 生日：050125 → 20050125
PHONE_NUMBER = "15988654075"  # 手机号

# 时间设置
TARGET_TIME = None  # 运行时输入
EARLY_MS = 150               # 提前多少毫秒点击（可微调）

# 按钮选择器
BUTTON_SELECTOR = (
    "#modal > div > div.NoticeModalView_notice_wrap__fhTTz > "
    "div.NoticeModalView_floating__Mx9Cs > a"
)
# =========================================

def _parse_time(hms: str) -> _dt.time:
    h, m, s = map(int, hms.split(":"))
    return _dt.time(h, m, s)

def show_countdown(target_dt: _dt.datetime):
    """显示倒计时"""
    while True:
        now = _dt.datetime.now()
        remaining = (target_dt - now).total_seconds()
        
        if remaining <= 0:
            print(f"\r🚀 时间到了！{now.strftime('%H:%M:%S.%f')[:-3]} 开始点击！", flush=True)
            break
        
        hours = int(remaining // 3600)
        minutes = int((remaining % 3600) // 60)
        seconds = int(remaining % 60)
        milliseconds = int((remaining % 1) * 1000)
        
        if hours > 0:
            countdown_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}.{milliseconds:03d}"
        else:
            countdown_str = f"{minutes:02d}:{seconds:02d}.{milliseconds:03d}"
        
        print(f"\r⏰ 距离 {TARGET_TIME} 还有: {countdown_str}", end="", flush=True)
        time.sleep(0.01)  # 10ms 刷新一次

def crawl_form_elements(driver, wait):
    """爬取表单页面的所有元素并保存到文件"""
    print("\n🔍 正在爬取表单页面元素...")
    
    try:
        # 等待页面完全加载
        time.sleep(3)
        
        # 收集所有表单元素信息
        elements_info = {
            "timestamp": _dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "page_title": driver.title,
            "current_url": driver.current_url,
            "inputs": [],
            "buttons": [],
            "checkboxes": [],
            "selects": [],
            "textareas": [],
            "labels": [],
            "all_elements": []
        }
        
        # 获取所有input元素
        inputs = driver.find_elements(By.TAG_NAME, "input")
        for i, input_elem in enumerate(inputs):
            try:
                input_info = {
                    "index": i,
                    "tag": "input",
                    "type": input_elem.get_attribute("type"),
                    "name": input_elem.get_attribute("name"),
                    "id": input_elem.get_attribute("id"),
                    "class": input_elem.get_attribute("class"),
                    "placeholder": input_elem.get_attribute("placeholder"),
                    "value": input_elem.get_attribute("value"),
                    "required": input_elem.get_attribute("required"),
                    "xpath": f"//input[{i+1}]",
                    "css_selector": f"input:nth-of-type({i+1})",
                    "is_displayed": input_elem.is_displayed(),
                    "is_enabled": input_elem.is_enabled(),
                    "text": input_elem.text
                }
                elements_info["inputs"].append(input_info)
                
                # 如果是复选框，单独记录
                if input_elem.get_attribute("type") == "checkbox":
                    checkbox_info = input_info.copy()
                    checkbox_info["is_selected"] = input_elem.is_selected()
                    elements_info["checkboxes"].append(checkbox_info)
                    
            except Exception as e:
                print(f"获取input元素{i}信息时出错: {e}")
        
        # 获取所有button元素
        buttons = driver.find_elements(By.TAG_NAME, "button")
        for i, button in enumerate(buttons):
            try:
                button_info = {
                    "index": i,
                    "tag": "button",
                    "type": button.get_attribute("type"),
                    "class": button.get_attribute("class"),
                    "id": button.get_attribute("id"),
                    "text": button.text,
                    "xpath": f"//button[{i+1}]",
                    "css_selector": f"button:nth-of-type({i+1})",
                    "is_displayed": button.is_displayed(),
                    "is_enabled": button.is_enabled()
                }
                elements_info["buttons"].append(button_info)
            except Exception as e:
                print(f"获取button元素{i}信息时出错: {e}")
        
        # 获取所有select元素
        selects = driver.find_elements(By.TAG_NAME, "select")
        for i, select in enumerate(selects):
            try:
                select_info = {
                    "index": i,
                    "tag": "select",
                    "name": select.get_attribute("name"),
                    "id": select.get_attribute("id"),
                    "class": select.get_attribute("class"),
                    "xpath": f"//select[{i+1}]",
                    "css_selector": f"select:nth-of-type({i+1})",
                    "is_displayed": select.is_displayed(),
                    "is_enabled": select.is_enabled(),
                    "options": []
                }
                
                # 获取选项
                options = select.find_elements(By.TAG_NAME, "option")
                for j, option in enumerate(options):
                    select_info["options"].append({
                        "index": j,
                        "value": option.get_attribute("value"),
                        "text": option.text,
                        "selected": option.is_selected()
                    })
                
                elements_info["selects"].append(select_info)
            except Exception as e:
                print(f"获取select元素{i}信息时出错: {e}")
        
        # 获取所有textarea元素
        textareas = driver.find_elements(By.TAG_NAME, "textarea")
        for i, textarea in enumerate(textareas):
            try:
                textarea_info = {
                    "index": i,
                    "tag": "textarea",
                    "name": textarea.get_attribute("name"),
                    "id": textarea.get_attribute("id"),
                    "class": textarea.get_attribute("class"),
                    "placeholder": textarea.get_attribute("placeholder"),
                    "value": textarea.get_attribute("value"),
                    "xpath": f"//textarea[{i+1}]",
                    "css_selector": f"textarea:nth-of-type({i+1})",
                    "is_displayed": textarea.is_displayed(),
                    "is_enabled": textarea.is_enabled(),
                    "text": textarea.text
                }
                elements_info["textareas"].append(textarea_info)
            except Exception as e:
                print(f"获取textarea元素{i}信息时出错: {e}")
        
        # 获取所有label元素
        labels = driver.find_elements(By.TAG_NAME, "label")
        for i, label in enumerate(labels):
            try:
                label_info = {
                    "index": i,
                    "tag": "label",
                    "for": label.get_attribute("for"),
                    "class": label.get_attribute("class"),
                    "text": label.text,
                    "xpath": f"//label[{i+1}]",
                    "css_selector": f"label:nth-of-type({i+1})",
                    "is_displayed": label.is_displayed()
                }
                elements_info["labels"].append(label_info)
            except Exception as e:
                print(f"获取label元素{i}信息时出错: {e}")
        
        # 获取页面HTML源码（可选）
        elements_info["page_source"] = driver.page_source
        
        # 保存到文件
        timestamp = _dt.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"form_elements_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(elements_info, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 表单元素信息已保存到: {filename}")
        print(f"📊 发现元素统计:")
        print(f"   - Input元素: {len(elements_info['inputs'])}个")
        print(f"   - 复选框: {len(elements_info['checkboxes'])}个")
        print(f"   - Button元素: {len(elements_info['buttons'])}个")
        print(f"   - Select元素: {len(elements_info['selects'])}个")
        print(f"   - Textarea元素: {len(elements_info['textareas'])}个")
        print(f"   - Label元素: {len(elements_info['labels'])}个")
        
        # 特别显示复选框信息
        if elements_info['checkboxes']:
            print(f"\n📋 复选框详细信息:")
            for i, checkbox in enumerate(elements_info['checkboxes']):
                print(f"   {i+1}. ID: {checkbox['id']}, Class: {checkbox['class']}")
                print(f"      XPath: {checkbox['xpath']}")
                print(f"      显示: {checkbox['is_displayed']}, 启用: {checkbox['is_enabled']}, 选中: {checkbox['is_selected']}")
        
        return filename
        
    except Exception as e:
        print(f"❌ 爬取表单元素时出错: {e}")
        return None

def get_time_input():
    """从控制台获取时间字符串，支持 21:00、21:00:00、9点、9点30分、21点5分等格式"""
    while True:
        s = input("请输入目标时间（如 21:00、21:00:00、9点、9点30分、21点5分）：").strip()
        # 处理常见格式
        s = s.replace('：', ':').replace('点', ':').replace('分', ':').replace(' ', '')
        s = re.sub(r'[^0-9:]', '', s)
        parts = s.split(':')
        try:
            if len(parts) == 1 and parts[0]:
                h = int(parts[0])
                m = 0
                s = 0
            elif len(parts) == 2:
                h, m = map(int, parts)
                s = 0
            elif len(parts) == 3:
                h, m, s = map(int, parts)
            else:
                raise ValueError
            if not (0 <= h < 24 and 0 <= m < 60 and 0 <= s < 60):
                raise ValueError
            return f"{h:02d}:{m:02d}:{s:02d}"
        except Exception:
            print("格式错误，请重新输入。例如 21:00、21:00:00、9点、9点30分、21点5分")

def main() -> None:
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--incognito")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()),
                              options=chrome_options)
    wait = WebDriverWait(driver, 15)

    global TARGET_TIME
    TARGET_TIME = get_time_input()

    try:
        print(f"正在打开 {TARGET_URL}")
        driver.get(TARGET_URL)

        print(f"\n�� 目标时间: {TARGET_TIME} (提前 {EARLY_MS}ms)")
        print("📝 生日:", BIRTH_DATE)
        print("📞 手机:", PHONE_NUMBER)
        
        input(f"\n请在浏览器中完成登录，确保能看到报名按钮，然后回到终端按 Enter 开始倒计时…\n")

        # 计算目标时间
        today = _dt.date.today()
        target_dt = _dt.datetime.combine(today, _parse_time(TARGET_TIME))
        
        # 如果目标时间已过，按明天计算
        if _dt.datetime.now() >= target_dt:
            target_dt += _dt.timedelta(days=1)

        # 减去提前量
        early_sec = EARLY_MS / 1000.0
        click_time = target_dt - _dt.timedelta(seconds=early_sec)
        
        print(f"\n⏱️  准确点击时间: {click_time.strftime('%H:%M:%S.%f')[:-3]}")
        print("开始倒计时...\n")

        # 显示倒计时
        show_countdown(click_time)

        # 点击报名按钮
        print("\n🎯 正在点击报名按钮...")
        try:
            # 尝试多种选择器
            button = None
            selectors = [
                BUTTON_SELECTOR,
                "a[href*='apply'], button[class*='apply'], a[class*='apply']",
                "//a[contains(text(), '참여 신청') or contains(text(), '신청')]",
                "//button[contains(text(), '참여 신청') or contains(text(), '신청')]"
            ]
            
            for selector in selectors:
                try:
                    if selector.startswith("//"):
                        button = wait.until(EC.element_to_be_clickable((By.XPATH, selector)))
                    else:
                        button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
                    break
                except:
                    continue
            
            if button:
                driver.execute_script("arguments[0].click();", button)
                actual_time = _dt.datetime.now()
                print(f"✅ 已点击报名按钮！实际时间: {actual_time.strftime('%H:%M:%S.%f')[:-3]}")
            else:
                print("❌ 未找到报名按钮，请手动点击")
                input("手动点击报名按钮后按 Enter 继续...")

        except Exception as e:
            print(f"❌ 点击按钮失败: {e}")
            input("请手动点击报名按钮，进入表单页面后按 Enter 继续...")

        # 等待表单页面加载
        print("\n📋 等待表单页面加载...")
        time.sleep(2)

        # 爬取表单元素
        crawl_form_elements(driver, wait)

        # 自动填写表单
        print("\n📝 开始自动填写表单...")
        
        try:
            # 填写生日
            print("正在填写生日...")
            birth_selectors = [
                "//input[contains(@placeholder, '생년월일')]",
                "//input[contains(@name, 'birth')]", 
                "//input[@type='date']",
                "input[placeholder*='생년월일'], input[name*='birth'], input[type='date']"
            ]
            
            birth_input = None
            for selector in birth_selectors:
                try:
                    if selector.startswith("//"):
                        birth_input = wait.until(EC.presence_of_element_located((By.XPATH, selector)))
                    else:
                        birth_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
                    break
                except:
                    continue
            
            if birth_input:
                birth_input.clear()
                birth_input.send_keys(BIRTH_DATE)
                print(f"✅ 生日已填写: {BIRTH_DATE}")
            else:
                print("❌ 未找到生日输入框")

            time.sleep(0.5)

            # 填写手机号
            print("正在填写手机号...")
            phone_selectors = [
                "//input[contains(@placeholder, '연락처')]",
                "//input[contains(@name, 'phone')]",
                "//input[@type='tel']",
                "input[placeholder*='연락처'], input[name*='phone'], input[type='tel']"
            ]
            
            phone_input = None
            for selector in phone_selectors:
                try:
                    if selector.startswith("//"):
                        phone_input = wait.until(EC.presence_of_element_located((By.XPATH, selector)))
                    else:
                        phone_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
                    break
                except:
                    continue
            
            if phone_input:
                phone_input.clear()
                phone_input.send_keys(PHONE_NUMBER)
                print(f"✅ 手机号已填写: {PHONE_NUMBER}")
            else:
                print("❌ 未找到手机号输入框")

            time.sleep(0.5)

            # 勾选同意条款 - 使用更强的选择器
            print("正在勾选同意条款...")
            try:
                # 尝试多种方式找到复选框
                checkbox_selectors = [
                    "//input[@type='checkbox']",
                    "input[type='checkbox']",
                    "//input[@type='checkbox' and @name]",
                    "//input[@type='checkbox' and contains(@class, 'agree')]",
                    "//input[@type='checkbox' and contains(@id, 'agree')]"
                ]
                
                checkboxes_found = []
                for selector in checkbox_selectors:
                    try:
                        if selector.startswith("//"):
                            checkboxes = driver.find_elements(By.XPATH, selector)
                        else:
                            checkboxes = driver.find_elements(By.CSS_SELECTOR, selector)
                        
                        for checkbox in checkboxes:
                            if checkbox.is_displayed() and checkbox.is_enabled():
                                checkboxes_found.append(checkbox)
                        
                        if checkboxes_found:
                            break
                    except:
                        continue
                
                if checkboxes_found:
                    for i, checkbox in enumerate(checkboxes_found):
                        if not checkbox.is_selected():
                            driver.execute_script("arguments[0].click();", checkbox)
                            print(f"✅ 已勾选第{i+1}个同意条款")
                            time.sleep(0.3)
                else:
                    print("⚠️  未找到可见的复选框，请查看爬取的元素文件")
                    
            except Exception as e:
                print(f"⚠️  勾选条款时出错: {e}")

            print("\n📤 信息填写完成！正在提交...")

            # 自动提交
            submit_selectors = [
                "//button[contains(text(), '참여 신청')]",
                "//button[contains(text(), '신청')]",
                "//button[contains(@class, 'submit')]",
                "button[class*='submit'], input[type='submit']"
            ]
            
            submit_button = None
            for selector in submit_selectors:
                try:
                    if selector.startswith("//"):
                        submit_button = wait.until(EC.element_to_be_clickable((By.XPATH, selector)))
                    else:
                        submit_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
                    break
                except:
                    continue
            
            if submit_button:
                driver.execute_script("arguments[0].click();", submit_button)
                submit_time = _dt.datetime.now()
                print(f"🎉 已提交表单！提交时间: {submit_time.strftime('%H:%M:%S.%f')[:-3]}")
            else:
                print("❌ 未找到提交按钮，请手动提交")

            input("\n🎊 操作完成！查看结果后按 Enter 关闭浏览器…")

        except Exception as e:
            print(f"❌ 自动填写失败: {e}")
            input("请手动完成表单填写和提交，完成后按 Enter 关闭浏览器…")

    finally:
        driver.quit()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit("\n👋 用户中断脚本。") 