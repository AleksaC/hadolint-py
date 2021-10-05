#!/usr/bin/env python

import base64
import json
import os
import re
from typing import List

from urllib.request import Request
from urllib.request import urlopen


def get(url: str, headers: dict) -> dict:
    req = Request(url, headers=headers)
    resp = urlopen(req, timeout=30)
    return json.loads(resp.read())


def get_releases() -> List[str]:
    gh_token = os.environ["GH_TOKEN"]
    auth = base64.b64encode(f"AleksaC:{gh_token}".encode()).decode()

    base_url = "https://api.github.com/repos/{}/{}/{}"
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": f"Basic {auth}",
    }

    hadolint_releases = get(
        base_url.format("hadolint", "hadolint", "releases"), headers=headers
    )

    hook_tags = get(
        base_url.format("AleksaC", "hadolint-py", "tags"),
        headers=headers,
    )

    new_releases = []
    latest = hook_tags[0]["name"]
    for release in hadolint_releases:
        version = release["tag_name"]
        if version == latest:
            break
        new_releases.append(version)

    return new_releases


def update_version(version: str) -> None:
    with open("setup.py", "r+") as f:
        validator = f.read()
        f.seek(0)
        f.write(
            re.sub(
                r"HADOLINT_VERSION = \"\d+\.\d+.\d+\"\n",
                f'HADOLINT_VERSION = "{version}"\n',
                validator,
            )
        )
        f.truncate()


def push_tag(version: str) -> None:
    os.system(f"./tag.sh {version}")


if __name__ == "__main__":
    releases = get_releases()
    for release in reversed(releases):
        print(f"Adding new release: {release}")
        update_version(release.replace("v", ""))
        push_tag(release)
