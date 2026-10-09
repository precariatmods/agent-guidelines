$ErrorActionPreference = "Stop"

$MeetingMinutesRoot = $PSScriptRoot
$CacheRoot = Join-Path $MeetingMinutesRoot ".cache"

$localPaths = @{
    PIP_CACHE_DIR         = Join-Path $CacheRoot "pip"
    WHISPER_MODEL_DIR     = Join-Path $CacheRoot "whisper"
    SPEAKER_MODEL_DIR     = Join-Path $CacheRoot "speaker-models"
}
foreach ($entry in $localPaths.GetEnumerator()) {
    New-Item -ItemType Directory -Path $entry.Value -Force | Out-Null
    [Environment]::SetEnvironmentVariable($entry.Key, $entry.Value, "Process")
}
