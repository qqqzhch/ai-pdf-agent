#!/usr/bin/env python3
"""
AI PDF Agent 团队 - 创建任务队列 Cron 任务

Cron 配置：
- 频率：每 10 分钟
- 超时：最多 2 分钟
- 执行：任务队列检查和自动执行
- 目标：自动触发下一个任务，支持任务依赖
"""

import json

# ============================================================================
# Cron 任务配置
# ============================================================================

TASK_QUEUE_CRON_JOB = {
    "name": "AI PDF Agent - 任务队列管理（每 10 分钟）",
    "schedule": {
        "kind": "cron",
        "expr": "*/10 * * * *",  # ✅ 每 10 分钟
        "tz": "Asia/Shanghai"
    },
    "payload": {
        "kind": "agentTurn",
        "message": """
## 你现在是任务队列管理器

### 核心职责

1. **检查待执行任务**
   - 读取 TEAM_STATUS.json
   - 检查是否有 status=pending 的任务
   - 检查是否有 status=in_progress 且超时（> 2 小时）的任务

2. **检查任务依赖**
   - 对于待执行任务，检查其 depends_on 字段
   - 确保所有依赖任务都是 status=completed
   - 只有没有依赖或依赖已完成的任务标记为 "ready"

3. **分配任务**
   - 对于所有 "ready" 的任务
   - 根据任务类型（type）自动选择合适的团队成员
   - 开发任务 → 李开发或赵栈
   - 测试任务 → 王测试
   - 文档任务 → 陈文档
   - 部署任务 → 刘运维
   - 更新任务状态为 assigned
   - 记录 assigned_at 时间

4. **发送任务给成员**
   - 使用 sessions_send 向对应的成员发送任务消息
   - 消息包含完整的任务信息（ID、标题、描述、优先级等）
   - 告知成员更新 TEAM_STATUS.json

5. **处理超时任务**
   - 对于 status=in_progress 且 > 2 小时的任务
   - 标记为 failed
   - 记录错误原因（"任务超时（> 2 小时）"）
   - 通知 CTO（通过发送消息到主会话）

6. **更新状态和日志**
   - 所有操作后更新 TEAM_STATUS.json
   - 所有关键操作记录到 TEAM_LOG.md
   - 记录格式：
     ### HH:MM:SS - 操作类型
     - 详细信息

### 任务分配规则

**自动分配：**
- development（后端开发）→ 李开发
- testing（测试任务）→ 王测试
- documentation（文档任务）→ 陈文档
- deployment（部署任务）→ 刘运维
- fullstack（全栈开发）→ 赵栈
- frontend（前端开发）→ 赵栈
- backend（后端开发）→ 李开发

### 任务执行流程

1. **成员收到任务**
   - 读取 TEAM_STATUS.json
   - 更新任务状态为 in_progress
   - 记录 started_at 时间

2. **成员执行任务**
   - 执行具体的开发/测试/文档工作
   - 可能调用 exec 运行命令
   - 可能调用 sessions_spawn 启动子任务

3. **任务完成**
   - 更新任务状态为 completed
   - 记录 completed_at 时间
   - 计算 duration_ms
   - 更新成员的 tasks_completed 计数

4. **成员通知完成**
   - 使用 sessions_send 通知张架构
   - 或者直接更新 TEAM_STATUS.json

5. **Cron 下次检查**
   - 10 分钟后再次运行
   - 自动检查是否有新任务
   - 自动分配下一个任务
   - 自动处理依赖

### 关键特性

**自动化流程：**
- ✅ 每 10 分钟自动检查
- ✅ 自动检查任务依赖
- ✅ 自动分配任务
- ✅ 自动处理超时
- ✅ 完全自动化的任务队列

**共享文件：**
- TEAM_CONFIG.json - 团队配置
- TEAM_STATUS.json - 任务状态
- TEAM_LOG.md - 操作日志

**成员会话：**
- 所有成员使用 `cleanup="keep"` 保持会话
- 成员可以接收任务并执行
- 成员完成后更新状态

**注意：**
- 永远不要等待成员响应
- 完成分配后立即返回
- 成员会自主更新状态
- 下次 cron 检查会自动继续

### 时间控制

- Cron 频率：每 10 分钟
- Cron 执行超时：最多 2 分钟
- 任务超时阈值：2 小时
- 快速检查：如果没有待执行任务，立即返回

**你现在准备好了！每 10 分钟自动运行！**
        """,
        "timeoutSeconds": 120  # ✅ 最多 2 分钟
    },
    "sessionTarget": "isolated",  # ✅ 独立会话
    "wakeMode": "now",  # ✅ 立即执行
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
            print(f"   执行超时：最多 2 分钟")
            print(f"   会话类型：isolated")
            
            print("\n📊 任务队列特性：")
            print("   ✅ 每 10 分钟自动检查")
            print("   ✅ 自动检查任务依赖")
            print("   ✅ 自动分配任务")
            print("   ✅ 自动处理超时")
            print("   ✅ 完全自动化的任务队列")
            
            print("\n🔄 工作流程：")
            print("   1. 检查待执行任务")
            print("   2. 检查任务依赖")
            print("   3. 分配任务给合适成员")
            print("   4. 发送任务给成员")
            print("   5. 成员执行并更新状态")
            print("   6. Cron 下次检查继续")
            
            print("\n🎉 任务队列已启动！")
            print("\n下一步：")
            print("1. 作为 CTO（我），你可以：")
            print("   ✅ 添加任务到队列")
            print("   ✅ 查看任务状态")
            print("   ✅ 查看工作日志")
            print("\n2. 团队成员会自动：")
            print("   ✅ 接收分配的任务")
            print("   ✅ 执行任务")
            print("   ✅ 更新状态")
            print("   ✅ Cron 自动检查继续")
            
            print("\n3. 完全自动化的流程：")
            print("   ✅ 添加任务 → 自动排队")
            print("   ✅ Cron 检查 → 自动分配")
            print("   ✅ 成员执行 → 自动继续")
            print("   ✅ 下次检查 → 下个任务")
            
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

if __name__ == "__main__":
    success = create_task_queue_cron()
    
    print("\n" + "="*70)
    if success:
        print("✅ 任务队列 Cron 任务创建成功！")
        print("="*70)
        
        print("\n🎉 关键特性：")
        print("1. ✅ 每 10 分钟自动检查")
        print("2. ✅ 自动检查任务依赖")
        print("3. ✅ 自动分配任务")
        print("4. ✅ 自动处理超时")
        print("5. ✅ 完全自动化的任务队列")
        
        print("\n🎉 工作流程：")
        print("1. 添加任务 → 自动排队")
        print("2. Cron 检查 → 自动分配")
        print("3. 成员执行 → 自动继续")
        print("4. 下次检查 → 下个任务")
        
        print("\n🎉 任务队列系统已就绪！")
    else:
        print("⚠️ 任务队列 Cron 任务创建部分完成")
        print("="*70)
        print("\n即使没有 Cron，任务队列系统仍然可以使用。")
