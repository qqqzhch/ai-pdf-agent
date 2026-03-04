#!/usr/bin/env python3
"""
AI PDF Agent 团队 - 自动恢复脚本

OpenClaw 重启后自动恢复：
1. 检查配置文件是否存在
2. 如果不存在，提示初始化
3. 如果存在，提示恢复会话
"""

import json
import os
from datetime import datetime

# ============================================================================
# 文件路径
# ============================================================================

TEAM_CONFIG_PATH = "/root/.openclaw/workspace/ai-pdf-agent/TEAM_CONFIG.json"
TEAM_STATUS_PATH = "/root/.openclaw/workspace/ai-pdf-agent/TEAM_STATUS.json"
TEAM_LOG_PATH = "/root/.openclaw/workspace/ai-pdf-agent/TEAM_LOG.md"

# ============================================================================
# 检查函数
# ============================================================================

def check_config_files():
    """检查配置文件"""
    print("\n" + "="*70)
    print("🔍 检查 AI PDF Agent 团队配置文件")
    print("="*70)
    
    files = {
        "TEAM_CONFIG.json": TEAM_CONFIG_PATH,
        "TEAM_STATUS.json": TEAM_STATUS_PATH,
        "TEAM_LOG.md": TEAM_LOG_PATH
    }
    
    all_exist = True
    for name, path in files.items():
        if os.path.exists(path):
            size = os.path.getsize(path)
            print(f"✅ {name} ({size} 字节)")
        else:
            print(f"❌ {name} (不存在）")
            all_exist = False
    
    return all_exist

def load_team_status():
    """加载团队状态"""
    print("\n" + "="*70)
    print("📋 加载团队状态")
    print("="*70)
    
    try:
        with open(TEAM_STATUS_PATH, 'r', encoding='utf-8') as f:
            status = json.load(f)
        
        # 显示状态
        print(f"最后更新：{status.get('last_updated', 'N/A')}")
        print(f"当前项目：{status.get('current_project', '无')}")
        print(f"已完成项目：{status.get('projects_completed', 0)}")
        print(f"任务数量：{len(status.get('tasks', []))}")
        print(f"Agent 数量：{len(status.get('agents', {}))}")
        
        return status
    except Exception as e:
        print(f"❌ 加载团队状态失败：{str(e)}")
        return None

def check_agent_sessions(status):
    """检查 Agent 会话状态"""
    print("\n" + "="*70)
    print("🤝 检查 Agent 会话状态")
    print("="*70)
    
    if not status:
        return False
    
    agents = status.get('agents', {})
    active_count = 0
    idle_count = 0
    
    for agent_name, agent_info in agents.items():
        agent_status = agent_info.get('status', 'unknown')
        current_task = agent_info.get('current_task', None)
        
        if agent_status == 'idle':
            idle_count += 1
            print(f"   {agent_name}: {agent_status} (待命）")
        elif agent_status == 'working':
            active_count += 1
            print(f"   {agent_name}: {agent_status} (任务：{current_task})")
        else:
            print(f"   {agent_name}: {agent_status}")
    
    print(f"\n活跃：{active_count}, 空闲：{idle_count}")
    return active_count == 0 and idle_count == len(agents)

# ============================================================================
# 主执行
# ============================================================================

def main():
    print("\n" + "="*70)
    print("🚀 AI PDF Agent 团队 - 自动恢复检查")
    print("="*70)
    
    # 1. 检查配置文件
    config_exists = check_config_files()
    
    if not config_exists:
        print("\n" + "="*70)
        print("⚠️ 配置文件不完整")
        print("="*70)
        print("\n需要先运行团队初始化：")
        print("  python3 init_team.py")
        return
    
    # 2. 加载团队状态
    status = load_team_status()
    
    if not status:
        print("\n❌ 无法加载团队状态")
        return
    
    # 3. 检查 Agent 会话
    all_idle = check_agent_sessions(status)
    
    print("\n" + "="*70)
    print("📋 恢复建议")
    print("="*70)
    
    if all_idle:
        print("\n✅ 配置文件完整")
        print("✅ 所有 Agent 都在空闲状态")
        print("\n建议操作：")
        print("1. 重新创建所有 Agent 会话")
        print("   运行：python3 init_team.py")
        print("\n2. 创建张架构的 Cron 任务")
        print("   运行：python3 create_zhang_cron.py")
        print("\n3. 交给 CTO 项目任务")
        print("   告诉我（CTO）：'实现新功能'")
    else:
        print("\n✅ 配置文件完整")
        print("✅ Agent 会话活跃")
        print("\n团队运行正常，无需恢复")
    
    print("\n" + "="*70)

if __name__ == "__main__":
    main()
