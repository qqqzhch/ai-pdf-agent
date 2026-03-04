#!/usr/bin/env python3
"""
AI PDF Agent 团队 - 任务队列和自动执行管理器

解决关键问题：
1. 没有定时任务，谁来触发下一个任务？
2. 任务完成后，如何自动启动下一个任务？
3. 如何维护任务队列和依赖关系？

解决方案：
- 使用轻量级 cron 任务（每 1 分钟）
- 只检查是否有待执行任务
- 有任务时快速触发
- 无任务时立即返回（< 0.5 秒）
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path

# ============================================================================
# 文件路径
# ============================================================================

TEAM_STATUS_PATH = "/root/.openclaw/workspace/ai-pdf-agent/TEAM_STATUS.json"
TEAM_LOG_PATH = "/root/.openclaw/workspace/ai-pdf-agent/TEAM_LOG.md"

# ============================================================================
# 任务队列管理
# ============================================================================

def load_team_status():
    """加载团队状态"""
    try:
        with open(TEAM_STATUS_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        default_status = {
            "last_updated": datetime.now().isoformat(),
            "current_project": None,
            "projects_completed": 0,
            "tasks": [],
            "agents": {
                "张架构": {"status": "idle"},
                "李开发": {"status": "idle"},
                "赵栈": {"status": "idle"},
                "王测试": {"status": "idle"},
                "陈文档": {"status": "idle"},
                "刘运维": {"status": "idle"}
            }
        }
        with open(TEAM_STATUS_PATH, 'w', encoding='utf-8') as f:
            json.dump(default_status, f, indent=2, ensure_ascii=False)
        return default_status
    except Exception as e:
        return None

def save_team_status(status):
    """保存团队状态"""
    try:
        status['last_updated'] = datetime.now().isoformat()
        with open(TEAM_STATUS_PATH, 'w', encoding='utf-8') as f:
            json.dump(status, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        return False

def log_action(action_type, details):
    """记录日志"""
    try:
        log_entry = f"""
### {datetime.now().strftime('%H:%M:%S')} - {action_type}

{details}

"""
        with open(TEAM_LOG_PATH, 'a', encoding='utf-8') as f:
            f.write(log_entry)
    except Exception:
        pass

# ============================================================================
# 任务队列操作
# ============================================================================

def add_tasks(task_list):
    """添加任务到队列"""
    status = load_team_status()
    if not status:
        return False
    
    current_time = datetime.now().isoformat()
    added_count = 0
    
    for task in task_list:
        task['created_at'] = current_time
        status['tasks'].append(task)
        added_count += 1
    
    if save_team_status(status):
        log_action("任务添加", f"添加了 {added_count} 个任务到队列")
        for task in task_list:
            log_action("", f"- {task['id']}: {task['title']}")
        
        return True
    else:
        return False

def get_pending_tasks():
    """获取待执行任务"""
    status = load_team_status()
    if not status:
        return []
    
    return [t for t in status['tasks'] if t.get('status') == 'pending']

def get_ready_tasks(status):
    """获取可以执行的任务（依赖已满足）"""
    pending_tasks = [t for t in status['tasks'] if t.get('status') == 'pending']
    ready_tasks = []
    
    for task in pending_tasks:
        depends_on = task.get('depends_on')
        
        if not depends_on:
            ready_tasks.append(task)
        else:
            if isinstance(depends_on, str):
                depends_on = [depends_on]
            
            all_completed = True
            for dep_id in depends_on:
                dep_task = [t for t in status['tasks'] if t.get('id') == dep_id]
                if dep_task and dep_task[0].get('status') != 'completed':
                    all_completed = False
                    break
            
            if all_completed:
                ready_tasks.append(task)
    
    return ready_tasks

def assign_tasks(tasks):
    """分配任务给合适的团队成员"""
    if not tasks:
        return 0
    
    assignee_map = {
        'development': '李开发',
        'testing': '王测试',
        'documentation': '陈文档',
        'deployment': '刘运维',
        'fullstack': '赵栈',
        'frontend': '赵栈',
        'backend': '李开发'
    }
    
    assigned_count = 0
    
    for task in tasks:
        task_type = task.get('type', 'development')
        assignee = assignee_map.get(task_type, '李开发')
        
        task['assignee'] = assignee
        task['status'] = 'assigned'
        task['assigned_at'] = datetime.now().isoformat()
        
        assigned_count += 1
    
    return assigned_count

# ============================================================================
# 任务执行管理
# ============================================================================

def check_and_execute_tasks():
    """
    检查并执行任务
    
    这是 Cron 任务的核心逻辑：
    1. 加载状态
    2. 检查是否有待执行任务
    3. 如果没有，立即返回（< 0.5 秒）
    4. 如果有，分配并启动任务
    5. 快速返回（< 2 秒）
    """
    start_time = datetime.now()
    
    try:
        status = load_team_status()
        
        if not status:
            return {
                'success': False,
                'error': '无法加载团队状态',
                'duration_seconds': (datetime.now() - start_time).total_seconds()
            }
        
        ready_tasks = get_ready_tasks(status)
        
        if not ready_tasks:
            return {
                'success': True,
                'action': 'no_tasks',
                'message': '没有待执行任务',
                'pending_count': len(get_pending_tasks(status)),
                'duration_seconds': (datetime.now() - start_time).total_seconds()
            }
        
        assigned_count = assign_tasks(ready_tasks)
        
        if assigned_count == 0:
            return {
                'success': True,
                'action': 'no_assign',
                'message': '没有任务可分配',
                'duration_seconds': (datetime.now() - start_time).total_seconds()
            }
        
        save_team_status(status)
        
        log_action("任务队列检查", f"""
发现待执行任务: {len(ready_tasks)} 个
分配任务: {assigned_count} 个
总耗时: {(datetime.now() - start_time).total_seconds():.3f} 秒
""")
        
        return {
            'success': True,
            'action': 'tasks_executed',
            'tasks_found': len(ready_tasks),
            'tasks_assigned': assigned_count,
            'duration_seconds': (datetime.now() - start_time).total_seconds()
        }
        
    except Exception as e:
        log_action("错误", str(e))
        return {
            'success': False,
            'error': str(e),
            'duration_seconds': (datetime.now() - start_time).total_seconds()
        }

# ============================================================================
# 主执行
# ============================================================================

def main():
    """主执行函数"""
    start_time = datetime.now()
    
    result = check_and_execute_tasks()
    
    duration = (datetime.now() - start_time).total_seconds()
    
    return {
        'success': result.get('success', False),
        'action': result.get('action', ''),
        'duration_seconds': duration,
        'message': f"执行完成，耗时 {duration:.2f} 秒"
    }

if __name__ == '__main__':
    result = main()
    print(json.dumps(result, indent=2, ensure_ascii=False))
