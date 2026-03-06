#!/usr/bin/env python3
"""
创建 V2 团队状态监控 Cron Job

功能：
1. 30 分钟检查团队状态
2. 自动汇报异常
3. 汇总任务进展
"""

import json
import time
from datetime import datetime
from pathlib import Path

# 配置
WORKSPACE = Path("/root/.openclaw/workspace/ai-pdf-agent")
TEAM_STATE_PATH = WORKSPACE / "team_state_v2.json"
TEAM_V2_PATH = WORKSPACE / "TEAM_V2.md"
TEAM_V2_SUMMARY_PATH = WORKSPACE / "TEAM_V2_SUMMARY.md"
TEAM_CONFIG_PATH = WORKSPACE / "TEAM_CONFIG_V2.json"


def check_team_status():
    """检查团队状态"""
    try:
        # 读取团队状态
        if TEAM_STATE_PATH.exists():
            with open(TEAM_STATE_PATH, 'r', encoding='utf-8') as f:
                state = json.load(f)
        else:
            return {
                "status": "error",
                "message": "团队状态文件不存在"
            }

        # 检查队列状态
        queue = state.get("queue", {})
        pending = len(queue.get("pending", []))
        in_progress = len(queue.get("in_progress", {}))
        completed = len(queue.get("completed", []))
        failed = len(queue.get("failed", []))

        total = pending + in_progress + completed + failed

        # 检查成员状态
        members = state.get("members", {})
        idle_count = sum(1 for m in members.values() if m.get("status") == "idle")
        busy_count = sum(1 for m in members.values() if m.get("status") == "busy")

        # 检查是否有异常
        has_issues = failed > 0 or in_progress > 0

        # 生成状态报告
        report = {
            "timestamp": datetime.now().isoformat(),
            "queue": {
                "total": total,
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
            "status": "active" if has_issues else "normal",
            "has_issues": has_issues
        }

        # 保存状态
        state["last_check"] = datetime.now().isoformat()
        with open(TEAM_STATE_PATH, 'w', encoding='utf-8') as f:
            json.dump(state, f, indent=2, ensure_ascii=False)

        return report

    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }


def generate_summary_message(report):
    """生成汇总消息"""
    if report["status"] == "error":
        return f"❌ 团队状态检查失败: {report['message']}"

    # 汇总队列状态
    queue = report["queue"]
    members = report["members"]

    # 基本状态
    message = f"""
📊 团队状态报告
时间: {report['timestamp']}

📋 任务队列:
  总计: {queue['total']}
  ⏳ 待处理: {queue['pending']}
  🟡 进行中: {queue['in_progress']}
  ✅ 已完成: {queue['completed']}
  ❌ 已失败: {queue['failed']}

👥 团队成员:
  总数: {members['total']}
  🟢 空闲: {members['idle']}
  🟡 忙碌: {members['busy']}
"""

    # 如果有异常，添加异常详情
    if report["has_issues"]:
        message += f"\n⚠️ 状态异常: 有 {queue['in_progress']} 个任务正在进行中，{queue['failed']} 个任务失败"

    return message


def main():
    """主函数"""
    print("🔍 检查 V2 团队状态...")
    print("")

    # 检查团队状态
    report = check_team_status()

    # 生成消息
    message = generate_summary_message(report)

    # 输出消息
    print(message)
    print("")

    # 如果正常进行中，返回 HEARTBEAT_OK
    if report["status"] == "normal" and not report["has_issues"]:
        print("HEARTBEAT_OK")
    else:
        print("状态异常，需要关注！")


if __name__ == "__main__":
    main()
