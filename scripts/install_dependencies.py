#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
install_dependencies.py
依赖安装脚本 - 自动安装项目所需的所有依赖
"""

import subprocess
import sys
import os

def run_command(command):
    """运行命令并返回结果"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def check_python():
    """检查Python版本"""
    print("🔍 检查Python版本...")
    version = sys.version_info
    print(f"📍 Python版本: {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ 需要Python 3.8或更高版本")
        return False
    
    print("✅ Python版本符合要求")
    return True

def check_pip():
    """检查pip是否可用"""
    print("\n🔍 检查pip...")
    success, stdout, stderr = run_command("pip3 --version")
    
    if success:
        print(f"✅ pip3可用: {stdout.strip()}")
        return True
    else:
        print("❌ pip3不可用")
        print("💡 请安装pip3")
        return False

def install_requirements():
    """安装requirements.txt中的依赖"""
    print("\n📦 安装项目依赖...")
    
    if not os.path.exists("requirements.txt"):
        print("❌ 找不到requirements.txt文件")
        return False
    
    print("📋 正在安装依赖包...")
    success, stdout, stderr = run_command("pip3 install -r requirements.txt")
    
    if success:
        print("✅ 依赖安装成功")
        return True
    else:
        print(f"❌ 依赖安装失败: {stderr}")
        return False

def install_core_packages():
    """安装核心包"""
    print("\n📦 安装核心包...")
    
    core_packages = [
        "selenium>=4.20.0",
        "webdriver-manager>=4.0.1",
        "requests>=2.28.0",
        "beautifulsoup4>=4.11.0"
    ]
    
    for package in core_packages:
        print(f"📍 安装 {package}...")
        success, stdout, stderr = run_command(f"pip3 install {package}")
        
        if success:
            print(f"✅ {package} 安装成功")
        else:
            print(f"❌ {package} 安装失败: {stderr}")
            return False
    
    return True

def verify_installation():
    """验证安装"""
    print("\n🔍 验证安装...")
    
    test_imports = [
        ("selenium", "from selenium import webdriver"),
        ("webdriver_manager", "from webdriver_manager.chrome import ChromeDriverManager"),
        ("requests", "import requests"),
        ("bs4", "from bs4 import BeautifulSoup")
    ]
    
    all_success = True
    for name, import_cmd in test_imports:
        try:
            exec(import_cmd)
            print(f"✅ {name} 导入成功")
        except ImportError as e:
            print(f"❌ {name} 导入失败: {e}")
            all_success = False
    
    return all_success

def main():
    """主函数"""
    print("🚀 开始安装项目依赖...\n")
    
    # 检查Python版本
    if not check_python():
        sys.exit(1)
    
    # 检查pip
    if not check_pip():
        sys.exit(1)
    
    # 尝试安装requirements.txt
    if os.path.exists("requirements.txt"):
        if not install_requirements():
            print("⚠️ requirements.txt安装失败，尝试手动安装核心包...")
            if not install_core_packages():
                sys.exit(1)
    else:
        print("⚠️ 未找到requirements.txt，安装核心包...")
        if not install_core_packages():
            sys.exit(1)
    
    # 验证安装
    if verify_installation():
        print("\n🎉 所有依赖安装成功!")
        print("💡 现在可以运行项目脚本了")
        print("\n📋 建议运行以下命令测试:")
        print("   python3 quick_test.py")
        print("   python3 test_url_access.py")
    else:
        print("\n❌ 部分依赖安装失败")
        print("💡 请手动安装失败的包")
        sys.exit(1)

if __name__ == "__main__":
    main()