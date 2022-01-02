from django.conf import settings

class Router:
    db_apps_map = settings.DB_ROUTING
    default_db = settings.DEFAULT_DB

    def _router(self, app_label, **hints):
        for db, apps in self.db_apps_map.items():
            if app_label in apps:
                return db
        return self.default_db

    def db_for_read(self, model, **hints):
        return self._router(model._meta.app_label, **hints)

    def db_for_write(self, model, **hints):
        return self._router(model._meta.app_label, **hints)

    def allow_relation(self, obj1, obj2, **hints):
        return self._router(obj1, **hints) == self._router(obj2, **hints)

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        return db == self._router(app_label,  **hints)
