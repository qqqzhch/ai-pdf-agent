# AI PDF Agent - 异常任务处理方案

## 方案选择

**最终方案：** 方案 A（依赖分析 + 重试机制 + 状态追踪）

**选择原因：**
- ✅ 简单可靠，易于实现
- ✅ 明确的失败处理
- ✅ 不会无限重试
- ✅ 确保任务完整性
- ✅ 用户明确知道任务状态

---

## 🎯 核心策略

### 1. 依赖分析

**目的：** 确保跳过的任务不影响其他任务执行

**实现：**
- 定义任务依赖关系
- 检查任务是否有依赖者
- 只跳过无依赖的任务
- 阻塞依赖当前任务的其他任务

### 2. 重试机制

**目的：** 给任务多次机会，避免因临时问题失败

**实现：**
- 超时任务自动重试 3 次
- 每次重试间隔递增（1 分钟、5 分钟、10 分钟）
- 记录重试历史
- 重试失败后标记为阻塞

### 3. 状态追踪

**目的：** 记录完整执行历史，支持诊断和恢复

**实现：**
- 记录每次尝试的开始和结束时间
- 记录错误信息
- 记录阻塞原因
- 支持任务诊断

---

## 🔧 完整实现

### 数据结构

```python
# 任务依赖定义
TASK_DEPENDENCIES = {
    'TASK-1.1.1': [],  # 无依赖
    'TASK-2.1': ['TASK-1.1.2'],
    'TASK-3.1': ['TASK-2.2'],
    'TASK-4.1': ['TASK-2.2'],
    'TASK-4.5': ['TASK-3.3', 'TASK-4.1'],
    'TASK-5.1': ['TASK-3.1', 'TASK-4.1'],
    'TASK-6.3': ['TASK-5.1'],
    # ... 其他任务
}

# 任务状态
task_states = {
    'TASK-6.3': {
        'status': 'blocked',  # pending, running, completed, failed, blocked
        'retry_count': 3,
        'last_error': '执行超时',
        'blocked_by': None,
        'blocking': ['TASK-6.4', 'TASK-6.5'],  # 阻塞的任务
        'attempts': [
            {
                'start': '2026-03-03 19:30',
                'end': '2026-03-03 20:55',
                'status': 'timeout'
            },
        ],
    },
}
```

---

### 核心函数

```python
def get_dependents(task_id):
    """获取依赖当前任务的所有任务"""
    dependents = []
    for tid, deps in TASK_DEPENDENCIES.items():
        if task_id in deps:
            dependents.append(tid)
    return dependents

def can_skip_task(task_id):
    """检查任务是否可以跳过"""
    # 1. 检查是否有依赖任务
    dependents = get_dependents(task_id)
    
    # 2. 如果有依赖任务，不能跳过
    if dependents:
        logger.warning(f"不能跳过 {task_id}，有依赖任务: {dependents}")
        return False
    
    # 3. 可以跳过
    return True

def can_execute_task(task_id):
    """检查任务是否可以执行"""
    # 1. 检查依赖是否完成
    deps = TASK_DEPENDENCIES.get(task_id, [])
    if not all(is_completed(dep) for dep in deps):
        return False, "依赖任务未完成"
    
    # 2. 检查是否被阻塞
    state = task_states.get(task_id)
    if state and state['status'] == 'blocked':
        return False, f"被阻塞：{state['blocked_by']}"
    
    # 3. 检查是否已完成
    if is_completed(task_id):
        return False, "已完成"
    
    return True, None

def mark_as_blocked(task_id, reason):
    """标记任务为阻塞"""
    state = task_states.setdefault(task_id, {})
    state['status'] = 'blocked'
    state['blocked_by'] = reason
    
    # 标记依赖任务
    dependents = get_dependents(task_id)
    for dep in dependents:
        mark_as_blocked(dep, f"依赖任务 {task_id} 被阻塞")

def schedule_retry(task_id, delay):
    """安排任务重试"""
    state = task_states.get(task_id, {})
    state['retry_count'] = state.get('retry_count', 0) + 1
    state['status'] = 'pending'
    
    # 记录重试历史
    if 'attempts' not in state:
        state['attempts'] = []
    
    state['attempts'].append({
        'start': datetime.now().isoformat(),
        'end': None,
        'status': 'retrying',
    })
    
    # 安排延迟执行
    schedule_task(task_id, delay=delay)

def get_retry_count(task_id):
    """获取任务重试次数"""
    state = task_states.get(task_id, {})
    return state.get('retry_count', 0)
```

