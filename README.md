# Weverse 自动化工具集

一个集成了 Weverse 自动报名和演唱会信息分析功能的 Python 工具集。

## 🚀 快速开始

### 1. 一键启动（推荐）

```bash
# 自动激活虚拟环境并进入项目
./start.sh
```

这个脚本会自动：
- 创建/激活虚拟环境
- 安装必要依赖
- 测试API连通性
- 进入项目环境

### 2. 手动环境准备

```bash
# 手动激活虚拟环境
source .venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 2. 功能使用

#### 演唱会信息分析
```bash
# 基本使用
python -m src.concert.concert_analyzer https://weverse.io/nct127/notice/27925

# 启用AI分析（需要API密钥）
export DEEPSEEK_API_KEY="your_api_key"
python -m src.concert.concert_analyzer https://weverse.io/nct127/notice/27925 --enable-ai

# 查看帮助
python -m src.concert.concert_analyzer --help
```

#### Weverse 自动报名
```bash
# 基础自动报名
python -m src.weverse.weverse_auto

# 带邮箱验证码的自动报名
python -m src.weverse.weverse_with_email
```

## 📁 项目结构

```
├── src/                    # 源代码目录
│   ├── core/              # 核心模块
│   │   ├── browser_setup.py    # 浏览器设置
│   │   ├── config.py           # 配置文件
│   │   ├── time_handler.py     # 时间处理
│   │   └── url_handler.py      # URL处理
│   ├── weverse/           # Weverse功能
│   │   ├── button_clicker.py   # 按钮点击
│   │   ├── form_crawler.py     # 表单爬取
│   │   ├── form_filler.py      # 表单填写
│   │   ├── form_submitter.py   # 表单提交
│   │   ├── email_verifier.py   # 邮箱验证
│   │   ├── verification_helper.py # 验证辅助
│   │   ├── weverse_auto.py     # 主程序
│   │   └── weverse_with_email.py # 带邮箱验证
│   └── concert/           # 演唱会分析
│       ├── ai_analyzer.py      # AI分析器
│       ├── concert_info_extractor.py # 信息提取
│       └── concert_analyzer.py # 主程序
├── tests/                 # 测试文件
├── docs/                  # 文档
├── config/                # 配置文件
├── scripts/               # 脚本文件
├── .venv/                 # 虚拟环境
├── requirements.txt       # 依赖文件
└── activate_env.sh        # 环境激活脚本
```

## 🔧 配置说明

### AI分析配置

**API密钥已配置完成！** 当前使用的DeepSeek API密钥：`sk-d246fe03fd164cf3abf49f45d0220d21`

在 `config/ai_config.py` 中可以查看和修改AI服务配置：

```python
# DeepSeek配置
DEEPSEEK_CONFIG = {
    'api_key': os.getenv('DEEPSEEK_API_KEY', 'sk-d246fe03fd164cf3abf49f45d0220d21'),
    'base_url': 'https://api.deepseek.com',
    'model_name': 'deepseek-chat'
}
```

### API连通性测试

```bash
# 测试API是否正常工作
python scripts/test_api.py
```

### 环境变量

```bash
# AI分析API密钥
export DEEPSEEK_API_KEY="your_deepseek_api_key"
export OPENAI_API_KEY="your_openai_api_key"

# 邮箱配置（用于验证码获取）
export EMAIL_ADDRESS="your_email@example.com"
export EMAIL_PASSWORD="your_email_password"
```

### 个人信息配置

编辑 `src/core/config.py` 文件，设置个人信息：

```python
# 个人信息配置
BIRTH_DATE = "1990-01-01"  # 生日
PHONE_NUMBER = "010-1234-5678"  # 电话号码
```

## 📚 功能详解

### 1. 演唱会信息分析

- **自动提取**: 从 Weverse 页面提取演唱会时间信息
- **时间转换**: 自动将韩国时间转换为中国时间
- **实时显示**: 实时显示当前时间和倒计时
- **AI分析**: 支持 DeepSeek 和 OpenAI 模型分析演唱会信息

### 2. Weverse 自动报名

- **定时点击**: 精确到毫秒的定时点击报名按钮
- **表单填写**: 自动填写个人信息表单
- **邮箱验证**: 自动获取并填入邮箱验证码
- **多重保障**: 多种选择器确保兼容性

## 🛠️ 故障排除

### 常见问题

1. **虚拟环境问题**
   ```bash
   # 重新创建虚拟环境
   rm -rf .venv
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. **浏览器驱动问题**
   ```bash
   # 更新Chrome驱动
   pip install --upgrade webdriver-manager
   ```

3. **导入模块问题**
   ```bash
   # 确保在项目根目录运行
   cd /path/to/project
   python -m src.concert.concert_analyzer --help
   ```

### 调试模式

```bash
# 启用详细日志
python -m src.concert.concert_analyzer --debug https://example.com

# 使用非无头模式（显示浏览器窗口）
python -m src.concert.concert_analyzer --no-headless https://example.com
```

## 📖 文档链接

- [演唱会分析器详细文档](docs/CONCERT_ANALYZER.md)
- [Weverse自动化详细文档](docs/WEVERSE_AUTO.md)
- [邮箱验证设置指南](docs/EMAIL_VERIFICATION.md)

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

本项目采用 MIT 许可证。