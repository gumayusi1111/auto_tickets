#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Weverse文章分析器
通过命令行输入账号密码和目标URL，自动登录并分析文章内容
"""

import sys
import os
import time
import getpass
import argparse
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config.ai_config import DEEPSEEK_CONFIG
from src.core.browser_setup import setup_driver, create_wait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException, NoSuchElementException
from selenium.webdriver.common.keys import Keys
import requests
import json

class WeverseAnalyzer:
    def __init__(self, headless=False):
        self.driver = None
        self.wait = None
        self.headless = headless
        
    def init_browser(self):
        """初始化浏览器"""
        try:
            print("🚀 正在初始化浏览器...")
            self.driver = setup_driver(headless=self.headless, stealth_mode=True)
            self.wait = create_wait(self.driver, 20)
            print("✅ 浏览器初始化成功")
            return True
        except Exception as e:
            print(f"❌ 浏览器初始化失败: {e}")
            return False
    
    def login_weverse(self, username, password):
        """登录Weverse"""
        try:
            print("🔐 正在登录Weverse...")
            
            # 访问Weverse登录页面
            login_url = "https://weverse.io/"
            print(f"📍 访问: {login_url}")
            self.driver.get(login_url)
            
            # 等待页面加载
            time.sleep(3)
            
            # 查找并点击登录按钮
            try:
                # 尝试多种可能的登录按钮选择器
                login_selectors = [
                    "button[data-testid='login-button']",
                    "a[href*='login']",
                    "button:contains('로그인')",
                    "button:contains('Login')",
                    "[class*='login']",
                    "[id*='login']"
                ]
                
                login_button = None
                for selector in login_selectors:
                    try:
                        if ':contains(' in selector:
                            # 使用XPath查找包含文本的元素
                            xpath = f"//button[contains(text(), '로그인') or contains(text(), 'Login')]"
                            login_button = self.driver.find_element(By.XPATH, xpath)
                        else:
                            login_button = self.driver.find_element(By.CSS_SELECTOR, selector)
                        break
                    except NoSuchElementException:
                        continue
                
                if not login_button:
                    # 如果找不到登录按钮，尝试直接访问登录页面
                    login_direct_url = "https://account.weverse.io/login"
                    print(f"📍 直接访问登录页面: {login_direct_url}")
                    self.driver.get(login_direct_url)
                    time.sleep(3)
                else:
                    print("🔍 找到登录按钮，正在点击...")
                    self.driver.execute_script("arguments[0].click();", login_button)
                    time.sleep(3)
                
            except Exception as e:
                print(f"⚠️ 查找登录按钮时出错: {e}")
                # 尝试直接访问登录页面
                login_direct_url = "https://account.weverse.io/login"
                print(f"📍 直接访问登录页面: {login_direct_url}")
                self.driver.get(login_direct_url)
                time.sleep(3)
            
            # 输入用户名
            print("📝 输入用户名...")
            username_selectors = [
                "input[name='loginId']",
                "input[type='email']",
                "input[placeholder*='이메일']",
                "input[placeholder*='email']",
                "input[id*='email']",
                "input[id*='username']",
                "input[class*='email']",
                "input[class*='username']"
            ]
            
            username_input = None
            for selector in username_selectors:
                try:
                    username_input = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
                    break
                except TimeoutException:
                    continue
            
            if not username_input:
                raise Exception("无法找到用户名输入框")
            
            username_input.clear()
            username_input.send_keys(username)
            time.sleep(1)
            
            # 输入密码
            print("🔑 输入密码...")
            password_selectors = [
                "input[name='password']",
                "input[type='password']",
                "input[placeholder*='비밀번호']",
                "input[placeholder*='password']",
                "input[id*='password']",
                "input[class*='password']"
            ]
            
            password_input = None
            for selector in password_selectors:
                try:
                    password_input = self.driver.find_element(By.CSS_SELECTOR, selector)
                    break
                except NoSuchElementException:
                    continue
            
            if not password_input:
                raise Exception("无法找到密码输入框")
            
            password_input.clear()
            password_input.send_keys(password)
            time.sleep(1)
            
            # 点击登录按钮
            print("🚀 提交登录...")
            submit_selectors = [
                "button[type='submit']",
                "button:contains('로그인')",
                "button:contains('Login')",
                "input[type='submit']",
                "[class*='login'][class*='button']",
                "[id*='login'][id*='button']"
            ]
            
            submit_button = None
            for selector in submit_selectors:
                try:
                    if ':contains(' in selector:
                        xpath = f"//button[contains(text(), '로그인') or contains(text(), 'Login')]"
                        submit_button = self.driver.find_element(By.XPATH, xpath)
                    else:
                        submit_button = self.driver.find_element(By.CSS_SELECTOR, selector)
                    break
                except NoSuchElementException:
                    continue
            
            if submit_button:
                self.driver.execute_script("arguments[0].click();", submit_button)
            else:
                # 尝试按回车键
                password_input.send_keys(Keys.RETURN)
            
            # 等待登录完成
            print("⏳ 等待登录完成...")
            time.sleep(5)
            
            # 检查是否登录成功
            current_url = self.driver.current_url
            if "login" not in current_url.lower():
                print("✅ 登录成功")
                return True
            else:
                print("❌ 登录可能失败，请检查账号密码")
                return False
                
        except Exception as e:
            print(f"❌ 登录过程中出错: {e}")
            return False
    
    def analyze_article(self, target_url):
        """分析指定URL的文章内容"""
        try:
            print(f"📖 正在分析文章: {target_url}")
            
            # 访问目标URL
            self.driver.get(target_url)
            time.sleep(5)
            
            # 等待页面加载完成
            self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            
            # 尝试查找文章内容
            content_selectors = [
                "#modal > div > div.NoticeModalView_notice_wrap__fhTTz > div.NoticeModalView_detail__t4JWo.NoticeModalView_-show_button__r9Yi5 > div > p:nth-child(1)",
                "[class*='NoticeModalView_detail']",
                "[class*='notice'] [class*='detail']",
                "[class*='content']",
                "[class*='article']",
                "[class*='post']",
                "main",
                "article",
                ".content",
                ".article-content",
                ".post-content"
            ]
            
            article_content = None
            content_text = ""
            
            for selector in content_selectors:
                try:
                    article_content = self.driver.find_element(By.CSS_SELECTOR, selector)
                    content_text = article_content.text.strip()
                    if content_text and len(content_text) > 10:  # 确保找到有意义的内容
                        print(f"✅ 使用选择器找到内容: {selector}")
                        break
                except NoSuchElementException:
                    continue
            
            if not content_text:
                # 如果没有找到特定内容，获取页面主要文本
                print("⚠️ 未找到特定文章内容，尝试获取页面主要文本...")
                try:
                    body = self.driver.find_element(By.TAG_NAME, "body")
                    content_text = body.text.strip()
                except Exception:
                    content_text = "无法获取页面内容"
            
            if content_text:
                print(f"📄 文章内容长度: {len(content_text)} 字符")
                print(f"📄 内容预览: {content_text[:200]}...")
                
                # 使用AI分析内容
                analysis_result = self.analyze_with_ai(content_text, target_url)
                return analysis_result
            else:
                print("❌ 无法获取文章内容")
                return None
                
        except Exception as e:
            print(f"❌ 分析文章时出错: {e}")
            return None
    
    def analyze_with_ai(self, content, url):
        """使用AI分析文章内容"""
        try:
            print("🤖 正在使用AI分析文章内容...")
            
            # 准备AI分析请求
            headers = {
                'Authorization': f'Bearer {DEEPSEEK_CONFIG["api_key"]}',
                'Content-Type': 'application/json'
            }
            
            prompt = f"""
