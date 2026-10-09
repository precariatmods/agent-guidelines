param(
    [string]$PythonCommand = "",
    [switch]$Yes
)

$ErrorActionPreference = "Stop"
. (Join-Path $PSScriptRoot "environment.ps1")

$venv = Join-Path $PSScriptRoot ".venv"
$venvPython = Join-Path $venv "Scripts\python.exe"
$componentChecker = Join-Path $PSScriptRoot "scripts\check_python_components.py"
$pythonPathFile = Join-Path $PSScriptRoot ".python-path"
$speakerModel = Join-Path $env:SPEAKER_MODEL_DIR "3dspeaker_speech_campplus_sv_zh-cn_16k-common.onnx"
$speakerModelUrl = "https://github.com/k2-fsa/sherpa-onnx/releases/download/speaker-recongition-models/3dspeaker_speech_campplus_sv_zh-cn_16k-common.onnx"
$readyPython = $null

if (Test-Path -LiteralPath $venvPython -PathType Leaf) {
    & $venvPython $componentChecker
    if ($LASTEXITCODE -eq 0) {
        $readyPython = $venvPython
        if (Test-Path -LiteralPath $speakerModel -PathType Leaf) {
            Set-Content -LiteralPath $pythonPathFile -Value $readyPython -Encoding UTF8
            Write-Host "既存のmeeting-minutes環境を使用します: $venv"
            exit 0
        }
    }
    Write-Host "既存環境に不足またはバージョン違いがあります。" -ForegroundColor Yellow
}

$basePython = $null
if ($PythonCommand) {
    $basePython = $PythonCommand
}
elseif (Get-Command py -ErrorAction SilentlyContinue) {
    $basePython = (& py -3.11 -c "import sys; print(sys.executable)" 2>$null)
}
elseif (Get-Command python -ErrorAction SilentlyContinue) {
    $basePython = (Get-Command python).Source
}

if ($basePython) {
    & $basePython $componentChecker
    if ($LASTEXITCODE -eq 0) {
        $readyPython = $basePython
        if (Test-Path -LiteralPath $speakerModel -PathType Leaf) {
            Set-Content -LiteralPath $pythonPathFile -Value $basePython -Encoding UTF8
            Write-Host "導入済みのPython環境を使用します: $basePython"
            exit 0
        }
    }
}

if (-not $Yes) {
    Write-Host ""
    Write-Host "初回の環境構築が必要です。" -ForegroundColor Yellow
    Write-Host "Pythonライブラリと音声モデルの保存に、最大約2GBの空き容量を使用する可能性があります。" -ForegroundColor Yellow
    $answer = Read-Host "meeting-minutes内へインストールしますか？ [y/N]"
    if ($answer -notmatch "^(y|yes)$") {
        Write-Host "インストールを中止しました。"
        exit 1
    }
}

if ($readyPython) {
    Write-Host "公開話者特徴モデルをダウンロードします。"
    Invoke-WebRequest -Uri $speakerModelUrl -OutFile $speakerModel -UseBasicParsing
    Set-Content -LiteralPath $pythonPathFile -Value $readyPython -Encoding UTF8
    Write-Host "導入済みのPython環境を使用します: $readyPython"
    exit 0
}

if (-not (Test-Path -LiteralPath $venvPython -PathType Leaf)) {
    if (-not $basePython) {
        throw "Pythonが見つかりません。Python 3.11を導入してください。"
    }
    & $basePython -m venv $venv
    if ($LASTEXITCODE -ne 0) {
        throw "仮想環境の作成に失敗しました。Python 3.11を確認してください。"
    }
}

& $venvPython -m pip install --upgrade pip
if ($LASTEXITCODE -ne 0) { throw "pipの更新に失敗しました。" }

& $venvPython -m pip install -r (Join-Path $PSScriptRoot "scripts\requirements.txt")
if ($LASTEXITCODE -ne 0) { throw "依存関係の導入に失敗しました。" }

& $venvPython $componentChecker
if ($LASTEXITCODE -ne 0) { throw "Pythonコンポーネントの確認に失敗しました。" }

Invoke-WebRequest -Uri $speakerModelUrl -OutFile $speakerModel -UseBasicParsing

Set-Content -LiteralPath $pythonPathFile -Value $venvPython -Encoding UTF8

Write-Host "環境構築が完了しました: $venv"
Write-Host "モデルとパッケージのキャッシュ: $CacheRoot"
