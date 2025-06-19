#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_button_click_delay.py
按钮点击和延迟计算测试文件
"""

import sys
import os
from datetime import datetime, timedelta
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.weverse.browser.setup import setup_driver
from src.weverse.analysis.time_processor import test_real_network_latency, show_countdown_with_dynamic_timing
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


def create_test_html():
    """创建测试用的HTML页面"""
    html_content = """
<!DOCTYPE html>
<html>
<head>
    <title>按钮点击和延迟测试</title>
    <style>
        body { font-family: Arial, sans-serif; padding: 20px; }
        .button { 
            background: #007bff; 
            color: white; 
            padding: 10px 20px; 
            border: none; 
            border-radius: 5px; 
            cursor: pointer; 
            margin: 10px;
            font-size: 16px;
        }
        .button:hover { background: #0056b3; }
        .disabled { background: #ccc; cursor: not-allowed; }
        .test-section { margin: 20px 0; padding: 15px; border: 1px solid #ddd; }
        .time-display { font-size: 18px; font-weight: bold; color: #333; }
        #countdown { color: #ff6b35; font-size: 24px; }
    </style>
</head>
<body>
    <h1>🧪 按钮点击和延迟计算测试页面</h1>
    
    <div class="test-section">
        <h2>⏰ 时间测试区域</h2>
        <p class="time-display">当前时间: <span id="current-time"></span></p>
        <p class="time-display">目标时间: <span id="target-time"></span></p>
        <p class="time-display">倒计时: <span id="countdown">计算中...</span></p>
    </div>
    
    <div class="test-section">
        <h2>🖱️ 按钮测试区域</h2>
        <button id="login-btn" class="button">登录按钮</button>
        <button id="submit-btn" class="button">提交按钮</button>
        <button id="apply-btn" class="button">申请按钮</button>
        <button id="disabled-btn" class="button disabled" disabled>禁用按钮</button>
    </div>
    
    <div class="test-section">
        <h2>📊 点击结果</h2>
        <div id="click-results"></div>
    </div>
    
    <script>
        // 设置目标时间为30秒后
        const targetTime = new Date(Date.now() + 30000);
        document.getElementById('target-time').textContent = targetTime.toLocaleTimeString();
        
        // 更新当前时间和倒计时
        function updateTime() {
            const now = new Date();
            document.getElementById('current-time').textContent = now.toLocaleTimeString();
            
            const diff = targetTime - now;
            if (diff > 0) {
                const seconds = Math.floor(diff / 1000);
                const ms = diff % 1000;
                document.getElementById('countdown').textContent = `${seconds}.${String(ms).padStart(3, '0')}秒`;
            } else {
                document.getElementById('countdown').textContent = '时间到！';
                document.getElementById('countdown').style.color = '#28a745';
            }
        }
        
        setInterval(updateTime, 10); // 每10ms更新一次
        
        // 按钮点击事件
        document.querySelectorAll('.button:not(.disabled)').forEach(btn => {
            btn.addEventListener('click', function() {
                const clickTime = new Date();
                const result = `
                    <p>✅ 按钮 "${this.textContent}" 被点击</p>
                    <p>⏱️ 点击时间: ${clickTime.toLocaleTimeString()}.${clickTime.getMilliseconds()}</p>
                    <p>📍 元素ID: ${this.id}</p>
                    <hr>
                `;
                document.getElementById('click-results').innerHTML = result + document.getElementById('click-results').innerHTML;
            });
        });
        
        // 在目标时间模拟自动点击
        setTimeout(() => {
            const applyBtn = document.getElementById('apply-btn');
            applyBtn.style.background = '#28a745';
            applyBtn.textContent = '自动点击已触发!';
        }, 30000);
    </script>
</body>
</html>
    """
    
    test_file_path = project_root / "tests" / "test_button_click.html"
    with open(test_file_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    return str(test_file_path)


def test_button_detection_and_click(driver):
    """测试按钮检测和点击功能"""
    print("\n🖱️ 测试1: 按钮检测和点击")
    print("=" * 50)
    
    try:
        wait = WebDriverWait(driver, 10)
        
        # 测试不同类型的按钮
        button_selectors = [
            ("login-btn", "登录按钮"),
            ("submit-btn", "提交按钮"), 
            ("apply-btn", "申请按钮")
        ]
        
        for btn_id, btn_name in button_selectors:
            try:
                # 查找按钮
                button = wait.until(EC.element_to_be_clickable((By.ID, btn_id)))
                print(f"✅ 找到 {btn_name}: {btn_id}")
                
                # 获取按钮信息
                btn_text = button.text
                btn_enabled = button.is_enabled()
                btn_displayed = button.is_displayed()
                
                print(f"   📝 按钮文本: {btn_text}")
                print(f"   🔘 是否可用: {btn_enabled}")
                print(f"   👁️ 是否可见: {btn_displayed}")
                
                if btn_enabled and btn_displayed:
                    # 记录点击前时间
                    before_click = datetime.now()
                    
                    # 点击按钮
                    button.click()
                    
                    # 记录点击后时间
                    after_click = datetime.now()
                    click_duration = (after_click - before_click).total_seconds() * 1000
                    
                    print(f"   ⚡ 点击耗时: {click_duration:.2f}ms")
                    print(f"   ✅ {btn_name} 点击成功!")
                    
                    time.sleep(1)  # 等待1秒观察效果
                else:
                    print(f"   ❌ {btn_name} 不可点击")
                    
            except Exception as e:
                print(f"   ❌ {btn_name} 测试失败: {e}")
            
            print()
            
    except Exception as e:
        print(f"❌ 按钮测试失败: {e}")


def test_delay_calculation():
    """测试延迟计算功能"""
    print("\n⏱️ 测试2: 延迟计算")
    print("=" * 50)
    
    try:
        # 测试真实网络延迟检测
        print("🌐 开始真实网络延迟测试...")
        latency_stats = test_real_network_latency(duration=10, test_url="https://www.weverse.io")
        
        print("\n📊 延迟测试结果:")
        print(f"   平均延迟: {latency_stats['avg_ms']:.1f}ms")
        print(f"   推荐提前: {latency_stats['recommended_advance_ms']:.1f}ms")
        print(f"   置信度: {latency_stats['confidence']}")
        
        return latency_stats
        
    except Exception as e:
        print(f"❌ 延迟计算测试失败: {e}")
        return None


def test_precise_timing():
    """测试精确计时功能"""
    print("\n🎯 测试3: 精确计时测试")
    print("=" * 50)
    
    # 设置一个10秒后的目标时间
    target_time = datetime.now() + timedelta(seconds=10)
    print(f"🎯 目标时间: {target_time.strftime('%H:%M:%S.%f')[:-3]}")
    print(f"⏱️ 开始10秒精确倒计时...")
    
    # 简化的倒计时测试
    start_time = datetime.now()
    while True:
        current_time = datetime.now()
        remaining = (target_time - current_time).total_seconds()
        
        if remaining <= 0:
            actual_duration = (current_time - start_time).total_seconds()
            print(f"\r🎉 时间到！实际用时: {actual_duration:.3f}秒")
            break
            
        print(f"\r⏰ 倒计时: {remaining:.3f}秒", end="", flush=True)
        time.sleep(0.01)  # 10ms精度
    
    print()


def main():
    """主测试函数"""
    print("🧪 按钮点击和延迟计算测试")
    print("=" * 60)
    
    # 创建测试HTML文件
    print("📄 创建测试HTML页面...")
    test_html_path = create_test_html()
    print(f"✅ 测试页面已创建: {test_html_path}")
    
    # 启动浏览器
    print("\n🌐 启动浏览器...")
    driver = None
    
    try:
        # 设置浏览器 (非无头模式，方便观察)
        driver = setup_driver(headless=False)
        print("✅ 浏览器启动成功")
        
        # 打开测试页面
        file_url = f"file://{test_html_path}"
        driver.get(file_url)
        print(f"✅ 测试页面已加载: {file_url}")
        
        # 等待页面加载
        time.sleep(2)
        
        # 执行测试
        test_button_detection_and_click(driver)
        latency_stats = test_delay_calculation()
        test_precise_timing()
        
        print("\n🎊 所有测试完成!")
        print("🖱️ 你可以在浏览器中手动点击按钮观察效果")
        print("⏰ 观察倒计时是否准确")
        
        # 保持浏览器打开30秒供观察
        print("\n⏳ 保持浏览器打开30秒供测试...")
        for i in range(30, 0, -1):
            print(f"\r🔄 剩余时间: {i}秒", end="", flush=True)
            time.sleep(1)
        
        print("\n✅ 测试完成!")
        
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}")
        
    finally:
        if driver:
            print("\n🔄 关闭浏览器...")
            driver.quit()
            print("✅ 浏览器已关闭")


if __name__ == "__main__":
    main() 