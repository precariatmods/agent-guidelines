param(
    [Parameter(Mandatory = $true)]
    [string]$Audio,
    [string]$PersonMaster = "work\master\person.csv",
    [int]$NumSpeakers = 0,
    [switch]$NonInteractive,
    [switch]$ReuseTranscript,
    [switch]$Force
)

$ErrorActionPreference = "Stop"
. (Join-Path $PSScriptRoot "environment.ps1")

$pythonPathFile = Join-Path $PSScriptRoot ".python-path"
$componentChecker = Join-Path $PSScriptRoot "scripts\check_python_components.py"
$speakerModel = Join-Path $env:SPEAKER_MODEL_DIR "3dspeaker_speech_campplus_sv_zh-cn_16k-common.onnx"
$needsSetup = -not (Test-Path -LiteralPath $pythonPathFile -PathType Leaf)
if (-not $needsSetup) {
    $candidatePython = (Get-Content -LiteralPath $pythonPathFile -Raw).Trim()
    if (-not (Test-Path -LiteralPath $candidatePython -PathType Leaf)) {
        $needsSetup = $true
    }
    elseif (-not (Test-Path -LiteralPath $speakerModel -PathType Leaf)) {
        $needsSetup = $true
    }
    else {
        & $candidatePython $componentChecker
        $needsSetup = $LASTEXITCODE -ne 0
    }
}
if ($needsSetup) {
    & powershell.exe -NoProfile -ExecutionPolicy Bypass -File (Join-Path $PSScriptRoot "setup.ps1")
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}
$python = (Get-Content -LiteralPath $pythonPathFile -Raw).Trim()
if (-not (Test-Path -LiteralPath $python -PathType Leaf)) {
    throw "記録されたPythonが見つかりません: $python"
}

function Get-MeetingMinutesPath([string]$Path) {
    if ([IO.Path]::IsPathRooted($Path)) { return $Path }
    return Join-Path $PSScriptRoot $Path
}

$arguments = @(
    (Join-Path $PSScriptRoot "scripts\process_meeting_audio.py"),
    (Get-MeetingMinutesPath $Audio),
    (Get-MeetingMinutesPath $PersonMaster),
    (Join-Path $PSScriptRoot "work")
)
if ($NumSpeakers -gt 0) { $arguments += @("--num-speakers", "$NumSpeakers") }
if ($NonInteractive) { $arguments += "--non-interactive" }
if ($ReuseTranscript) { $arguments += "--reuse-transcript" }
if ($Force) { $arguments += "--force" }

& $python @arguments
exit $LASTEXITCODE
