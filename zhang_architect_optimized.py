"""
AI PDF Agent 团队 - 张架构的优化自治逻辑

优化目标：
1. 没有新任务时立即返回（< 0.5 秒）
2. 有新任务时快速执行（< 2 分钟）
3. 最小化对主会话的影响
"""

import json
from datetime import datetime, timedelta
import os

# ============================================================================
# 文件路径
# ============================================================================

TEAM_CONFIG_PATH = "/root/.openclaw/workspace/ai-pdf-agent/TEAM_CONFIG.json"
TEAM_STATUS_PATH = "/root/.openclaw/workspace/ai-pdf-agent/TEAM_STATUS.json"
TEAM_LOG_PATH = "/root/.openclaw/workspace/ai-pdf-agent/TEAM_LOG.md"

# ============================================================================
# 快速检查函数
# ============================================================================

def quick_check_needs_action():
    """
    快速检查是否需要执行任何操作
    时间：< 0.5 秒
    """
    try:
        # 1. 读取状态（最快方式）
        with open(TEAM_STATUS_PATH, 'r', encoding='utf-8') as f:
            team_status = json.load(f)
        
        # 2. 快速扫描任务
        tasks = team_status.get('tasks', [])
        
        # 3. 检查条件
        has_pending = any(t.get('status') == 'pending' for t in tasks)
        has_in_progress = any(t.get('status') == 'in_progress' for t in tasks)
        
        # 4. 检查超时（快速检查）
        current_time = datetime.now()
        has_timeout = False
        
        for task in tasks:
            if task.get('status') == 'in_progress':
                started_at_str = task.get('started_at')
                if started_at_str:
                    started_at = datetime.fromisoformat(started_at_str)
                    duration = (current_time - started_at).total_seconds() / 60  # 分钟
                    if duration > 120:  # 超过 2 小时
                        has_timeout = True
                        break
        
        # 5. 返回结果
        return {
            'needs_action': has_pending or has_timeout,
            'has_pending': has_pending,
            'has_in_progress': has_in_progress,
            'has_timeout': has_timeout,
            'pending_count': sum(1 for t in tasks if t.get('status') == 'pending'),
            'in_progress_count': sum(1 for t in tasks if t.get('status') == 'in_progress'),
            'total_tasks': len(tasks)
        }
    except Exception as e:
        return {
            'needs_action': False,
'error': str(e)
        }

# ============================================================================
# 快速执行函数
# ============================================================================

def quick_execute_action():
    """
    快速执行必要操作
    时间：< 2 分钟
    """
    start_time = datetime.now()
    
    try:
        # 1. 读取配置和状态
        with open(TEAM_CONFIG_PATH, 'r', encoding='utf-8') as f:
            team_config = json.load(f)
        
        with open(TEAM_STATUS_PATH, 'r', encoding='utf-8') as f:
            team_status = json.load(f)
        
        # 2. 检查条件
        check_result = quick_check_needs_action()
        
        # 3. 如果不需要，记录并返回
        if not check_result['needs_action']:
            log_check("无新任务", check_result, start_time)
            return {
                'success': True,
                'action_taken': False,
                'reason': 'no_new_tasks',
                'duration_seconds': (datetime.now() - start_time).total_seconds()
            }
        
        # 4. 有超时，处理超时
        if check_result['has_timeout']:
            handle_timeout(team_config, team_status, start_time)
            return {
                'success': True,
                'action_taken': True,
                'reason': 'timeout_handled',
                'duration_seconds': (datetime.now() - start_time).total_seconds()
            }
        
        # 5. 有待新任务，分配任务
        if check_result['has_pending']:
            assigned = assign_pending_tasks(team_config, team_status, start_time)
            return {
                'success': True,
                'action_taken': True,
                'reason': 'tasks_assigned',
                'tasks_assigned': assigned,
                'duration_seconds': (datetime.now() - start_time).total_seconds()
            }
        
        # 6. 没有操作
        return {
            'success': True,
            'action_taken': False,
            'reason': 'unknown',
            'duration_seconds': (datetime.now() - start_time).total_seconds()
        }
    except Exception as e:
        log_error(str(e), start_time)
        return {
            'success': False,
            'error': str(e),
            'duration_seconds': (datetime.now() - start_time).total_seconds()
        }

# ============================================================================
# 任务分配函数
# ============================================================================

def assign_pending_tasks(team_config, team_status, start_time):
    """
    分配待处理任务
    """
    assigned_tasks = []
    
    try:
        # 1. 获取待处理任务
        tasks = team_status.get('tasks', [])
        pending_tasks = [t for t in tasks if t.get('status') == 'pending']
        
        # 2. 读取配置
        members = team_config.get('members', {})
        
        # 3. 分配任务
        for task in pending_tasks:
            # 选择执行人
            assignee = select_assignee(task, members)
            
            if assignee:
                # 更新任务
                task['status'] = 'assigned'
                task['assignee'] = assignee
                task['assigned_at'] = datetime.now().isoformat()
                
                assigned_tasks.append({
                    'task_id': task.get('id'),
                    'assignee': assignee
                })
        
        # 4. 保存状态
        team_status['last_updated'] = datetime.now().isoformat()
        with open(TEAM_STATUS_PATH, 'w', encoding='utf-8') as f:
            json.dump(team_status, f, indent=2, ensure_ascii=False)
        
        # 5. 记录日志
        log_assignment(assigned_tasks, start_time)
        
        return assigned_tasks
    except Exception as e:
        log_error(f"任务分配失败：{str(e)}", start_time)
        return []

