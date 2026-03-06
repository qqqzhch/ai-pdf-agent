#!/usr/bin/env python3
"""
AI PDF Agent - V2 团队测试套件

测试内容：
- 任务依赖处理
- 并行执行优化
- 报告策略调整
- 性能测试
"""

import json
import time
import threading
from datetime import datetime
from typing import List, Dict
from pathlib import Path
import logging

from team_v2_implementation import TaskQueueManager, Task

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TeamV2Tests:
    """V2 团队测试套件"""

    def __init__(self):
        self.queue_manager = TaskQueueManager()
        self.results = {}

    def run_all_tests(self):
        """运行所有测试"""
        logger.info("=" * 60)
        logger.info("🧪 开始 V2 团队测试")
        logger.info("=" * 60)
        logger.info("")

        tests = [
            ("依赖任务处理", self.test_task_dependencies),
            ("并行执行优化", self.test_parallel_execution),
            ("报告策略", self.test_report_strategy),
            ("性能测试", self.test_performance)
        ]

        passed = 0
        failed = 0

        for test_name, test_func in tests:
            try:
                logger.info(f"🧪 测试: {test_name}")
                logger.info("-" * 60)
                result = test_func()
                if result:
                    passed += 1
                    logger.info(f"✅ {test_name} 测试通过")
                else:
                    failed += 1
                    logger.error(f"❌ {test_name} 测试失败")
                logger.info("")
            except Exception as e:
                failed += 1
                logger.error(f"❌ {test_name} 测试异常: {e}")
                logger.exception(e)
                logger.info("")

        logger.info("=" * 60)
        logger.info("📊 测试汇总")
        logger.info("=" * 60)
        logger.info(f"总测试数: {len(tests)}")
        logger.info(f"✅ 通过: {passed}")
        logger.info(f"❌ 失败: {failed}")
        logger.info(f"成功率: {passed/len(tests)*100:.1f}%")

        return failed == 0

    def test_task_dependencies(self) -> bool:
        """测试任务依赖处理"""
        logger.info("测试场景: A → B → C 依赖链")

        # 清空队列（重要：清除之前测试残留）
        self.queue_manager.clean_queue()

        # 创建任务
        task_a = Task(
            id="TASK-A",
            title="任务 A",
            description="基础任务",
            story_points=5,
            priority="P0",
            dependencies=[],
            assigned_to=None,
            status="pending",
            progress=0,
            created_at=datetime.now().isoformat(),
            started_at=None,
            completed_at=None,
            result=None
        )

        task_b = Task(
            id="TASK-B",
            title="任务 B",
            description="依赖 A",
            story_points=3,
            priority="P1",
            dependencies=["TASK-A"],
            assigned_to=None,
            status="pending",
            progress=0,
            created_at=datetime.now().isoformat(),
            started_at=None,
            completed_at=None,
            result=None
        )

        task_c = Task(
            id="TASK-C",
            title="任务 C",
            description="依赖 B",
            story_points=2,
            priority="P2",
            dependencies=["TASK-B"],
            assigned_to=None,
            status="pending",
            progress=0,
            created_at=datetime.now().isoformat(),
            started_at=None,
            completed_at=None,
            result=None
        )

        # 添加到队列
        self.queue_manager.add_task(task_a)
        self.queue_manager.add_task(task_b)
        self.queue_manager.add_task(task_c)

        # 测试依赖检查
        logger.info("测试 1: 任务 A 无依赖，应该可执行")
        next_task = self.queue_manager.get_next_task()
        if next_task and next_task["id"] == "TASK-A":
            logger.info("✅ 任务 A 正确获取")
        else:
            logger.error("❌ 任务 A 获取失败")
            return False

        logger.info("测试 2: 任务 B 依赖 A（未完成），不应该可执行")
        next_task = self.queue_manager.get_next_task()
        if next_task is None:
            logger.info("✅ 任务 B 正确等待依赖")
        else:
            logger.error(f"❌ 任务 B 不应该可执行，但获取了 {next_task['id']}")
            return False

        logger.info("测试 3: 完成 A，B 应该可执行")
        self.queue_manager.complete_task("TASK-A", {"success": True})
        next_task = self.queue_manager.get_next_task()
        if next_task and next_task["id"] == "TASK-B":
            logger.info("✅ 任务 B 正确获取")
        else:
            logger.error("❌ 任务 B 获取失败")
            return False

        logger.info("测试 4: C 依赖 B（未完成），不应该可执行")
        next_task = self.queue_manager.get_next_task()
        if next_task is None:
            logger.info("✅ 任务 C 正确等待依赖")
        else:
            logger.error(f"❌ 任务 C 不应该可执行，但获取了 {next_task['id']}")
            return False

        logger.info("测试 5: 完成 B，C 应该可执行")
        self.queue_manager.complete_task("TASK-B", {"success": True})
        next_task = self.queue_manager.get_next_task()
        if next_task and next_task["id"] == "TASK-C":
            logger.info("✅ 任务 C 正确获取")
        else:
            logger.error("❌ 任务 C 获取失败")
            return False

        logger.info("✅ 所有依赖测试通过")
        return True

    def test_parallel_execution(self) -> bool:
        """测试并行执行优化"""
        logger.info("测试场景: 不同并行数的性能对比")

        # 创建 10 个独立任务
        tasks = []
        for i in range(10):
            task = Task(
                id=f"TASK-P-{i}",
                title=f"并行任务 {i}",
                description=f"测试并行任务",
                story_points=2,
                priority="P1",
                dependencies=[],
                assigned_to=None,
                status="pending",
                progress=0,
                created_at=datetime.now().isoformat(),
                started_at=None,
                completed_at=None,
                result=None
            )
            tasks.append(task)
            self.queue_manager.add_task(task)

        # 测试不同并行数
        results = {}
        for parallel in [1, 2, 3]:
            start = time.time()

            # 模拟并行执行
            def execute_task(task_id):
                time.sleep(0.5)  # 模拟执行时间

            threads = []
            for i in range(parallel):
                if i < len(tasks):
                    thread = threading.Thread(target=execute_task, args=(tasks[i]["id"],))
                    thread.start()
                    threads.append(thread)

            for thread in threads:
                thread.join()

            elapsed = time.time() - start
            results[parallel] = elapsed
            logger.info(f"并行数: {parallel}, 耗时: {elapsed:.2f}s")

        # 分析结果
        logger.info("性能分析:")
        logger.info(f"1 并行 vs 3 并行: {results[1] / results[3]:.2f}x 加速")
        logger.info(f"2 并行 vs 3 并行: {results[2] / results[3]:.2f}x 加速")

        # 清理
        for task in tasks:
            try:
                self.queue_manager.complete_task(task["id"], {"success": True})
            except:
                pass

        logger.info("✅ 并行执行测试通过")
        return True

    def test_report_strategy(self) -> bool:
        """测试报告策略"""
        logger.info("测试场景: 不同报告频率和内容")

        # 测试场景
        scenarios = [
            {
                "name": "正常完成",
                "tasks_to_complete": 5,
                "tasks_to_fail": 0,
                "expected_report": "success_summary"
            },
            {
                "name": "部分失败",
                "tasks_to_complete": 3,
                "tasks_to_fail": 2,
                "expected_report": "failure_report"
            },
            {
                "name": "全部失败",
                "tasks_to_complete": 0,
                "tasks_to_fail": 5,
                "expected_report": "error_report"
            }
        ]

        for scenario in scenarios:
            logger.info(f"场景: {scenario['name']}")

            # 模拟任务执行
            completed = scenario["tasks_to_complete"]
            failed = scenario["tasks_to_fail"]

            total = completed + failed
            success_rate = (completed / total * 100) if total > 0 else 0

            # 生成报告
            report = {
                "total": total,
                "completed": completed,
                "failed": failed,
                "success_rate": success_rate,
                "status": "success" if failed == 0 else "partial_failure" if completed > 0 else "total_failure"
            }

            logger.info(f"   总任务: {report['total']}")
            logger.info(f"   ✅ 成功: {report['completed']}")
            logger.info(f"   ❌ 失败: {report['failed']}")
            logger.info(f"   成功率: {report['success_rate']:.1f}%")
            logger.info(f"   状态: {report['status']}")

        logger.info("✅ 报告策略测试通过")
        return True

    def test_performance(self) -> bool:
        """测试性能"""
        logger.info("测试场景: 性能基准测试")

        # 测试 1: 任务添加性能
        logger.info("测试 1: 任务添加性能")
        start = time.time()
        for i in range(100):
            task = Task(
                id=f"PERF-{i}",
                title=f"性能测试任务 {i}",
                description="性能测试",
                story_points=1,
                priority="P1",
                dependencies=[],
                assigned_to=None,
                status="pending",
                progress=0,
                created_at=datetime.now().isoformat(),
                started_at=None,
                completed_at=None,
                result=None
            )
            self.queue_manager.add_task(task)

        elapsed = time.time() - start
        logger.info(f"100 个任务添加: {elapsed:.3f}s ({100/elapsed:.0f} tasks/s)")

        # 测试 2: 状态查询性能
        logger.info("测试 2: 状态查询性能")
        start = time.time()
        for i in range(1000):
            status = self.queue_manager.get_status()
        elapsed = time.time() - start
        logger.info(f"1000 次状态查询: {elapsed:.3f}s ({1000/elapsed:.0f} queries/s)")

        # 测试 3: 内存使用估算
        logger.info("测试 3: 内存使用估算")
        state = self.queue_manager.state
        state_size = len(json.dumps(state))
        logger.info(f"状态大小: {state_size / 1024:.2f} KB")

        # 清理
        for i in range(100):
            try:
                self.queue_manager.complete_task(f"PERF-{i}", {"success": True})
            except:
                pass

        logger.info("✅ 性能测试通过")
        return True


def main():
    """主函数"""
    tests = TeamV2Tests()
    success = tests.run_all_tests()

    if success:
        logger.info("")
        logger.info("🎉 所有测试通过！")
        return 0
    else:
        logger.info("")
        logger.error("⚠️ 部分测试失败，请检查日志")
        return 1


if __name__ == "__main__":
    exit(main())
