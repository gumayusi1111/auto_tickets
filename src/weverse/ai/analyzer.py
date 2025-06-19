"""AI分析模块"""

import requests
import json
import sys
import os

# 添加项目根目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
from config import ai_config


def extract_time_with_ai(content):
    """使用AI直接提取时间信息"""
    try:
        # 构建时间提取提示
        prompt = f"""
你是一个专业的时间信息提取助手。请仔细分析以下Weverse文章内容，提取所有相关的时间信息。

文章内容：
{content}

请按照以下JSON格式返回提取的时间信息：

```json
{{
  "申请开始时间": "YYYY-MM-DD HH:MM",
  "申请结束时间": "YYYY-MM-DD HH:MM", 
  "活动时间": "YYYY-MM-DD HH:MM",
  "集合时间": "YYYY-MM-DD HH:MM",
  "时区": "KST",
  "关键时间点": [
    {{
      "描述": "具体事件描述",
      "时间": "YYYY-MM-DD HH:MM",
      "重要性": "高"
    }}
  ]
}}
```

提取规则：
1. 年份：如果文章中没有明确年份，根据上下文推断（通常是2025年）
2. 时间格式：统一使用24小时制，格式为YYYY-MM-DD HH:MM
3. 时区：韩国活动默认为KST时区
4. 空值处理：如果某个时间信息不存在，设为null
5. 关键词识别：
   - 申请/신청 = 申请时间
   - 활동/活动/공연 = 活动时间  
   - 집합/集合/모임 = 集合时间
   - 시작/开始 = 开始时间
   - 종료/结束/마감 = 结束时间

请只返回JSON格式的结果，不要添加任何其他说明文字。
"""
        
        # 优先使用chat模式，失败后切换到推理模式
        model_name = "deepseek-chat"  # 默认使用chat模式
        
        data = {
            "model": model_name,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.0,  # 设为0获得最确定的结果
            "max_tokens": 1000
        }
        
        # 增加超时时间和重试机制
        max_retries = 3
        timeout_seconds = 60
        
        for attempt in range(max_retries):
            try:
                print(f"🤖 正在调用AI进行时间提取... (尝试 {attempt + 1}/{max_retries}, 模型: {model_name}, 超时: {timeout_seconds}s)")
                response = requests.post(
                    f"{ai_config.DEEPSEEK_CONFIG['base_url']}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {ai_config.DEEPSEEK_CONFIG['api_key']}",
                        "Content-Type": "application/json"
                    },
                    json=data,
                    timeout=timeout_seconds
                )
                break  # 成功则跳出循环
            except requests.exceptions.Timeout:
                if attempt < max_retries - 1:
                    print(f"⏰ 请求超时，正在重试... ({attempt + 1}/{max_retries})")
                    # 如果是chat模式失败，在第二次重试时切换到推理模型
                    if model_name == "deepseek-chat" and attempt == 1:
                        print("🔄 chat模式失败，切换到推理模型")
                        model_name = "deepseek-reasoner"
                        data["model"] = model_name
                        data["response_format"] = {"type": "json_object"}  # 添加JSON格式要求
                        timeout_seconds = 120  # 增加超时时间
                    continue
                else:
                    raise  # 最后一次重试失败则抛出异常
            except Exception as e:
                if attempt < max_retries - 1:
                    print(f"❌ 请求失败: {e}，正在重试... ({attempt + 1}/{max_retries})")
                    # 如果是chat模式失败，尝试切换到推理模型
                    if model_name == "deepseek-chat" and attempt == 1:
                        print("🔄 chat模式失败，切换到推理模型")
                        model_name = "deepseek-reasoner"
                        data["model"] = model_name
                        data["response_format"] = {"type": "json_object"}
                        timeout_seconds = 120
                    continue
                else:
                    raise
        
        if response.status_code == 200:
            result = response.json()
            print(f"🔍 API响应结构: {json.dumps(result, ensure_ascii=False, indent=2)[:500]}...")
            
            if 'choices' in result and len(result['choices']) > 0:
                ai_response = result['choices'][0]['message']['content']
                
                # 检查空响应
                if not ai_response or ai_response.strip() == "":
                    print("❌ AI返回空响应")
                    return None
                
                ai_response = ai_response.strip()
                print(f"🔍 原始AI响应: {ai_response[:200]}...")
                
                try:
                    # 清理AI响应，移除可能的markdown格式
                    cleaned_response = ai_response.strip()
                    
                    # 如果包含```json标记，提取JSON部分
                    if '```json' in cleaned_response:
                        start = cleaned_response.find('```json') + 7
                        end = cleaned_response.find('```', start)
                        if end != -1:
                            cleaned_response = cleaned_response[start:end].strip()
                            print(f"🔍 提取JSON部分: {cleaned_response[:200]}...")
                    elif '```' in cleaned_response:
                        # 处理没有json标记的代码块
                        start = cleaned_response.find('```') + 3
                        end = cleaned_response.find('```', start)
                        if end != -1:
                            cleaned_response = cleaned_response[start:end].strip()
                            print(f"🔍 提取代码块: {cleaned_response[:200]}...")
                    
                    # 移除可能的前后空白和换行
                    cleaned_response = cleaned_response.strip()
                    
                    # 再次检查是否为空
                    if not cleaned_response:
                        print("❌ 清理后响应为空")
                        return None
                    
                    print(f"🔍 最终清理后内容: {cleaned_response[:200]}...")
                    
                    # 尝试解析JSON
                    time_data = json.loads(cleaned_response)
                    print(f"✅ AI时间提取成功: {json.dumps(time_data, ensure_ascii=False, indent=2)}")
                    return time_data
                    
                except json.JSONDecodeError as e:
                    print(f"❌ AI返回的不是有效JSON: {ai_response[:500]}...")
                    print(f"JSON解析错误: {e}")
                    print(f"🔍 尝试解析的内容: '{cleaned_response[:200]}...'")
                    
                    # 尝试修复常见的JSON格式问题
                    try:
                        import re
                        fixed_response = cleaned_response
                        print(f"🔧 开始JSON修复，原内容: '{fixed_response[:100]}...'")
                        
                        # 1. 移除可能的注释
                        fixed_response = re.sub(r'//.*?\n', '\n', fixed_response)
                        fixed_response = re.sub(r'/\*.*?\*/', '', fixed_response, flags=re.DOTALL)
                        
                        # 2. 移除多余的空白字符
                        fixed_response = re.sub(r'\s+', ' ', fixed_response)
                        fixed_response = fixed_response.strip()
                        
                        # 3. 尝试提取可能的JSON对象
                        json_match = re.search(r'\{.*\}', fixed_response, re.DOTALL)
                        if json_match:
                            fixed_response = json_match.group(0)
                            print(f"🔧 提取JSON对象: '{fixed_response[:100]}...'")
                        
                        # 4. 修复常见的引号问题
                        fixed_response = re.sub(r'([{,]\s*)(\w+)(:)', r'\1"\2"\3', fixed_response)
                        
                        # 5. 确保字符串值被正确引用
                        fixed_response = re.sub(r':\s*([^"\[\{][^,}\]]*[^,}\]\s])', r': "\1"', fixed_response)
                        
                        print(f"🔧 修复后内容: '{fixed_response[:200]}...'")
                        
                        # 尝试再次解析
                        time_data = json.loads(fixed_response)
                        print(f"✅ JSON修复成功: {json.dumps(time_data, ensure_ascii=False, indent=2)}")
                        return time_data
                        
                    except Exception as fix_error:
                        print(f"❌ JSON修复失败: {fix_error}")
                        print(f"🔧 修复尝试的内容: '{fixed_response[:200]}...' if 'fixed_response' in locals() else '无'")
                        
                        # 最后尝试：返回一个默认的空结构
                        print("🔧 返回默认空结构")
                        return {
                            "application_start_time": None,
                            "application_end_time": None,
                            "activity_time": None,
                            "gathering_time": None,
                            "timezone": "Asia/Seoul",
                            "key_times": []
                        }
            else:
                print("❌ AI响应格式异常")
                return None
        else:
            print(f"❌ AI时间提取失败: HTTP {response.status_code}")
            return None
            
    except requests.exceptions.Timeout:
        print("❌ AI时间提取超时")
        return None
    except Exception as e:
        print(f"❌ AI时间提取出错: {e}")
        return None


