param(
    [ValidateRange(1, 65535)][int]$Port = 8000,
    [switch]$ForPrivateTunnel
)
$ErrorActionPreference = 'Stop'
if (-not (Get-Command uvx -ErrorAction SilentlyContinue)) {
    throw 'uvx not found. Install uv first.'
}
if ($ForPrivateTunnel) {
    if ($env:SCRAPLING_MCP_AUTH_TOKEN) {
        throw 'ForPrivateTunnel requires removing SCRAPLING_MCP_AUTH_TOKEN to avoid ambiguity.'
    }
    Write-Warning 'UNAUTHENTICATED loopback HTTP: ONLY use behind a private local tunnel, never a public forwarded port.'
} elseif (-not $env:SCRAPLING_MCP_AUTH_TOKEN) {
    throw 'Missing SCRAPLING_MCP_AUTH_TOKEN. Generate a random 32-byte token as described in README.'
}
if (-not $env:SCRAPLING_EXECUTABLE_PATH) {
    $candidate = 'C:\Program Files\Google\Chrome\Application\chrome.exe'
    if (Test-Path $candidate) { $env:SCRAPLING_EXECUTABLE_PATH = $candidate }
}
$argsList = @('--from', 'scrapling[ai]==0.4.15', 'scrapling-mcp', '--http',
              '--host', '127.0.0.1', '--port', [string]$Port)
if ($ForPrivateTunnel) { $argsList += '--no-auth' }
Write-Host "Starting Scrapling MCP at http://127.0.0.1:$Port/mcp (Ctrl+C to stop)"
& uvx @argsList
if ($LASTEXITCODE -ne 0) { throw "uvx exited with code $LASTEXITCODE" }
