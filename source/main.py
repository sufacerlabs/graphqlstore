"""Modulo CLI princial de punto de entrada."""

try:
    # para produccio (pypi)
    from source.cli.main import CLI
except ImportError:
    # para desarrollo (local)
    from cli.main import CLI  # type: ignore[no-redef]


def main():
    """Función principal para ejecutar la CLI."""

    cli = CLI()
    cli.ejecutar()


if __name__ == "__main__":
    main()