def analyze_with_ai(content, time_info=None):
    """使用AI分析文章内容"""
    try:
        # 构建分析提示
        prompt = f"""
请分析以下Weverse文章内容，并提供抢票策略建议：

文章内容：
{content}

时间信息：
{time_info if time_info else '未检测到具体时间'}

请提供：
1. 活动类型和重要性分析
2. 抢票难度评估
3. 最佳抢票时机建议
4. 注意事项和策略

请用中文回答，简洁明了。
"""
        
        headers = {
            "Authorization": f"Bearer {ai_config.DEEPSEEK_CONFIG['api_key']}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "deepseek-chat",
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.7,
            "max_tokens": 1000
        }
        
        response = requests.post(f"{ai_config.DEEPSEEK_CONFIG['base_url']}/chat/completions", headers=headers, json=data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            if 'choices' in result and len(result['choices']) > 0:
                return result['choices'][0]['message']['content']
            else:
                print("❌ AI响应格式异常")
                return None
        else:
            print(f"❌ AI分析失败: HTTP {response.status_code}")
            print(f"错误信息: {response.text}")
            return None
            
    except requests.exceptions.Timeout:
        print("❌ AI分析超时")
        return None
    except requests.exceptions.RequestException as e:
        print(f"❌ AI分析网络错误: {e}")
        return None
    except Exception as e:
        print(f"❌ AI分析异常: {e}")
        return None