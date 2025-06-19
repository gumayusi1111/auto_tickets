# Weverse 自动报名脚本 - 重构版本

## 项目结构

```
auto/
├── weverse_complete_auto.py      # 原始版本（单文件）
├── weverse_auto_refactored.py    # 重构版本（模块化）
├── requirements.txt              # 依赖包
├── README_refactored.md         # 重构版本说明
└── modules/                     # 功能模块目录
    ├── __init__.py             # 模块包初始化
    ├── config.py               # 配置信息
    ├── browser_setup.py        # 浏览器初始化
    ├── time_handler.py         # 时间处理
    ├── button_clicker.py       # 按钮点击
    ├── form_crawler.py         # 表单爬取
    ├── form_filler.py          # 表单填写
    ├── form_submitter.py       # 表单提交
    └── url_handler.py          # URL处理
```

## 模块说明

### 1. config.py - 配置模块
- 存储目标URL、个人信息、时间设置等配置
- 集中管理所有可配置参数

### 2. browser_setup.py - 浏览器设置模块
- `setup_driver()`: 初始化Chrome浏览器
- `create_wait()`: 创建WebDriverWait对象

### 3. time_handler.py - 时间处理模块
- `get_time_input()`: 获取用户输入的目标时间
- `calculate_target_time()`: 计算准确的点击时间
- `show_countdown()`: 显示倒计时

### 4. button_clicker.py - 按钮点击模块
- `click_apply_button()`: 尝试多种选择器点击报名按钮

### 5. form_crawler.py - 表单爬取模块
- `crawl_form_elements()`: 爬取页面表单元素并保存到JSON文件

### 6. form_filler.py - 表单填写模块
- `fill_birth_date()`: 填写生日信息
- `fill_phone_number()`: 填写手机号
- `check_agreement_boxes()`: 勾选同意条款

### 7. form_submitter.py - 表单提交模块
- `submit_form()`: 提交表单
- `auto_fill_and_submit_form()`: 自动填写并提交表单的主流程

### 8. url_handler.py - URL处理模块
- `get_target_url()`: 获取目标URL的主函数
- `get_url_from_args()`: 从命令行参数获取URL
- `get_url_interactive()`: 交互式获取URL
- `validate_url()`: 验证URL格式

### 9. email_verifier.py - 邮箱验证码获取模块
- `EmailVerifier`: 邮箱连接和操作类
- `get_verification_code_interactive()`: 交互式获取验证码

### 10. verification_helper.py - 验证码处理辅助模块
- `get_verification_code()`: 通用验证码获取函数
- `get_qq_verification_code()`: QQ邮箱专用函数
- `auto_input_verification_code()`: 自动获取并输入验证码

## 使用方法

### 运行重构版本

#### 1. 基础版本（无邮箱验证码）
```bash
# 使用完整参数名
python3 weverse_auto_refactored.py --url "https://weverse.io/nct127/notice/27902"

# 使用简短参数名
python3 weverse_auto_refactored.py -u "https://weverse.io/example/notice/12345"

# 查看帮助信息
python3 weverse_auto_refactored.py --help

# 交互式输入URL
python3 weverse_auto_refactored.py
```

#### 2. 邮箱验证码版本
```bash
# 使用授权码（推荐）
python3 weverse_with_email_verification.py \
  --url "https://weverse.io/example" \
  --email "your_email@qq.com" \
  --email-password "your_auth_code" \
  --sender-filter "weverse"

# 使用真实密码
python3 weverse_with_email_verification.py \
  --url "https://weverse.io/example" \
  --email "your_email@qq.com" \
  --email-password "your_real_password" \
  --use-real-password \
  --sender-filter "weverse"

# 交互式配置（会提示选择密码类型）
python3 weverse_with_email_verification.py
```

#### 3. 使用默认URL
```bash
# 直接运行，按Enter使用默认URL
python3 weverse_auto_refactored.py
```

### 运行原始版本
```bash
python3 weverse_complete_auto.py
```

## 重构优势

1. **模块化设计**: 每个功能独立成模块，便于维护和测试
2. **代码复用**: 各模块可以独立使用或组合使用
3. **配置集中**: 所有配置信息集中在config.py中
4. **职责分离**: 每个模块只负责特定功能
5. **易于扩展**: 新增功能只需添加新模块
6. **便于调试**: 可以单独测试每个模块的功能
7. **灵活的URL输入**: 支持命令行参数、交互式输入和默认配置
8. **URL验证**: 自动验证URL格式，提供安全提示
9. **邮箱验证码自动化**: 支持多种邮箱服务商的验证码自动获取
10. **智能验证码识别**: 自动提取邮件中的验证码并填入表单
11. **灵活的密码方式**: 支持授权码和真实密码两种登录方式
12. **完整的测试套件**: 提供详细的测试脚本和使用示例

## 依赖要求

确保已安装以下依赖包：
```
pyautogui==0.9.54
selenium==4.15.2
webdriver-manager==4.0.1
imaplib2>=0.57
email-validator>=1.3.0
beautifulsoup4>=4.11.0
requests>=2.28.0
```

安装命令：
```bash
pip3 install -r requirements.txt
```

## 注意事项

1. 使用前请在 `modules/config.py` 中修改个人信息
2. 确保Chrome浏览器已安装
3. 脚本会自动下载对应版本的ChromeDriver
4. 运行时需要手动登录Weverse账号
5. **邮箱安全**: 推荐使用授权码，真实密码仅用于测试
6. **邮箱设置**: 确保邮箱已开启IMAP服务，详见 `EMAIL_VERIFICATION_GUIDE.md`
7. **测试文件**: 所有测试脚本已移至 `tests/` 文件夹