#!/usr/bin/env python3
"""
部署 V2 团队监控 Cron Job

功能：
1. 30 分钟自动检查团队状态
2. 自动汇报异常
3. 管理任务队列
"""

import json
import sys
from pathlib import Path
from datetime import datetime

# 配置
WORKSPACE = Path("/root/.openclaw/workspace/ai-pdf-agent")
TEAM_STATE_PATH = WORKSPACE / "team_state_v2.json"
REPORT_PATH = WORKSPACE / "team_reports_v2.json"


def load_team_state():
    """加载团队状态"""
    try:
        if TEAM_STATE_PATH.exists():
            with open(TEAM_STATE_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"queue": {"pending": [], "in_progress": {}, "completed": [], "failed": []}}
    except Exception as e:
        print(f"❌ 加载状态失败: {e}")
        return None


def check_team_status():
    """检查团队状态"""
    state = load_team_state()
    if not state:
        return {
            "status": "error",
            "message": "无法加载团队状态"
        }

    queue = state.get("queue", {})
    pending = len(queue.get("pending", []))
    in_progress = len(queue.get("in_progress", {}))
    completed = len(queue.get("completed", []))
    failed = len(queue.get("failed", []))

    total = pending + in_progress + completed + failed

    # 检查是否有需要关注的问题
    issues = []
    if in_progress > 0:
        issues.append(f"有 {in_progress} 个任务正在进行中")
    if failed > 0:
        issues.append(f"有 {failed} 个任务失败")

    return {
        "timestamp": datetime.now().isoformat(),
        "status": "ok" if not issues else "warning",
        "queue": {
            "total": total,
            "pending": pending,
            "in_progress": in_progress,
            "completed": completed,
            "failed": failed
        },
        "issues": issues,
        "needs_attention": len(issues) > 0
    }


def save_report(report):
    """保存报告"""
    try:
        reports = []
        if REPORT_PATH.exists():
            with open(REPORT_PATH, 'r', encoding='utf-8') as f:
                reports = json.load(f)
        
        # 添加新报告
        reports.append(report)
        
        # 只保留最近 100 条报告
        if len(reports) > 100:
            reports = reports[-100:]
        
        with open(REPORT_PATH, 'w', encoding='utf-8') as f:
            json.dump(reports, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"❌ 保存报告失败: {e}")


def main():
    """主函数"""
    report = check_team_status()
    save_report(report)

    # 如果有问题，输出汇报
    if report["needs_attention"]:
        print("🚨 团队状态需要关注！")
        print(f"时间: {report['timestamp']}")
        print(f"状态: {report['status']}")
        print(f"问题: {', '.join(report['issues'])}")
        print(f"任务队列: 总计 {report['queue']['total']}, 待处理 {report['queue']['pending']}, 进行中 {report['queue']['in_progress']}, 已完成 {report['queue']['completed']}, 失败 {report['queue']['failed']}")
    else:
        # 正常进行中，不输出任何内容（静默）
        pass


if __name__ == "__main__":
    main()
