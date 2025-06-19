"""浏览器设置模块"""

import sys
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager


def setup_driver(headless=False):
    """设置并返回Chrome WebDriver，优化反检测功能和网络连接"""
    options = Options()
    
    # 基础设置
    if headless:
        options.add_argument('--headless=new')  # 使用新的headless模式
    
    # 核心反检测参数
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('--disable-web-security')
    options.add_argument('--disable-features=VizDisplayCompositor')
    options.add_argument('--disable-extensions')
    options.add_argument('--disable-plugins')
    options.add_argument('--disable-images')  # 禁用图片加载提升速度
    # options.add_argument('--disable-javascript')  # 注释掉，保持JS功能
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-software-rasterizer')
    options.add_argument('--disable-background-timer-throttling')
    options.add_argument('--disable-backgrounding-occluded-windows')
    options.add_argument('--disable-renderer-backgrounding')
    options.add_argument('--disable-field-trial-config')
    options.add_argument('--disable-back-forward-cache')
    options.add_argument('--disable-ipc-flooding-protection')
    
    # 隐私和安全设置
    options.add_argument('--no-first-run')
    options.add_argument('--no-default-browser-check')
    options.add_argument('--disable-default-apps')
    options.add_argument('--disable-popup-blocking')
    options.add_argument('--disable-translate')
    options.add_argument('--disable-background-networking')
    options.add_argument('--disable-sync')
    options.add_argument('--metrics-recording-only')
    options.add_argument('--no-report-upload')
    
    # 窗口和显示设置
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--start-maximized')
    
    # 实验性选项
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_experimental_option("detach", True)
    
    # 启用性能日志以支持网络请求监控 - 修复：使用正确的配置方式
    options.set_capability('goog:loggingPrefs', {
        'performance': 'ALL',
        'browser': 'ALL',
        'network': 'ALL'
    })
    
    # 设置日志级别
    options.add_argument('--enable-logging')
    options.add_argument('--log-level=0')
    options.add_argument('--v=1')
    
    # 高级反检测prefs设置
    prefs = {
        "profile.default_content_setting_values": {
            "notifications": 2,  # 禁用通知
            "geolocation": 2,    # 禁用地理位置
            "media_stream": 2,   # 禁用摄像头麦克风
        },
        "profile.default_content_settings.popups": 0,
        "profile.managed_default_content_settings.images": 2,  # 禁用图片
        "profile.password_manager_enabled": False,
        "credentials_enable_service": False,
        "profile.password_manager_leak_detection": False,
        "autofill.profile_enabled": False,
        "autofill.credit_card_enabled": False,
        "translate_enabled": False,
        "safebrowsing.enabled": False
    }
    options.add_experimental_option("prefs", prefs)
    
    # 设置真实的用户代理（最新Chrome版本）
    user_agents = [
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
    ]
    import random
    options.add_argument(f'--user-agent={random.choice(user_agents)}')
    
    try:
        # 方法1: 首先尝试使用系统的ChromeDriver
        try:
            # 在macOS上尝试常见的Chrome路径
            import platform
            if platform.system() == "Darwin":  # macOS
                options.binary_location = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
            
            # 尝试不指定service路径，让系统自己找
            driver = webdriver.Chrome(options=options)
            print("✅ 使用系统ChromeDriver启动成功")
            
        except Exception as system_error:
            print(f"⚠️ 系统ChromeDriver启动失败: {system_error}")
            
            # 方法2: 尝试使用手动下载的ChromeDriver
            manual_paths = [
                "./chromedriver",  # 当前目录
                "/usr/local/bin/chromedriver",  # 系统路径
                "/opt/homebrew/bin/chromedriver",  # Homebrew路径
                os.path.expanduser("~/chromedriver"),  # 用户目录
            ]
            
            manual_driver_found = False
            for path in manual_paths:
                if os.path.exists(path) and os.access(path, os.X_OK):
                    try:
                        service = Service(path)
                        driver = webdriver.Chrome(service=service, options=options)
                        print(f"✅ 使用手动ChromeDriver启动成功: {path}")
                        manual_driver_found = True
                        break
                    except Exception as manual_error:
                        continue
            
            if not manual_driver_found:
                # 方法3: 尝试使用webdriver-manager (可能需要网络)
                print("🔄 正在下载最新的ChromeDriver...")
                try:
                    # 设置镜像源以提高下载成功率
                    os.environ['WDM_LOCAL'] = '1'  # 优先使用本地缓存
                    os.environ['WDM_LOG_LEVEL'] = '0'  # 减少日志输出
                    
                    service = Service(ChromeDriverManager().install())
                    driver = webdriver.Chrome(service=service, options=options)
                    print("✅ 使用下载的ChromeDriver启动成功")
                    
                except Exception as download_error:
                    print(f"❌ ChromeDriver下载失败: {download_error}")
                    print("\n🛠️ 解决方案:")
                    print("1. 检查网络连接")
                    print("2. 手动下载ChromeDriver并放到项目目录")
                    print("3. 确保Chrome浏览器已安装")
                    
                    # 提供手动下载指导
                    print("\n📥 手动下载步骤:")
                    print("1. 访问: https://googlechromelabs.github.io/chrome-for-testing/")
                    print("2. 下载与你Chrome版本匹配的ChromeDriver")
                    print("3. 解压后将chromedriver文件放到项目根目录")
                    print("4. 运行: chmod +x ./chromedriver")
                    
                    raise Exception("无法获取ChromeDriver，请手动下载")
        
        # 执行反检测脚本
        stealth_js = """
        // 移除webdriver属性
        Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
        
        // 修改plugins
        Object.defineProperty(navigator, 'plugins', {
            get: () => [1, 2, 3, 4, 5]
        });
        
        // 修改languages
        Object.defineProperty(navigator, 'languages', {
            get: () => ['en-US', 'en', 'zh-CN', 'zh']
        });
        
        // 修改platform
        Object.defineProperty(navigator, 'platform', {
            get: () => 'MacIntel'
        });
        
        // 修改hardwareConcurrency
        Object.defineProperty(navigator, 'hardwareConcurrency', {
            get: () => 8
        });
        
        // 修改deviceMemory
        Object.defineProperty(navigator, 'deviceMemory', {
            get: () => 8
        });
        
        // 移除自动化相关属性
        delete window.chrome.runtime.onConnect;
        delete window.chrome.runtime.onMessage;
        
        // 伪造chrome对象
        window.chrome = {
            runtime: {},
            loadTimes: function() {},
            csi: function() {},
            app: {}
        };
        
        // 修改权限查询
        const originalQuery = window.navigator.permissions.query;
        window.navigator.permissions.query = (parameters) => (
            parameters.name === 'notifications' ?
                Promise.resolve({ state: Notification.permission }) :
                originalQuery(parameters)
        );
        
        // 伪造WebGL指纹
        const getParameter = WebGLRenderingContext.getParameter;
        WebGLRenderingContext.prototype.getParameter = function(parameter) {
            if (parameter === 37445) {
                return 'Intel Inc.';
            }
            if (parameter === 37446) {
                return 'Intel Iris OpenGL Engine';
            }
            return getParameter(parameter);
        };
        """
        
        driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
            'source': stealth_js
        })
        
        # 设置视口大小
        driver.execute_cdp_cmd('Emulation.setDeviceMetricsOverride', {
            'width': 1920,
            'height': 1080,
            'deviceScaleFactor': 1,
            'mobile': False
        })
        
        # 设置时区
        driver.execute_cdp_cmd('Emulation.setTimezoneOverride', {
            'timezoneId': 'Asia/Shanghai'
        })
        
        # 设置地理位置
        driver.execute_cdp_cmd('Emulation.setGeolocationOverride', {
            'latitude': 39.9042,
            'longitude': 116.4074,
            'accuracy': 100
        })
        
        return driver
        
    except Exception as e:
        print(f"❌ 浏览器启动失败: {e}")
        print("请确保已安装Chrome浏览器")
        print("正在尝试自动下载ChromeDriver...")
        sys.exit(1)


def create_wait(driver, timeout=10):
    """创建WebDriverWait对象"""
    return WebDriverWait(driver, timeout)


def download_chromedriver_manually():
    """提供手动下载ChromeDriver的指导"""
    print("\n🔧 手动下载ChromeDriver指导:")
    print("=" * 50)
    print("1. 打开Chrome浏览器，访问 chrome://version/")
    print("2. 记下你的Chrome版本号 (例如: 131.0.6778.xxx)")
    print("3. 访问: https://googlechromelabs.github.io/chrome-for-testing/")
    print("4. 下载对应版本的ChromeDriver for macOS")
    print("5. 解压文件，将chromedriver文件放到项目根目录")
    print("6. 在终端运行: chmod +x ./chromedriver")
    print("7. 重新运行程序")
    print("=" * 50)