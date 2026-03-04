"""
AI PDF Agent 团队 - 团队配置

定义团队结构和成员信息
"""

import json
from datetime import datetime

# ============================================================================
# 团队配置
# ============================================================================

TEAM_CONFIG = {
    "team_name": "AI PDF Agent fanc",
    "cto": "CTO（首席技术官）",
    "leader": "张架构",
    "created_at": datetime.now().isoformat(),
    "members": {
        "张架构": {
            "name": "张架构",
            "role": "技术架构负责人",
            "skills": {
                "架构设计": "高级",
                "技术选型": "高级",
                "任务分配": "高级",
                "进度监控": "高级",
                "代码审查": "高级"
            },
            "responsibilities": [
                "系统架构设计",
                "技术方案制定",
                "任务分配协调",
                "跨团队协作",
                "代码审查和技术评审",
                "进度监控和汇报"
            ],
            "session_key": None,  # 创建后填充
            "status": "idle",
            "created_at": None
        },
        "李开发": {
            "name": "李开发",
            "role": "后端核心开发工程师",
            "skills": {
                "Python": "高级",
                "PyMuPDF": "高级",
                "pytest": "高级",
                "REST_API": "中级",
                "数据结构": "高级"
            },
            "responsibilities": [
                "核心功能开发",
                "PDF 处理引擎开发",
                "插件系统实现",
                "单元测试编写",
                "Bug 修复",
                "代码优化"
            ],
            "session_key": None,
            "status": "idle",
            "created_at": None
        },
        "赵栈": {
            "name": "赵栈",
            "role": "全栈开发工程师",
            "skills": {
                "Python": "高级",
                "Click": "高级",
                "argparse": "高级",
                "CLI设计": "高级",
                "Web开发": "中级"
            },
            "responsibilities": [
                "CLI 命令开发",
                "用户界面开发",
                "集成前后端",
                "集成测试",
                "Bug 修复",
                "性能优化"
            ],
            "session_key": None,
            "status": "idle",
            "created_at": None
        },
        "王测试": {
            "name": "王测试",
            "role": "测试工程师",
            "skills": {
                "pytest": "高级",
                "单元测试": "高级",
                "集成测试": "高级",
                "性能测试": "中级",
                "自动化测试": "中级"
            },
            "responsibilities": [
                "测试框架开发",
                "单元测试编写",
                "集成测试编写",
                "测试套件运行",
                "测试报告生成",
                "质量保证"
            ],
            "session_key": None,
            "status": "idle",
            "created_at": None
        },
        "陈文档": {
            "name": "陈文档",
            "role": "文档工程师",
            "skills": {
                "Markdown": "高级",
                "reStructuredText": "中级",
                "Jekyll": "中级",
                "技术写作": "高级",
                "文档管理": "高级"
            },
            "responsibilities": [
                "README 维护",
                "API 文档编写",
                "用户手册编写",
                "开发指南编写",
                "更新日志维护",
                "文档站点管理"
            ],
            "session_key": None,
            "status": "idle",
            "created_at": None
        },
        "刘运维": {
            "name": "刘运维",
            "role": "DevOps 工程师",
            "skills": {
                "GitHub_Actions": "高级",
                "Docker": "中级",
                "Kubernetes": "初级",
                "CI_CD": "高级",
                "监控": "中级"
            },
            "responsibilities": [
                "CI/CD 配置",
                "环境搭建",
                "应用部署",
                "系统监控",
                "日志管理",
                "故障处理"
            ],
            "session_key": None,
            "status": "idle",
            "created_at": None
        }
    },
    "workflows": {
        "development": {
            "sequence": ["李开发", "王测试", "陈文档"],
            "description": "后端开发工作流"
        },
        "fullstack": {
            "sequence": ["李开发", "赵栈", "王测试", "陈文档"],
            "description": "全栈开发工作流"
        },
        "deployment": {
            "sequence": ["刘运维"],
            "description": "部署工作流"
        }
    }
}

# ============================================================================
# 初始化团队状态
# ============================================================================

TEAM_STATUS = {
    "last_updated": datetime.now().isoformat(),
    "current_project": None,
    "projects_completed": 0,
    "tasks": [],
    "agents": {}
}

# 初始化所有 Agent 的状态
for member_name in TEAM_CONFIG["members"]:
    TEAM_STATUS["agents"][member_name] = {
        "status": "idle",  # idle, working, error
        "current_task": None,
        "tasks_completed": 0,
        "tasks_failed": 0,
        "total_duration_ms": 0,
        "last_active": None
    }

# ============================================================================
# 保存配置和状态
# ============================================================================

def save_team_config():
    """保存团队配置到文件"""
    with open("/root/.openclaw/workspace/ai-pdf-agent/TEAM_CONFIG.json", "w", encoding="utf-8") as f:
        json.dump(TEAM_CONFIG, f, indent=2, ensure_ascii=False)
    print("✅ TEAM_CONFIG.json 已保存")

def save_team_status():
    """保存团队状态到文件"""
    with open("/root/.openclaw/workspace/ai-pdf-agent/TEAM_STATUS.json", "w", encoding="utf-8") as f:
        json.dump(TEAM_STATUS, f, indent=2, ensure_ascii=False)
    print("✅ TEAM_STATUS.json 已保存")

def init_team_log():
    """初始化团队日志"""
    with open("/root/.openclaw/workspace/ai-pdf-agent/TEAM_LOG.md", "w", encoding="utf-8") as f:
        f.write("# AI PDF Agent 团队日志\n\n")
        f.write(f"**团队创建时间：** {TEAM_CONFIG['created_at']}\n\n")
        f.write(f"**CTO：** {TEAM_CONFIG['cto']}\n\n")
        f.write(f"**团队领导：** {TEAM_CONFIG['leader']}\n\n")
        f.write("---\n\n")
        f.write("## 团队成员\n\n")
        
        for member_name, member_info in TEAM_CONFIG["members"].items():
            f.write(f"### {member_name}\n\n")
            f.write(f"- **角色：** {member_info['role']}\n")
            f.write(f"- **职责：** {', '.join(member_info['responsibilities'])}\n")
            f.write(f"- **技能：** {', '.join(member_info['skills'].keys())}\n\n")
    
    print("✅ TEAM_LOG.md 已初始化")

# ============================================================================
# 主执行
# ============================================================================

if __name__ == "__main__":
    # 保存配置
    save_team_config()
    
    # 保存状态
    save_team_status()
    
    # 初始化日志
    init_team_log()
    
    print("\n🎉 AI PDF Agent 团队配置已初始化！")
    print(f"   团队名称：{TEAM_CONFIG['team_name']}")
    print(f"   CTO：{TEAM_CONFIG['cto']}")
    print(f"   团队领导：{TEAM_CONFIG['leader']}")
    print(f"   团队成员：{len(TEAM_CONFIG['members'])} 人")