请分析以下Weverse文章内容，并提供详细的分析报告：

文章URL: {url}
文章内容:
{content}

请从以下几个方面进行分析：
1. 文章主题和类型（公告、活动、互动等）
2. 关键信息提取（时间、地点、重要事项等）
3. 情感色彩分析
4. 对粉丝的影响和意义
5. 需要关注的重点信息
6. 建议的后续行动

请用中文回复，格式清晰易读。
"""
            
            data = {
                'model': DEEPSEEK_CONFIG['model_name'],
                'messages': [
                    {
                        'role': 'user',
                        'content': prompt
                    }
                ],
                'max_tokens': 2000,
                'temperature': 0.3
            }
            
            response = requests.post(
                f"{DEEPSEEK_CONFIG['base_url']}/chat/completions",
                headers=headers,
                json=data,
                timeout=DEEPSEEK_CONFIG['timeout']
            )
            
            if response.status_code == 200:
                result = response.json()
                if 'choices' in result and len(result['choices']) > 0:
                    analysis = result['choices'][0]['message']['content']
                    print("✅ AI分析完成")
                    return {
                        'url': url,
                        'content': content,
                        'analysis': analysis,
                        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
                    }
                else:
                    print("❌ AI响应格式异常")
                    return None
            else:
                print(f"❌ AI分析失败: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ AI分析过程中出错: {e}")
            return None
    
    def save_analysis(self, analysis_result, output_file=None):
        """保存分析结果"""
        try:
            if not output_file:
                timestamp = time.strftime('%Y%m%d_%H%M%S')
                output_file = f"weverse_analysis_{timestamp}.json"
            
            output_path = project_root / "data" / output_file
            output_path.parent.mkdir(exist_ok=True)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(analysis_result, f, ensure_ascii=False, indent=2)
            
            print(f"💾 分析结果已保存到: {output_path}")
            return str(output_path)
            
        except Exception as e:
            print(f"❌ 保存分析结果时出错: {e}")
            return None
    
    def close(self):
        """关闭浏览器"""
        if self.driver:
            self.driver.quit()
            print("🔄 浏览器已关闭")

def main():
    parser = argparse.ArgumentParser(description='Weverse文章分析器')
    parser.add_argument('--url', '-u', required=True, help='目标文章URL')
    parser.add_argument('--username', '-n', help='Weverse用户名/邮箱')
    parser.add_argument('--password', '-p', help='Weverse密码')
    parser.add_argument('--headless', action='store_true', help='无头模式运行')
    parser.add_argument('--output', '-o', help='输出文件名')
    
    args = parser.parse_args()
    
    print("🎵 Weverse文章分析器")
    print("=" * 50)
    
    # 获取登录信息
    username = args.username
    password = args.password
    
    if not username:
        username = input("📧 请输入Weverse用户名/邮箱: ")
    
    if not password:
        password = getpass.getpass("🔑 请输入Weverse密码: ")
    
    if not username or not password:
        print("❌ 用户名和密码不能为空")
        return 1
    
    analyzer = WeverseAnalyzer(headless=args.headless)
    
    try:
        # 初始化浏览器
        if not analyzer.init_browser():
            return 1
        
        # 登录Weverse
        if not analyzer.login_weverse(username, password):
            print("❌ 登录失败，请检查账号密码")
            return 1
        
        # 分析文章
        analysis_result = analyzer.analyze_article(args.url)
        
        if analysis_result:
            print("\n" + "=" * 80)
            print("📊 AI分析结果")
            print("=" * 80)
            print(analysis_result['analysis'])
            print("=" * 80)
            
            # 保存结果
            saved_path = analyzer.save_analysis(analysis_result, args.output)
            if saved_path:
                print(f"\n✅ 分析完成！结果已保存到: {saved_path}")
            
            return 0
        else:
            print("❌ 文章分析失败")
            return 1
            
    except KeyboardInterrupt:
        print("\n\n⚠️ 用户中断操作")
        return 1
    except Exception as e:
        print(f"\n\n💥 程序执行过程中发生错误: {e}")
        return 1
    finally:
        analyzer.close()

if __name__ == "__main__":
    sys.exit(main())