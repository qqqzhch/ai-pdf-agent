"""
进一步测试和优化方案
"""

from team import DynamicTaskScheduler


def get_optimization_tasks():
    """获取优化任务"""
    return [
        {
            "id": "OPT-1",
            "title": "修复测试收集错误",
            "description": """修复 5 个测试文件的收集错误：
- tests/test_plugin_system_integration.py (3 个测试类)
- tests/converters/test_csv_converter.py
- tests/converters/test_epub_converter.py
- tests/converters/test_html_converter.py
- tests/converters/test_image_converter.py
- tests/converters/test_json_converter.py

解决方法：
1. 重命名测试类（避免 pytest 收集）
2. 使用 pytest.mark 跳过测试类
3. 将测试类移到 fixtures 模块""",
            "priority": 0,
            "dependencies": [],
            "timeout": 3600
        },
        {
            "id": "OPT-2",
            "title": "格式化团队管理代码",
            "description": """使用 Black 格式化 team/ 目录：
- team/__init__.py
- team/agent_pool.py
- team/heartbeat.py
- team/task_scheduler.py

命令：black team/""",
            "priority": 0,
            "dependencies": [],
            "timeout": 600
        },
        {
            "id": "OPT-3",
            "title": "安装开发依赖",
            "description": """安装开发依赖：
- pylint（代码质量检查）
- black（代码格式化）
- isort（import 排序）
- pytest-cov（代码覆盖率）
- mypy（类型检查）

命令：pip install pylint black isort pytest-cov mypy""",
            "priority": 1,
            "dependencies": [],
            "timeout": 600
        },
        {
            "id": "OPT-4",
            "title": "运行完整测试套件",
            "description": """运行完整测试套件并验证：
1. 修复收集错误后运行测试
2. 记录测试结果
3. 分析失败用例
4. 生成测试报告
5. 计算代码覆盖率

命令：pytest tests/ -v --cov=plugins --cov-report=html""",
            "priority": 2,
            "dependencies": ["OPT-1"],
            "timeout": 1800
        },
        {
            "id": "OPT-5",
            "title": "运行代码质量检查",
            "description": """运行代码质量检查：
1. pylint 检查（plugins/, team/）
2. mypy 类型检查
3. 修复发现的问题
4. 配置 pylint 和 mypy 规则

命令：
- pylint plugins/ team/ --errors-only
- mypy plugins/ team/""",
            "priority": 2,
            "dependencies": ["OPT-3"],
            "timeout": 3600
        },
        {
            "id": "OPT-6",
            "title": "性能基准测试",
            "description": """运行性能基准测试：
1. 测试不同大小 PDF 的处理时间
2. 测试内存使用
3. 对比优化前后性能
4. 生成性能报告
5. 识别性能瓶颈""",
            "priority": 3,
            "dependencies": ["OPT-4"],
            "timeout": 3600
        },
        {
            "id": "OPT-7",
            "title": "优化慢速测试",
            "description": """优化慢速测试：
1. 识别耗时 > 1 秒的测试
2. 分析慢速原因
3. 优化测试实现
4. 添加性能断言
5. 使用 pytest.mark.slow 标记慢速测试""",
            "priority": 3,
            "dependencies": ["OPT-4"],
            "timeout": 3600
        },
        {
            "id": "OPT-8",
            "title": "添加集成测试快照",
            "description": """添加集成测试快照：
1. 为关键功能添加快照测试
2. 使用 pytest-snapshot 插件
3. 确保输出一致性
4. 支持快照更新机制
5. 在 CI 中验证快照""",
            "priority": 2,
            "dependencies": ["OPT-4"],
            "timeout": 3600
        },
        {
            "id": "OPT-9",
            "title": "配置 pre-commit hooks",
            "description": """配置 pre-commit hooks：
1. 安装 pre-commit
2. 创建 .pre-commit-config.yaml
3. 配置 black、isort、pylint hooks
4. 配置 pytest hook
5. 安装并测试 hooks""",
            "priority": 1,
            "dependencies": ["OPT-2", "OPT-3"],
            "timeout": 1800
        },
        {
            "id": "OPT-10",
            "title": "清理临时文件",
            "description": """清理临时文件：
1. 删除 team/ 目录（测试用）
2. 删除 test_team.py
3. 删除 assign_tasks.py
4. 删除 start_team.py
5. 清理 .pytest_cache""",
            "priority": 4,
            "dependencies": ["OPT-5"],
            "timeout": 300
        }
    ]


def main():
    """启动优化任务"""
    print("=" * 60)
    print("🔧 进一步测试和优化")
    print("=" * 60)
    
    # 创建调度器
    scheduler = DynamicTaskScheduler()
    
    # 加载优化任务
    tasks = get_optimization_tasks()
    print(f"\n📋 加载 {len(tasks)} 个优化任务...")
    scheduler.update_tasks(tasks)
    
    # 查看执行计划
    print("\n📋 执行计划:")
    groups = scheduler.plan_execution()
    print(f"共 {len(groups)} 个任务组")
    for i, group in enumerate(groups):
        print(f"\n组 {i + 1}/{len(groups)} ({len(group)} 个任务):")
        for task in group:
            print(f"  - {task['id']}: {task['title']}")
    
    print("\n" + "=" * 60)
    print("🚀 优化任务已准备就绪！")
    print("💡 提示：使用 scheduler.execute() 开始执行")
    print("=" * 60)
    
    return scheduler


if __name__ == "__main__":
    scheduler = main()
    
    # 立即执行
    print("\n🚀 开始执行优化任务...")
    print("=" * 60)
    
    try:
        scheduler.execute()
        
        print("\n" + "=" * 60)
        print("✅ 所有优化任务完成！")
        print("=" * 60)
        
    except KeyboardInterrupt:
        print("\n\n⚠️ 任务执行被中断")
    except Exception as e:
        print(f"\n\n❌ 执行出错：{e}")
        import traceback
        traceback.print_exc()
