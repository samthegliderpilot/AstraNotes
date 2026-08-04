#!/usr/bin/env bash
# Tag the current commit for release and push the tag to every remote.
# Tag name is today's date (v2026.08.03); if that tag already exists
# (a second release same day), appends .1, .2, etc.
set -e

base="v$(date +%Y.%m.%d)"
tag="$base"
n=1
while [ -n "$(git tag -l "$tag")" ]; do
    tag="$base.$n"
    n=$((n + 1))
done

echo "Tagging $tag"
git tag -a "$tag" -m "$tag"

for remote in $(git remote); do
    echo "Pushing $tag to $remote"
    git push "$remote" "$tag"
done

echo "Released $tag to: $(git remote | tr '\n' ' ')"
