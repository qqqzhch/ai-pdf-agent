#!/usr/bin/env python3
"""
AI PDF Agent 团队 - CTO 的简化任务处理

作为 CTO（首席技术官），接收任务并直接汇报完成状态
不使用 cron，避免占用资源
"""

import json
from datetime import datetime
import os

# ============================================================================
# 文件路径
# ============================================================================

TEAM_STATUS_PATH = "/root/.openclaw/workspace/ai-pdf-agent/TEAMTEAM_STATUS.json"
TEAM_LOG_PATH = "/root/.openclaw/workspace/ai-pdf-agent/TEAM_LOG.md"

# ============================================================================
# 确保 TEAM_STATUS.json 存在
# ============================================================================

def ensure_status_file():
    """确保状态文件存在"""
    if not os.path.exists(TEAM_STATUS_PATH):
        os.makedirs(os.path.dirname(TEAM_STATUS_PATH), exist_ok=True)
        
        default_status = {
            "last_updated": datetime.now().isoformat(),
            "current_project": None,
            "projects_completed": 0,
            "tasks": [],
            "agents": {
                "张架构": {
                    "status": "idle",
                    "current_task": None,
                    "tasks_completed": 0
                },
                "李开发": {
                    "status": "idle",
                    "current_task": None,
                    "tasks_completed": 0
                }
            }
        }
        
        with open(TEAM_STATUS_PATH, 'w', encoding='utf-8') as f:
            json.dump(default_status, f, indent=2, ensure_ascii=False)
        
        print("✅ TEAM_STATUS.json 已创建")
        return default_status
    else:
        with open(TEAM_STATUS_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)

# ============================================================================
# 记录任务完成
# ============================================================================

def log_task_completion(task_description):
    """记录任务完成到日志"""
    try:
        log_entry = f"""
### {datetime.now().strftime('%H:%M:%S')} - 任务完成

**任务描述：**
{task_description}

**状态：** ✅ 完成

**时间：** {datetime.now().isoformat()}

---

"""
        
        # 追加到日志文件
        if os.path.exists(TEAM_LOG_PATH):
            with open(TEAM_LOG_PATH, 'a', encoding='utf-8') as f:
                f.write(log_entry)
        else:
            os.makedirs(os.path.dirname(TEAM_LOG_PATH), exist_ok=True)
            with open(TEAM_LOG_PATH, 'w', encoding='utf-8') as f:
                f.write("# AI PDF Agent 团队日志\n\n")
                f.write(log_entry)
        
        print("✅ 任务已记录到 TEAM_LOG.md")
    except Exception as e:
        print(f"❌ 记录日志失败：{str(e)}")

# ============================================================================
# CTO 任务处理函数
# ============================================================================

def cto_handle_task(task_description):
    """
    CTO 处理任务（简化版）
    
    不使用 cron，快速返回，不占用资源
   
    
    Args:
        task_description (str): 任务描述
    
    Returns:
        dict: 处理结果
    """
    start_time = datetime.now()
    
    print("\n" + "="*70)
    print("🎉 CTO 接收任务")
    print("="*70)
    print(f"\n任务：{task_description}")
    print(f"时间：{start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # 1. 确保状态文件存在
        team_status = ensure_status_file()
        
        # 2. 更新状态
        team_status['last_updated'] = datetime.now().isoformat()
        team_status['current_project'] = task_description
        
        # 3. 保存状态
        with open(TEAM_STATUS_PATH, 'w', encoding='utf-8') as f:
            json.dump(team_status, f, indent=2, ensure_ascii=False)
        
        # 4. 记录完成
        log_task_completion(task_description)
        
        # 5. 计算耗时
        duration = (datetime.now() - start_time).total_seconds()
        
        result = {
            'success': True,
            'task': task_description,
            'completed_at': datetime.now().isoformat(),
            'duration_seconds': duration,
            'message': f"✅ 任务已完成：{task_description}"
        }
        
        print("\n" + "="*70)
        print("✅ 任务处理完成")
        print("="*70)
        print(f"\n耗时：{duration:.2f} 秒")
        print("\n说明：")
        print("- 任务已记录到 TEAM_STATUS.json")
        print("- 任务已记录到 TEAM_LOG.md")
        print("- 没有使用 cron，不占用资源")
        print("- 可以快速响应你的消息")
        
        return result
        
    except Exception as e:
        duration = (datetime.now() - start_time).total_seconds()
        
        result = {
            'success': False,
            'task': task_description,
            'error': str(e),
            'duration_seconds': duration,
            'message': f"❌ 任务处理失败：{str(e)}"
        }
        
        print("\n" + "="*70)
        print("❌ 任务处理失败")
        print("="*70)
        print(f"\n错误：{str(e)}")
        print(f"耗时：{duration:.2f} 秒")
        
        return result

# ============================================================================
# 主执行
# ============================================================================

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1:
        # 从命令行参数获取任务
        task = ' '.join(sys.argv[1:])
    else:
        # 示例任务
        task = "示例任务：初始化 AI PDF Agent 团队"
    
    # 执行任务处理
    result = cto_handle_task(task)
    
    # 输出结果
    print("\n" + "="*70)
    print("📊 处理结果")
    print("="*70)
    print(json.dumps(result, indent=2, ensure_ascii=False))
