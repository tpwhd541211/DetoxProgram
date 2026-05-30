import os
import sys

try:
    from celery import Celery
except ImportError:
    # Fallback mock for Celery if not installed, allows running via BackgroundTasks
    class DummyConf:
        def update(self, **kwargs): pass
    class DummyCelery:
        def __init__(self, *args, **kwargs):
            self.conf = DummyConf()
        def task(self, *args, **kwargs):
            def decorator(func):
                func.delay = lambda *a, **kw: func(None, *a, **kw) if 'bind' in kwargs and kwargs['bind'] else func(*a, **kw)
                return func
            return decorator
    Celery = DummyCelery
    sys.modules['celery'] = type('dummy_celery', (object,), {'Celery': Celery})

# Use Redis as the broker and result backend (fallback to memory for local dev if not defined)
BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")

celery_app = Celery(
    "detox_worker",
    broker=BROKER_URL,
    backend=RESULT_BACKEND,
    include=["workers.parser_tasks"]
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Seoul",
    enable_utc=True,
    # Local dev fallback config
    task_always_eager=os.getenv("CELERY_ALWAYS_EAGER", "True").lower() in ("true", "1", "t")
)
