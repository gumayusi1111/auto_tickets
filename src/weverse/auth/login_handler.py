#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
login_handler.py
登录处理模块 - 简化版本
"""

import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException

def click_login_button_only(driver, wait, timeout=10):
    """
    简化的登录按钮点击（无延迟）
    """
    login_selectors = [
        'button[data-testid="login"]',
        '.login-button',
        '[class*="login"]',
        'a[href*="login"]',
        'button:contains("로그인")',
        'button:contains("Login")',
        'button:contains("登录")'
    ]
    
    for selector in login_selectors:
        try:
            element = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
            element.click()
            print("✅ 已点击: 登录按钮")
            return True
        except TimeoutException:
            continue
        except Exception as e:
            print(f"⚠️ 登录按钮点击失败: {e}")
            continue
    
    print("❌ 未找到登录按钮")
    return False

def click_confirm_login_button(driver, wait, timeout=5):
    """
    简化的确认登录按钮点击（无延迟）
    """
    confirm_selectors = [
        'button[data-testid="confirm"]',
        '.confirm-button',
        '[class*="confirm"]',
        'button:contains("확인")',
        'button:contains("Confirm")',
        'button:contains("确认")'
    ]
    
    for selector in confirm_selectors:
        try:
            element = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
            element.click()
            print("✅ 已点击: 确认登录按钮")
            return True
        except TimeoutException:
            continue
        except Exception:
            continue
    
    # 如果没有找到确认按钮，这是正常的，不报错
    return True

def wait_for_manual_login():
    """
    等待手动登录完成（无延迟版本）
    """
    print("请手动完成登录，然后按回车键继续...")
    input()  # 直接等待用户输入，不添加额外延迟
    print("✅ 登录完成，继续执行...")
    return True

def pre_click_network_analysis(minutes_ahead=1):
    """
    点击前网络分析 - 提前1分钟动态测试
    
    Args:
        minutes_ahead: 提前多少分钟进行测试
        
    Returns:
        dict: 网络分析结果和优化建议
    """
    print(f"\n🕐 点击前 {minutes_ahead} 分钟网络分析...")
    print("=" * 50)
    
    # 执行快速网络测试
    network_result = quick_network_test()
    
    # 基于当前网络状态给出建议
    latency_ms = network_result.get('avg_latency_ms', 200)
    preclick_ms = network_result.get('preclick_time_ms', 150)
    quality = network_result.get('network_quality', 'unknown')
    
    # 动态调整策略
    strategy = {
        'preclick_time': preclick_ms / 1000,  # 转换为秒
        'check_interval': min(0.05, latency_ms / 4000),  # 检测间隔
        'timeout': max(10, latency_ms / 20),  # 超时时间
        'retry_count': 3 if quality in ['excellent', 'good'] else 5,  # 重试次数
        'wait_after_click': max(0.5, latency_ms / 1000)  # 点击后等待时间
    }
    
    print(f"📊 网络分析结果:")
    print(f"   当前延迟: {latency_ms:.0f}ms")
    print(f"   网络质量: {quality}")
    print(f"   {network_result.get('recommendation', '无建议')}")
    
    print(f"\n⚡ 动态优化策略:")
    print(f"   提前点击时间: {strategy['preclick_time']:.3f}秒")
    print(f"   检测间隔: {strategy['check_interval']:.3f}秒")
    print(f"   超时时间: {strategy['timeout']:.1f}秒")
    print(f"   重试次数: {strategy['retry_count']} 次")
    print(f"   点击后等待: {strategy['wait_after_click']:.3f}秒")
    
    return {
        'network_result': network_result,
        'strategy': strategy,
        'timestamp': time.time()
    }


def smart_wait_for_element_dynamic(driver, wait, selector, strategy, element_name="元素"):
    """
    动态优化的智能等待函数
    
    Args:
        driver: WebDriver实例
        wait: WebDriverWait实例
        selector: 元素选择器
        strategy: 优化策略字典
        element_name: 元素名称
        
    Returns:
        WebElement or None: 找到的元素
    """
    print(f"🔍 动态智能等待: {element_name}")
    print(f"   策略: 间隔{strategy['check_interval']:.3f}s, 超时{strategy['timeout']:.1f}s")
    
    start_time = time.time()
    check_interval = strategy['check_interval']
    timeout = strategy['timeout']
    
    while time.time() - start_time < timeout:
        try:
            if selector.startswith("//"):
                element = driver.find_element(By.XPATH, selector)
            else:
                element = driver.find_element(By.CSS_SELECTOR, selector)
            
            if element.is_displayed() and element.is_enabled():
                elapsed = time.time() - start_time
                print(f"✅ {element_name}已就绪 (耗时: {elapsed:.2f}秒)")
                return element
                
        except (NoSuchElementException, Exception):
            pass
        
        time.sleep(check_interval)
    
    print(f"⏰ {element_name}等待超时 ({timeout:.1f}秒)")
    return None


def predictive_click_dynamic(element, strategy, element_name="元素"):
    """
    动态预测性点击
    
    Args:
        element: 要点击的元素
        strategy: 优化策略
        element_name: 元素名称
    """
    preclick_time = strategy['preclick_time']
    
    if preclick_time > 0.05:  # 只有当提前时间大于50ms时才显示
        print(f"⚡ 预测性点击 {element_name}: 提前 {preclick_time:.3f}秒")
    
    # 执行点击
    element.click()
    print(f"✅ 已点击: {element_name}")
    
    # 动态等待响应
    wait_time = strategy['wait_after_click']
    if wait_time > 0.5:
        print(f"⏳ 等待响应: {wait_time:.2f}秒")
    
    time.sleep(wait_time)


def click_login_button_dynamic(driver, wait):
    """
    动态优化版登录按钮点击
    """
    try:
        print("\n🚀 动态优化登录流程启动...")
        
        # 点击前1分钟网络分析
        analysis = pre_click_network_analysis(minutes_ahead=1)
        strategy = analysis['strategy']
        
        print("\n🔍 查找并点击登录按钮...")
        
        # 登录按钮选择器
        login_selectors = [
            "//button[contains(text(), '로그인') or contains(text(), 'Login') or contains(text(), '登录')]",
            "#root > div.fixed_bottom_layer.FixedBottomLayerView_fixed_wrap__J2yYZ > div.UserJoinInduceLayerView_container__8AjD7 > div > button",
            "button[class*='login']",
            "a[href*='login']",
            "[data-testid*='login']"
        ]
        
        login_clicked = False
        for i, selector in enumerate(login_selectors, 1):
            print(f"🎯 尝试选择器 {i}/{len(login_selectors)}")
            
            # 使用动态优化的智能等待
            login_button = smart_wait_for_element_dynamic(
                driver, wait, selector, strategy, f"登录按钮{i}"
            )
            
            if login_button:
                # 使用动态预测性点击
                predictive_click_dynamic(login_button, strategy, "登录按钮")
                login_clicked = True
                break
            else:
                print(f"   ❌ 选择器 {i} 未找到元素")
        
        if not login_clicked:
            print("⚠️  所有登录按钮选择器都失败，可能已经在登录页面")
            return False
        
        print("✅ 登录按钮点击完成")
        return True
        
    except Exception as e:
        print(f"❌ 动态登录按钮点击失败: {e}")
        return False


def click_confirm_login_button_dynamic(driver, wait):
    """
    动态优化版确认登录按钮点击
    """
    try:
        print("\n🔍 查找并点击确认登录按钮...")
        
        # 实时网络分析（确认按钮通常出现较快，使用快速测试）
        print("⚡ 实时网络状态检测...")
        network_result = quick_network_test()
        
        # 基于实时网络状态调整策略
        latency_ms = network_result.get('avg_latency_ms', 200)
        strategy = {
            'preclick_time': (latency_ms / 1000) * 0.75,  # 75%延迟时间
            'check_interval': min(0.05, latency_ms / 4000),
            'timeout': max(15, latency_ms / 15),  # 确认按钮给更长超时时间
            'wait_after_click': max(0.5, latency_ms / 1000)
        }
        
        print(f"📊 实时策略调整: 延迟{latency_ms:.0f}ms, 提前{strategy['preclick_time']:.3f}s")
        
        # 主要确认按钮选择器
        confirm_selector = "#modal > div > div.ModalButtonView_button_wrap__cqUzx.ModalButtonView_-grid__33dU2 > button.ModalButtonView_button__B5k-Z.ModalButtonView_-confirm__2YBz1"
        
        # 使用动态智能等待
        confirm_button = smart_wait_for_element_dynamic(
            driver, wait, confirm_selector, strategy, "确认登录按钮"
        )
        
        if confirm_button:
            # 动态预测性点击
            predictive_click_dynamic(confirm_button, strategy, "确认登录按钮")
            return True
        
        # 如果主选择器失败，尝试备用选择器
        print("🔄 尝试备用确认按钮选择器...")
        alternative_selectors = [
            "button[class*='confirm']",
            "button[class*='ModalButtonView_-confirm']",
            "//button[contains(text(), '확인') or contains(text(), 'Confirm') or contains(text(), '确认')]",
            "//button[contains(@class, 'confirm')]"
        ]
        
        for i, selector in enumerate(alternative_selectors, 1):
            print(f"🎯 尝试备用选择器 {i}/{len(alternative_selectors)}")
            
            # 为备用选择器使用更短的超时时间
            backup_strategy = strategy.copy()
            backup_strategy['timeout'] = 5  # 5秒超时
            
            button = smart_wait_for_element_dynamic(
                driver, wait, selector, backup_strategy, f"确认按钮{i}"
            )
            
            if button:
                predictive_click_dynamic(button, strategy, f"确认登录按钮(备用{i})")
                return True
        
        print("⚠️  所有确认登录按钮选择器都失败")
        return False
        
    except Exception as e:
        print(f"❌ 动态确认登录按钮点击失败: {e}")
        return False


def analyze_captured_requests(json_file_path):
    """
    分析抓包数据，评估直接POST请求的可行性
    
    Args:
        json_file_path: 抓包数据JSON文件路径
    
    Returns:
        dict: 分析结果
    """
    try:
        import json
        import os
        
        if not os.path.exists(json_file_path):
            print(f"❌ 文件不存在: {json_file_path}")
            return None
        
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print("📊 分析抓包数据...")
        
        # 提取POST请求
        post_requests = []
        if 'first_click_data' in data:
            post_requests.extend(data['first_click_data'].get('post_requests_only', []))
        if 'submit_data' in data:
            post_requests.extend(data['submit_data'].get('post_requests_only', []))
        
        analysis = {
            'total_post_requests': len(post_requests),
            'authentication_required': False,
            'csrf_tokens': [],
            'session_cookies': [],
            'api_endpoints': [],
            'direct_post_feasible': False
        }
        
        print(f"📡 发现 {len(post_requests)} 个POST请求:")
        
        for i, req in enumerate(post_requests, 1):
            url = req.get('url', '')
            headers = req.get('headers', {})
            
            print(f"\n{i}. {url}")
            
            # 检查认证相关头部
            auth_headers = ['authorization', 'x-csrf-token', 'x-requested-with', 'referer']
            for header in auth_headers:
                if header.lower() in [h.lower() for h in headers.keys()]:
                    analysis['authentication_required'] = True
                    if 'csrf' in header.lower():
                        analysis['csrf_tokens'].append(headers[header])
            
            # 检查Cookie
            if 'cookie' in [h.lower() for h in headers.keys()]:
                analysis['session_cookies'].append(url)
            
            analysis['api_endpoints'].append(url)
        
        # 评估直接POST的可行性
        if analysis['authentication_required']:
            print("\n❌ 直接POST请求困难:")
            print("   - 需要认证头部和CSRF令牌")
            print("   - 需要有效的会话Cookie")
            print("   - 服务器端可能有额外的验证")
        else:
            print("\n✅ 直接POST请求可能可行:")
            print("   - 无明显认证要求")
            analysis['direct_post_feasible'] = True
        
        return analysis
        
    except Exception as e:
        print(f"❌ 分析抓包数据失败: {e}")
        return None


# 向后兼容的函数别名
click_login_button_only = click_login_button_dynamic
click_confirm_login_button = click_confirm_login_button_dynamic