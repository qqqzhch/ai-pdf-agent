#!/usr/bin/env python3
"""
V2 团队监控脚本

功能：
1. 30 分钟自动检查团队状态
2. 自动汇报异常
3. 汇总任务进展
"""

import json
import time
from datetime import datetime
from pathlib import Path

# 项目路径
PROJECT_PATH = Path("/root/.openclaw/workspace/ai-pdf-agent")
TEAM_STATE_PATH = PROJECT_PATH / "TEAM_V2.json"


def check_team_status():
    """检查团队状态"""
    try:
        # 读取团队状态
        if not TEAM_STATE_PATH.exists():
            return {
                "status": "ok",
                "message": "团队状态文件不存在（首次运行）"
            }

        with open(TEAM_STATE_PATH, 'r', encoding='utf-8') as f:
            team_state = json.load(f)

        # 读取任务队列状态
        queue_state = team_state.get("queue", {})
        pending = len(queue_state.get("pending", []))
        in_progress = len(queue_state.get("in_progress", {}))
        completed = len(queue_state.get("completed", []))
        failed = len(queue_state.get("failed", []))

        # 读取团队成员状态
        members = team_state.get("members", {})
        idle_count = sum(1 for m in members.values() if m.get("status") == "idle")
        busy_count = sum(1 for m in members.values() if m.get("status") == "busy")

        # 检查是否有需要关注的问题
        issues = []
        if in_progress > 0:
            issues.append(f"有 {in_progress} 个任务正在进行中")
        if failed > 0:
            issues.append(f"有 {failed} 个任务失败")

        return {
            "timestamp": datetime.now().isoformat(),
            "status": "ok",
            "queue": {
                "total": pending + in_progress + completed + failed,
                "pending": pending,
                "in_progress": in_progress,
                "completed": completed,
                "failed": failed
            },
            "members": {
                "total": len(members),
                "idle": idle_count,
                "busy": busy_count
            },
            "issues": issues,
            "needs_attention": len(issues) > 0
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }


def main():
    """主函数"""
    # 检查团队状态
    report = check_team_status()

    # 如果有问题，输出汇报
    if report["status"] == "ok" and report["needs_attention"]:
        print("🚨️ 团队状态需要关注！")
        print(f"时间: {report['timestamp']}")
        print(f"状态: {report['status']}")
        print(f"问题: {', '.join(report['issues'])}")
        print("")
        print("📋 任务队列:")
        queue = report["queue"]
        print(f"   总计: {queue['total']}")
        print(f"   ⏳ 待处理: {queue['pending']}")
        print(f"   🟡 进行中: {queue['in_progress']}")
        print(f"   ✅ 已完成: {queue['completed']}")
        print(f"   ❌ 已失败: {queue['failed']}")
        print("")
        print("👥 团队成员:")
        members = report["members"]
        print(f"   总数: {members['total']}")
        print(f"   🟢 空闲: {members['idle']}")
        print(f"   🟡 忙碌: {members['busy']}")
    elif report["status"] == "error":
        print(f"❌ 状态检查失败: {report.get('message', 'Unknown error')}")
    else:
        # 正常进行中，不输出任何内容（静默）
        print("HEARTBEAT_OK")


if __name__ == "__main__":
    main()
