$ErrorActionPreference = 'Stop'
$oldPath = $env:Path
try {
    $env:Path = ($env:Path -split ';' | Where-Object {
        $_ -and $_ -notmatch 'conda|miniconda|miniforge|pixi|rattler|comfy-env|\\Library\\bin'
    }) -join ';'
    $sourceRoot = Split-Path -Parent $PSScriptRoot
    $outputRoot = Join-Path (Split-Path -Parent $sourceRoot) ((Split-Path -Leaf $sourceRoot) + '_打包')
    New-Item -ItemType Directory -Path $outputRoot -Force | Out-Null
    $pythonPath = Join-Path $outputRoot '.venv-build\Scripts\python.exe'
    if (-not (Test-Path -LiteralPath $pythonPath)) {
        py -3.12 -m venv (Join-Path $outputRoot '.venv-build')
        if ($LASTEXITCODE -ne 0) { throw '创建 Python 3.12 构建环境失败。' }
    }
    & $pythonPath -m pip install 'PySide6==6.12.0' 'pyinstaller==6.22.3'
    if ($LASTEXITCODE -ne 0) { throw '安装构建依赖失败。' }
    & $pythonPath -m PyInstaller --noconfirm --clean --distpath (Join-Path $outputRoot 'dist') --workpath (Join-Path $outputRoot 'build') (Join-Path $PSScriptRoot 'ProjectCreator.spec')
    if ($LASTEXITCODE -ne 0) { throw '打包失败。' }
    $bad = @(Get-ChildItem -LiteralPath (Join-Path $outputRoot 'dist\ProjectCreator') -Recurse -File -Filter 'icu*.dll')
    if ($bad.Count -gt 0) { throw ('产物含不允许的 ICU DLL：' + ($bad.FullName -join ', ')) }
    Write-Output ('检查通过：产物无 ICU DLL。输出目录：' + $outputRoot)
} finally {
    $env:Path = $oldPath
}
