# turl_street_group_assignment/celery.py
import os

from celery import Celery

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "turl_street_group_assignment.settings")

app = Celery("turl_street_group_assignment")

# Use Redis as the broker; look for an environment variable,
# and default to Redis using the service name from Docker Compose.
broker_url = os.environ.get("CELERY_BROKER_URL", "redis://redis:6379/0")
app.conf.broker_url = broker_url

# Load task modules from all registered Django app configs.
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
