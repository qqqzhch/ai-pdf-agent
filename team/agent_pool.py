"""
Agent 管理池

管理 AI Agent 子会话的生命周期
"""

import json
import time
from typing import Dict, Optional
from pathlib import Path


class AgentPool:
    """Agent 会话管理池"""
    
    def __init__(self, config_path: str = "team/config.json"):
        self.config_path = Path(config_path)
        self.config = self._load_config()
        self.active_sessions: Dict[str, dict] = {}
        self.session_history: Dict[str, list] = {}
        
    def _load_config(self) -> dict:
        """加载团队配置"""
        with open(self.config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def spawn_agent(
        self,
        role: str,
        task: dict,
        timeout: int = 3600
    ) -> Optional[str]:
        """
        创建 Agent 子会话
        
        Args:
            role: 角色（product_manager, developer, quality_engineer）
            task: 任务描述
            timeout: 超时时间（秒）
        
        Returns:
            session_key: 会话键值（失败返回 None）
        """
        if role not in self.config["roles"]:
            print(f"❌ 未知角色: {role}")
            return None
        
        role_config = self.config["roles"][role]
        
        # 检查并发限制
        active_count = sum(
            1 for s in self.active_sessions.values()
            if s["role"] == role
        )
        
        if active_count >= role_config["max_concurrent"]:
            print(f"⚠️ {role} 并发数已达上限: {active_count}")
            return None
        
        # 创建子会话
        try:
            # 这里需要调用 sessions_spawn
            # 为了测试，先返回模拟的 session_key
            session_key = f"{role}_{task['id']}_{int(time.time())}"
            
            self.active_sessions[session_key] = {
                "role": role,
                "task_id": task["id"],
                "task_title": task["title"],
                "start_time": time.time(),
                "status": "running"
            }
            
            print(f"✅ 创建 Agent 会话: {session_key} ({role})")
            return session_key
            
        except Exception as e:
            print(f"❌ 创建 Agent 会话失败: {e}")
            return None
    
    def get_session_status(self, session_key: str) -> Optional[dict]:
        """获取会话状态"""
        return self.active_sessions.get(session_key)
    
    def complete_session(self, session_key: str, success: bool = True):
        """
        标记会话完成
        
        Args:
            session_key: 会话键值
            success: 是否成功
        """
        if session_key not in self.active_sessions:
            print(f"⚠️ 会话不存在: {session_key}")
            return
        
        session = self.active_sessions[session_key]
        session["status"] = "completed" if success else "failed"
        session["end_time"] = time.time()
        
        # 移动到历史记录
        if session["role"] not in self.session_history:
            self.session_history[session["role"]] = []
        
        self.session_history[session["role"]].append(session)
        del self.active_sessions[session_key]
        
        print(f"✅ 会话完成: {session_key} ({session['status']})")
    
    def get_active_sessions(self, role: Optional[str] = None) -> list:
        """
        获取活跃会话列表
        
        Args:
            role: 筛选角色（None 表示所有）
        
        Returns:
            活跃会话列表
        """
        sessions = list(self.active_sessions.values())
        
        if role:
            sessions = [s for s in sessions if s["role"] == role]
        
        return sessions
    
    def get_active_count(self, role: Optional[str] = None) -> int:
        """获取活跃会话数量"""
        return len(self.get_active_sessions(role))
