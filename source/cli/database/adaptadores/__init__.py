"""Modulo de adaptadores específicos para bases de datos."""

from .mysql import AdaptadorMySQL
from .postgresql import AdaptadorPostgreSQL

__all__ = ["AdaptadorMySQL", "AdaptadorPostgreSQL"]
