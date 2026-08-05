

# hadolint-py

[![Add new versions](https://github.com/AleksaC/hadolint-py/actions/workflows/add-new-versions.yml/badge.svg)](https://github.com/AleksaC/hadolint-py/actions/workflows/add-new-versions.yml)
[![Run tests](https://github.com/AleksaC/hadolint-py/actions/workflows/tests.yml/badge.svg)](https://github.com/AleksaC/hadolint-py/actions/workflows/tests.yml)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

Un paquete de Python que proporciona un binario de
[hadolint](https://github.com/hadolint/hadolint) instalable mediante pip.

El mecanismo mediante el cual se descarga el binario está básicamente copiado de
[shellcheck-py](https://github.com/shellcheck-py/shellcheck-py).

## Primeros pasos

### Instalación

El paquete aún no se ha publicado en PyPI, y es posible que nunca lo haga, ya que su propósito
principal no lo requiere. Sin embargo, puedes instalarlo a través de git:

```shell script
pip install git+https://github.com/AleksaC/hadolint-py.git@v2.15.1
```

Para instalar otra versión simplemente reemplaza v2.15.1 con la versión que desees.

### Con pre-commit

Este paquete se creó principalmente para proporcionar una forma conveniente de ejecutar hadolint
como un gancho de [pre-commit](https://pre-commit.com), ya que pre-commit no soporta
haskell. Una alternativa a esta solución es crear un gancho de docker, ya que
hadolint proporciona una imagen de docker, pero considero que esto añade una sobrecarga innecesaria.

Ejemplo de `.pre-commit-config.yaml` con las reglas `DL3025` y `DL3018` excluidas:

```yaml
repos:
  - repo: https://github.com/AleksaC/hadolint-py
    rev: v2.15.1
    hooks:
      - id: hadolint
        args: [--ignore, DL3025, --ignore, DL3018]
```

## Contacto 🙋‍♂️

-   [Sitio web personal](https://aleksac.me)
-   <a target="_blank" href="http://twitter.com/aleksa_c_"><img alt='Twitter followers' src="https://img.shields.io/twitter/follow/aleksa_c_.svg?style=social"></a>
-   aleksacukovic1@gmail.com
