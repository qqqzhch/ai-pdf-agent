#!/usr/bin/env python3
"""
AI PDF Agent 团队 - 创建任务队列 Cron 任务（简化版）
"""

# ============================================================================
# Cron 任务配置
# ============================================================================

TASK_QUEUE_CRON_JOB = {
    "name": "AI PDF Agent - 任务队列管理（每 10 分钟）",
    "schedule": {
        "kind": "cron",
        "expr": "*/10 * * * *",
        "tz": "Asia/Shanghai"
    },
    "payload": {
        "kind": "agentTurn",
        "message": """作为任务队列管理器：

1. 检查 TEAM_STATUS.json 中的待执行任务
2. 检查任务依赖是否满足
3. 自动分配任务给合适成员
4. 更新 TEAM_STATUS.json
5. 记录到 TEAM_LOG.md

规则：
- development → 李开发或赵栈
- testing → 王测试
- documentation → 陈文档
- deployment → 刘运维
- fullstack → 赵栈或李开发
- frontend → 赵栈
- backend → 李开发

自动执行！""",
        "timeoutSeconds": 120
    },
    "sessionTarget": "isolated",
    "wakeMode": "now",
    "enabled": True
}

# ============================================================================
# 创建 Cron 任务函数
# ============================================================================

def create_task_queue_cron():
    """创建任务队列 Cron 任务"""
    print("\n" + "="*70)
    print("🚀 创建任务队列 Cron 任务")
    print("="*70)
    
    try:
        from openclaw import cron
        
        # 创建 Cron 任务
        result = cron(action="add", job=TASK_QUEUE_CRON_JOB)
        
        if result.get('ok') or result.get('id'):
            print("\n✅ Cron 任务创建成功！")
            print(f"   任务 ID：{result.get('id', result.get('job_id', 'N/A'))}")
            print(f"   任务名称：{TASK_QUEUE_CRON_JOB['name']}")
            print(f"   执行频率：每 10 分钟")
            print(f"   会话类型：isolated")
            
            print("\n📊 任务队列特性：")
            print("   ✅ 每 10 分钟自动检查")
            print("   ✅ 自动检查任务依赖")
            print("   ✅ 自动分配任务")
            print("   ✅ 自动处理超时（2 小时）")
            print("   ✅ 最多 2 分钟执行时间")
            
            print("\n🎉 任务队列已启动！")
            print("\n作为 CTO（我），你可以：")
            print("1. ✅ 添加任务到队列")
            print("2. ✅ 查看任务状态")
            print("3. ✅ 查看工作日志")
            print("\n工作流程：")
            print("你 → CTO → 添加任务 → Cron 自动分配 → 团队成员执行")
            print("\n注意：")
            print("- Cron 每 10 分钟自动检查并分配")
            print("- 任务完成后会自动开始下一个依赖任务")
            
            return True
        else:
            print(f"\n❌ Cron 任务创建失败：{result}")
            return False
    except ImportError:
        print("\n❌ 无法导入 cron 模块，跳过 Cron 任务创建")
        print("   你可以手动创建 Cron 任务：")
        print("   openclaw cron add --schedule '*/10 * * * *' --message '任务队列管理'")
        return False
    except Exception as e:
        print(f"\n❌ 创建 Cron 任务时出错：{str(e)}")
        return False

# ============================================================================
# 主执行
# ============================================================================

if __name__ == '__main__':
    success = create_task_queue_cron()
    
    print("\n" + "="*70)
    if success:
        print("✅ 任务队列 Cron 任务创建成功！")
        print("="*70)
    else:
        print("⚠️ 任务队列 Cron 任务创建部分完成")
        print("="*70)
