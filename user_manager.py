"""
用户认证管理模块
支持员工和用户两种身份
"""

import os
import json
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Dict, Optional, List

class UserManager:
    def __init__(self, data_file='users.json'):
        self.data_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), data_file)
        self.users = self._load_users()
        self.sessions = {}  # session_id -> user_data
    
    def _load_users(self):
        """加载用户数据"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        
        # 创建默认用户数据
        default_users = {
            'admin': {
                'username': 'admin',
                'password': self._hash_password('admin123'),
                'role': 'employee',
                'real_name': '系统管理员',
                'phone': '13800138000',
                'email': 'admin@faultsystem.com',
                'created_at': datetime.now().isoformat(),
                'last_login': None
            },
            'user1': {
                'username': 'user1',
                'password': self._hash_password('user123'),
                'role': 'user',
                'real_name': '张三',
                'phone': '13900139000',
                'email': 'user1@example.com',
                'created_at': datetime.now().isoformat(),
                'last_login': None
            }
        }
        
        self._save_users(default_users)
        return default_users
    
    def _save_users(self, users=None):
        """保存用户数据"""
        if users is None:
            users = self.users
        
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(users, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存用户数据失败: {e}")
    
    def _hash_password(self, password: str) -> str:
        """密码哈希处理"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def register(self, username: str, password: str, role: str, 
                 real_name: str, phone: str, email: str) -> Dict:
        """用户注册"""
        if username in self.users:
            return {'success': False, 'message': '用户名已存在'}
        
        if role not in ['employee', 'user']:
            return {'success': False, 'message': '角色类型错误'}
        
        user_data = {
            'username': username,
            'password': self._hash_password(password),
            'role': role,
            'real_name': real_name,
            'phone': phone,
            'email': email,
            'created_at': datetime.now().isoformat(),
            'last_login': None
        }
        
        self.users[username] = user_data
        self._save_users()
        
        return {'success': True, 'message': '注册成功'}
    
    def login(self, username: str, password: str) -> Dict:
        """用户登录"""
        if username not in self.users:
            return {'success': False, 'message': '用户名或密码错误'}
        
        user = self.users[username]
        
        # 检查用户数据是否完整
        if 'password' not in user:
            print(f"警告：用户 {username} 数据不完整，缺少密码字段")
            return {'success': False, 'message': '用户数据错误，请联系管理员'}
        
        if user['password'] != self._hash_password(password):
            return {'success': False, 'message': '用户名或密码错误'}
        
        # 更新最后登录时间
        user['last_login'] = datetime.now().isoformat()
        self._save_users()
        
        # 创建会话
        session_id = secrets.token_urlsafe(32)
        self.sessions[session_id] = {
            'username': username,
            'role': user['role'],
            'real_name': user['real_name'],
            'login_time': datetime.now().isoformat(),
            'expires_at': (datetime.now() + timedelta(hours=24)).isoformat()
        }
        
        return {
            'success': True, 
            'message': '登录成功',
            'session_id': session_id,
            'user_data': {
                'username': username,
                'role': user['role'],
                'real_name': user['real_name']
            }
        }
    
    def verify_session(self, session_id: str) -> Optional[Dict]:
        """验证会话"""
        if session_id not in self.sessions:
            return None
        
        session = self.sessions[session_id]
        expires_at = datetime.fromisoformat(session['expires_at'])
        
        if datetime.now() > expires_at:
            # 会话过期
            del self.sessions[session_id]
            return None
        
        return session
    
    def logout(self, session_id: str) -> bool:
        """用户登出"""
        if session_id in self.sessions:
            del self.sessions[session_id]
            return True
        return False
    
    def get_user_info(self, username: str) -> Optional[Dict]:
        """获取用户信息"""
        return self.users.get(username)
    
    def update_user_info(self, username: str, **kwargs) -> Dict:
        """更新用户信息"""
        if username not in self.users:
            return {'success': False, 'message': '用户不存在'}
        
        user = self.users[username]
        
        # 允许更新的字段
        allowed_fields = ['real_name', 'phone', 'email']
        for field, value in kwargs.items():
            if field in allowed_fields:
                user[field] = value
        
        self._save_users()
        return {'success': True, 'message': '更新成功'}
    
    def change_password(self, username: str, old_password: str, new_password: str) -> Dict:
        """修改密码"""
        if username not in self.users:
            return {'success': False, 'message': '用户不存在'}
        
        user = self.users[username]
        
        if user['password'] != self._hash_password(old_password):
            return {'success': False, 'message': '原密码错误'}
        
        user['password'] = self._hash_password(new_password)
        self._save_users()
        
        return {'success': True, 'message': '密码修改成功'}
    
    def get_all_users(self, role_filter: str = None) -> List[Dict]:
        """获取所有用户（员工权限）"""
        users_list = []
        for username, user_data in self.users.items():
            if role_filter and user_data['role'] != role_filter:
                continue
            
            # 隐藏密码信息
            user_info = user_data.copy()
            user_info.pop('password', None)
            users_list.append(user_info)
        
        return users_list
    
    def get_user_stats(self) -> Dict:
        """获取用户统计信息（员工权限）"""
        from datetime import datetime, timedelta
        
        total_users = len(self.users)
        
        # 统计不同角色用户数量
        employee_count = sum(1 for user in self.users.values() if user['role'] == 'employee')
        user_count = total_users - employee_count
        
        # 统计今日活跃用户（模拟数据）
        today = datetime.now().date()
        active_today = sum(1 for user in self.users.values() 
                          if user.get('last_login') and 
                          datetime.fromisoformat(user['last_login']).date() == today)
        
        # 用户注册趋势（模拟数据）
        user_trend = [
            {'month': '1月', 'count': 5},
            {'month': '2月', 'count': 8},
            {'month': '3月', 'count': 12},
            {'month': '4月', 'count': 15},
            {'month': '5月', 'count': 18},
            {'month': '6月', 'count': 22},
            {'month': '7月', 'count': total_users}
        ]
        
        return {
            'total_users': total_users,
            'employee_count': employee_count,
            'user_count': user_count,
            'active_today': active_today,
            'user_trend': user_trend
        }

# 全局用户管理器实例
user_manager = UserManager()