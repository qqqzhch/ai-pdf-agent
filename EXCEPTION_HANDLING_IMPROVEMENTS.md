# 异常任务处理 - 改进建议

## 问题分析

### 当前策略（⚠️ 不安全）

```python
# 当前代码逻辑
if task_time > 25_minutes and no_completion_message:
    # 跳过任务，继续其他任务
    skip_task()
```

**⚠️ 潜在风险：**
1. **依赖任务可能失败** - 如果跳过的任务是其他任务的前置条件
2. **数据不一致** - 跳过的任务可能生成必要的文件
3. **测试覆盖不完整** - 跳跳过的测试任务可能导致质量下降
4. **文档缺失** - 跳过的文档任务可能导致用户困惑

---

## ✅ 改进方案

### 方案 1：依赖分析（推荐）

**策略：**
1. 分析任务依赖关系
2. 只跳过无依赖的独立任务
3. 依赖跳过任务的任务也标记为待处理

**实现：**
```python
# 任务依赖定义
TASK_DEPENDENCIES = {
    'TASK-1.1.1': [],  # 无依赖
    'TASK-2.1': ['TASK-1.1.2'],
    'TASK-3.1': ['TASK-2.2'],
    'TASK-4.1': ['TASK-2.2'],
    'TASK-4.5': ['TASK-3.3', 'TASK-4.1'],  # 需要图片读取插件和 Markdown 插件
    'TASK-5.1': ['TASK-3.1', 'TASK-4.1'],
    'TASK-6.3': ['TASK-5.1'],  # 需要 CLI 框架完成
}

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

def handle_timeout_task(task_id):
    """处理超时任务"""
    if can_skip_task(task_id):
        logger.warning(f"跳过任务 {task_id}（无依赖）")
        skip_task(task_id)
    else:
        logger.error(f"任务 {task_id} 有依赖，必须等待完成")
        # 等待或标记为阻塞
        mark_as_blocked(task_id)
```

---

### 方案 2：重试机制

**策略：**
1. 超时任务自动重试 3 次
2. 每次重试增加时间间隔
3. 全部失败后才标记为异常

**实现：**
```python
# 伪代码
MAX_RETRIES = 3
RETRY_DELAYS = [60, 300, 600]  # 1 分钟、5 分钟、10 分钟

def handle_timeout_task(task_id):
    """处理超时任务"""
    retry_count = get_retry_count(task_id)
    
    if retry_count < MAX_RETRIES:
        delay = RETRY_DELAYS[retry_count]
        logger.warning(f"任务 {task_id} 超时，{delay} 秒后重试（第 {retry_count + 1} 次）")
        schedule_retry(task_id, delay)
    else:
        logger.error(f"任务 {task_id} 重试 {MAX_RETRIES} 次均失败，标记为异常")
        mark_as_failed(task_id)
        # 检查依赖任务
        check_dependents(task_id)
```

---

### 方案 3：任务优先级队列（最灵活）

**策略：**
1. 每个任务有优先级和依赖列表
2. 自动调度，优先执行高优先级且无依赖的任务
3. 异常任务根据优先级决定处理方式

**实现：**
```python
# 任务定义
TASKS = {
    'TASK-1.1.1': {
        'priority': 'high',
        'dependencies': [],
        'retries': 3,
    },
    'TASK-4.5': {
        'priority': 'medium',
        'dependencies': ['TASK-3.3', 'TASK-4.1'],
        'retries': 3,
    },
    'TASK-6.3': {
        'priority': 'low',
        'dependencies': ['TASK-5.1'],
        'retries': 3,
    },
}

def get_ready_tasks():
    """获取可执行任务"""
    ready = []
    for task_id, config in TASKS.items():
        # 1. 检查是否已完成
        if is_completed(task_id):
            continue
        
        # 2. 检查是否运行中
        if is_running(task_id):
            continue
        
        # 3. 检查依赖是否完成
        deps = config['dependencies']
        if all(is_completed(dep) for dep in deps):
            ready.append(task_id)
    
    return ready

def schedule_tasks():
    """调度任务"""
    while not all_completed():
        # 1. 找出所有可执行任务
        ready_tasks = get_ready_tasks()
        
        # 2. 按优先级排序
        priority_order = {'high': 0, 'medium': 1, 'low': 2}
        ready_tasks.sort(key=lambda t: priority_order[TASKS[t]['priority']])
        
        # 3. 最多并行 3 个任务
        for task in
```

---

### 方案 4：任务状态追踪和恢复

**策略：**
1. 每个任务记录执行历史
2. 支持手动恢复任务
3. 提供任务诊断工具

