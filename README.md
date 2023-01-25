# hadolint-py

[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

A python package that provides a pip-installable
[hadolint](https://github.com/hadolint/hadolint) binary.

The mechanism by which the binary is downloaded is basically copied from
[shellcheck-py](https://github.com/shellcheck-py/shellcheck-py).

## Getting started

### Installation

The package hasn't been published to PyPI yet, and may never be, as its primary
purpose doesn't require it. However you can install it through git:

```shell script
pip install git+git://github.com/AleksaC/hadolint-py.git@v2.12.0
```

To install another version simply replace the v2.12.0 with the version you want.

### With pre-commit

This package was primarily built to provide a convenient way of running hadolint
as a [pre-commit](https://pre-commit.com) hook, since haskell isn't supported by
pre-commit. An alternative to this solution is to create a docker hook since
hadolint provides a docker image, but I think that it has unnecessary amount of overhead.

Example `.pre-commit-config.yaml` with rules `DL3025` and `DL3018` excluded:

```yaml
repos:
  - repo: https://github.com/AleksaC/hadolint-py
    rev: v2.12.0
    hooks:
      - id: hadolint
        args: [--ignore, DL3025, --ignore, DL3018]
```

## Contact 🙋‍♂️

-   [Personal website](https://aleksac.me)
-   <a target="_blank" href="http://twitter.com/aleksa_c_"><img alt='Twitter followers' src="https://img.shields.io/twitter/follow/aleksa_c_.svg?style=social"></a>
-   aleksacukovic1@gmail.com
