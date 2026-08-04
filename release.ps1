# Tag the current commit for release and push the tag to every remote.
# Tag name is today's date (v2026.08.03); if that tag already exists
# (a second release same day), appends .1, .2, etc.

$base = "v" + (Get-Date -Format "yyyy.MM.dd")
$tag = $base
$n = 1
while (git tag -l $tag) {
    $tag = "$base.$n"
    $n++
}

Write-Host "Tagging $tag"
git tag -a $tag -m $tag
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

foreach ($remote in (git remote)) {
    Write-Host "Pushing $tag to $remote"
    git push $remote $tag
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}

Write-Host "Released $tag to: $((git remote) -join ' ')"
