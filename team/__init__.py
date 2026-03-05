"""
AI Agent 团队管理系统 - Version 2.0

精简团队架构（3 人）：
- 产品经理：需求分析、任务分解、优先级排序
- 开发工程师：代码实现、测试、调试（最多 3 个并行）
- 质量工程师：代码审查、测试验证、文档完善

核心特性：
- 智能并行识别
- 动态任务更新
- 30 分钟定时监控
- 异常自动重试
"""

from .agent_pool import AgentPool
from .heartbeat import HeartbeatMonitor
from .task_scheduler import DynamicTaskScheduler

__all__ = ["AgentPool", "DynamicTaskScheduler", "HeartbeatMonitor"]
