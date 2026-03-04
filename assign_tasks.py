"""
给 AI Agent 团队分配任务

不做新功能的前提下，8 大类任务
"""

from team import DynamicTaskScheduler
import time


def main():
    """分配任务给团队"""
    print("=" * 60)
    print("🎯 给 AI Agent 团队分配任务")
    print("=" * 60)
    
    # 创建调度器
    scheduler = DynamicTaskScheduler()
    
    # 定义所有任务
    all_tasks = [
        # ========== 1. 文档优化 ==========
        {
            "id": "DOC-1",
            "title": "完善 README.md",
            "description": """完善 README.md，包括：
- 清晰的安装说明（pip install ai-pdf-agent）
- 详细的使用示例（读取、转换功能）
- 常见问题解答（FAQ）
- 支持的 PDF 特性说明
- 依赖版本要求""",
            "priority": 0,
            "dependencies": [],
            "timeout": 3600
        },
        {
            "id": "DOC-2",
            "title": "编写 EXAMPLES.md",
            "description": """编写 EXAMPLES.md，包含：
- 基础示例：读取 PDF 文本、表格、图片
- 进阶示例：批量处理、自定义插件
- 转换示例：PDF to Markdown/HTML/JSON
- 错误处理示例：异常捕获、重试机制
- 性能优化示例：缓存、并行处理""",
            "priority": 1,
            "dependencies": ["DOC-1"],
            "timeout": 3600
        },
        {
            "id": "DOC-3",
            "title": "添加性能基准测试文档",
            "description": """创建 PERFORMANCE.md，包含：
- 各功能模块性能基准数据
- 不同 PDF 文件大小的处理时间
- 内存使用情况
- 性能优化建议
- 与其他库的性能对比""",
            "priority": 2,
            "dependencies": [],
            "timeout": 3600
        },
        {
            "id": "DOC-4",
            "title": "创建故障排除指南",
            "description": """创建 TROUBLESHOOTING.md，包含：
- 常见错误及解决方案
- 依赖安装问题
- 权限问题
- 编码问题
- 大文件处理问题""",
            "priority": 1,
            "dependencies": [],
            "timeout": 3600
        },
        
        # ========== 2. 测试增强 ==========
        {
            "id": "TEST-1",
            "title": "增加边界条件测试",
            "description": """增加边界条件测试：
- 空文件测试
- 大文件测试（>100MB）
- 损坏的 PDF 文件测试
- 密码保护的 PDF 测试
- 特殊字符和编码测试
- 极端参数值测试""",
            "priority": 0,
            "dependencies": [],
            "timeout": 3600
        },
        {
            "id": "TEST-2",
            "title": "添加更多真实 PDF 文件测试",
            "description": """添加真实 PDF 文件测试：
- 从测试数据目录读取不同类型的 PDF
- 技术文档、论文、图书
- 包含复杂表格的 PDF
- 包含大量图片的 PDF
- 混合内容的 PDF
- 验证提取结果的准确性""",
            "priority": 1,
            "dependencies": [],
            "timeout": 3600
        },
        {
            "id": "TEST-3",
            "title": "性能测试回归检查",
            "description": """实现性能测试回归检查：
- 记录性能基准数据
- 每次运行性能测试并与基准对比
- 性能下降超过 10% 时报警
- 生成性能趋势报告
- 集成到 CI/CD 流程""",
            "priority": 2,
            "dependencies": [],
            "timeout": 3600
        },
        {
            "id": "TEST-4",
            "title": "集成测试覆盖更多场景",
            "description": """扩展集成测试覆盖：
- 端到端测试（读取 -> 转换 -> 输出）
- 多格式转换测试
- 插件系统集成测试
- CLI 命令测试
- 错误恢复测试
- 并发处理测试""",
            "priority": 1,
            "dependencies": [],
            "timeout": 3600
        },
        
        # ========== 3. 代码质量 ==========
        {
            "id": "QUAL-1",
            "title": "运行代码检查工具",
            "description": """配置并运行代码检查工具：
- pylint：代码质量检查
- black：代码格式化
- isort：import 排序
- mypy：类型检查（可选）
- 配置 pre-commit hooks
- 添加 .github/workflows/lint.yml""",
            "priority": 0,
            "dependencies": [],
            "timeout": 3600
        },
        {
            "id": "QUAL-2",
            "title": "添加类型注解",
            "description": """为核心模块添加类型注解：
- 添加 typing import
- 函数参数和返回值类型注解
- 类属性类型注解
- 使用 mypy 检查
- 修复类型错误""",
            "priority": 2,
            "dependencies": [],
            "timeout": 3600
        },
        {
            "id": "QUAL-3",
            "title": "重构复杂函数",
            "description": """重构复杂函数：
- 识别复杂度 > 10 的函数
- 拆分为更小的函数
- 提取重复逻辑
- 提高代码可读性
- 保持功能不变""",
            "priority": 2,
            "dependencies": [],
            "timeout": 3600
        },
        {
            "id": "QUAL-4",
            "title": "减少代码重复",
            "description": """减少代码重复：
- 识别重复代码块
- 提取公共函数/类
- 创建工具模块
- 统一错误处理逻辑
- 统一日志格式""",
            "priority": 1,
            "dependencies": [],
            "timeout": 3600
        },
        
        # ========== 4. 性能优化 ==========
        {
            "id": "PERF-1",
            "title": "缓存机制优化",
            "description": """优化缓存机制：
- 实现文件内容缓存
- 添加缓存失效策略
- 支持自定义缓存大小
- 缓存命中率统计
- 添加缓存调试信息""",
            "priority": 1,
            "dependencies": [],
            "timeout": 3600
        },
        {
            "id": "PERF-2",
            "title": "内存使用优化",
            "description": """优化内存使用：
- 使用生成器替代列表
- 及时释放大对象
- 使用内存分析工具
- 优化数据结构
- 减少内存复制""",
            "priority": 2,
            "dependencies": [],
            "timeout": 3600
        },
        {
            "id": "PERF-3",
            "title": "大文件处理优化",
            "description": """优化大文件处理：
- 流式读取大文件
- 分页处理机制
- 进度显示
- 内存占用控制
- 支持断点续传""",
            "priority": 1,
            "dependencies": [],
            "timeout": 3600
        },
        {
            "id": "PERF-4",
            "title": "并行处理优化",
            "description": """优化并行处理：
- 使用 concurrent.futures
- 任务队列管理
- 线程池大小配置
- 避免全局锁竞争
- 并行度自适应""",
            "priority": 2,
            "dependencies": [],
            "timeout": 3600
        },
        
        # ========== 5. 错误处理 ==========
        {
            "id": "ERR-1",
            "title": "更友好的错误提示",
            "description": """改进错误提示：
- 自定义异常类
- 错误码分类
- 友好的错误消息
- 建议解决方案
- 多语言支持（可选）""",
            "priority": 1,
            "dependencies": [],
            "timeout": 3600
        },
        {
            "id": "ERR-2",
            "title": "添加更多异常捕获",
            "description": """添加更全面的异常捕获：
- 文件操作异常
- 网络请求异常
- JSON 解析异常
- PDF 解析异常
- 插件加载异常""",
            "priority": 1,
            "dependencies": [],
            "timeout": 3600
        },
        {
            "id": "ERR-3",
            "title": "错误日志改进",
            "description": """改进错误日志：
- 结构化日志格式（JSON）
- 日志级别配置
- 错误堆栈记录
- 上下文信息记录
- 日志文件轮转""",
            "priority": 1,
            "dependencies": [],
            "timeout": 3600
        },
        {
            "id": "ERR-4",
            "title": "用户引导改进",
            "description": """改进用户引导：
- 详细的错误说明
- 快速修复建议
- 相关文档链接
- 命令行自动补全
- 交互式帮助""",
            "priority": 2,
            "dependencies": [],
            "timeout": 3600
        },
        
        # ========== 6. 依赖管理 ==========
        {
            "id": "DEP-1",
            "title": "更新依赖包到最新版本",
            "description": """更新依赖包：
- 运行 pip list --outdated
- 测试新版本兼容性
- 更新 requirements.txt
- 更新 pyproject.toml
- 更新锁文件""",
            "priority": 2,
            "dependencies": [],
            "timeout": 3600
        },
        {
            "id": "DEP-2",
            "title": "移除未使用的依赖",
            "description": """移除未使用的依赖：
- 使用 pipdeptree 分析依赖
- 移除冗余依赖
- 优化依赖树
- 减少安装包大小
- 更新文档""",
            "priority": 2,
            "dependencies": [],
            "timeout": 3600
        },
        {
            "id": "DEP-3",
            "title": "添加开发依赖",
            "description": """添加开发依赖：
- pytest（测试）
- black（格式化）
- pylint（检查）
- mypy（类型检查）
- pre-commit（git hooks）
- 添加到 [tool.poetry.dev-dependencies]""",
            "priority": 1,
            "dependencies": [],
            "timeout": 3600
        },
        {
            "id": "DEP-4",
            "title": "锁定依赖版本",
            "description": """锁定依赖版本：
- 使用 poetry.lock
- 使用 requirements.lock
- 记录 Python 版本
- 记录操作系统版本
- 添加兼容性说明""",
            "priority": 1,
            "dependencies": [],
            "timeout": 3600
        },
        
        # ========== 7. CI/CD 完善 ==========
        {
            "id": "CICD-1",
            "title": "添加更多测试矩阵",
            "description": """添加测试矩阵：
- 不同 Python 版本（3.10, 3.11, 3.12）
- 不同操作系统（Ubuntu, macOS, Windows）
- 使用 GitHub Actions matrix
- 并行运行测试
- 收集测试结果""",
            "priority": 2,
            "dependencies": [],
            "timeout": 3600
        },
        {
            "id": "CICD-2",
            "title": "自动化部署流程",
            "description": """实现自动化部署：
- 版本号自动生成（语义化版本）
- 构建 wheel 包
- 发布到 PyPI
- 生成 GitHub Release
- 自动更新 CHANGELOG""",
            "priority": 2,
            "dependencies": [],
            "timeout": 3600
        },
        {
            "id": "CICD-3",
            "title": "版本发布自动化",
            "description": """版本发布自动化：
- 使用 semantic-release
- 自动更新版本号
- 自动生成 Release Notes
- 自动打 tag
- 自动推送 PyPI""",
            "priority": 3,
            "dependencies": [],
            "timeout": 3600
        },
        {
            "id": "CICD-4",
            "title": "代码覆盖率报告",
            "description": """代码覆盖率报告：
- 使用 pytest-cov
- 生成 HTML 报告
- 上传到 Codecov
- 设置覆盖率阈值
- PR 时检查覆盖率变化""",
            "priority": 1,
            "dependencies": [],
            "timeout": 3600
        },
        
        # ========== 8. 清理工作 ==========
        {
            "id": "CLEAN-1",
            "title": "删除临时脚本文件",
            "description": """删除临时脚本文件：
- add_test_tasks.py
- create_task_queue_cron.py
- create_task_queue_cron_v2.py
- create_zhang_cron.py
- cto_init_team.py
- cto_simple.py
- init_team.py
- recover_team.py
- update_task_001.py
- zhang_architect_optimized.py
- test_results.md
- FINAL_ARCHITECTURE.md
- PROBLEM_EXPLANATION.md
- TEAMTEAM_STATUS.json
- TEAM_ARCHITECTURE.md
- TEAM_CONFIG.json
- TEAM_LOG.md
- TEAM_STATUS.json
- USAGE.md
- task_queue.py
- team_config.py
- prompts/ 目录""",
            "priority": 0,
            "dependencies": [],
            "timeout": 1800
        },
        {
            "id": "CLEAN-2",
            "title": "整理项目结构",
            "description": """整理项目结构：
- 规范化目录命名
- 移动文档到 docs/ 目录
- 移动示例到 examples/ 目录
- 移动测试到 tests/ 目录
- 添加 .gitignore
- 添加 .dockerignore""",
            "priority": 1,
            "dependencies": ["CLEAN-1"],
            "timeout": 3600
        }
    ]
    
    print(f"\n📋 总共 {len(all_tasks)} 个任务")
    print("=" * 60)
    
    # 添加任务到调度器
    scheduler.update_tasks(all_tasks)
    
    # 查看执行计划
    print("\n📋 执行计划:")
    groups = scheduler.plan_execution()
    print(f"共 {len(groups)} 个任务组")
    for i, group in enumerate(groups):
        print(f"\n组 {i + 1}/{len(groups)} ({len(group)} 个任务):")
        for task in group:
            print(f"  - {task['id']}: {task['title']}")
    
    print("\n" + "=" * 60)
    
    # 询问是否开始执行
    print("\n🚀 任务已准备就绪！")
    print("💡 提示：使用 scheduler.execute() 开始执行任务")
    print("💡 提示：每 30 分钟会自动汇报进度")
    print("💡 提示：可以在执行过程中动态添加/修改/删除任务")
    print("=" * 60)
    
    return scheduler


if __name__ == "__main__":
    scheduler = main()
    
    # 可以在这里立即执行，或者返回调度器供后续使用
    # scheduler.execute()
