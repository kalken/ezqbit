# Assemble a qBittorrent alternative WebUI folder: the original WebUI files plus the ezqbit CSS.
# Windows counterpart of build.sh; needs only Windows PowerShell 5.1 or newer.
#
# Usage:
#   .\build.ps1 <version> <out-dir>    download the WebUI of that qBittorrent release, e.g. 5.2.4
#   .\build.ps1 <www-dir> <out-dir>    use a local copy of qBittorrent's src\webui\www
#
# The original files are left as they are, except for one @import line added to the top
# of private\css\style.css and public\css\login.css.
#
# If scripts are blocked, run it as:
#   powershell -ExecutionPolicy Bypass -File .\build.ps1 5.2.4 C:\ezqbit-webui

param(
    [Parameter(Mandatory = $true, Position = 0)] [string] $Source,
    [Parameter(Mandatory = $true, Position = 1)] [string] $Out
)

$ErrorActionPreference = "Stop"
$here = $PSScriptRoot

if ((Test-Path $Out) -and (Get-ChildItem -Force $Out | Select-Object -First 1)) {
    throw "$Out already exists and is not empty"
}
New-Item -ItemType Directory -Force -Path $Out | Out-Null
$Out = (Resolve-Path $Out).Path

$tmp = $null
try {
    if (Test-Path -PathType Container $Source) {
        $www = (Resolve-Path $Source).Path
    }
    else {
        $tmp = Join-Path ([IO.Path]::GetTempPath()) ("ezqbit-" + [Guid]::NewGuid())
        New-Item -ItemType Directory -Path $tmp | Out-Null
        $zip = Join-Path $tmp "src.zip"
        $url = "https://github.com/qbittorrent/qBittorrent/archive/refs/tags/release-$Source.zip"
        Write-Host "Downloading $url"
        # GitHub requires TLS 1.2, which older Windows PowerShell does not enable by default
        [Net.ServicePointManager]::SecurityProtocol = [Net.ServicePointManager]::SecurityProtocol -bor [Net.SecurityProtocolType]::Tls12
        $ProgressPreference = "SilentlyContinue"  # the progress bar makes downloads very slow
        Invoke-WebRequest -UseBasicParsing -Uri $url -OutFile $zip
        Expand-Archive -Path $zip -DestinationPath $tmp
        $www = Join-Path $tmp "qBittorrent-release-$Source\src\webui\www"
    }

    foreach ($d in "public", "private") {
        if (-not (Test-Path -PathType Container (Join-Path $www $d))) {
            throw "$(Join-Path $www $d) not found; expected qBittorrent's src\webui\www"
        }
        Copy-Item -Recurse -Path (Join-Path $www $d) -Destination $Out
    }

    Copy-Item (Join-Path $here "css\ezqbit.css") (Join-Path $Out "private\css\")
    Copy-Item (Join-Path $here "css\ezqbit-login.css") (Join-Path $Out "public\css\")

    # Prepend a line plus a blank line, keeping the file's own bytes and line endings (UTF-8, no BOM)
    function Add-FirstLine([string] $file, [string] $line) {
        $utf8 = New-Object System.Text.UTF8Encoding($false)
        $text = [IO.File]::ReadAllText($file, $utf8)
        [IO.File]::WriteAllText($file, "$line`n`n$text", $utf8)
    }
    Add-FirstLine (Join-Path $Out "private\css\style.css") '@import url("ezqbit.css");'
    Add-FirstLine (Join-Path $Out "public\css\login.css") '@import url("ezqbit-login.css");'

    Write-Host "Built $Out"
}
finally {
    if ($tmp) { Remove-Item -Recurse -Force $tmp -ErrorAction SilentlyContinue }
}
