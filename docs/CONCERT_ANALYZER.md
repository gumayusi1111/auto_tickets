# 演唱会信息分析工具

这是一个强大的演唱会信息提取和AI分析工具，专门用于从Weverse等平台提取演唱会信息，并通过大模型进行智能分析。

## 🌟 主要功能

- **信息提取**: 从Weverse页面自动提取演唱会信息
- **时间转换**: 自动将韩国时间转换为中国时间
- **AI分析**: 支持DeepSeek和OpenAI模型进行智能分析
- **实时显示**: 实时更新当前时间和演唱会倒计时
- **多选择器**: 支持自定义CSS选择器
- **无头模式**: 支持后台运行

## 📦 安装依赖

```bash
# 安装Python依赖
pip install -r requirements.txt

# 或者使用自动安装脚本
python install_dependencies.py
```

## 🔑 API密钥配置

### 方法1: 环境变量（推荐）

```bash
# DeepSeek API密钥
export DEEPSEEK_API_KEY="your_deepseek_api_key_here"

# OpenAI API密钥
export OPENAI_API_KEY="your_openai_api_key_here"

# 永久设置（添加到 ~/.bashrc 或 ~/.zshrc）
echo 'export DEEPSEEK_API_KEY="your_key"' >> ~/.bashrc
echo 'export OPENAI_API_KEY="your_key"' >> ~/.bashrc
source ~/.bashrc
```

### 方法2: 命令行参数

```bash
python concert_analyzer.py URL --api-key "your_api_key"
```

### 方法3: 交互式输入

程序运行时会自动提示输入API密钥（如果环境变量中没有找到）。

## 🚀 使用方法

### 基本用法

```bash
# 分析指定URL的演唱会信息
python concert_analyzer.py https://weverse.io/nct127/notice/27925
```

### 高级用法

```bash
# 使用OpenAI模型
python concert_analyzer.py https://weverse.io/nct127/notice/27925 --model openai

# 使用自定义选择器
python concert_analyzer.py https://weverse.io/nct127/notice/27925 --selector "p:nth-child(1)"

# 禁用AI分析
python concert_analyzer.py https://weverse.io/nct127/notice/27925 --no-ai

# 无头模式运行
python concert_analyzer.py https://weverse.io/nct127/notice/27925 --headless

# 自定义更新间隔
python concert_analyzer.py https://weverse.io/nct127/notice/27925 --interval 5

# 直接指定API密钥
python concert_analyzer.py https://weverse.io/nct127/notice/27925 --api-key "your_key"
```

### 测试AI连接

```bash
# 测试DeepSeek连接
python concert_analyzer.py --test-ai --model deepseek

# 测试OpenAI连接
python concert_analyzer.py --test-ai --model openai --api-key "your_openai_key"
```

## 📋 命令行参数

| 参数 | 简写 | 说明 | 默认值 |
|------|------|------|--------|
| `url` | - | Weverse页面URL（必需） | - |
| `--selector` | `-s` | CSS选择器 | 自动检测 |
| `--model` | `-m` | AI模型类型（deepseek/openai） | deepseek |
| `--no-ai` | - | 禁用AI分析 | False |
| `--headless` | - | 无头模式 | False |
| `--interval` | `-i` | 更新间隔（秒） | 1 |
| `--test-ai` | - | 测试AI连接 | False |
| `--api-key` | - | 直接指定API密钥 | None |

## 🎯 支持的页面格式

### Weverse公告页面

- 标准格式: `https://weverse.io/{artist}/notice/{id}`
- 示例: `https://weverse.io/nct127/notice/27925`

### 自定义选择器

如果默认选择器无法提取信息，可以使用自定义选择器：

```bash
# 使用自定义选择器
python concert_analyzer.py URL --selector "#modal p:nth-child(1)"
python concert_analyzer.py URL --selector ".notice-content p"
python concert_analyzer.py URL --selector "[class*='detail'] p"
```

## 🤖 AI分析功能

### 支持的模型

1. **DeepSeek** (推荐)
   - 模型: `deepseek-chat`
   - API地址: `https://api.deepseek.com`
   - 特点: 中文理解能力强，成本较低

