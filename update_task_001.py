#!/usr/bin/env python3
"""更新任务状态"""

import json
from datetime import datetime

TEAM_STATUS_PATH = "/root/.openclaw/workspace/ai-pdf-agent/TEAM_STATUS.json"
TEAM_LOG_PATH = "/root/.openclaw/workspace/ai-pdf-agent/TEAM_LOG.md"

# 加载状态
with open(TEAM_STATUS_PATH, 'r', encoding='utf-8') as f:
    status = json.load(f)

# 更新 TASK-001
for task in status['tasks']:
    if task['id'] == 'TASK-001':
        task['assignee'] = '王测试'
        task['status'] = 'assigned'
        task['assigned_at'] = datetime.now().isoformat()
        break

# 更新时间戳
status['last_updated'] = datetime.now().isoformat()

# 保存状态
with open(TEAM_STATUS_PATH, 'w', encoding='utf-8') as f:
    json.dump(status, f, indent=2, ensure_ascii=False)

# 记录日志
with open(TEAM_LOG_PATH, 'a', encoding='utf-8') as f:
    log = f"""
### {datetime.now().strftime('%H:%M:%S')} - 任务分配

**任务 ID：** TASK-001
**任务标题：** readme 验证安装和基本使用
**任务类型：** testing
**优先级：** high
**分配给：** 王测试
**分配时间：** {task['assigned_at']}

**任务描述：**
使用 ai-pdf 命令验证安装是否成功
测试基本功能是否正常工作

"""
    f.write(log)

print("✅ 任务 TASK-001 已分配给王测试")
print(f"   分配时间：{task['assigned_at']}")
