"""
启动 AI Agent 团队任务执行
"""

from team import DynamicTaskScheduler


def get_all_tasks():
    """获取所有任务"""
    return [
        # ========== 1. 文档优化 ==========
        {
            "id": "DOC-1",
            "title": "完善 README.md",
            "description": "完善 README.md，包括安装说明、使用示例、FAQ",
            "priority": 0,
            "dependencies": [],
            "timeout": 3600
        },
        {
            "id": "DOC-2",
            "title": "编写 EXAMPLES.md",
            "description": "编写 EXAMPLES.md，包含各种使用示例",
            "priority": 1,
            "dependencies": ["DOC-1"],
            "timeout": 3600
        },
        {
            "id": "DOC-3",
            "title": "添加性能基准测试文档",
            "description": "创建 PERFORMANCE.md",
            "priority": 2,
            "dependencies": [],
            "timeout": 3600
        },
        {
            "id": "DOC-4",
            "title": "创建故障排除指南",
            "description": "创建 TROUBLESHOOTING.md",
            "priority": 1,
            "dependencies": [],
            "timeout": 3600
        },
        
        # ========== 2. 测试增强 ==========
        {
            "id": "TEST-1",
            "title": "增加边界条件测试",
            "description": "增加边界条件测试",
            "priority": 0,
            "dependencies": [],
            "timeout": 3600
        },
        {
            "id": "TEST-2",
            "title": "添加更多真实 PDF 文件测试",
            "description": "添加真实 PDF 文件测试",
            "priority": 1,
            "dependencies": [],
            "timeout": 3600
        },
        {
            "id": "TEST-3",
            "title": "性能测试回归检查",
            "description": "实现性能测试回归检查",
            "priority": 2,
            "dependencies": [],
            "timeout": 3600
        },
        {
            "id": "TEST-4",
            "title": "集成测试覆盖更多场景",
            "description": "扩展集成测试覆盖",
            "priority": 1,
            "dependencies": [],
            "timeout": 3600
        },
        
        # ========== 3. 代码质量 ==========
        {
            "id": "QUAL-1",
            "title": "运行代码检查工具",
            "description": "配置并运行代码检查工具（pylint、black、isort）",
            "priority": 0,
            "dependencies": [],
            "timeout": 3600
        },
        {
            "id": "QUAL-2",
            "title": "添加类型注解",
            "description": "为核心模块添加类型注解",
            "priority": 2,
            "dependencies": [],
            "timeout": 3600
        },
        {
            "id": "QUAL-3",
            "title": "重构复杂函数",
            "description": "重构复杂函数",
            "priority": 2,
            "dependencies": [],
            "timeout": 3600
        },
        {
            "id": "QUAL-4",
            "title": "减少代码重复",
            "description": "减少代码重复",
            "priority": 1,
            "dependencies": [],
            "timeout": 3600
        },
        
        # ========== 4. 性能优化 ==========
        {
            "id": "PERF-1",
            "title": "缓存机制优化",
            "description": "优化缓存机制",
            "priority": 1,
            "dependencies": [],
            "timeout": 3600
        },
        {
            "id": "PERF-2",
            "title": "内存使用优化",
            "description": "优化内存使用",
            "priority": 2,
            "dependencies": [],
            "timeout": 3600
        },
        {
            "id": "PERF-3",
            "title": "大文件处理优化",
            "description": "优化大文件处理",
            "priority": 1,
            "dependencies": [],
            "timeout": 3600
        },
        {
            "id": "PERF-4",
            "title": "并行处理优化",
            "description": "优化并行处理",
            "priority": 2,
            "dependencies": [],
            "timeout": 3600
        },
        
        # ========== 5. 错误处理 ==========
        {
            "id": "ERR-1",
            "title": "更友好的错误提示",
            "description": "改进错误提示",
            "priority": 1,
            "dependencies": [],
            "timeout": 3600
        },
        {
            "id": "ERR-2",
            "title": "添加更多异常捕获",
            "description": "添加更全面的异常捕获",
            "priority": 1,
            "dependencies": [],
            "timeout": 3600
        },
        {
            "id": "ERR-3",
            "title": "错误日志改进",
            "description": "改进错误日志",
            "priority": 1,
            "dependencies": [],
            "timeout": 3600
        },
        {
            "id": "ERR-4",
            "title": "用户引导改进",
            "description": "改进用户引导",
            "priority": 2,
            "dependencies": [],
            "timeout": 3600
        },
        
        # ========== 6. 依赖管理 ==========
        {
            "id": "DEP-1",
            "title": "更新依赖包到最新版本",
            "description": "更新依赖包",
            "priority": 2,
            "dependencies": [],
            "timeout": 3600
        },
        {
            "id": "DEP-2",
            "title": "移除未使用的依赖",
            "description": "移除未使用的依赖",
            "priority": 2,
            "dependencies": [],
            "timeout": 3600
        },
        {
            "id": "DEP-3",
            "title": "添加开发依赖",
            "description": "添加开发依赖",
            "priority": 1,
            "dependencies": [],
            "timeout": 3600
        },
        {
            "id": "DEP-4",
            "title": "锁定依赖版本",
            "description": "锁定依赖版本",
            "priority": 1,
            "dependencies": [],
            "timeout": 3600
        },
        
        # ========== 7. CI/CD 完善 ==========
        {
            "id": "CICD-1",
            "title": "添加更多测试矩阵",
            "description": "添加测试矩阵",
            "priority": 2,
            "dependencies": [],
            "timeout": 3600
        },
        {
            "id": "CICD-2",
            "title": "自动化部署流程",
            "description": "实现自动化部署",
            "priority": 2,
            "dependencies": [],
            "timeout": 3600
        },
        {
            "id": "CICD-3",
            "title": "版本发布自动化",
            "description": "版本发布自动化",
            "priority": 3,
            "dependencies": [],
            "timeout": 3600
        },
        {
            "id": "CICD-4",
            "title": "代码覆盖率报告",
            "description": "代码覆盖率报告",
            "priority": 1,
            "dependencies": [],
            "timeout": 3600
        },
        
        # ========== 8. 清理工作 ==========
        {
            "id": "CLEAN-1",
            "title": "删除临时脚本文件",
            "description": "删除临时脚本文件",
            "priority": 0,
            "dependencies": [],
            "timeout": 1800
        },
        {
            "id": "CLEAN-2",
            "title": "整理项目结构",
            "description": "整理项目结构",
            "priority": 1,
            "dependencies": ["CLEAN-1"],
            "timeout": 3600
        }
    ]


def main():
    """启动团队任务执行"""
    print("=" * 60)
    print("🚀 启动 AI Agent 团队任务执行")
    print("=" * 60)
    
    # 创建调度器
    scheduler = DynamicTaskScheduler()
    
    # 加载所有任务
    all_tasks = get_all_tasks()
    print(f"\n📋 加载 {len(all_tasks)} 个任务...")
    scheduler.update_tasks(all_tasks)
    
    # 开始执行
    print("\n🚀 开始执行任务...")
    print("=" * 60)
    
    try:
        scheduler.execute()
        
        print("\n" + "=" * 60)
        print("✅ 所有任务执行完成！")
        print("=" * 60)
        
    except KeyboardInterrupt:
        print("\n\n⚠️ 任务执行被中断")
        print("💡 提示：任务状态已保存，可以继续执行")
        
    except Exception as e:
        print(f"\n\n❌ 执行出错：{e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