2. **OpenAI**
   - 模型: `gpt-3.5-turbo`
   - API地址: `https://api.openai.com`（支持中转服务）
   - 特点: 分析能力强，响应速度快

### AI分析内容

- **基本信息提取**: 艺人名称、演唱会主题、地点等
- **时间验证**: 验证时区转换的准确性
- **重要提醒**: 距离演出时间、关键时间节点
- **行动建议**: 购票时间、准备事项等

## 📊 输出格式

### 基本信息

```
📝 提取的信息:
------------------------------
NCT 127 WORLD TOUR 'NEO CITY : THE UNITY' - SEOUL
2024년 1월 15일 (월) 19:00 KST
장소: 고척스카이돔

⏰ 时间信息:
------------------------------
时间1: 2024-01-15 20:00:00 (中国时间)
```

### AI分析结果

```
🤖 AI分析结果:
------------------------------
**演唱会基本信息**：
- 艺人/团体名称: NCT 127
- 演唱会名称: WORLD TOUR 'NEO CITY : THE UNITY'
- 举办地点: 首尔高尺天空巨蛋
- 演出时间: 2024年1月15日 20:00 (中国时间)

**时间分析**：
- 时区转换正确：韩国时间19:00 = 中国时间20:00
- 演出为单场，无多个时间点

**重要提醒**：
- 距离演出还有: 15天3小时
- 建议提前关注购票信息

**建议行动**：
- 设置购票提醒
- 准备护照等出行证件
- 关注官方购票渠道
```

## 🔧 配置文件

可以通过修改 `config_ai.py` 文件来自定义配置：

```python
# 修改AI模型配置
DEEPSEEK_CONFIG = {
    'api_key': 'your_key',
    'base_url': 'https://api.deepseek.com',
    'model_name': 'deepseek-chat',
    'max_tokens': 2000,
    'temperature': 0.7
}

# 修改显示配置
DISPLAY_CONFIG = {
    'update_interval': 1,
    'max_text_length': 500,
    'clear_screen': True
}
```

## 🛠️ 故障排除

### 常见问题

1. **浏览器无法启动**
   ```bash
   # 运行浏览器测试
   python quick_test.py
   ```

2. **无法提取信息**
   ```bash
   # 使用自定义选择器
   python concert_analyzer.py URL --selector "p"
   ```

3. **AI分析失败**
   ```bash
   # 测试AI连接
   python concert_analyzer.py --test-ai
   ```

4. **时间解析错误**
   - 检查页面内容是否包含标准时间格式
   - 尝试不同的选择器

### 调试模式

```bash
# 禁用无头模式查看浏览器操作
python concert_analyzer.py URL --no-headless

# 禁用AI分析专注于信息提取
python concert_analyzer.py URL --no-ai
```

## 📝 开发说明

### 项目结构

```
auto/
├── concert_analyzer.py          # 主程序
├── config_ai.py                 # AI配置文件
├── modules/
│   ├── concert_info_extractor.py # 信息提取器
│   ├── ai_analyzer.py           # AI分析器
│   ├── browser_setup.py         # 浏览器设置
│   └── url_handler.py           # URL处理
├── requirements.txt             # 依赖列表
└── README_CONCERT_ANALYZER.md   # 使用说明
```

### 扩展功能

1. **添加新的AI模型**
   - 在 `ai_analyzer.py` 中添加新的模型配置
   - 更新 `config_ai.py` 中的配置

2. **支持新的页面格式**
   - 在 `config_ai.py` 中添加新的选择器
   - 更新时间解析正则表达式

3. **自定义分析提示词**
   - 修改 `config_ai.py` 中的 `PROMPT_TEMPLATES`

## 🔗 相关链接

- [DeepSeek API文档](https://platform.deepseek.com/api-docs/)
- [OpenAI API文档](https://platform.openai.com/docs/)
- [Selenium文档](https://selenium-python.readthedocs.io/)
- [Weverse官网](https://weverse.io/)

## 📄 许可证

本项目仅供学习和个人使用，请遵守相关网站的使用条款。

## 🤝 贡献

欢迎提交Issue和Pull Request来改进这个工具！

---

**注意**: 使用本工具时请遵守目标网站的robots.txt和使用条款，避免过于频繁的请求。