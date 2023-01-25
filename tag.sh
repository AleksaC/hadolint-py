#!/usr/bin/env bash

set -euo pipefail

git add -u
git commit -m "Add version $1"
git pull --ff-only
git tag $1
git push
git push --tags
