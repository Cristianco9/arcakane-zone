"""Filtros comunes de la API."""
from rest_framework.filters import SearchFilter


class BusquedaFilter(SearchFilter):
    """Mantiene el parámetro ``q`` que ya usaba el catálogo HTML."""

    search_param = "q"
