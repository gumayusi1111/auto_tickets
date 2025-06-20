# 全自动表单填写使用指南

## 概述

本指南介绍如何使用改进后的全自动模式，该模式现在支持使用具体的CSS选择器来精确定位和填写表单元素。

## 功能特点

1. **精确元素定位**：使用具体的CSS选择器，而不是通用搜索
2. **高速填写**：目标在0.5秒内完成所有表单填写
3. **自动勾选复选框**：支持多个复选框的自动勾选
4. **智能备用方案**：当具体选择器失败时，自动使用通用检测方法

## 配置文件说明

### 1. 表单选择器配置 (`config/form_selectors.py`)

```python
WEVERSE_FORM_SELECTORS = {
    # 输入框
    'birth_date': '#requiredProperties-birthDate',
    'phone_number': '#requiredProperties-phoneNumber',
    
    # 复选框（SVG元素选择器）
    'checkboxes': [
        # 第一个复选框
        '#root > div > div > div > form > section.sc-jJEKmz.hKDpP > div > div > div:nth-child(2) > div > div.sc-fWPcWZ.hNoznW > label > span.sc-khAkCZ.sc-hTZgZg.ewSqYc.fpLDWJ > svg',
        # 第二个复选框  
        '#root > div > div > div > form > section.sc-jJEKmz.hKDpP > div > div > div:nth-child(3) > div > div.sc-fWPcWZ.hNoznW > label > span.sc-khAkCZ.sc-hTZgZg.ewSqYc.fpLDWJ > svg'
    ],
    
    # 提交按钮选择器
    'submit_button_selectors': [
        'button[type="submit"]',
        'button:contains("참여 신청")',
        'button:contains("신청")',
        'button:last-of-type',
    ]
}
```

### 2. 用户数据配置 (`config/user_data.py`)

```python
DEFAULT_USER_DATA = {
    'birth_date': '19900101',      # 生日格式：YYYYMMDD
    'phone_number': '01012345678',  # 韩国手机号格式
}
```

## 使用方法

### 1. 更新表单选择器

如果您发现了新的表单元素选择器，可以在 `config/form_selectors.py` 中更新：

```python
# 编辑 config/form_selectors.py
WEVERSE_FORM_SELECTORS = {
    'birth_date': '您的生日输入框选择器',
    'phone_number': '您的手机号输入框选择器',
    'checkboxes': [
        '第一个复选框选择器',
        '第二个复选框选择器'
    ],
    # ...
}
```

### 2. 更新用户数据

修改 `config/user_data.py` 来设置您的个人信息：

```python
DEFAULT_USER_DATA = {
    'birth_date': '19951225',      # 您的生日
    'phone_number': '01098765432',  # 您的手机号
}
```

### 3. 运行全自动模式

```bash
# 运行主程序
python src/weverse/core/main.py

# 选择模式 1（全自动模式）
```

## 测试功能

### 测试表单填写

```bash
# 运行测试脚本
python tests/test_auto_form_fill.py
```

测试脚本功能：
- 验证配置文件是否正确加载
- 测试表单元素检测
- 测试表单填写流程
- 显示性能分析结果

## 性能优化

### 闪电表单处理器的优化策略

1. **并行处理**：同时查找和填写多个表单元素
2. **JavaScript注入**：直接使用JS设置值，避免模拟键盘输入
3. **智能检测**：优先使用具体选择器，失败时使用通用方法

### 性能目标

- 元素检测：< 0.1秒
- 表单填写：< 0.3秒
- 表单提交：< 0.1秒
- **总目标：< 0.5秒**

## 故障排除

### 1. 元素未找到

如果提示"未找到表单元素"：
- 检查选择器是否正确
- 使用监控模式重新获取选择器
- 查看页面是否完全加载

### 2. 填写失败

如果表单填写失败：
- 检查输入格式是否正确
- 确认元素是否可见和可用
- 查看控制台错误信息

### 3. 复选框点击失败

复选框使用SVG元素时：
- 程序会自动查找可点击的父元素
- 如果失败，尝试获取包含`<input type="checkbox">`的元素选择器

## 最佳实践

1. **定期更新选择器**：网站可能会更新，需要及时更新选择器
2. **使用监控模式**：先用监控模式获取准确的选择器
3. **测试验证**：修改后使用测试脚本验证功能
4. **备份配置**：保存多套选择器配置以应对网站变化

## 注意事项

- 请确保遵守网站的使用条款
- 不要过于频繁地运行程序
- 保护好您的个人信息
- 定期检查和更新配置文件 