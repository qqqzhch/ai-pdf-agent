<#
.SYNOPSIS
    Simple PDF Installer
.DESCRIPTION
    跨平台自动安装脚本（支持多 pip 镜像源）
.NOTES
    Author: Simple PDF Team
#>

param(
    [switch]$Help,
    [switch]$Reinstall,
    [switch]$Test,
    [string]$PipMirror = "default",
    [ValidateSet("default", "tuna", "tsinghua", "aliyun", "ustc", "chima", "pypi")]
    [string]$PipIndex = $null
)

# 镜像源配置
$MIRRORS = @{
    "default" = "https://pypi.org/simple"
    "tuna"    = "https://pypi.tuna.tsinghua.edu.cn/simple"
    "tsinghua" = "https://pypi.tuna.tsinghua.edu.cn/simple"
    "aliyun"  = "https://mirrors.aliyun.com/pypi/simple"
    "ustc"    = "https://mirrors.ustc.edu.cn/pypi/simple"
    "chima"  = "https://pypi.mirrors.china.edu/simple"
    "pypi"    = "https://pypi.org/simple"
}

function Show-Help {
    Write-Host "Simple PDF Installer - PowerShell 版本" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "用法: .\install.ps1 [选项]"
    Write-Host ""
    Write-Host "选项:"
    Write-Host "  -Help             显示帮助信息"
    Write-Host "  -Reinstall         卸载并重新安装"
    Write-Host "  -Test              安装后测试"
    Write-Host "  -PipMirror <name>  指定 pip 镜像源（default, tuna, tsinghua, aliyun, ustc, chima, pypi）"
    Write-Host "  -PipIndex <url>   指定自定义 pip 索引 URL"
    Write-Host ""
    Write-Host "示例:"
    Write-Host "  .\install.ps1                    # 安装 Simple PDF"
    Write-Host "  .\install.ps1 -Reinstall            # 重新安装"
    Write-Host "  .\install.ps1 -Test                # 安装并测试"
    Write-Host "  .\install.ps1 -PipMirror tuna      # 使用清华大学镜像"
    Write-Host "  .\install.ps1 -PipIndex https://pypi.tuna.tsinghua.edu.cn/simple"
}

function Set-PipMirror {
    param([string]$Mirror)

    Write-Host "🔄 设置 pip 镜像源..." -ForegroundColor Yellow
    
    if ($Mirror -eq "default") {
        Write-Host "使用默认源：$($MIRRORS['default'])" -ForegroundColor Gray
        [Environment]::SetEnvironmentVariable("PIP_INDEX_URL", $null, "User")
    } else {
        $mirrorUrl = $MIRRORS[$Mirror]
        if (-not $mirrorUrl) {
            Write-Host "❌ 未知镜像源：$Mirror" -ForegroundColor Red
            Write-Host "可用的源：default, tuna, tsinghua, aliyun, ustc, chima, pypi" -ForegroundColor Gray
            return $false
        }
        
        Write-Host "使用镜像源：$Mirror" -ForegroundColor Gray
        Write-Host "URL: $mirrorUrl" -ForegroundColor Gray
        
        # 设置环境变量
        [Environment]::SetEnvironmentVariable("PIP_INDEX_URL", $mirrorUrl, "User")
        
        Write-Host "✅ pip 源已设置" -ForegroundColor Green
    }
    
    return $true
}

function Install-Prerequisites {
    Write-Host "📦 检查 Python..." -ForegroundColor Yellow

    try {
        $pythonVersion = python --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Python 已安装: $pythonVersion" -ForegroundColor Green
        } else {
            Write-Host "❌ Python 未安装，请先安装 Python 3.8+" -ForegroundColor Red
            exit 1
        }
    } catch {
        Write-Host "❌ Python 未安装，请先安装 Python 3.8+" -ForegroundColor Red
        exit 1
    }

    Write-Host "📦 检查 pip..." -ForegroundColor Yellow
    
    # 清除缓存环境变量
    $env:PIP_INDEX_URL = $null
    
    try {
        $pipVersion = pip --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ pip 已安装: $pipVersion" -ForegroundColor Green
        } else {
            Write-Host "❌ pip 未安装" -ForegroundColor Red
            exit 1
        }
    } catch {
        Write-Host "❌ pip 未安装" -ForegroundColor Red
        exit 1
    }

    Write-Host ""
}