---

### 异常处理逻辑

```python
def handle_timeout_task(task_id):
    """处理超时任务（不跳过）"""
    retry_count = get_retry_count(task_id)
    
    # 1. 重试机制（最多 3 次）
    if retry_count < 3:
        delays = [60, 300, 600]  # 1, 5, 10 分钟
        delay = delays[retry_count]
        
        logger.warning(
            f"任务 {task_id} 超时，"
            f"{delay // 60} 分钟后重试（第 {retry_count + 1}/3 次）"
        )
        schedule_retry(task_id, delay)
        return True  # 继续等待
    
    # 2. 重试次数用完，检查是否可跳过
    logger.error(f"任务 {task_id} 重试 3 次均失败，标记为阻塞")
    
    # 3. 分析依赖任务
    dependents = get_dependents(task_id)
    
    if dependents:
        logger.error(f"以下任务被阻塞（依赖 {task_id}）：{dependents}")
        
        # 阻塞依赖任务
        for dep in dependents:
            mark_as_blocked(dep, reason=f"依赖任务 {task_id} 失败")
        
        # 4. 通知用户
        notify_user(
            f"任务 {task_id} 执行失败（（重试 3 次均超时）",
            f"被阻塞的任务：{dependents}"
        )
    else:
        logger.warning(f"任务 {task_id} 无依赖任务，标记为失败")
        
        # 4. 通知用户
        notify_user(
            f"任务 {task_id} 执行失败（（重试 3 次均超时）",
            "无依赖任务受影响"
        )
    
    # 5. 不继续执行其他任务
    return False  # 停止后续任务执行
```

---

## 📊 任务依赖关系

| 任务 | 依赖任务 | 可跳过？ | 优先级 |
|------|---------|---------|---------|
| TASK-1.1.1 | 无 | ❌ 否 | high |
| TASK-1.1.2 | TASK-1.1.1 | ❌ 否 | high |
| TASK-1.1.3 | TASK-1.1.1 | ❌ 否 | high |
| TASK-1.1.4 | TASK-1.1.1 | ❌ 否 | high |
| TASK-1.1.5 | TASK-1.1.1, TASK-1.1.2 | ❌ 否 | high |
| TASK-2.1 | TASK-1.1.2 | ❌ 否 | high |
| TASK-2.2 | TASK-1.1.2 | ❌ 否 | high |
| TASK-2.3 | TASK-2.1, TASK-2.2 | ❌ 否 | high |
| TASK-3.1 | TASK-2.2 | ❌ 否 | high |
| TASK-3.2 | TASK-2.2 | ❌ 否 | high |
| TASK-3.3 | TASK-2.2 | ❌ 否 | high |
| TASK-3.4 | TASK-2.2 | ❌ 否 | high |
| TASK-3.5 | TASK-2.2 | ❌ 否 | high |
| TASK-4.1 | TASK-2.2 | ❌ 否 | high |
| TASK-4.2 | TASK-2.2 | ❌ 否 | medium |
| TASK-4.3 | TASK-2.2 | ❌ 否 | medium |
| TASK-4.4 | TASK-2.2 | ❌ 否 | medium |
| TASK-4.5 | TASK-3.3, TASK-4.1 | ❌ 否 | medium |
| TASK-4.6 | TASK-2.2 | ❌ 否 | medium |
| TASK-5.1 | TASK-3.1, TASK-4.1 | ❌ 否 | high |
| TASK-5.2 | TASK-5.1 | ❌ 否 | medium |
| TASK-5.3 | TASK-5.1 | ❌ 否 | medium |
| TASK-5.4 | TASK-5.1 | ❌ 否 | medium |
| TASK-5.5 | TASK-5.1 | ❌ 否 | low |
| TASK-6.1 | TASK-5.1 | ✅ 是 | low |
| TASK-6.2 | TASK-5.1 | ✅ 是 | low |
| TASK-6.3 | TASK-5.1 | ❌ 否 | low |
| TASK-6.4 | TASK-5.1 | ✅ 是 | low |
| TASK-6.5 | TASK-5.1 | ✅ 是 | low |
| TASK-6.6 | TASK-5.1 | ✅ 是 | low |

