"""Modulo CLI princial de punto de entrada."""

from source.cli.main import CLI


def main():
    """Función principal para ejecutar la CLI."""

    cli = CLI()
    cli.ejecutar()


if __name__ == "__main__":
    main()
