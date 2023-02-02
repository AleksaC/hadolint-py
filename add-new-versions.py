#!/usr/bin/env python

import argparse
import base64
import http
import json
import os
import re
import subprocess
import sys
from functools import lru_cache
from urllib.request import Request
from urllib.request import urlopen

from typing import Any
from typing import NamedTuple
from typing import Optional

import jinja2


VERSION_RE = re.compile("^v?(?P<major>[0-9]+)\.(?P<minor>[0-9]+)\.(?P<patch>[0-9]+)$")

OS = {"darwin", "linux", "windows"}
ARCH = {"x86_64", "arm64"}

TEMPLATES_DIR = "templates"

REPO = "hadolint/hadolint"
MIRROR_REPO = "AleksaC/hadolint-py"

MIN_VERSION = "v2.10.0"


class Version(NamedTuple):
    major: int
    minor: int
    patch: int

    @classmethod
    def from_string(cls, version: str) -> "Version":
        if match := re.match(VERSION_RE, version):
            return cls(*map(int, match.groups()))

        raise ValueError("Invalid version", version)

    def __repr__(self):
        return f"{self.major}.{self.minor}.{self.patch}"

    def __lte__(self, other: "Version") -> bool:
        if self.major != other.major:
            return self.major < other.major
        elif self.minor != other.minor:
            return self.minor < other.minor
        else:
            return self.patch <= other.patch


class Template(NamedTuple):
    src: str
    dest: str
    vars: dict[str, Any]


def _get(
    url: str, headers: Optional[dict[str, str]] = None
) -> http.client.HTTPResponse:
    if headers is None:
        headers = {}

    req = Request(url, headers=headers)
    resp = urlopen(req, timeout=30)

    return resp


def get_json(url: str, headers: Optional[dict[str, str]] = None) -> dict:
    return json.loads(_get(url, headers).read())


def get_text(url: str, headers: Optional[dict[str, str]] = None) -> str:
    return _get(url, headers).read().decode()


@lru_cache
def get_gh_auth_headers():
    gh_token = os.environ["GH_TOKEN"]
    auth = base64.b64encode(f"AleksaC:{gh_token}".encode()).decode()
    return {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": f"Basic {auth}",
    }


def get_versions(
    repo: str, *, from_releases: bool = True, min_version: Optional[Version] = None
) -> list[Version]:
    base_url = "https://api.github.com/repos/{}/{}?per_page=100&page={}"

    versions: list[Version] = []
    page = 1
    while releases_page := get_json(
        base_url.format(repo, "releases" if from_releases else "tags", page),
        headers=get_gh_auth_headers(),
    ):
        for release in releases_page:
            if from_releases and (release["draft"] or release["prerelease"]):
                continue
            tag_name = release["tag_name"] if from_releases else release["name"]

            try:
                version = Version.from_string(tag_name)
            except ValueError as e:
                print(f"Could not parse version: {tag_name}")
                print(e)
            else:
                if min_version and version < min_version:
                    return versions
                versions.append(version)

        page += 1

    return versions


def get_missing_versions(
    repo: str, mirror_repo: str, min_version: Optional[Version] = None
) -> list[Version]:
    versions = get_versions(repo, min_version=min_version)
    mirrored = get_versions(mirror_repo, from_releases=False, min_version=min_version)

    missing = []
    for new in reversed(versions):
        for existing in mirrored:
            if new == existing:
                break
        else:
            missing.append(new)

    return missing


def get_archives(repo: str, version: Version) -> dict[str, tuple[str, str]]:
    release_url = f"https://api.github.com/repos/{repo}/releases/tags/v{version}"
    release = get_json(release_url, headers=get_gh_auth_headers())

    checksums, binaries = {}, {}
    for file in release["assets"]:
        file_name = file["name"]
        if file["name"].endswith(".sha256"):
            checksums[file_name] = file["browser_download_url"]
        else:
            binaries[file_name] = file["browser_download_url"]

    archives = {}

    for checksum_name, checksum_url in checksums.items():
        sha, binary_name = (
            get_text(checksum_url, headers=get_gh_auth_headers()).strip().split()
        )

        if binary_name.startswith("*"):
            binary_name = binary_name[1:]
        if not checksum_name.startswith(binary_name):
            raise AssertionError

        archive = (binaries[binary_name], sha)
        _, os, arch = (
            binary_name[:-4].split("-")
            if binary_name.endswith(".exe")
            else binary_name.split("-")
        )

        os_normalized, arch_normalized = os.lower(), arch.lower()

        if os_normalized not in OS or arch_normalized not in ARCH:
            raise ValueError("Unsupported plaform!", os, arch)

        archives[f"{os_normalized}-{arch_normalized}"] = archive

    return archives


def render_templates(templates: list[Template]) -> None:
    for src, dest, vars in templates:
        with open(os.path.join(TEMPLATES_DIR, src)) as f:
            template_file = f.read()

        template = jinja2.Template(template_file, keep_trailing_newline=True)

        with open(dest, "w") as f:
            f.write(template.render(**vars))


def push_tag(version: Version) -> None:
    subprocess.run(["./tag.sh", f"v{version}"], check=True)


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--render-only", default=False, action="store_true")
    args = parser.parse_args(argv)

    versions = get_missing_versions(REPO, MIRROR_REPO, Version.from_string(MIN_VERSION))

    for version in versions:
        print(f"Adding new version: v{version}")

        archives = get_archives(REPO, version)

        render_templates(
            [
                Template(
                    src="setup.py.j2",
                    dest="setup.py",
                    vars={"hadolint_version": str(version), "archives": str(archives)},
                ),
                Template(
                    src="README.md.j2",
                    dest="README.md",
                    vars={"hadolint_version": str(version)},
                ),
            ]
        )

        if not args.render_only:
            push_tag(version)

    return 0


if __name__ == "__main__":
    sys.exit(main())
