"""Modulo CLI princial de punto de entrada."""

try:
    from source.cli.main import CLI
except ImportError:
    from cli.main import CLI  # type: ignore


def main():
    """Función principal para ejecutar la CLI."""

    cli = CLI()
    cli.ejecutar()


if __name__ == "__main__":
    main()
