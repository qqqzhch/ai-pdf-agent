"""
动态任务调度器

核心功能：
- 智能并行识别
- 动态任务更新
- 依赖关系检测
- 执行计划生成
"""

import json
import time
from typing import Dict, List, Optional
from pathlib import Path
from .agent_pool import AgentPool


class DynamicTaskScheduler:
    """动态任务调度器"""
    
    def __init__(
        self,
        config_path: str = "team/config.json",
        state_path: str = "team/team_state.json"
    ):
        self.config_path = Path(config_path)
        self.state_path = Path(state_path)
        
        self.config = self._load_config()
        self.state = self._load_state()
        
        self.agent_pool = AgentPool(config_path)
        self.tasks: List[dict] = []
    
    def _load_config(self) -> dict:
        """加载配置"""
        with open(self.config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _load_state(self) -> dict:
        """加载状态"""
        if not self.state_path.exists():
            return self._create_initial_state()
        
        with open(self.state_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _create_initial_state(self) -> dict:
        """创建初始状态"""
        return {
            "version": "2.0",
            "status": "idle",
            "tasks": {
                "total": 0,
                "pending": 0,
                "in_progress": 0,
                "completed": 0,
                "failed": 0
            },
            "task_list": [],
            "active_agents": [],
            "execution_plan": {
                "groups": [],
                "current_group_index": 0
            },
            "metrics": {
                "start_time": None,
                "end_time": None,
                "total_duration_ms": 0
            },
            "last_update": None
        }
    
    def save_state(self):
        """保存状态"""
        self.state["last_update"] = time.time()
        
        with open(self.state_path, 'w', encoding='utf-8') as f:
            json.dump(self.state, f, indent=2, ensure_ascii=False)
    
    def update_tasks(self, new_tasks: List[dict]):
        """
        动态更新任务列表
        
        Args:
            new_tasks: 新的任务列表
        """
        print("🔄 检测任务变化...")
        
        # 检测变化
        changes = self._detect_changes(new_tasks)
        
        # 处理变化
        if changes["added"]:
            print(f"✅ 新增 {len(changes['added'])} 个任务")
            for task in changes["added"]:
                self._add_task(task)
        
        if changes["removed"]:
            print(f"🗑️ 删除 {len(changes['removed'])} 个任务")
            for task_id in changes["removed"]:
                self._remove_task(task_id)
        
        if changes["modified"]:
            print(f"✏️ 修改 {len(changes['modified'])} 个任务")
            for task in changes["modified"]:
                self._update_task(task)
        
        # 更新状态
        self._update_task_state()
        self.save_state()
        
        # 如果有变化，重新规划
        if any(changes.values()):
            print("🔄 重新规划执行...")
            self.replan()
    
    def _detect_changes(self, new_tasks: List[dict]) -> Dict[str, list]:
        """检测任务变化"""
        old_task_ids = {t["id"] for t in self.tasks}
        new_task_ids = {t["id"] for t in new_tasks}
        
        added = [t for t in new_tasks if t["id"] not in old_task_ids]
        removed = list(old_task_ids - new_task_ids)
        
        modified = [
            t for t in new_tasks
            if t["id"] in old_task_ids and t != self._get_task(t["id"])
        ]
        
        return {
            "added": added,
            "removed": removed,
            "modified": modified
        }
    
    def _add_task(self, task: dict):
        """添加任务"""
        self.tasks.append(task)
    
    def _remove_task(self, task_id: str):
        """删除任务"""
        # 检查是否正在运行
        session_key = self._find_session_by_task(task_id)
        if session_key:
            print(f"⚠️ 任务 {task_id} 正在运行，等待完成")
            return
        
        self.tasks = [t for t in self.tasks if t["id"] != task_id]
    
    def _update_task(self, new_task: dict):
        """更新任务"""
        # 检查是否正在运行
        session_key = self._find_session_by_task(new_task["id"])
        if session_key:
            print(f"⚠️ 任务 {new_task['id']} 正在运行，暂不更新")
            return
        
        for i, t in enumerate(self.tasks):
            if t["id"] == new_task["id"]:
                self.tasks[i] = new_task
                break
    
    def _get_task(self, task_id: str) -> Optional[dict]:
        """获取任务"""
        for task in self.tasks:
            if task["id"] == task_id:
                return task
        return None
    
    def _find_session_by_task(self, task_id: str) -> Optional[str]:
        """根据任务 ID 查找会话"""
        for session_key, session in self.agent_pool.active_sessions.items():
            if session.get("task_id") == task_id:
                return session_key
        return None
    
    def _update_task_state(self):
        """更新任务统计"""
        total = len(self.tasks)
        pending = len([t for t in self.tasks if self._get_task_status(t["id"]) == "pending"])
        in_progress = len([t for t in self.tasks if self._get_task_status(t["id"]) == "in_progress"])
        completed = len([t for t in self.tasks if self._get_task_status(t["id"]) == "completed"])
        failed = len([t for t in self.tasks if self._get_task_status(t["id"]) == "failed"])
        
        self.state["tasks"] = {
            "total": total,
            "pending": pending,
            "in_progress": in_progress,
            "completed": completed,
            "failed": failed
        }
        
        self.state["task_list"] = self.tasks
    
    def _get_task_status(self, task_id: str) -> str:
        """获取任务状态"""
        session_key = self._find_session_by_task(task_id)
        if session_key:
            return "in_progress"
        
        # 从历史记录查找
        for role, history in self.agent_pool.session_history.items():
            for session in history:
                if session.get("task_id") == task_id:
                    return "completed" if session["status"] == "completed" else "failed"
        
        return "pending"
    
    def plan_execution(self) -> List[List[dict]]:
        """
        规划执行计划
        
        Returns:
            任务组列表（每组可并行执行）
        """
        print("📋 规划执行计划...")
        
        # 1. 按优先级排序
        sorted_tasks = sorted(self.tasks, key=lambda t: t.get("priority", 999))
        
        # 2. 识别并行组
        groups = self._identify_parallel_groups(sorted_tasks)
        
        # 3. 保存执行计划
        self.state["execution_plan"] = {
            "groups": groups,
            "current_group_index": 0
        }
        
        print(f"📋 生成 {len(groups)} 个任务组")
        for i, group in enumerate(groups):
            print(f"  组 {i}: {[t['id'] for t in group]}")
        
        return groups
    
    def _identify_parallel_groups(self, tasks: List[dict]) -> List[List[dict]]:
        """
        识别可并行执行的任务组
        
        策略：
        1. 无依赖关系的任务可以并行
        2. 每组最多 3 个任务（配置限制）
        """
        groups = []
        remaining_tasks = tasks.copy()
        
        while remaining_tasks:
            current_group = []
            used_task_ids = set()
            
            # 找出可并行任务
            for task in remaining_tasks:
                if len(current_group) >= self.config["scheduler"]["max_parallel_tasks"]:
                    break
                
                # 检查依赖
                dependencies = task.get("dependencies", [])
                if all(dep in used_task_ids for dep in dependencies):
                    current_group.append(task)
                    used_task_ids.add(task["id"])
            
            if not current_group:
                # 循环依赖，强制取一个
                current_group.append(remaining_tasks[0])
                used_task_ids.add(remaining_tasks[0]["id"])
            
            groups.append(current_group)
            remaining_tasks = [t for t in remaining_tasks if t["id"] not in used_task_ids]
        
        return groups
    
    def replan(self):
        """重新规划执行"""
        groups = self.plan_execution()
        self.save_state()
    
    def execute(self):
        """执行任务"""
        if self.state["status"] == "running":
            print("⚠️ 任务正在执行中")
            return
        
        self.state["status"] = "running"
        self.state["metrics"]["start_time"] = time.time()
        self.save_state()
        
        groups = self.plan_execution()
        
        for group_idx, group in enumerate(groups):
            print(f"\n🚀 执行任务组 {group_idx + 1}/{len(groups)}")
            
            # 并行执行
            if len(group) > 1:
                self._execute_parallel(group)
            else:
                self._execute_task(group[0])
        
        self.state["status"] = "completed"
        self.state["metrics"]["end_time"] = time.time()
        self.state["metrics"]["total_duration_ms"] = (
            self.state["metrics"]["end_time"] - self.state["metrics"]["start_time"]
        ) * 1000
        self.save_state()
        
        print("\n✅ 所有任务执行完成！")
    
    def _execute_task(self, task: dict):
        """执行单个任务"""
        print(f"🔨 执行任务: {task['id']} - {task['title']}")
        
        # 创建开发工程师会话
        session_key = self.agent_pool.spawn_agent(
            role="developer",
            task=task,
            timeout=task.get("timeout", 3600)
        )
        
        if session_key:
            # 模拟执行（实际会等待 sessions_spawn 完成）
            time.sleep(1)
            
            # 标记完成
            self.agent_pool.complete_session(session_key, success=True)
            
            # 创建质量工程师会话进行审查
            qa_session = self.agent_pool.spawn_agent(
                role="quality_engineer",
                task=task,
                timeout=600
            )
            
            if qa_session:
                time.sleep(0)
                self.agent_pool.complete_session(qa_session, success=True)
    
    def _execute_parallel(self, tasks: List[dict]):
        """并行执行多个任务"""
        print(f"🚀 并行执行 {len(tasks)} 个任务")
        
        # 创建所有会话
        session_keys = []
        for task in tasks:
            session_key = self.agent_pool.spawn_agent(
                role="developer",
                task=task,
                timeout=task.get("timeout", 3600)
            )
            if session_key:
                session_keys.append((session_key, task))
        
        # 等待所有完成（模拟）
        time.sleep(2)
        
        # 标记完成
        for session_key, task in session_keys:
            self.agent_pool.complete_session(session_key, success=True)
        
        # 质量审查（串行）
        for session_key, task in session_keys:
            qa_session = self.agent_pool.spawn_agent(
                role="quality_engineer",
                task=task,
                timeout=600
            )
            if qa_session:
                time.sleep(0)
                self.agent_pool.complete_session(qa_session, success=True)