**实现：**
```python
# 任务历史
task_history = {
    'TASK-6.3': {
        'attempts': [
            {'start': '2026-03-03 19:30', 'end': '2026-03-03 20:55', 'status': 'timeout'},
            {'start': '2026-03-03 20:56', 'end': None, 'status': 'running'},
        ],
        'last_error': '执行超时',
        'can_skip': False,
        'dependents': ['TASK-6.4', 'TASK-6.5'],
    },
}

def diagnose_task(task_id):
    """诊断任务"""
    history = task_history[task_id]
    
    print(f"任务 {task_id} 诊断报告：")
    print(f"  尝试次数：{len(history['attempts'])}")
    print(f"  最后状态：{history['attempts'][-1]['status']}")
    print(f"  错误信息：{history['last_error']}")
    print(f"  是否可跳过：{history['can_skip']}")
    print(f"  依赖任务：{history['dependents']}")

def resume_task(task_id):
    """恢复任务"""
    history = task_history[task_id]
    
    # 检查是否可以恢复
    if history['attempts'][-1]['status'] == 'running':
        print(f"任务 {task_id} 正在运行中")
        return False
    
    # 检查依赖是否完成
    if not all(is_completed(dep) for dep in history['dependents']):
        print(f"任务 {task_id} 依赖任务未完成")
        return False
    
    # 恢复任务
    execute_task(task_id)
    return True
```

---

## ✅ 推荐实现：混合方案

**结合方案 1 + 方案 2 + 方案 4**

**策略：**
1. **依赖分析** - 确保跳过的任务不影响其他任务
2. **重试机制** - 超时任务重试 3 次
3. **状态追踪** - 记录完整历史，支持诊断
4. **自动恢复** - 如果条件满足，自动恢复跳过的任务

**实现逻辑：**
```python
def handle_timeout_task(task_id):
    """处理超时任务（完整版）"""
    retry_count = get_retry_count(task_id)
    
    # 1. 重试机制
    if retry_count < 3:
        logger.warning(f"任务 {task_id} 重试中（第 {retry_count + 1}/3 次）")
        schedule_retry(task_id)
        return
    
    # 2. 重试次数用完，检查是否可跳过
    if can_skip_task(task_id):
        # 检查依赖任务
        dependents = get_dependents(task_id)
        
        if dependents:
            logger.error(f"任务 {task_id} 有依赖任务，不能跳过：{dependents}")
            mark_as_blocked(task_id)
        else:
            logger.warning(f"任务 {task_id} 标记为跳过（无依赖）")
            mark_as_skipped(task_id)
    else:
        logger.error(f"任务 {task_id} 不能跳过，必须完成")
        mark_as_blocked(task_id)

def check_auto_resume():
    """检查是否可以自动恢复任务"""
    for blocked_task in get_blocked_tasks():
        # 1. 检查依赖是否完成
        deps = TASK_DEPENDENCIES.get(blocked_task, [])
        if all(is_completed(dep) for dep in deps):
            logger.info(f"任务 {blocked_task} 依赖已满足，自动恢复")
            resume_task(blocked_task)
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

## 💡 下一步建议

### 短期优化

1. **实现依赖分析系统**
   - 定义任务依赖关系
   - 实现依赖检查逻辑
   - 防止跳过有依赖的任务

2. **添加重试机制**
   - 每个任务最多重试 3 次
   - 自动调度重试
   - 记录重试历史

3. **任务状态追踪**
   - 记录完整执行历史
   - 支持诊断和恢复
   - 提供任务日志

### 长期优化

4. **任务优先级调度**
   - 根据优先级自动调度
   - 最大化资源利用
   - 支持优先级调整

5. **自动恢复机制**
   - 如果条件满足，自动恢复跳过的任务
   - 避免手动干预
   - 支持批量恢复

6. **任务诊断工具**
   - 分析失败原因
   - 提供修复建议
   - 生成诊断报告

---

## ✅ 总结

**当前策略：** ⚠️ 简单跳过
- 优点：简单、快速
- 缺点：可能影响其他任务

**推荐策略：** ✅ 依赖分析 + 重试机制
- 优点：安全、可靠、可恢复
- 缺点：实现复杂

**关键建议：**
1. ✅ 定义任务依赖关系
2. ✅ 实现依赖检查逻辑
3. ✅ 添加重试机制
4. ✅ 记录任务历史

---

## 🔧 实施步骤

### 第一阶段：依赖分析
1. 定义 `TASK_DEPENDENCIES` 字典
2. 实现 `get_dependents()` 函数
3. 实现 `can_skip_task()` 函数
4. 更新 `handle_timeout_task()` 逻辑

### 第二阶段：重试机制
1. 定义 `MAX_RETRIES = 3`
2. 定义 `RETRY_DELAYS = [60, 300, 600]`
3. 实现 `get_retry_count()` 函数
4. 实现 `schedule_retry()` 函数

### 第三阶段：状态追踪
1. 创建 `task_history` 字典
2. 实现 `diagnose_task()` 函数
3. 实现 `resume_task()` 函数
4. 添加任务日志记录

---

**感谢你的反馈！异常任务处理确实需要更安全的机制。** 🙏✨
