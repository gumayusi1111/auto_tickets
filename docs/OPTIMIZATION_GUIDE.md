# Weverse 自动化工具延迟优化指南

## 🚀 最新优化内容（2024更新）

### 1. 延迟计算优化 - 区分场景

#### 外部请求 vs 页面内跳转

我们发现了一个重要区别：
- **外部请求（Postman场景）**：730ms - 从外部直接请求服务器，需要建立新连接
- **页面内跳转（实际场景）**：~300ms - 页面内导航，复用连接，可能有缓存

#### 优化后的延迟计算：

**页面内跳转（默认推荐）**：
```
总延迟 = 300ms (网络延迟) + 80ms (浏览器开销) + 100ms (安全边际) = 480ms
```

**外部请求（Postman测试）**：
```
总延迟 = 730ms (网络延迟) + 80ms (浏览器开销) + 100ms (安全边际) = 910ms
```

#### 为什么页面内跳转更快？
1. **复用TCP/HTTPS连接** - 无需重新握手
2. **浏览器缓存** - 静态资源可能已缓存
3. **无需DNS解析** - 域名已解析
4. **Keep-Alive连接** - HTTP持久连接

#### 配置文件位置：
`config/latency_config.py` - 可以通过修改 `scenario` 参数切换场景

### 2. 监控功能增强

#### 修复的问题：
1. **循环检测失败** - 增加了页面状态检查
2. **错误处理优化** - 避免因单个错误中断监控
3. **调试信息增强** - 显示详细的错误堆栈

#### 新增功能：
1. **实时用户操作追踪**
   - 自动记录所有点击、输入、复选框选择等操作
   - 记录操作的元素XPath和详细信息
   
2. **增强的网络请求监控**
   - 详细记录POST/PUT等重要请求
   - 显示请求和响应数据摘要
   
3. **持续监控模式**
   - 点击申请按钮后持续监控
   - 直到用户在终端按Enter结束
   - 自动保存完整的操作链路数据

### 3. 使用方法

#### 基本运行：
```bash
python -m src.weverse.core.main
```

#### 切换延迟场景：
编辑 `config/latency_config.py`：
```python
'scenario': 'internal',  # 页面内跳转（推荐）
# 或
'scenario': 'external',  # 外部请求（Postman场景）
```

### 4. 数据输出

监控数据会保存在 `data/` 目录下，包括：
- 网络请求完整记录
- 用户操作序列
- 页面状态快照
- 表单元素分析

### 5. 性能指标

- **页面内跳转延迟**：480ms（优化后）
- **外部请求延迟**：910ms（Postman场景）
- **表单填写速度**：0.5秒内完成（自动模式）
- **监控采样率**：每0.5秒检查一次

### 6. 故障排除

#### 循环检测失败：
- 原因：页面未完全加载或JavaScript执行错误
- 解决：程序已增加页面状态检查，会自动跳过错误继续监控

#### 延迟不准确：
- 检查实际场景是页面内跳转还是外部请求
- 根据实际情况调整 `config/latency_config.py` 中的场景设置
- 启用动态检测功能自动适应网络变化

### 7. 推荐设置

对于Weverse自动报名场景，推荐使用：
- **场景**：`internal`（页面内跳转）
- **总延迟**：480ms
- **动态调整**：启用

这样可以获得更快的响应速度，同时保持稳定性。

## 📊 监控数据示例

```json
{
  "user_actions": [
    {
      "type": "click",
      "element": "BUTTON",
      "description": "点击提交按钮"
    },
    {
      "type": "input",
      "element": "INPUT",
      "description": "输入生日信息"
    }
  ],
  "network_requests": [
    {
      "method": "POST",
      "url": "https://api.weverse.io/form/submit",
      "status": 200
    }
  ]
}
``` 