---

## 🔄 任务调度器

```python
def schedule_tasks():
    """调度任务（不跳过异常任务）"""
    while not all_completed():
        ready_tasks = []
        
        # 1. 找出所有可执行任务
        for task_id in TASKS.keys():
            can_run, reason = can_execute_task(task_id)
            if can_run:
                ready_tasks.append(task_id)
        
        # 2. 如果没有可执行任务，检查是否全部完成或阻塞
        if not ready_tasks:
            # 检查是否有阻塞任务
            blocked_tasks = get_blocked_tasks()
            if blocked_tasks:
                logger.error(f"以下任务被阻塞，无法继续：{blocked_tasks}")
                
                # 生成阻塞报告
                generate_blocked_report(blocked_tasks)
                
                return False  # 停止调度
            
            # 全部完成
            logger.info("所有任务已完成")
            return True
        
        # 3. 按优先级排序
        priority_order = {'high': 0, 'medium': 1, 'low': 2}
        ready_tasks.sort(key=lambda t: priority_order[TASKS[t]['priority']])
        
        # 4. 最多并行 3 个任务
        for task in ready_tasks[:3]:
            execute_task(task)
        
        # 5. 等待一段时间再检查
        time.sleep(60)  # 每分钟检查一次
```

---

## 📊 状态报告

### 任务状态报告

```python
def generate_task_status_report():
    """生成任务状态报告"""
    report = {
        'total_tasks': len(TASKS),
        'completed': len(get_completed_tasks()),
        'running': len(get_running_tasks()),
        'blocked': len(get_blocked_tasks()),
        'pending': len(get_pending_tasks()),
    }
    
    return report
```

### 阻塞任务报告

```python
def generate_blocked_report(blocked_tasks):
    """生成阻塞任务报告"""
    report = "阻塞任务报告\n"
    report += "=" * 50 + "\n\n"
    
    for task_id in blocked_tasks:
        state = task_states.get(task_id, {})
        report += f"任务：{task_id}\n"
        report += f"  状态：{state.get('status', 'unknown')}\n"
        report += f"  阻塞原因：{state.get('blocked_by', 'unknown')}\n"
        report += f"  重试次数：{state.get('retry_count', 0)}\n"
        report += f"  最后错误：{state.get('last_error', '无')}\n"
        report += "\n"
    
    # 发送报告
    notify_user("任务阻塞报告", report)
```

---

## 🎯 诊断工具

```python
def diagnose_task(task_id):
    """诊断任务"""
    state = task_states.get(task_id, {})
    
    print(f"任务 {task_id} 诊断报告：")
    print(f"  状态：{state.get('status', 'unknown')}")
    print(f"  重试次数：{state.get('retry_count', 0)}")
    print(f"  最后错误：{state.get('last_error', '无')}")
    
    # 显示依赖任务
    deps = TASK_DEPENDENCIES.get(task_id, [])
    print(f"  依赖任务：{deps}")
    
    # 显示被阻塞的任务
    dependents = get_dependents(task_id)
    if dependents:
        print(f"  被阻塞的任务：{dependents}")
    
    # 显示执行历史
    attempts = state.get('attempts', [])
    if attempts:
        print(f"  执行历史：")
        for i, attempt in enumerate(attempts, 1):
            print(f"    尝试 {i}：")
            print(f"      开始：{attempt.get('start', 'unknown')}")
            print(f"      结束：{attempt.get('end', 'unknown')}")
            print(f"      状态：{attempt.get('status', 'unknown')}")
```

