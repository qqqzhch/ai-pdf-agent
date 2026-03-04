"""
AI PDF Agent 团队 - 创建张架构的优化 Cron 任务

Cron 配置：
- 频率：每 5 分钟
- 超时：2 分钟（快速返回）
- 执行：张架构优化的自治逻辑
- 目标：最小化对主会话的影响
"""

import json

# ============================================================================
# Cron 任务配置
# ============================================================================

ZHANG_ARCHITECT_CRON_JOB = {
    "name": "张架构 - 团队自治管理（优化版）",
    "schedule": {
        "kind": "every",
        "everyMs": 300000,  # ✅ 5 分钟
        "tz": "Asia/Shanghai"
    },
    "payload": {
        "kind": "agentTurn",
        "message": """
## 你现在是张架构（AI PDF Agent 团队技术架构负责人）

### 优化执行逻辑（重要！）

**关键目标：最小化对主会话的影响**

#### 执行策略

**步骤 1：快速检查（< 0.5 秒）
1. 读取 TEAM_STATUS.json
2. 快速扫描是否有新任务（status=pending）
3. 快速检查是否有超时任务（status=in_progress + > 2 小时）
4. 如果都没有：立即执行返回（< 1 秒）

**步骤 2：需要操作时快速执行（< 2 分钟）
如果有新任务或超时：
1. 读取 TEAM_CONFIG.json
2. 分配新任务给合适成员
3. 处理超时任务
4. 更新 TEAM_STATUS.json
5. 记录到 TEAM_LOG.md
6. 立即返回（不要等待）

#### 行为规则

**✅ 关键：**
- 没有新任务时：**立即返回**（< 1 秒）
- 有新任务时：**快速执行**（< 2 分钟）
- 永远不要等待任何结果
- 完成操作后立即返回

#### 任务分配规则

- development（后端开发）→ 李开发
- testing（测试任务）→ 王测试
- documentation（文档任务）→ 陈文档
- deployment（部署任务）→ 刘运维
- fullstack（全栈开发）→ 赵栈
- frontend（前段开发）→ 赵栈

#### 超时处理

- status=in_progress 的任务
- 如果 > 2 小时未完成 → 标记为 failed
- 记录超时信息
- 通知 CTO（通过消息 tool）

#### 工作流程（优化版）

```
快速检查（< 0.5 秒）
    ↓
有新任务 或 超时？
    ↓
    ├─ 是 → 快速执行（< 2 分钟）
    │        ├─> 分配任务
    │        ├─> 处理超时
    │        ├─> 更新状态
    │        └─> 立即返回
    │
    └─ 否 → 立即返回（< 1 秒）
```

#### 关键优势

1. **无任务时无开销** - 几乎不占用模型时间
2. **快速执行** - 有任务时也很快
3. **不影响主会话** - 大部分时间你都可以正常响应
4. **自动化** - 完全自动执行

#### 共享文件

- TEAM_CONFIG.json - 团队配置
- TEAM_STATUS.json - 项目状态
- TEAM_LOG.md - 团队日志

#### 注意事项

**⚠️ 重要：**
- 永远不要等待团队成员的响应
- 只分配任务，不跟踪执行
- 成员会自动更新 TEAM_STATUS.json
- 成员完成后会自动通知你

**你现在准备好执行了。每 5 分钟自动检查一次。**
        """,
        "timeoutSeconds": 120  # ✅ 2 分钟严格限制
    },
    "sessionTarget": "isolated",  # ✅ 独立会话
    "wakeMode": "now",  # ✅ 立即执行
    "enabled": True
}

# ============================================================================
# 创建 Cron 任务函数
# ============================================================================

def create_zhang_architect_cron():
    """
    创建张架构的优化 Cron 任务
    """
    print("\n" + "="*70)
    print("🚀 创建张架构的优化 Cron 任务")
    print("="*70)
    
    try:
        from openclaw import cron
        
        # 创建 Cron 任务
        result = cron(action="add", job=ZHANG_ARCHITECT_CRON_JOB)
        
        if result.get('ok') or result.get('id'):
            print("\n✅ Cron 任务创建成功！")
            print(f"   任务 ID：{result.get('id', result.get('job_id', 'N/A'))}")
            print(f"   任务名称：{ZHANG_ARCHITECT_CRON_JOB['name']}")
            print(f"   执行频率：每 5 分钟")
            print(f"   超时限制：2 分钟")
            print(f"   会话类型：isolated")
            
            print("\n📊 执行逻辑：")
            print("   1. 快速检查（< 0.5 秒）")
            print("   2. 如果没有新任务：立即返回（< 1 秒）")
            print("   3. 如果有新任务：快速执行（< 2 分钟）")
            print("   4. 最小化对主会话的影响")
            
            print("\n🎉 张架构现在会自动运行！")
            print("\n优化效果：")
            print("   ✅ 无任务时几乎无开销")
            print("   ✅ 有任务时快速执行")
            print("   ✅ 不影响主会话响应")
            
            return True
        else:
            print(f"\n❌ Cron 任务创建失败：{result}")
            return False
    except ImportError:
        print("\n❌ 无法导入 cron 模块，跳过 Cron 任务创建")
        print("   你可以手动创建 Cron 任务")
        return False
    except Exception as e:
        print(f"\n❌ 创建 Cron 任务时出错：{str(e)}")
        return False

# ============================================================================
# 主执行
# ============================================================================

if __name__ == "__main__":
    success = create_zhangarchitect_cron()
    
    print("\n" + "="*70)
    if success:
        print("✅ AI PDF Agent 团队优化架构配置完成！")
        print("="*70)
        
        print("\n📋 下一步操作：")
        print("\n作为 CTO（我），你可以：")
        print("1. ✅ 交给项目任务给我（CTO）")
        print("2. ✅ 我会分析任务并分配给张架构")
        print("3. ✅ 张架构会自动协调整个成员")
        print("4. ✅ 只在异常或卡住时汇报")
        
        print("\n作为用户（你），你可以：")
        print("1. ✅ 查看 TEAM_STATUS.json 了解进度")
        print("2. ✅ 查看 TEAM_LOG.md 了解历史")
        print("3. ✅ 直接与我（CTO）沟通")
        print("4. ✅ 查看成员工作状态")
        
        print("\n🎉 架构已优化完成！团队可以自主运行了！")
    else:
        print("⚠️ AI PDF Agent 团队优化架构配置部分完成")
        print("="*70)
        print("\n即使没有自动创建 Cron，团队仍然可以使用。")
