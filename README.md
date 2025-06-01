# Documentacion del proyecto GraphQLStore

## Resumen del proyecto

GraphQLStore es una aplicacion CLI disenada para gestionar bases de datos
usando GraphQL. Esta etapa del proyecto es temprana, con una estructura basica.

## Estructura del proyecto

```
graphqlstore/
├── .github/workflows/      # configuracion CI/CD
├── source/                 # codigo fuente
├── tests/                  # archivos de prueba
└── (archivos de configuracion)
    ├── Pipfile              # gestion de dependencias
    ├── Pipfile.lock         # bloque de dependencias
    ├── pyproject.toml       # configuracion del proyecto y empaquetado
    ├── setup.cfg            # configuracion adicional de setuptools
    ├── pytest.ini           # configuracion de pytest
    ├── .pre-commit-config.yaml  # configuracion de pre-commit
    ├── .gitignore           # archivos ignorados por git
    └── README.md            # documentacion del proyecto
└── LICENSE                  # licencia del proyecto
```

## Implementacionn actual

### Funcionalidad principal

La aplicacion actualmente tiene una implementacion minima con:
- Un punto de entrada CLI simple en main.py que muestra un mensaje de bienvenida.
- Estructura basica del proyecto con directorios de codigo fuente y pruebas.

### Entorno de desarrollo

Las siguientes herramientas de desarrollo estan configuradas:

1. **Gestión de Paquetes**
   - Uso de Pipfile con pipenv para la gestión de dependencias
   - Dependencia principal: `rich` para una salida mejorada en terminal
   - Varias dependencias de desarrollo incluyendo herramientas de prueba y calidad de código

2. **Herramientas de calidad de código**
   - Configuración de `pre-commit` para hooks automáticos
   - Formateo de código con `black`
   - Análisis estático con `flake8` y `pylint`
   - Comprobación de tipos con `mypy`

3. **Pruebas**
   - Uso de `pytest` para ejecutar pruebas
   - `pytest-cov` para medir la cobertura de pruebas
   - Configuración de `pytest.ini` para generar informes de cobertura
   - Prueba simple en test_main.py que verifica el mensaje de bienvenida

4. **Configuración de empaquetado**
   - `pyproject.toml` para definir metadatos del proyecto, dependencias y configuraciones de herramientas
   - Punto de entrada  CLI configurado como `graphqlstore = "source.main:main"`
   - `setup.cfg` para configuraciones adicionales de setuptools, incluyendo referencia al archivo de licencia

### Flujo CI/CD

dos pipelines de CI/CD están configurados para automatizar el proceso de desarrollo y despliegue:

1. **CI Pipeline** (`.github/workflows/ci.yml`): 
   - Ejecuta pruebas y verifica la calidad del código en cada push a la rama principal o en pull requests.

2. **CD Pipeline** (`.github/workflows/cd.yml`):
   - Desencadenado por etiquetas de versión (v*.*.*)
   - Construye el paquete
   - Sube artefactos
   - Publica en PyPI
   - Crea lanzamientos en GitHub

### Licencia

El proyecto usa una licencia privada que prohíbe:
- Redistribución
- Modificación
- Creación de obras derivadas
- Uso comercial
- Compartición pública

## Inicio rápido

Con el fin de facilitar el inicio rápido del proyecto, se ha configurado un entorno de desarrollo con `pipenv`. Esto permite gestionar las dependencias y ejecutar scripts de manera sencilla.

```bash
# NOTA: Asegúrate de tener pipenv instalado. Si no lo tienes, puedes instalarlo con pip, pipx o tu gestor de paquetes preferido.

# Instalar las dependencias incluidas las de desarrollo
pipenv install --dev

# Opcionalmente, si necesitas una "primera linea de defensa" para la calidad del código, puedes ejecutar:
pipenv run pre-commit install

# Ejecutar las pruebas
pipenv run pytest

# Ejecutar el script principal
pipenv run python source/main.py
```

La otra es descargando el proyecto desde pypi:

```bash
# Instalar el paquete desde PyPI
pip install graphqlstore
# Ejecutar el comando CLI
graphqlstore
```

## Siguientes pasos

El proyecto está en una fase inicial de desarrollo. Los siguientes pasos incluyen:
- Expandir la intefaz CLI para incluir más comandos
- Implementar la funcionalidad de GraphQL
- Agregar capacidades de conexión a bases de datos
- Mejorar la documentación y ejemplos de uso