---

## ✅ 方案优势

### 1. 明确的失败处理
- ✅ 重试 3 次后明确失败
- ✅ 不无限重试
- ✅ 清晰的状态转换

### 2. 依赖完整性
- ✅ 确保依赖任务完整性
- ✅ 不会因跳过任务导致数据不一致
- ✅ 清晰的阻塞关系

### 3. 状态追踪
- ✅ 完整的执行历史
- ✅ 支持诊断和分析
- ✅ 清晰的失败原因

### 4. 用户通知
- ✅ 及时通知任务失败
- ✅ 清晰的阻塞关系
- ✅ 明确的下一步建议

---

## 🔧 实施步骤

### 第一阶段：依赖分析（优先级：P0）

1. **定义任务依赖关系**
   - 创建 `TASK_DEPENDENCIES` 字典
   - 定义所有任务的依赖关系

2. **实现依赖检查逻辑**
   - 实现 `get_dependents()` 函数
   - 实现 `can_skip_task()` 函数
   - 实现 `can_execute_task()` 函数

3. **实现阻塞机制**
   - 实现 `mark_as_blocked()` 函数
   - 阻塞依赖任务
   - 更新任务状态

### 第二阶段：重试机制（优先级：P0）

1. **定义重试策略**
   - 设置 `MAX_RETRIES = 3`
   - 定义 `RETRY_DELAYS = [60, 300, 600]`

2. **实现重试逻辑**
   - 实现 `get_retry_count()` 函数
   - 实现 `schedule_retry()` 函数
   - 实现延迟调度

3. **实现状态追踪**
   - 记录每次尝试
   - 记录错误信息
   - 记录执行时间

### 第三阶段：异常处理集成（优先级：P0）

1. **实现 `handle_timeout_task()`**
   - 检查重试次数
   - 安排重试或标记阻塞
   - 通知用户

2. **集成到任务调度器**
   - 在超时时调用处理函数
   - 更新调度逻辑

3. **实现报告生成**
   - `generate_task_status_report()`
   - `generate_blocked_report()`

### 第四阶段：诊断工具（优先级：P1）

1. **实现任务诊断**
   - `diagnate_task()` 函数
   - 显示完整任务信息

2. **实现任务恢复**
   - 检查恢复条件
   - 安排重新执行

---

## 📊 方案对比

| 特性 | 方案 A | 方案 B | 方案 C |
|------|--------|--------|--------|
| 重试策略 | 3 次有限重试 | 无限重试 | 智能分析 |
| 依赖分析 | ✅ 是 | ✅ 是 | ✅ 是 |
| 状态追踪 | ✅ 是 | ✅ 是 | ✅ 是 |
| 实现复杂度 | ⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐ |
| 可靠性 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| 用户体验 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |

---

## ✅ 总结

**方案 A（依赖分析 + 重试机制 + 状态追踪）**是最佳选择：

**核心优势：**
1. ✅ 简单可靠，易于实现
2. ✅ 明确的失败处理
3. ✅ 不会无限重试
4. ✅ 确保任务完整性
5. ✅ 清晰的状态追踪

**实施建议：**
1. 第一阶段：依赖分析
2. 第二阶段：重试机制
3. 第三阶段：异常处理集成
4. 第四阶段：诊断工具

**预期效果：**
- ⚡️ 异常任务自动处理
- ⚡️ 不会影响其他任务
- ⚡️ 清晰的状态报告
- ⚡️ 支持诊断和恢复

---

*异常任务处理方案 A - 依赖分析 + 重试机制 + 状态追踪*