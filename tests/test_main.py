"""Prueba para la función main del módulo source.main."""

import re
from source.main import main


def test_main_output(capfd):
    """Test the main function output."""
    main()
    out, _ = capfd.readouterr()

    # assert that the output contains the expected welcome message
    assert re.search(r"Bienvenido a GraphQLStore CLI!", out)
