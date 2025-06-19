#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
email_verifier.py
邮箱验证码获取模块
支持QQ邮箱、163邮箱、Gmail等主流邮箱服务
"""

import imaplib
import email
import re
import time
import ssl
from email.header import decode_header
from typing import Optional, Dict, List


class EmailVerifier:
    """邮箱验证码获取器"""
    
    # 邮箱服务器配置
    EMAIL_SERVERS = {
        'qq.com': {
            'imap_server': 'imap.qq.com',
            'imap_port': 993,
            'use_ssl': True
        },
        '163.com': {
            'imap_server': 'imap.163.com',
            'imap_port': 993,
            'use_ssl': True
        },
        '126.com': {
            'imap_server': 'imap.126.com',
            'imap_port': 993,
            'use_ssl': True
        },
        'gmail.com': {
            'imap_server': 'imap.gmail.com',
            'imap_port': 993,
            'use_ssl': True
        },
        'outlook.com': {
            'imap_server': 'outlook.office365.com',
            'imap_port': 993,
            'use_ssl': True
        },
        'hotmail.com': {
            'imap_server': 'outlook.office365.com',
            'imap_port': 993,
            'use_ssl': True
        }
    }
    
    def __init__(self, email_address: str, password: str):
        """初始化邮箱验证器
        
        Args:
            email_address: 邮箱地址
            password: 邮箱密码或授权码
        """
        self.email_address = email_address
        self.password = password
        self.domain = email_address.split('@')[1].lower()
        self.imap_conn = None
        
        if self.domain not in self.EMAIL_SERVERS:
            raise ValueError(f"不支持的邮箱域名: {self.domain}")
    
    def connect(self, use_auth_code: bool = True) -> bool:
        """连接到邮箱服务器
        
        Args:
            use_auth_code: 是否使用授权码（False表示使用真实密码）
        """
        try:
            server_config = self.EMAIL_SERVERS[self.domain]
            
            if server_config['use_ssl']:
                self.imap_conn = imaplib.IMAP4_SSL(
                    server_config['imap_server'], 
                    server_config['imap_port']
                )
            else:
                self.imap_conn = imaplib.IMAP4(
                    server_config['imap_server'], 
                    server_config['imap_port']
                )
            
            # 根据邮箱类型和密码类型选择不同的连接方式
            if not use_auth_code:
                print(f"使用真实密码连接 {self.email_address}...")
            else:
                print(f"使用授权码连接 {self.email_address}...")
            
            # 登录
            self.imap_conn.login(self.email_address, self.password)
            print(f"✅ 成功连接到 {self.email_address}")
            return True
            
        except Exception as e:
            error_msg = str(e).lower()
            if 'authentication failed' in error_msg or 'login failed' in error_msg:
                if use_auth_code:
                    print(f"❌ 授权码认证失败: {e}")
                    print("💡 提示: 请确保已开启IMAP服务并使用正确的授权码")
                else:
                    print(f"❌ 密码认证失败: {e}")
                    print("💡 提示: 请确认密码正确，某些邮箱可能需要开启'不够安全的应用'访问权限")
            else:
                print(f"❌ 连接邮箱失败: {e}")
            return False
    
    def disconnect(self):
        """断开邮箱连接"""
        if self.imap_conn:
            try:
                self.imap_conn.close()
                self.imap_conn.logout()
                print("📤 已断开邮箱连接")
            except:
                pass
    
    def get_latest_emails(self, sender_filter: str = None, subject_filter: str = None, 
                         count: int = 10, since_minutes: int = 10) -> List[Dict]:
        """获取最新邮件
        
        Args:
            sender_filter: 发件人过滤（可选）
            subject_filter: 主题过滤（可选）
            count: 获取邮件数量
            since_minutes: 获取多少分钟内的邮件
            
        Returns:
            邮件列表
        """
        try:
            # 选择收件箱
            self.imap_conn.select('INBOX')
            
            # 构建搜索条件
            search_criteria = ['UNSEEN']  # 只搜索未读邮件
            
            # 时间过滤
            import datetime
            since_time = datetime.datetime.now() - datetime.timedelta(minutes=since_minutes)
            date_str = since_time.strftime('%d-%b-%Y')
            search_criteria.append(f'SINCE "{date_str}"')
            
            if sender_filter:
                search_criteria.append(f'FROM "{sender_filter}"')
            
            if subject_filter:
                search_criteria.append(f'SUBJECT "{subject_filter}"')
            
            # 搜索邮件
            search_query = ' '.join(search_criteria)
            status, messages = self.imap_conn.search(None, search_query)
            
            if status != 'OK':
                print("❌ 搜索邮件失败")
                return []
            
            email_ids = messages[0].split()
            emails = []
            
            # 获取最新的邮件（倒序）
            for email_id in email_ids[-count:]:
                try:
                    status, msg_data = self.imap_conn.fetch(email_id, '(RFC822)')
                    if status == 'OK':
                        email_body = msg_data[0][1]
                        email_message = email.message_from_bytes(email_body)
                        
                        # 解析邮件信息
                        subject = self._decode_header(email_message['Subject'])
                        sender = self._decode_header(email_message['From'])
                        date = email_message['Date']
                        
                        # 获取邮件内容
                        content = self._get_email_content(email_message)
                        
                        emails.append({
                            'id': email_id.decode(),
                            'subject': subject,
                            'sender': sender,
                            'date': date,
                            'content': content
                        })
                        
                except Exception as e:
                    print(f"⚠️  解析邮件失败: {e}")
                    continue
            
            return emails
            
        except Exception as e:
            print(f"❌ 获取邮件失败: {e}")
            return []
    
    def extract_verification_code(self, email_content: str, patterns: List[str] = None) -> Optional[str]:
        """从邮件内容中提取验证码
        
        Args:
            email_content: 邮件内容
            patterns: 自定义正则表达式模式列表
            
        Returns:
            验证码字符串或None
        """
        if patterns is None:
            # 默认验证码匹配模式
            patterns = [
                r'验证码[：:]*\s*([A-Za-z0-9]{4,8})',
                r'verification code[：:]*\s*([A-Za-z0-9]{4,8})',
                r'验证码为[：:]*\s*([A-Za-z0-9]{4,8})',
                r'code[：:]*\s*([A-Za-z0-9]{4,8})',
                r'验证码\s*([A-Za-z0-9]{4,8})',
                r'([A-Za-z0-9]{6})\s*为您的验证码',
                r'([A-Za-z0-9]{4,8})\s*是您的验证码',
                r'\b([A-Za-z0-9]{4,8})\b.*验证码',
                r'\b([0-9]{4,8})\b'  # 纯数字验证码
            ]
        
        for pattern in patterns:
            matches = re.findall(pattern, email_content, re.IGNORECASE)
            if matches:
                return matches[0]
        
        return None
    
    def wait_for_verification_code(self, sender_filter: str = None, subject_filter: str = None,
                                 timeout: int = 300, check_interval: int = 10) -> Optional[str]:
        """等待并获取验证码
        
        Args:
            sender_filter: 发件人过滤
            subject_filter: 主题过滤
            timeout: 超时时间（秒）
            check_interval: 检查间隔（秒）
            
        Returns:
            验证码字符串或None
        """
        print(f"🔍 开始监听验证码邮件...")
        print(f"📧 发件人过滤: {sender_filter or '无'}")
        print(f"📝 主题过滤: {subject_filter or '无'}")
        print(f"⏱️  超时时间: {timeout}秒")
        
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                # 获取最新邮件
                emails = self.get_latest_emails(
                    sender_filter=sender_filter,
                    subject_filter=subject_filter,
                    count=5,
                    since_minutes=5
                )
                
                for email_info in emails:
                    print(f"📨 检查邮件: {email_info['subject']} - {email_info['sender']}")
                    
                    # 提取验证码
                    verification_code = self.extract_verification_code(email_info['content'])
                    
                    if verification_code:
                        print(f"🎉 找到验证码: {verification_code}")
                        return verification_code
                
                print(f"⏳ 未找到验证码，{check_interval}秒后重试...")
                time.sleep(check_interval)
                
            except Exception as e:
                print(f"⚠️  检查邮件时出错: {e}")
                time.sleep(check_interval)
        
        print(f"⏰ 超时：{timeout}秒内未收到验证码")
        return None
    
    def _decode_header(self, header_value: str) -> str:
        """解码邮件头部信息"""
        if not header_value:
            return ""
        
        try:
            decoded_parts = decode_header(header_value)
            decoded_string = ""
            
            for part, encoding in decoded_parts:
                if isinstance(part, bytes):
                    if encoding:
                        decoded_string += part.decode(encoding)
                    else:
                        decoded_string += part.decode('utf-8', errors='ignore')
                else:
                    decoded_string += part
            
            return decoded_string
        except:
            return str(header_value)
    
    def _get_email_content(self, email_message) -> str:
        """获取邮件内容"""
        content = ""
        
        if email_message.is_multipart():
            for part in email_message.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition"))
                
                if content_type == "text/plain" and "attachment" not in content_disposition:
                    try:
                        body = part.get_payload(decode=True)
                        if body:
                            content += body.decode('utf-8', errors='ignore')
                    except:
                        pass
                elif content_type == "text/html" and "attachment" not in content_disposition:
                    try:
                        body = part.get_payload(decode=True)
                        if body:
                            # 简单的HTML标签清理
                            html_content = body.decode('utf-8', errors='ignore')
                            # 移除HTML标签
                            import re
                            clean_content = re.sub(r'<[^>]+>', '', html_content)
                            content += clean_content
                    except:
                        pass
        else:
            try:
                body = email_message.get_payload(decode=True)
                if body:
                    content = body.decode('utf-8', errors='ignore')
            except:
                pass
        
        return content


def get_verification_code_interactive():
    """交互式获取验证码"""
    print("=== 邮箱验证码获取工具 ===")
    
    # 获取用户输入
    email_address = input("请输入邮箱地址: ").strip()
    password = input("请输入邮箱密码/授权码: ").strip()
    
    # 可选过滤条件
    sender_filter = input("发件人过滤（可选，直接回车跳过）: ").strip() or None
    subject_filter = input("主题过滤（可选，直接回车跳过）: ").strip() or None
    
    try:
        # 创建验证器
        verifier = EmailVerifier(email_address, password)
        
        # 连接邮箱
        if not verifier.connect():
            return None
        
        try:
            # 等待验证码
            verification_code = verifier.wait_for_verification_code(
                sender_filter=sender_filter,
                subject_filter=subject_filter,
                timeout=300,  # 5分钟超时
                check_interval=10  # 10秒检查一次
            )
            
            if verification_code:
                print(f"\n🎊 成功获取验证码: {verification_code}")
                return verification_code
            else:
                print("\n❌ 未能获取到验证码")
                return None
                
        finally:
            verifier.disconnect()
            
    except Exception as e:
        print(f"❌ 操作失败: {e}")
        return None


if __name__ == "__main__":
    # 示例用法
    code = get_verification_code_interactive()
    if code:
        print(f"获取到的验证码: {code}")