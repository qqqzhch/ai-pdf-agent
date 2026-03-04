"""
定时任务监控器

功能：
- 30 分钟检查一次团队状态
- 汇报进度
- 异常报警
- 完成总结
"""

import json
import time
from typing import Dict
from pathlib import Path


class HeartbeatMonitor:
    """团队状态监控器"""
    
    def __init__(
        self,
        state_path: str = "team/team_state.json",
        config_path: str = "team/config.json"
    ):
        self.state_path = Path(state_path)
        self.config_path = Path(config_path)
        
        self.config = self._load_config()
        self.state = self._load_state()
    
    def _load_config(self) -> dict:
        """加载配置"""
        with open(self.config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _load_state(self) -> dict:
        """加载状态"""
        if not self.state_path.exists():
            return {}
        
        with open(self.state_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def check_and_report(self) -> str:
        """
        检查团队状态并生成报告
        
        Returns:
            报告文本
        """
        self.state = self._load_state()
        
        if not self.state:
            return "📊 团队未初始化"
        
        report_lines = []
        
        # 1. 检查失败任务
        failed = self.state.get("tasks", {}).get("failed", 0)
        if failed > 0:
            report_lines.append(f"❌ 有 {failed} 个任务失败")
            report_lines.append(self._report_failed_tasks())
        
        # 2. 检查是否卡住
        if self._is_stuck():
            report_lines.append("⚠️ 团队似乎卡住了，2 小时无进展")
        
        # 3. 进度汇报
        in_progress = self.state.get("tasks", {}).get("in_progress", 0)
        if in_progress > 0:
            progress = self._calculate_progress()
            report_lines.append(f"📊 团队进度：{progress:.1f}%")
            report_lines.append(self._report_task_summary())
        
        # 4. 全部完成
        if self._is_completed():
            report_lines.append("✅ 所有任务已完成！")
            report_lines.append(self._report_completion_summary())
        
        return "\n".join(report_lines)
    
    def _calculate_progress(self) -> float:
        """计算进度百分比"""
        tasks = self.state.get("tasks", {})
        total = tasks.get("total", 0)
        completed = tasks.get("completed", 0)
        
        if total == 0:
            return 0.0
        
        return (completed / total) * 100
    
    def _is_stuck(self) -> bool:
        """检查是否卡住"""
        heartbeat = self.config.get("heartbeat", {})
        check_after_ms = heartbeat.get("check_stuck_after_ms", 7200000) 
        
        last_update = self.state.get("last_update")
        if not last_update:
            return False
        
        elapsed_ms = (time.time() - last_update) * 1000
        return elapsed_ms > check_after_ms
    
    def _is_completed(self) -> bool:
        """检查是否全部完成"""
        tasks = self.state.get("tasks", {})
        total = tasks.get("total", 0)
        completed = tasks.get("completed", 0)
        
        return total > 0 and completed == total
    
    def _report_task_summary(self) -> str:
        """生成任务摘要"""
        tasks = self.state.get("tasks", {})
        
        summary = (
            f"  待处理: {tasks.get('pending', 0)}\n"
            f"  进行中: {tasks.get('in_progress', 0)}\n"
            f"  已完成: {tasks.get('completed', 0)}\n"
            f"  失败: {tasks.get('failed', 0)}"
        )
        
        return summary
    
    def _report_failed_tasks(self) -> str:
        """生成失败任务报告"""
        task_list = self.state.get("task_list", [])
        failed_tasks = [t for t in task_list if t.get("status") == "failed"]
        
        if not failed_tasks:
            return ""
        
        lines = ["\n失败任务详情："]
        for task in failed_tasks:
            lines.append(f"  - {task.get('id')}: {task.get('title', 'Unknown')}")
            if task.get("error"):
                lines.append(f"    错误: {task.get('error')}")
        
        return "\n".join(lines)
    
    def _report_completion_summary(self) -> str:
        """生成完成总结"""
        metrics = self.state.get("metrics", {})
        duration_ms = metrics.get("total_duration_ms", 0)
        duration_min = duration_ms / 1000 / 60
        
        summary = (
            f"\n📊 执行统计：\n"
            f"  总耗时: {duration_min:.1f} 分钟\n"
            f"  任务总数: {self.state.get('tasks', {}).get('total', 0)}\n"
            f"  成功: {self.state.get('tasks', {}).get('completed', 0)}\n"
            f"  失败: {self.state.get('tasks', {}).get('failed', 0)}"
        )
        
        return summary
    
    def should_alert(self) -> bool:
        """检查是否需要报警"""
        # 1. 有失败任务
        failed = self.state.get("tasks", {}).get("failed", 0)
        if failed > 0:
            return True
        
        # 2. 卡住
        if self._is_stuck():
            return True
        
        # 3. 全部完成
        if self._is_completed():
            return True
        
        return False


def heartbeat_team_monitor() -> str:
    """
    定时任务入口函数
    
    由 cron 定时调用，检查团队状态并汇报
    
    Returns:
        报告文本（如果需要报警，返回报警文本）
    """
    monitor = HeartbeatMonitor()
    report = monitor.check_and_report()
    
    # 如果需要报警，标记为需要立即汇报
    if monitor.should_alert():
        return f"🚨 需要关注：\n{report}"
    
    # 正常汇报
    if report.strip():
        return report
    
    return "HEARTBEAT_OK"


if __name__ == "__main__":
    # 测试
    print(heartbeat_team_monitor())
