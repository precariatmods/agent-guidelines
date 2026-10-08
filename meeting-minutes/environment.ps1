$ErrorActionPreference = "Stop"

$MeetingMinutesRoot = $PSScriptRoot
$CacheRoot = Join-Path $MeetingMinutesRoot ".cache"

$localPaths = @{
    PIP_CACHE_DIR         = Join-Path $CacheRoot "pip"
    HF_HOME               = Join-Path $CacheRoot "huggingface"
    TORCH_HOME            = Join-Path $CacheRoot "torch"
    WHISPER_MODEL_DIR     = Join-Path $CacheRoot "whisper"
    PYANNOTE_CACHE_DIR    = Join-Path $CacheRoot "pyannote"
}
foreach ($entry in $localPaths.GetEnumerator()) {
    New-Item -ItemType Directory -Path $entry.Value -Force | Out-Null
    [Environment]::SetEnvironmentVariable($entry.Key, $entry.Value, "Process")
}

$envFile = Join-Path $MeetingMinutesRoot ".env"
if (Test-Path -LiteralPath $envFile -PathType Leaf) {
    foreach ($line in Get-Content -LiteralPath $envFile) {
        $trimmed = $line.Trim()
        if (-not $trimmed -or $trimmed.StartsWith("#")) {
            continue
        }
        $parts = $trimmed.Split("=", 2)
        if ($parts.Count -ne 2 -or -not $parts[0].Trim()) {
            throw ".env の形式が不正です: $line"
        }
        [Environment]::SetEnvironmentVariable(
            $parts[0].Trim(),
            $parts[1].Trim(),
            "Process"
        )
    }
}
