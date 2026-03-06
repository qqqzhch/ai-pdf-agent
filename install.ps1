<#
.SYNOPSIS
    Simple PDF Installer
.DESCRIPTION
    跨平台自动安装脚本（Windows PowerShell）
.NOTES
    Author: Simple PDF Team
#>

param(
    [switch]$Help,
    [switch]$Reinstall,
    [switch]$Test
)

function Show-Help {
    Write-Host "Simple PDF Installer - Windows PowerShell 版本" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "用法: .\install.ps1 [选项]"
    Write-Host ""
    Write-Host "选项:"
    Write-Host "  -Help     显示帮助信息"
    Write-Host "  -Reinstall  卸载并重新安装"
    Write-Host "  -Test     安装后测试"
    Write-Host ""
    Write-Host "示例:"
    Write-Host "  .\install.ps1           # 安装 Simple PDF"
    Write-Host "  .\install.ps1 -Reinstall   # 重新安装"
    Write-Host "  .\install.ps1 -Test     # 安装并测试"
}

function Install-Prerequisites {
    Write-Host "📦 检查 Python..." -"ForegroundColor Yellow"

    try {
        $pythonVersion = python --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Python 已安装: $pythonVersion" -"ForegroundColor Green"
        } else {
            Write-Host "❌ Python 未安装，请先安装 Python 3.8+" -"ForegroundColor Red
            exit 1
        }
    } catch {
        Write-Host "❌ Python 未安装，请先安装 Python 3.8+" -"ForegroundColor Red
        exit 1
    }

    Write-Host "📦 检查 pip..." -"ForegroundColor Yellow
    try {
        $pipVersion = pip --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ pip 已安装: $pipVersion" -"ForegroundColor Green"
        } else {
            Write-Host "❌ pip 未安装" -"ForegroundColor Red
            exit 1
        }
    } catch {
        Write-Host "❌ pip 未安装" -"ForegroundColor Red
        exit 1
    }
}

function Install-Package {
    param([string]$ProjectDir)

    Write-Host "🚀 开始安装 Simple PDF..." -"ForegroundColor Cyan
    Write-Host ""

    if ($Reinstall) {
        Write-Host "🗑️  卸载旧版本..." -"ForegroundColor Yellow
        pip uninstall simple-pdf -y 2>&1 | Out-Null
    }

    Write-Host "📦 升级 pip..." -"ForegroundColor Yellow
    pip install --upgrade pip 2>&1 | Out-Null
    Write-Host "✅ pip 升级完成" -"ForegroundColor Green
    Write-Host ""

    Write-Host "📦 安装 Simple PDF..." -"ForegroundColor Yellow
    Set-Location $ProjectDir
    pip install -e . 2>&1 | ForEach-Object { Write-Host $_ }

    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Simple PDF 安装成功！" -"ForegroundColor Green
    } else {
        Write-Host "❌ Simple PDF 安装失败！" -"ForegroundColor Red
        exit 1
    }

    Write-Host ""
}

function Test-Installation {
    Write-Host "🧪 测试安装..." -"ForegroundColor Cyan
    Write-Host ""

    Write-Host "1️⃣  测试命令: simple-pdf --version"
    try {
        $result = simple-pdf --version 2>&1
        Write-Host "✅ 命令工作正常" -"ForegroundColor Green
        Write-Host "   输出: $result" -"ForegroundColor Gray
    } catch {
        Write-Host "❌ 命令执行失败" -"ForegroundColor Red
        exit 1
    }

    Write-Host ""
    Write-Host "2️⃣  测试命令: simple-pdf --help"
    try {
        $result = simple-pdf --help 2>&1
        Write-Host "✅ 帮助信息显示正常" -"ForegroundColor Green
    } catch {
        Write-Host "❌ 帮助信息显示失败" -"ForegroundColor Red
        exit 1
    }

    Write-Host ""
    Write-Host "🎉 测试完成！" -"ForegroundColor Green
}

function Show-Usage {
    Write-Host "📋 使用方法：" -"ForegroundColor Cyan
    Write-Host ""
    Write-Host "激活虚拟环境：" -"ForegroundColor Yellow
    Write-Host "  .\venv\Scripts\Activate.ps1    # PowerShell" -"ForegroundColor White
    Write-Host "  .\venv\Scripts\activate.bat     # CMD" -"ForegroundColor White
    Write-Host ""
    Write-Host "使用命令：" -"ForegroundColor Yellow
    Write-Host "  simple-pdf --version           # 显示版本" -"ForegroundColor White
    Write-Host "  simple-pdf --help              # 显示帮助" -"ForegroundColor White
    Write-Host "  simple-pdf read document.pdf -o output.txt    # 读取 PDF" -"ForegroundColor White
    Write-Host "  simple-pdf convert document.pdf --format markdown -o output.md    # 转换为 Markdown" -"ForegroundColor White
}

# 主函数
if ($Help) {
    Show-Help
    exit 0
}

Write-Host "========================================" -"ForegroundColor Cyan
Write-Host "Simple PDF Installer" -"ForegroundColor Cyan
Write-Host "========================================" -"ForegroundColor Cyan
Write-Host ""

$projectDir = $PSScriptRoot
Write-Host "📁 项目目录: $projectDir" -"ForegroundColor Gray
Write-Host ""

# 检查前提条件
Install-Prerequisites

# 安装包
Install-Package -ProjectDir $projectDir

# 测试安装
if ($Test -or !$Help) {
    Test-Installation
}

# 显示使用方法
Show-Usage

Write-Host ""
Write-Host "✅ 安装完成！" -"ForegroundColor Green
Write-Host ""
