#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
download_chromedriver.py
ChromeDriver 下载脚本 - 解决网络连接问题
"""

import os
import sys
import platform
import subprocess
import requests
import zipfile
from pathlib import Path


def get_chrome_version():
    """获取Chrome浏览器版本"""
    system = platform.system()
    
    try:
        if system == "Darwin":  # macOS
            # 方法1: 通过命令行获取
            result = subprocess.run([
                "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome", 
                "--version"
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                version = result.stdout.strip().split()[-1]
                return version
            
            # 方法2: 通过Info.plist获取
            plist_path = "/Applications/Google Chrome.app/Contents/Info.plist"
            if os.path.exists(plist_path):
                result = subprocess.run([
                    "defaults", "read", plist_path, "CFBundleShortVersionString"
                ], capture_output=True, text=True)
                if result.returncode == 0:
                    return result.stdout.strip()
        
        elif system == "Windows":
            # Windows Chrome版本检测
            import winreg
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                               r"Software\Google\Chrome\BLBeacon")
            version, _ = winreg.QueryValueEx(key, "version")
            return version
            
        elif system == "Linux":
            # Linux Chrome版本检测
            result = subprocess.run(["google-chrome", "--version"], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout.strip().split()[-1]
    
    except Exception as e:
        print(f"⚠️ 无法自动检测Chrome版本: {e}")
        return None
    
    return None


def download_chromedriver(version=None, force_version=None):
    """下载ChromeDriver"""
    print("🚀 ChromeDriver 下载器")
    print("=" * 40)
    
    # 确定系统架构
    system = platform.system()
    machine = platform.machine()
    
    if system == "Darwin":
        if machine == "arm64":
            platform_name = "mac-arm64"
        else:
            platform_name = "mac-x64"
    elif system == "Windows":
        platform_name = "win64" if machine.endswith("64") else "win32"
    elif system == "Linux":
        platform_name = "linux64"
    else:
        print(f"❌ 不支持的系统: {system}")
        return False
    
    print(f"🖥️ 检测到系统: {system} ({platform_name})")
    
    # 获取Chrome版本
    if force_version:
        chrome_version = force_version
        print(f"🎯 使用指定版本: {chrome_version}")
    else:
        chrome_version = get_chrome_version()
        if chrome_version:
            print(f"✅ 检测到Chrome版本: {chrome_version}")
        else:
            print("⚠️ 无法检测Chrome版本，使用默认版本")
            chrome_version = "131.0.6778.87"  # 默认版本
    
    # 获取主版本号
    major_version = chrome_version.split('.')[0]
    
    try:
        # 尝试下载ChromeDriver
        print(f"📥 正在下载 ChromeDriver {chrome_version}...")
        
        # Chrome for Testing API
        base_url = "https://googlechromelabs.github.io/chrome-for-testing"
        api_url = f"{base_url}/latest-patch-versions-per-build-with-downloads.json"
        
        # 备用下载源
        mirrors = [
            "https://googlechromelabs.github.io/chrome-for-testing",
            "https://storage.googleapis.com/chrome-for-testing-public",
            "https://chromedriver.storage.googleapis.com"
        ]
        
        download_success = False
        
        for mirror_base in mirrors:
            try:
                print(f"🔗 尝试镜像源: {mirror_base}")
                
                if "googlechromelabs" in mirror_base:
                    # 新API方式
                    download_url = f"{mirror_base}/{major_version}/mac-x64/chromedriver-mac-x64.zip"
                else:
                    # 旧API方式
                    download_url = f"{mirror_base}/{chrome_version}/chromedriver_{platform_name}.zip"
                
                print(f"📡 下载地址: {download_url}")
                
                # 下载文件
                response = requests.get(download_url, timeout=30, stream=True)
                response.raise_for_status()
                
                # 保存到临时文件
                zip_path = "chromedriver.zip"
                with open(zip_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                
                print(f"✅ 下载完成: {zip_path}")
                
                # 解压文件
                print("📂 正在解压...")
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall("./")
                
                # 查找chromedriver文件
                extracted_files = []
                for root, dirs, files in os.walk("./"):
                    for file in files:
                        if file == "chromedriver" or file == "chromedriver.exe":
                            extracted_files.append(os.path.join(root, file))
                
                if extracted_files:
                    chromedriver_path = extracted_files[0]
                    final_path = "./chromedriver"
                    
                    # 移动到项目根目录
                    if chromedriver_path != final_path:
                        os.rename(chromedriver_path, final_path)
                    
                    # 设置执行权限 (macOS/Linux)
                    if system != "Windows":
                        os.chmod(final_path, 0o755)
                    
                    print(f"✅ ChromeDriver 安装成功: {final_path}")
                    
                    # 清理临时文件
                    os.remove(zip_path)
                    download_success = True
                    break
                
            except Exception as e:
                print(f"❌ 镜像源 {mirror_base} 失败: {e}")
                continue
        
        if download_success:
            print("\n🎉 ChromeDriver 下载完成!")
            print("现在可以重新运行程序了")
            return True
        else:
            print("\n❌ 所有下载源都失败了")
            return False
            
    except Exception as e:
        print(f"❌ 下载失败: {e}")
        return False


def manual_download_guide():
    """手动下载指导"""
    print("\n🔧 手动下载指导:")
    print("=" * 40)
    print("如果自动下载失败，请手动下载:")
    print()
    print("1. 检查Chrome版本:")
    print("   - 打开Chrome浏览器")
    print("   - 访问 chrome://version/")
    print("   - 记下版本号")
    print()
    print("2. 下载ChromeDriver:")
    print("   - 访问: https://googlechromelabs.github.io/chrome-for-testing/")
    print("   - 选择对应版本的ChromeDriver")
    print("   - 下载 mac-x64 版本 (macOS)")
    print()
    print("3. 安装:")
    print("   - 解压下载的文件")
    print("   - 将 chromedriver 文件放到项目根目录")
    print("   - 运行: chmod +x ./chromedriver")
    print()
    print("4. 重新运行程序")


def main():
    """主函数"""
    print("🔧 ChromeDriver 管理工具")
    print("=" * 40)
    
    if len(sys.argv) > 1:
        # 命令行指定版本
        version = sys.argv[1]
        success = download_chromedriver(force_version=version)
    else:
        # 自动检测版本
        success = download_chromedriver()
    
    if not success:
        manual_download_guide()
        return False
    
    return True


if __name__ == "__main__":
    main() 