# ============================================================================
# 选择执行人函数
# ============================================================================

def select_assignee(task, members):
    """
    根据任务类型选择合适的执行人
    """
    task_type = task.get('type', 'development')
    
    # 任务类型映射
    assignee_map = {
        'development': '李开发',
        'testing': '王测试',
        'documentation': '陈文档',
        'deployment': '刘运维',
        'fullstack': '赵栈',
        'frontend': '赵栈',
        'backend': '李开发'
    }
    
    # 返回选择的执行人
    return assignee_map.get(task_type)

# ============================================================================
# 超时处理函数
# ============================================================================

def handle_timeout(team_config, team_status, start_time):
    """
    处理超时任务
    """
    try:
        # 1. 获取超时任务
        tasks = team_status.get('tasks', [])
        current_time = datetime.now()
        
        timeout_tasks = []
        for task in tasks:
            if task.get('status') == 'in_progress':
                started_at_str = task.get('started_at')
                if started_at_str:
                    started_at = datetime.fromisoformat(started_at_str)
                    duration = (current_time - started_at).total_seconds() / 60
                    if duration > 120:  # 超过 2 小时
                        task['status'] = 'failed'
                        task['error'] = f'任务超时（{duration:.1f} 分钟）'
                        timeout_tasks.append({
                            'task_id': task.get('id'),
                            'assignee': task.get('assignee'),
                            'duration_minutes': duration
                        })
        
        # 2. 保存状态
        if timeout_tasks:
            team_status['last_updated'] = datetime.now().isoformat()
            with open(TEAM_STATUS_PATH, 'w', encoding='utf-8') as f:
                json.dump(team_status, f, indent=2, ensure_ascii=False)
            
            # 3. 记录日志
            log_timeout(timeout_tasks, start_time)
        
        return timeout_tasks
    except Exception as e:
        log_error(f"超时处理失败：{str(e)}", start_time)
        return []

# ============================================================================
# 日志函数
# ============================================================================

def log_check(reason, check_result, start_time):
    """记录检查日志"""
    try:
        log_entry = f"""
### {datetime.now().strftime('%H:%M:%S')} - 进度检查
- 原因：{reason}
- 待处理：{check_result.get('pending_count', 0)} 个
- 进行中：{check_result.get('in_progress_count', 0)} 个
- 总任务：{check_result.get('total_tasks', 0)} 个
"""
        append_to_log(log_entry)
    except Exception:
        pass

def log_assignment(assigned_tasks, start_time):
    """记录分配日志"""
    try:
        if not assigned_tasks:
            return
        
        log_entry = f"""
### {datetime.now().strftime('%H:%M:%S')} - 任务分配
"""
        for task in assigned_tasks:
            log_entry += f"- {task['task_id']} → {task['assignee']}\n"
        
        append_to_log(log_entry)
    except Exception:
        pass

def log_timeout(timeout_tasks, start_time):
    """记录超时日志"""
    try:
        if not timeout_tasks:
            return
        
        log_entry = f"""
### {datetime.now().strftime('%H:%M:%S')} - 任务超时
"""
        for task in timeout_tasks:
            log_entry += f"- {task['task_id']} ({task['assignee']}) 超时 {task['duration_minutes']:.1f} 分钟\n"
        
        append_to_log(log_entry)
    except Exception:
        pass

def log_error(error, start_time):
    """记录错误日志"""
    try:
        log_entry = f"""
### {datetime.now().strftime('%H:%M:%S')} - 错误
- {error}
"""
        append_to_log(log_entry)
    except Exception:
        pass

def append_to_log(content):
    """追加到日志文件"""
    try:
        with open(TEAM_LOG_PATH, 'a', encoding='utf-8') as f:
            f.write(content)
    except Exception:
        pass

# ============================================================================
# 主执行函数
# ============================================================================

def main():
    """
    张架构的优化主执行函数
    """
    start_time = datetime.now()
    
    try:
        # 1. 快速检查
        check_result = quick_check_needs_action()
        
        # 2. 不需要操作，立即返回
        if not check_result['needs_action']:
            # 记录检查
            log_check("无新任务", check_result, start_time)
            
            # 计算耗时
            duration = (datetime.now() - start_time).total_seconds()
            
            # 立即返回
            return {
                'success': True,
                'action_taken': False,
                'reason': 'no_new_tasks',
                'duration_seconds': duration,
                'message': '✅ 检查完成，无新任务，立即返回'
            }
        
        # 3. 需要操作，快速执行
        result = quick_execute_action()
        
        # 计算总耗时
        duration = (datetime.now() - start_time).total_seconds()
        
        return {
            'success': result.get('success', False),
            'action_taken': result.get('action_taken', False),
            'reason': result.get('reason', ''),
            'duration_seconds': duration,
            'message': f"✅ 操作完成：{result.get('reason', '')}，耗时 {duration:.2f} 秒"
        }
    except Exception as e:
        duration = (datetime.now() - start_time).total_seconds()
        
        return {
            'success': False,
            'error': str(e),
            'duration_seconds': duration,
            'message': f"❌ 执行失败：{str(e)}，耗时 {duration:.2f} 秒"
        }

if __name__ == '__main__':
    result = main()
    print(result.get('message', str(result)))
