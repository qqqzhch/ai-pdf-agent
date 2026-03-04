"""
测试：团队管理系统

演示动态任务更新和执行
"""

import json
import time
from team import DynamicTaskScheduler


def main():
    """测试团队管理系统"""
    print("=" * 60)
    print("AI Agent 团队管理系统 - Version 2.0")
    print("=" * 60)
    
    # 创建调度器
    scheduler = DynamicTaskScheduler()
    
    # 初始任务
    print("\n📋 添加初始任务...")
    initial_tasks = [
        {
            "id": "TASK-1",
            "title": "完善 README.md",
            "description": "完善安装说明、使用示例、FAQ",
            "priority": 1,
            "dependencies": []
        },
        {
            "id": "TASK-2",
            "title": "添加边界条件测试",
            "description": "增加边界条件测试用例",
            "priority": 2,
            "dependencies": []
        },
        {
            "id": "TASK-3",
            "title": "运行代码检查工具",
            "description": "运行 pylint、black、isort",
            "priority": 1,
            "dependencies": []
        }
    ]
    
    scheduler.update_tasks(initial_tasks)
    
    # 查看执行计划
    print("\n" + "=" * 60)
    
    # 执行任务
    print("\n🚀 开始执行任务...")
    scheduler.execute()
    
    # 查看最终状态
    print("\n" + "=" * 60)
    print("📊 最终状态:")
    print(json.dumps(scheduler.state, indent=2, ensure_ascii=False))
    
    # 测试动态更新
    print("\n" + "=" * 60)
    print("🔄 测试动态任务更新...")
    
    # 添加新任务
    print("\n➕ 添加新任务...")
    new_task = {
        "id": "TASK-4",
        "title": "优化性能",
        "description": "缓存大文件处理优化",
        "priority": 0,
        "dependencies": []
    }
    
    scheduler.update_tasks(initial_tasks + [new_task])
    
    # 修改优先级
    print("\n✏️ 修改任务优先级...")
    updated_tasks = [t for t in initial_tasks if t["id"] != "TASK-2"]
    updated_tasks.append({
        "id": "TASK-2",
        "title": "添加边界条件测试",
        "description": "增加边界条件测试用例",
        "priority": 0,  # 提升优先级
        "dependencies": []
    })
    
    scheduler.update_tasks(updated_tasks + [new_task])
    
    # 删除任务
    print("\n🗑️ 删除任务...")
    remaining_tasks = [t for t in updated_tasks if t["id"] != "TASK-3"]
    scheduler.update_tasks(remaining_tasks + [new_task])
    
    print("\n✅ 动态更新测试完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()
