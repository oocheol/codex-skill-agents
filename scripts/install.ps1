param(
    [string]$Destination = "$env:USERPROFILE\.codex\skills"
)

$ErrorActionPreference = "Stop"

$RepoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$SkillRoot = Join-Path $RepoRoot "skills"

if (-not (Test-Path $SkillRoot)) {
    throw "Cannot find skills directory: $SkillRoot"
}

New-Item -ItemType Directory -Path $Destination -Force | Out-Null

Get-ChildItem -Path $SkillRoot -Directory | ForEach-Object {
    $target = Join-Path $Destination $_.Name
    if (Test-Path $target) {
        Remove-Item -Path $target -Recurse -Force
    }
    Copy-Item -Path $_.FullName -Destination $Destination -Recurse
    Write-Host "Installed $($_.Name) -> $target"
}

Write-Host ""
Write-Host "Done. Restart Codex to pick up the installed skills."
