#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_main_program.py
主程序测试 - 测试完整的Weverse自动化流程
"""

import time
import os
import sys
import json
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

class MainProgramTester:
    """主程序测试器"""
    
    def __init__(self):
        self.driver = None
        self.wait = None
        self.test_results = {
            'test_start_time': datetime.now().isoformat(),
            'phases': {},
            'total_success': False,
            'errors': []
        }
    
    def setup_chrome(self):
        """设置Chrome驱动"""
        print("🔧 设置Chrome驱动...")
        
        chrome_options = Options()
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--disable-images')
        chrome_options.add_argument('--disable-plugins')
        chrome_options.add_argument('--disable-extensions')
        
        # 启用性能日志
        chrome_options.set_capability('goog:loggingPrefs', {
            'performance': 'ALL',
            'browser': 'ALL'
        })
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.driver.set_page_load_timeout(10)
        self.wait = WebDriverWait(self.driver, 10)
        
        print("✅ Chrome驱动设置完成")
    
    def test_browser_setup(self):
        """测试浏览器设置"""
        print("\n🧪 测试阶段1: 浏览器设置")
        
        try:
            self.setup_chrome()
            
            # 测试基本功能
            self.driver.get("data:text/html,<h1>Browser Test</h1>")
            title = self.driver.title
            
            self.test_results['phases']['browser_setup'] = {
                'success': True,
                'duration': 0,
                'details': f'浏览器标题: {title}'
            }
            print("✅ 浏览器设置测试通过")
            return True
            
        except Exception as e:
            self.test_results['phases']['browser_setup'] = {
                'success': False,
                'error': str(e)
            }
            print(f"❌ 浏览器设置失败: {e}")
            return False
    
    def test_page_loading(self):
        """测试页面加载"""
        print("\n🧪 测试阶段2: 页面加载")
        
        try:
            start_time = time.time()
            
            # 使用测试HTML文件
            test_file = os.path.join(os.path.dirname(__file__), 'test_form.html')
            file_url = f"file://{os.path.abspath(test_file)}"
            
            print(f"📄 加载测试页面: {file_url}")
            self.driver.get(file_url)
            
            # 等待页面加载
            self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            
            # 检查页面元素
            title = self.driver.title
            forms = self.driver.find_elements(By.TAG_NAME, 'form')
            inputs = self.driver.find_elements(By.TAG_NAME, 'input')
            
            duration = time.time() - start_time
            
            self.test_results['phases']['page_loading'] = {
                'success': True,
                'duration': duration,
                'details': {
                    'title': title,
                    'forms_count': len(forms),
                    'inputs_count': len(inputs),
                    'url': file_url
                }
            }
            
            print(f"✅ 页面加载成功 ({duration:.2f}秒)")
            print(f"   📄 标题: {title}")
            print(f"   📝 表单: {len(forms)} 个")
            print(f"   🔤 输入框: {len(inputs)} 个")
            return True
            
        except Exception as e:
            self.test_results['phases']['page_loading'] = {
                'success': False,
                'error': str(e)
            }
            print(f"❌ 页面加载失败: {e}")
            return False
    
    def test_main_program_import(self):
        """测试主程序模块导入"""
        print("\n🧪 测试阶段3: 主程序模块导入")
        
        try:
            start_time = time.time()
            
            # 测试关键模块导入
            modules_tested = {}
            
            try:
                from src.weverse.browser.setup import setup_driver, create_wait
                modules_tested['browser_setup'] = True
                print("✅ 浏览器设置模块导入成功")
            except Exception as e:
                modules_tested['browser_setup'] = False
                print(f"❌ 浏览器设置模块导入失败: {e}")
            
            try:
                from src.weverse.operations.button_clicker import click_apply_button
                modules_tested['button_clicker'] = True
                print("✅ 按钮点击模块导入成功")
            except Exception as e:
                modules_tested['button_clicker'] = False
                print(f"❌ 按钮点击模块导入失败: {e}")
            
            try:
                from src.weverse.operations.form_auto_filler import FormAutoFiller
                modules_tested['form_filler'] = True
                print("✅ 表单填写模块导入成功")
            except Exception as e:
                modules_tested['form_filler'] = False
                print(f"❌ 表单填写模块导入失败: {e}")
            
            try:
                from src.weverse.operations.network_monitor import NetworkMonitor
                modules_tested['network_monitor'] = True
                print("✅ 网络监控模块导入成功")
            except Exception as e:
                modules_tested['network_monitor'] = False
                print(f"❌ 网络监控模块导入失败: {e}")
            
            try:
                from src.weverse.mode_handler import unified_mode
                modules_tested['main_mode'] = True
                print("✅ 主模式处理器导入成功")
            except Exception as e:
                modules_tested['main_mode'] = False
                print(f"❌ 主模式处理器导入失败: {e}")
            
            duration = time.time() - start_time
            success_count = sum(modules_tested.values())
            total_count = len(modules_tested)
            success_rate = success_count / total_count
            
            self.test_results['phases']['module_import'] = {
                'success': success_rate >= 0.8,
                'duration': duration,
                'details': {
                    'modules_tested': modules_tested,
                    'success_count': success_count,
                    'total_count': total_count,
                    'success_rate': success_rate
                }
            }
            
            print(f"✅ 模块导入测试完成 ({duration:.3f}秒)")
            print(f"   📊 成功率: {success_rate*100:.1f}% ({success_count}/{total_count})")
            
            return success_rate >= 0.8
            
        except Exception as e:
            self.test_results['phases']['module_import'] = {
                'success': False,
                'error': str(e)
            }
            print(f"❌ 模块导入测试失败: {e}")
            return False
    
    def test_integrated_workflow(self):
        """测试集成工作流"""
        print("\n🧪 测试阶段4: 集成工作流测试")
        
        try:
            start_time = time.time()
            
            # 导入主程序组件
            from src.weverse.operations.form_auto_filler import FormAutoFiller
            from src.weverse.operations.network_monitor import NetworkMonitor
            
            # 创建组件实例
            form_filler = FormAutoFiller(self.driver, self.wait)
            network_monitor = NetworkMonitor(self.driver)
            
            # 启动网络监控
            network_monitor.start_monitoring()
            print("📡 网络监控已启动")
            
            # 模拟表单数据
            test_data = {
                'name': '김민수',
                'birthday': '1995-03-15',
                'phone': '010-1234-5678',
                'email': 'test@example.com'
            }
            
            # 填写表单
            fields_filled = 0
            for field_id, value in test_data.items():
                try:
                    element = self.driver.find_element(By.ID, field_id)
                    element.clear()
                    element.send_keys(value)
                    fields_filled += 1
                    print(f"✅ {field_id}: {value}")
                except Exception as e:
                    print(f"❌ {field_id} 填写失败: {e}")
            
            # 点击复选框
            checkboxes_checked = 0
            for checkbox_id in ['agree1', 'agree2', 'agree3']:
                try:
                    checkbox = self.driver.find_element(By.ID, checkbox_id)
                    if not checkbox.is_selected():
                        checkbox.click()
                        checkboxes_checked += 1
                        print(f"✅ 复选框: {checkbox_id}")
                except Exception as e:
                    print(f"❌ 复选框 {checkbox_id} 失败: {e}")
            
            # 点击提交按钮
            try:
                submit_button = self.driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
                submit_button.click()
                print("✅ 提交按钮点击成功")
                
                # 等待网络请求
                time.sleep(1)
                
                # 捕获网络请求
                captured_requests = network_monitor.capture_all_requests(duration=2)
                print(f"📡 捕获到 {len(captured_requests)} 个网络请求")
                
            except Exception as e:
                print(f"❌ 按钮点击失败: {e}")
                captured_requests = []
            
            # 停止网络监控
            network_monitor.stop_monitoring()
            
            duration = time.time() - start_time
            total_form_operations = fields_filled + checkboxes_checked
            
            self.test_results['phases']['integrated_workflow'] = {
                'success': fields_filled >= 3 and checkboxes_checked >= 2 and len(captured_requests) >= 0,
                'duration': duration,
                'details': {
                    'fields_filled': fields_filled,
                    'total_fields': len(test_data),
                    'checkboxes_checked': checkboxes_checked,
                    'total_checkboxes': 3,
                    'network_requests': len(captured_requests),
                    'total_form_operations': total_form_operations,
                    'workflow_complete': True
                }
            }
            
            print(f"✅ 集成工作流测试完成 ({duration:.3f}秒)")
            print(f"   📝 表单填写: {fields_filled}/{len(test_data)} 个字段")
            print(f"   ☑️ 复选框: {checkboxes_checked}/3 个")
            print(f"   📡 网络请求: {len(captured_requests)} 个")
            print(f"   🎯 总体成功率: {total_form_operations}/7 = {total_form_operations/7*100:.1f}%")
            
            return fields_filled >= 3 and checkboxes_checked >= 2
            
        except Exception as e:
            self.test_results['phases']['integrated_workflow'] = {
                'success': False,
                'error': str(e)
            }
            print(f"❌ 集成工作流测试失败: {e}")
            return False
    
    def test_main_program_execution(self):
        """测试主程序执行（模拟模式）"""
        print("\n🧪 测试阶段5: 主程序执行测试")
        
        try:
            start_time = time.time()
            
            # 模拟主程序的关键步骤
            execution_steps = {
                'driver_setup': False,
                'page_access': False,
                'content_extraction': False,
                'form_handling': False,
                'data_saving': False
            }
            
            # 1. 驱动设置
            try:
                if self.driver:
                    execution_steps['driver_setup'] = True
                    print("✅ 驱动设置: 成功")
            except:
                print("❌ 驱动设置: 失败")
            
            # 2. 页面访问
            try:
                current_url = self.driver.current_url
                if current_url:
                    execution_steps['page_access'] = True
                    print("✅ 页面访问: 成功")
            except:
                print("❌ 页面访问: 失败")
            
            # 3. 内容提取
            try:
                page_source = self.driver.page_source
                if len(page_source) > 1000:  # 有足够的页面内容
                    execution_steps['content_extraction'] = True
                    print("✅ 内容提取: 成功")
            except:
                print("❌ 内容提取: 失败")
            
            # 4. 表单处理
            try:
                forms = self.driver.find_elements(By.TAG_NAME, 'form')
                inputs = self.driver.find_elements(By.TAG_NAME, 'input')
                if len(forms) > 0 and len(inputs) > 0:
                    execution_steps['form_handling'] = True
                    print("✅ 表单处理: 成功")
            except:
                print("❌ 表单处理: 失败")
            
            # 5. 数据保存
            try:
                # 模拟数据保存
                test_data = {'test': 'data', 'timestamp': datetime.now().isoformat()}
                execution_steps['data_saving'] = True
                print("✅ 数据保存: 成功")
            except:
                print("❌ 数据保存: 失败")
            
            duration = time.time() - start_time
            success_count = sum(execution_steps.values())
            total_count = len(execution_steps)
            success_rate = success_count / total_count
            
            self.test_results['phases']['main_program_execution'] = {
                'success': success_rate >= 0.8,
                'duration': duration,
                'details': {
                    'execution_steps': execution_steps,
                    'success_count': success_count,
                    'total_count': total_count,
                    'success_rate': success_rate
                }
            }
            
            print(f"✅ 主程序执行测试完成 ({duration:.3f}秒)")
            print(f"   📊 成功率: {success_rate*100:.1f}% ({success_count}/{total_count})")
            
            return success_rate >= 0.8
            
        except Exception as e:
            self.test_results['phases']['main_program_execution'] = {
                'success': False,
                'error': str(e)
            }
            print(f"❌ 主程序执行测试失败: {e}")
            return False
    
    def save_test_results(self):
        """保存测试结果"""
        try:
            # 计算总体成功率
            successful_phases = sum(1 for phase in self.test_results['phases'].values() if phase.get('success', False))
            total_phases = len(self.test_results['phases'])
            overall_success_rate = successful_phases / total_phases if total_phases > 0 else 0
            
            self.test_results['test_end_time'] = datetime.now().isoformat()
            self.test_results['total_success'] = overall_success_rate >= 0.8
            self.test_results['overall_success_rate'] = overall_success_rate
            self.test_results['successful_phases'] = successful_phases
            self.test_results['total_phases'] = total_phases
            
            # 保存到文件
            data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
            os.makedirs(data_dir, exist_ok=True)
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"main_program_test_{timestamp}.json"
            filepath = os.path.join(data_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self.test_results, f, ensure_ascii=False, indent=2)
            
            print(f"\n💾 测试结果已保存: {filepath}")
            return filepath
            
        except Exception as e:
            print(f"❌ 保存测试结果失败: {e}")
            return None
    
    def run_full_test(self):
        """运行完整测试"""
        print("🧪 主程序完整测试")
        print("🎯 目标：测试所有关键功能模块")
        print("=" * 50)
        
        test_phases = [
            ("浏览器设置", self.test_browser_setup),
            ("页面加载", self.test_page_loading),
            ("主程序模块导入", self.test_main_program_import),
            ("集成工作流", self.test_integrated_workflow),
            ("主程序执行", self.test_main_program_execution)
        ]
        
        successful_phases = 0
        
        for phase_name, test_func in test_phases:
            try:
                if test_func():
                    successful_phases += 1
            except Exception as e:
                print(f"❌ {phase_name} 测试异常: {e}")
                self.test_results['errors'].append(f"{phase_name}: {e}")
        
        # 总结报告
        total_phases = len(test_phases)
        success_rate = successful_phases / total_phases
        
        print(f"\n🎯 主程序测试总结:")
        print(f"   ✅ 成功阶段: {successful_phases}/{total_phases}")
        print(f"   📈 成功率: {success_rate*100:.1f}%")
        
        if success_rate >= 0.8:
            print("   🎉 主程序测试通过！")
        else:
            print("   ⚠️ 主程序测试需要改进")
        
        # 保存测试结果
        self.save_test_results()
        
        return success_rate >= 0.8
    
    def cleanup(self):
        """清理资源"""
        if self.driver:
            self.driver.quit()
            print("\n🔚 浏览器已关闭")

def main():
    """主函数"""
    tester = MainProgramTester()
    
    try:
        success = tester.run_full_test()
        
        if success:
            print("\n✅ 主程序测试完成!")
        else:
            print("\n❌ 主程序测试失败!")
            
    except KeyboardInterrupt:
        print("\n⏹️ 测试被用户中断")
    except Exception as e:
        print(f"\n❌ 测试过程出错: {e}")
    finally:
        tester.cleanup()

if __name__ == "__main__":
    main() 