from django.apps import AppConfig

class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.core'

    def ready(self):
        from django.contrib import admin
        admin.site.site_header = "Finovo Administration"
        admin.site.site_title = "Finovo Admin Portal"
        admin.site.index_title = "Welcome to Finovo Admin Portal"
