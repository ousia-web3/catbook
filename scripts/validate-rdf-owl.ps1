param(
    [switch]$SkipInstall
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = Resolve-Path (Join-Path $scriptDir "..\..")

function Invoke-Checked {
    param(
        [Parameter(Mandatory = $true)]
        [string]$FilePath,

        [Parameter(ValueFromRemainingArguments = $true)]
        [string[]]$Arguments
    )

    & $FilePath @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "$FilePath failed with exit code $LASTEXITCODE"
    }
}

Push-Location $repoRoot
try {
    if (-not $SkipInstall) {
        Invoke-Checked python -m pip install -r catbook\requirements-rdf.txt
    }

    Invoke-Checked python -m py_compile `
        catbook\research\build_cat_ontology_graph.py `
        catbook\research\export_cat_ontology_rdf.py `
        catbook\research\validate_cat_ontology_rdf.py

    Invoke-Checked python catbook\research\build_cat_ontology_graph.py
    Invoke-Checked python catbook\research\validate_cat_ontology_rdf.py

    Write-Host "Catbook RDF/OWL validation gate passed."
}
finally {
    Pop-Location
}
