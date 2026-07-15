from celery import Task


class CeleryBaseTask(Task):
    autoretry_for = (Exception,)
    max_retries = 5
    retry_backoff = True
    retry_backoff_max = 600
    retry_jitter = True
    acks_late = True
