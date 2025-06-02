"""Modulo CLI princial de punto de entrada."""

from rich.console import Console


def main():
    """Función principal para ejecutar la CLI."""

    console = Console()
    console.print("Bienvenido a GraphQLStore CLI!", style="bold green")


if __name__ == "__main__":
    main()
