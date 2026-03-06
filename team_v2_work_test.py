#!/usr/bin/env python3
"""
AI PDF Agent - V2 团队工作成果测试

测试目标：
1. 测试 V2 团队的任务处理能力
2. 测试任务拆分和估算
3. 测试团队自动执行
4. 生成工作成果报告
"""

import json
import time
from datetime import datetime
from pathlib import Path
import logging

from team_coordinator import TeamCoordinator
from team_v2_implementation import TaskQueueManager

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TeamV2WorkTest:
    """V2 团队工作测试"""

    def __init__(self):
        self.queue_manager = TaskQueueManager()
        self.coordinator = TeamCoordinator(self.queue_manager)

    def run_work_test(self):
        """运行工作成果测试"""
        logger.info("=" * 60)
        logger.info("🧪 V2 团队工作成果测试")
        logger.info("=" * 60)
        logger.info("")

        # 清空队列
        self.queue_manager.clean_queue()

        # 测试任务列表
        test_tasks = [
            "添加一个 PDF 转 Word 功能",
            "优化 PDF 读取性能",
            "编写单元测试",
            "更新文档",
            "添加 CLI 命令"
        ]

        results = []

        for i, task in enumerate(test_tasks, 1):
            logger.info(f"📋 任务 {i}/{len(test_tasks)}: {task}")
            logger.info("-" * 60)

            try:
                # 执行任务
                summary = self.coordinator.receive_user_request(task)

                # 记录结果
                result = {
                    "task": task,
                    "success": True,
                    "summary": summary
                }
                results.append(result)

                logger.info(f"✅ 任务 {i} 完成")
                logger.info("")

            except Exception as e:
                logger.error(f"❌ 任务 {i} 失败: {e}")
                result = {
                    "task": task,
                    "success": False,
                    "error": str(e)
                }
                results.append(result)
                logger.info("")

        # 生成汇总报告
        self._generate_summary_report(results)

        return results

    def _generate_summary_report(self, results):
        """生成汇总报告"""
        logger.info("=" * 60)
        logger.info("📊 工作成果汇总")
        logger.info("=" * 60)
        logger.info("")

        total = len(results)
        success = sum(1 for r in results if r["success"])
        failed = total - success

        logger.info(f"总任务数: {total}")
        logger.info(f"✅ 成功: {success}")
        logger.info(f"❌ 失败: {failed}")
        logger.info(f"成功率: {success/total*100:.1f}%")
        logger.info("")

        logger.info("详细结果:")
        for i, result in enumerate(results, 1):
            if result["success"]:
                logger.info(f"{i}. ✅ {result['task']}")
            else:
                logger.info(f"{i}. ❌ {result['task']} - {result['error']}")

        logger.info("")
        logger.info("=" * 60)
        logger.info("🎉 测试完成")
        logger.info("=" * 60)


def main():
    """主函数"""
    logger.info("🚀 启动 V2 团队工作测试...")

    test = TeamV2WorkTest()
    results = test.run_work_test()

    # 保存结果
    output_path = Path("/root/.openclaw/workspace/ai-pdf-agent/team_v2_work_test_results.json")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    logger.info(f"✅ 结果已保存到: {output_path}")

    return 0 if all(r["success"] for r in results) else 1


if __name__ == "__main__":
    exit(main())
