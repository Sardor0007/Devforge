import os
import django
from django.core.management import call_command

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'devforge.settings')
django.setup()

print("Running makemigrations...")
call_command('makemigrations', 'learn')
print("Running migrate...")
call_command('migrate')
print("Done!")
