#!/usr/bin/env bash

set -euo pipefail

git add -u
git commit -m "Update to version $1"
git pull --rebase
git push
git tag $1
git push origin $1