function Install-Package {
    param([string]$ProjectDir, [bool]$Reinstall)

    Write-Host "🚀 开始安装 Simple PDF..." -ForegroundColor Cyan
    Write-Host ""

    # 显示当前 pip 源
    $currentMirror = [Environment]::GetEnvironmentVariable("PIP_INDEX_URL", "User")
    if ($currentMirror) {
        Write-Host "📡 当前 pip 镜像源: $currentMirror" -ForegroundColor Cyan
    } else {
        Write-Host "📡 使用默认 pip 源像" -ForegroundColor Gray
    }
    Write-Host ""

    if ($Reinstall) {
        Write-Host "🗑️  卸载旧版本..." -ForegroundColor Yellow
        pip uninstall simple-pdf -y 2>&1 | Out-Null
    }

    Write-Host "📦 升级 pip..." -ForegroundColor Yellow
    pip install --upgrade pip 2>&1 | Out-Null
    Write-Host "✅ pip 升级完成" -ForegroundColor Green
    Write-Host ""

    Write-Host "📦 安装 Simple PDF..." -ForegroundColor Yellow
    Set-Location $ProjectDir
    
    try {
        pip install -e . 2>&1 | ForEach-Object { 
            Write-Host $_
        }
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host ""
            Write-Host "✅ Simple PDF 安装成功！" -ForegroundColor Green
        } else {
            Write-Host ""
            Write-Host "❌ Simple PDF 安装失败！" -ForegroundColor Red
            Write-Host "尝试使用备选方案..." -ForegroundColor Yellow
            
            # 尝试其他镜像源
            Write-Host ""
            Write-Host "🔄 尝试清华大学镜像源..." -ForegroundColor Yellow
            Set-PipMirror "tuna"
            
            Write-Host "📦 重新安装..." -ForegroundColor Yellow
            pip install -e . 2>&1 | ForEach-Object { 
                Write-Host $_
            }
            
            if ($LASTEXITCODE -ne 0) {
                Write-Host ""
                Write-Host "❌ 所有镜像源都失败！" -ForegroundColor Red
                exit 1
            } else {
                Write-Host ""
                Write-Host "✅ 使用清华大学镜像安装成功！" -ForegroundColor Green
                Write-Host ""
                Write-Host "💡 提示：可以设置环境变量永久使用该镜像源"
                Write-Host "   setx PIP_INDEX_URL https://pypi.tuna.tsinghua.edu.cn/simple"
            }
        }
    } catch {
        Write-Host ""
        Write-Host "❌ 安装过程出错！" -ForegroundColor Red
        Write-Host $_.Exception.Message -ForegroundColor Red
        exit 1
    }

    Write-Host ""
}

function Test-Installation {
    Write-Host "🧪 测试安装..." -ForegroundColor Cyan
    Write-Host ""

    Write-Host "1️⃣  测试命令: simple-pdf --version"
    try {
        $result = simple-pdf --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ 命令工作正常" -ForegroundColor Green
            Write-Host "   输出: $result" -ForegroundColor Gray
        } else {
            Write-Host "❌ 命令执行失败" -ForegroundColor Red
            Write-Host "尝试模块直接执行..." -ForegroundColor Yellow
            
            $result = python -m ai_pdf_agent.cli.cli --version 2>&1
            if ($LASTEXITCODE -eq 0) {
                Write-Host "✅ 模块直接执行成功" -ForegroundColor Green
                Write-Host "   输出: $result" -ForegroundColor Gray
                Write-Host ""
                Write-Host "💡 提示：可以使用模块方式执行命令"
                Write-Host "   python -m ai_pdf_agent.cli.cli --version"
            } else {
                Write-Host "❌ 模块执行也失败" -ForegroundColor Red
                exit 1
            }
        }
    } catch {
        Write-Host "❌ 命令执行失败" -ForegroundColor Red
        exit 1
    }

    Write-Host ""
    Write-Host "2️⃣  测试命令: simple-pdf --help"
    try {
        $result = simple-pdf --help 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ 帮助信息显示正常" -ForegroundColor Green
        } else {
            Write-Host "❌ 帮助信息显示失败" -ForegroundColor Red
        }
    } catch {
        Write-Host "❌ 帮助信息显示失败" -ForegroundColor Red
    }

    Write-Host ""
    Write-Host "✅ 测试完成！" -ForegroundColor Green
}

