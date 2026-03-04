"""
AI PDF Agent 团队 - CTO 团队初始化脚本

作为 CTO（首席技术官），一次性创建所有团队成员 Agent
"""

import json
import sys
import os

# ============================================================================
# 导入配置和提示词
# ============================================================================

# 添加项目路径到 Python 路径
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

try:
    from prompts.team_prompts import (
        ZHANG_ARCHITECT_PROMPT,
        LI_DEVELOPER_PROMPT,
        ZHAO_FULLSTACK_PROMPT,
        WANG_TESTER_PROMPT,
        CHEN_DOCS_PROMPT,
        LIU_OPS_PROMPT
    )
except ImportError:
    # 如果导入失败，使用内联提示词
    print("⚠️ 无法导入提示词，将使用简化提示词")
    ZHANG_ARCHITECT_PROMPT = "你是张架构 - 技术架构负责人"
    LI_DEVELOPER_PROMPT = "你是李开发 - 后端核心开发工程师"
    ZHAO_FULLSTACK_PROMPT = "你是赵栈 - 全栈开发工程师"
    WANG_TESTER_PROMPT = "你是王测试 - 测试工程师"
    CHEN_DOCS_PROMPT = "你是陈文档 - 文档工程师"
    LIU_OPS_PROMPT = "你是刘运维 - DevOps 工程师"

try:
    from team_config import TEAM_CONFIG, TEAM_STATUS, save_team_config, save_team_status
except ImportError:
    print("⚠️ 无法导入团队配置，将创建默认配置")
    TEAM_CONFIG = {"members": {}}
    TEAM_STATUS = {"agents": {}}

# ============================================================================
# 创建团队成员 Agent
# ============================================================================

def create_all_team_agents():
    """
    创建所有团队成员 Agent
    
    返回：{
        '张架构': session_key,
        '李开发': session_key,
        ...
    }
    """
    print("\n🚀 开始创建 AI PDF Agent 团队成员...\n")
    
    session_keys = {}
    
    # 1. 创建张架构（技术架构负责人）
    print("👤 创建张架构（技术架构负责人）...")
    try:
        from openclaw import sessions_spawn
        
        zhang_session = sessions_spawn(
            task=ZHANG_ARCHITECT_PROMPT,
            label="张架构-技术架构负责人",
            agentId="main",
            timeout=3600,  # 1 小时
            cleanup="keep"  # 保留会话
        )
        
        session_keys['张架构'] = zhang_session
        print(f"   ✅ 张架构已创建，会话：{zhang_session}")
    except Exception as e:
        print(f"   ❌ 创建张架构失败：{str(e)}")
        session_keys['张架构'] = None
    
    # 2. 创建李开发（后端核心开发）
    print("\n👨 创建李开发（后端核心开发工程师）...")
    try:
        li_session = sessions_spawn(
            task=LI_DEVELOPER_PROMPT,
            label="李开发-后端核心开发",
            agentId="main",
            timeout=7200,  # 2 小时
            cleanup="keep"
        )
        
        session_keys['李开发'] = li_session
        print(f"   ✅ 李开发已创建，会话：{li_session}")
    except Exception as e:
        print(f"   ❌ 创建李开发失败：{str(e)}")
        session_keys['李开发'] = None
    
    # 3. 创建赵栈（全栈开发）
    print("\n👨 创建赵栈（全栈开发工程师）...")
    try:
        zhao_session = sessions_spawn(
            task=ZHAO_FULLSTACK_PROMPT,
            label="赵栈-全栈开发",
            agentId="main",
            timeout=7200,
            cleanup="keep"
        )
        
        session_keys['赵栈'] = zhao_session
        print(f"   ✅ 赵栈已创建，会话：{zhao_session}")
    except Exception as e:
        print(f"   ❌ 创建赵栈失败：{str(e)}")
        session_keys['赵栈'] = None
    
    # 4. 创建王测试（测试工程师）
    print("\n🧪 创建王测试（测试工程师）...")
    try:
        wang_session = sessions_spawn(
            task=WANG_TESTER_PROMPT,
            label="王测试-测试工程师",
            agentId="main",
            timeout=7200,
            cleanup="keep"
        )
        
        session_keys['王测试'] = wang_session
        print(f"   ✅ 王测试已创建，会话：{wang_session}")
    except Exception as e:
        print(f"   ❌ 创建王测试失败：{str(e)}")
        session_keys['王测试'] = None
    
    # 5. 创建陈文档（文档工程师）
    print("\n📝 创建陈文档（文档工程师）...")
    try:
        chen_session = sessions_spawn(
            task=CHEN_DOCS_PROMPT,
            label="陈文档-文档工程师",
            agentId="main",
            timeout=7200,
            cleanup="keep"
        )
        
        session_keys['陈文档'] = chen_session
        print(f"   ✅ 陈文档已创建，会话：{chen_session}")
    except Exception as e:
        print(f"   ❌ 创建陈文档失败：{str(e)}")
        session_keys['陈文档'] = None
    
    # 6. 创建刘运维（DevOps 工程师）
    print("\n🔧 创建刘运维（DevOps 工程师）...")
    try:
        liu_session = sessions_spawn(
            task=LIU_OPS_PROMPT,
            label="刘运维-DevOps工程师",
            agentId="main",
            timeout=7200,
            cleanup="keep"
        )
        
        session_keys['刘运维'] = liu_session
        print(f"   ✅ 刘运维已创建，会话：{liu_session}")
    except Exception as e:
        print(f"   ❌ 创建刘运维失败：{str(e)}")
        session_keys['刘运维'] = None
    
    return session_keys

