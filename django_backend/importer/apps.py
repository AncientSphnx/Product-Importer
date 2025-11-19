"""Importer app configuration."""
from django.apps import AppConfig


class ImporterConfig(AppConfig):
    """Importer app config."""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'importer'