function Show-Usage {
    Write-Host "📋 使用方法" -ForegroundColor Cyan
    Write-Host ""
    
    if ($P: {PSVersionTable.PSVersion.Major} -ge 6) {
        Write-Host "激活虚拟环境（如果需要）：" -ForegroundColor Yellow
        Write-Host "  .\venv\Scripts\Activate.ps1  # PowerShell" -ForegroundColor White
        Write-Host "  .\venv\Scripts\activate.bat   # CMD" -ForegroundColor White
    } else {
        Write-Host "激活虚拟环境（如果需要）：" -ForegroundColor Yellow
        Write-Host "  .\venv\Scripts\activate.bat" -ForegroundColor White
    }
    
    Write-Host ""
    Write-Host "使用命令：" -ForegroundColor Yellow
    
    # 测试命令是否可用
    $commandAvailable = $false
    try {
        $null = Get-Command simple-pdf -ErrorAction SilentlyContinue
        if ($null -ne $null) {
            $commandAvailable = $true
        }
    } catch {}

    if ($commandAvailable) {
        Write-Host "  simple-pdf --version           # 显示版本" -ForegroundColor White
        Write-Host "  simple-pdf --help              # 显示帮助" -ForegroundColor White
        Write-Host "  simple-pdf read document.pdf -o output.txt    # 读取 PDF" -ForegroundColor White
        Write-Host "  simple-pdf convert document.pdf --format markdown -o output.md  # 转换为 Markdown" -ForegroundColor White
    } else {
        Write-Host "  python -m ai_pdf_agent.cli.cli --version           # 显示版本" -ForegroundColor White
        Write-Host "  python -m ai_pdf_agent.cli.cli --help              # 显示帮助" -ForegroundColor White
        Write-Host "  python -m ai_pdf_agent.cli.cli read document.pdf -o output.txt    # 读取 PDF" -ForegroundColor White
        Write-Host "  python -m ai_pdf_agent.cli.cli convert document.pdf --format markdown -o output.md  # 转换为 Markdown" -ForegroundColor White
    }
    
    Write-Host ""
    Write-Host "💡 pip 镜像源配置：" -ForegroundColor Cyan
    Write-Host "  -PipMirror <name>  指定预定义镜像源" -ForegroundColor Gray
    Write-Host "    可选：default, tuna, tsinghua, aliyun, ustc, chima, pypi" -ForegroundColor Gray
    Write-Host "  -PipIndex <url>   指定自定义镜像源 URL" -ForegroundColor Gray
}

# 主函数
if ($Help) {
    Show-Help
    exit 0
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Simple PDF Installer" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

if ($PipIndex) {
    Write-Host "⚙️  使用自定义 pip 索引: $PipIndex" -ForegroundColor Yellow
    [Environment]::SetEnvironmentVariable("PIP_INDEX_URL", $PipIndex, "User")
}

if ($PipMirror -ne "default") {
    Set-PipMirror $PipMirror
}

$projectDir = $PSScriptRoot
Write-Host "📁 项目目录: $projectDir" -ForegroundColor Gray
Write-Host ""

# 检查前提条件
Install-Prerequisites

# 安装包
Install-Package -ProjectDir $projectDir -Reinstall $Reinstall

# 测试安装
if ($Test -or !$Help) {
    Test-Installation
}

# 显示使用方法
Show-Usage

Write-Host ""
Write-Host "✅ 安装完成！" -ForegroundColor Green
Write-Host ""
