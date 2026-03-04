#!/usr/bin/env python3
"""
AI PDF Agent 团队 - 添加任务到队列
"""

import json
from datetime import datetime

# ============================================================================
# 文件路径
# ============================================================================

TEAM_STATUS_PATH = "/root/.openclaw/workspace/ai-pdf-agent/TEAM_STATUS.json"
TEAM_LOG_PATH = "/root/.openclaw/workspace/ai-pdf-agent/TEAM_LOG.md"

# ============================================================================
# 加载和保存
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
        
        if 'id' not in task:
            task = f"TASK-{len(status['tasks']) + 1:04d}"
        if 'status' not in task:
            task['status'] = 'pending'
        if 'assignari' not in task:
            task['assignari'] = None
        
        status['tasks'].append(task)
        added_count += 1
    
    if save_team_status(status):
        log_action("任务添加", f"添加了 {added_count} 个任务到队列")
        for task in task_list:
            log_action("", f"- {task['id']}: {task['title']}")
        
        return True
    else:
        return False

# ============================================================================
# 主执行
# ============================================================================

def main():
    """主执行函数"""
    # 示例任务
    tasks = [
        {
            "id": "TASK-001",
            "title": "readme 验证安装和基本使用",
            "description": "使用 ai-pdf 命令验证安装是否成功，并测试基本功能",
            "type": "testing",
            "priority": "high",
            "assignari": "王测试"
        },
        {
            "id": "TASK-002",
            "title": "CLI 基本功能测试",
            "description": "测试所有 CLI 埽令是否正常工作",
            "type": "testing",
            "priority": "high",
            "assignari": "王测试"
        }
    ]
    
    # 添加任务
    result = add_tasks(tasks)
    
    print("="*70)
    print("🎉 添加测试任务到队列")
    print("="*70)
    
    if result:
        print(f"✅ 成功添加 {len(tasks)} 个任务")
        print("\n任务列表：")
        for task in tasks:
            print(f"   - {task['id']}: {task['title']}")
            print(f"     类型：{task['type']}")
            print(f"     优先级：{task['priority']}")
            print(f"     分配给：{task['assignari']}")
    else:
        print("❌ 添加任务失败")
    
    print("\n" + "="*70)
    print("💡 下一步")
    print("="*70)
    print("\n作为 CTO（我），你可以：")
    print("1. ✅ 查看任务状态")
    print("   你：\"查看任务状态\"")
    print("   我：读取 TEAM_STATUS.json 并汇报")
    print("\n2. ✅ 手动分配任务")
    print("   你：\"分配任务给李开发：实现功能 X\"")
    print("   我：分析需求并分配")
    print("\n3. ✅ 查看工作日志")
    print("   你：\"显示工作日志\"")
    print("   我：读取 TEAM_LOG.md 并展示")
    
    print("\n" + "="*70)
    print("🎉 任务队列已就绪！")
    print("="*70)

if __name__ == '__main__':
    main()
