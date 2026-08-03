from django.apps import AppConfig


class WorkspaceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.workspace'
    verbose_name = 'Ish Maydoni'

    def ready(self):
        """
        Server ishga tushganda barcha workspace fayllarini
        DB dan diskka sinxronlash (Celery orqali background da).
        Bu server restart da disk fayllarini tiklaydi.
        """
        import sys
        # Skip database operations during management commands like migrate, test, etc.
        skip_commands = {'migrate', 'makemigrations', 'test', 'check', 'collectstatic', 'showmigrations', 'flush', 'sqlmigrate'}
        if any(cmd in sys.argv for cmd in skip_commands):
            return

        try:
            from django.db import connection
            # Migrations hali ishlamagan bo'lsa skip
            if 'apps_workspace' not in connection.introspection.table_names():
                return
            from apps.tasks import sync_all_workspaces
            sync_all_workspaces.delay()
        except Exception:
            # Celery worker ishlamayotgan bo'lsa — synchronous fallback
            try:
                from apps.workspace.models import Workspace
                from django.conf import settings
                import os
                for ws in Workspace.objects.all():
                    base_dir = settings.BASE_DIR / 'workspaces' / str(ws.pk)
                    os.makedirs(base_dir, exist_ok=True)
                    for f in ws.files.filter(is_folder=False):
                        rel = f.path.strip('/')
                        file_dir = base_dir / rel if rel else base_dir
                        os.makedirs(file_dir, exist_ok=True)
                        try:
                            with open(file_dir / f.name, 'w', encoding='utf-8') as fp:
                                fp.write(f.content or '')
                        except Exception:
                            pass
            except Exception:
                pass