# ============================================================================
# 更新团队配置
# ============================================================================

def update_team_config(session_keys):
    """
    更新团队配置，填充 session_key
    """
    print("\n📋 更新团队配置...\n")
    
    try:
        # 读取现有配置
        team_config_path = "/root/.openclaw/workspace/ai-pdf-agent/TEAM_CONFIG.json"
        with open(team_config_path, 'r', encoding='utf-8') as f:
            team_config = json.load(f)
        
        # 更新每个成员的 session_key
        for member_name in team_config['members']:
            if member_name in session_keys:
                team_config['members'][member_name]['session_key'] = session_keys[member_name]
                team_config['members'][member_name]['status'] = 'idle'
                team_config['members'][member_name]['created_at'] = json.dumps({
                    'session_key': session_keys[member_name]
                }, ensure_ascii=False)
                
                print(f"   ✅ {member_name}：{session_keys[member_name]}")
        
        # 保存更新后的配置
        with open(team_config_path, 'w', encoding='utf-8') as f:
            json.dump(team_config, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ 团队配置已更新：{team_config_path}")
        return team_config
    except Exception as e:
        print(f"❌ 更新团队配置失败：{str(e)}")
        return {}

# ============================================================================
# 主执行
# ============================================================================

def main():
    """
    CTO 的主执行函数
    """
    print("\n" + "="*70)
    print("🎉 AI PDF Agent 团队初始化")
    print("   CTO：首席技术官")
    print("="*70)
    
    # 1. 创建所有团队成员 Agent
    session_keys = create_all_team_agents()
    
    # 2. 更新团队配置
    team_config = update_team_config(session_keys)
    
    # 3. 总结
    print("\n" + "="*70)
    print("📊 团队创建总结")
    print("="*70)
    print(f"   团队名称：{team_config.get('team_name', 'AI PDF Agent')}")
    print(f"   CTO：{team_config.get('cto', 'CTO（首席技术官）')}")
    print(f"   团队领导：{team_config.get('leader', '张架构')}")
    print(f"   团队成员：{len(session_keys)} 人")
    print("\n   成员列表：")
    
    success_count = 0
    for member_name, session_key in session_keys.items():
        status = "✅" if session_key else "❌"
        print(f"     {status} {member_name}")
        if session_key:
            success_count += 1
    
    print(f"\n   成功：{success_count}/{len(session_keys)}")
    print("="*70 + "\n")
    
    if success_count == len(session_keys):
        print("🎉 AI PDF Agent 团队初始化成功！")
        print("\n下一步：")
        print("1. 交给 CTO（我）项目任务")
        print("2. CTO 分析任务并分配给张架构")
        print("3. 张架构自动协调整个成员")
        print("\n注意：")
        print("- 所有 Agent 都会长期存在（cleanup='keep'）")
        print("- 张架构会通过 cron 每 5 分钟自动检查进度")
        print("- 只在异常或卡住时汇报")
    else:
        print(f"⚠️ 部分成员创建失败（{len(session_keys) - success_count} 个）")
        print("请检查错误并重新初始化")

if __name__ == '__main__':
    main()
