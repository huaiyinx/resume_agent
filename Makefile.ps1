# Resume-Agent PowerShell Makefile（Windows 原生支持）
# US-20: Makefile 的 Windows PowerShell 等效版本
# 使用方式: .\Makefile.ps1 <target>
#   .\Makefile.ps1 install
#   .\Makefile.ps1 dev
#   .\Makefile.ps1 build
#   .\Makefile.ps1 test
#   .\Makefile.ps1 lint
#   .\Makefile.ps1 docker-up
#   .\Makefile.ps1 clean

param(
    [Parameter(Position=0)]
    [ValidateSet("install", "dev", "build", "test", "lint", "docker-build", "docker-up", "clean", "help")]
    [string]$Target = "help"
)

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

# 清除可能干扰 Python 的环境变量
$env:PYTHONHOME = $null
$env:PYTHONPATH = $null

function Invoke-Install {
    Write-Host ">>> 安装前端依赖..." -ForegroundColor Cyan
    Set-Location "$ScriptDir\frontend"
    pnpm install
    Set-Location $ScriptDir

    Write-Host ">>> 安装后端依赖..." -ForegroundColor Cyan
    Set-Location "$ScriptDir\backend"
    uv sync --extra dev
    Set-Location $ScriptDir

    Write-Host "安装完成！" -ForegroundColor Green
}

function Invoke-Dev {
    Write-Host ">>> 启动开发服务器（前端 + 后端）..." -ForegroundColor Cyan

    # 启动后端
    $backendJob = Start-Job -ScriptBlock {
        param($dir)
        Set-Location "$dir\backend"
        $env:PYTHONHOME = $null
        $env:PYTHONPATH = $null
        uv run uvicorn resume_agent.main:app --reload --port 8000
    } -ArgumentList $ScriptDir

    # 启动前端
    $frontendJob = Start-Job -ScriptBlock {
        param($dir)
        Set-Location "$dir\frontend"
        & ".\node_modules\.bin\vite"
    } -ArgumentList $ScriptDir

    Write-Host "前端: http://localhost:5173" -ForegroundColor Green
    Write-Host "后端: http://localhost:8000" -ForegroundColor Green
    Write-Host "按 Ctrl+C 停止..." -ForegroundColor Yellow

    try {
        # 等待任一 job 完成
        Wait-Job -Any $backendJob, $frontendJob
    } finally {
        Stop-Job $backendJob, $frontendJob -ErrorAction SilentlyContinue
        Remove-Job $backendJob, $frontendJob -ErrorAction SilentlyContinue
    }
}

function Invoke-Build {
    Write-Host ">>> 构建前端..." -ForegroundColor Cyan
    Set-Location "$ScriptDir\frontend"
    & ".\node_modules\.bin\tsc" -b
    & ".\node_modules\.bin\vite" build
    Set-Location $ScriptDir
    Write-Host "构建完成！" -ForegroundColor Green
}

function Invoke-Test {
    Write-Host ">>> 运行后端测试..." -ForegroundColor Cyan
    Set-Location "$ScriptDir\backend"
    uv run pytest
    Set-Location $ScriptDir

    Write-Host ">>> 运行前端类型检查..." -ForegroundColor Cyan
    Set-Location "$ScriptDir\frontend"
    & ".\node_modules\.bin\tsc" --noEmit
    Set-Location $ScriptDir

    Write-Host "测试通过！" -ForegroundColor Green
}

function Invoke-Lint {
    Write-Host ">>> 后端 lint..." -ForegroundColor Cyan
    Set-Location "$ScriptDir\backend"
    uv run ruff check .
    Set-Location $ScriptDir

    Write-Host ">>> 前端类型检查..." -ForegroundColor Cyan
    Set-Location "$ScriptDir\frontend"
    & ".\node_modules\.bin\tsc" --noEmit
    Set-Location $ScriptDir

    Write-Host "Lint 通过！" -ForegroundColor Green
}

function Invoke-DockerBuild {
    Write-Host ">>> 构建 Docker 镜像..." -ForegroundColor Cyan
    docker compose build
}

function Invoke-DockerUp {
    Write-Host ">>> 启动 Docker 容器..." -ForegroundColor Cyan
    docker compose up
}

function Invoke-Clean {
    Write-Host ">>> 清理构建产物..." -ForegroundColor Cyan
    if (Test-Path "$ScriptDir\frontend\dist") {
        Remove-Item -Recurse -Force "$ScriptDir\frontend\dist"
    }
    Get-ChildItem -Path $ScriptDir -Recurse -Directory -Filter "__pycache__" |
        Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
    Write-Host "清理完成！" -ForegroundColor Green
}

function Show-Help {
    Write-Host "Resume-Agent PowerShell Makefile" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "用法: .\Makefile.ps1 <target>"
    Write-Host ""
    Write-Host "可用 targets:"
    Write-Host "  install       安装前后端依赖"
    Write-Host "  dev           启动开发服务器（前端 + 后端）"
    Write-Host "  build         构建前端"
    Write-Host "  test          运行测试"
    Write-Host "  lint          代码检查"
    Write-Host "  docker-build  构建 Docker 镜像"
    Write-Host "  docker-up     启动 Docker 容器"
    Write-Host "  clean         清理构建产物"
    Write-Host "  help          显示帮助"
}

# === 路由 ===
switch ($Target) {
    "install"      { Invoke-Install }
    "dev"          { Invoke-Dev }
    "build"        { Invoke-Build }
    "test"         { Invoke-Test }
    "lint"         { Invoke-Lint }
    "docker-build" { Invoke-DockerBuild }
    "docker-up"    { Invoke-DockerUp }
    "clean"        { Invoke-Clean }
    "help"         { Show-Help }
}
