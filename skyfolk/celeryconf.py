import os

rabbitmq_host = os.environ.get('RABBITMQ_HOST', 'localhost')
broker_url = 'amqp://guest:guest@%s:5672/celery' % rabbitmq_host

accept_content = ['json']
task_serializer = 'json'
result_serializer = 'json'
enable_utc = True
result_cache_max = 32768
worker_disable_rate_limits = True
task_acks_late = True
broker_heartbeat = 0
result_backend = 'django-db'
result_persistent = True
result_compression = 'gzip'
broker_transport_options = {'visibility_timeout': 18000}
task_track_started = True
beat_scheduler = "django_celery_beat.schedulers:DatabaseScheduler"
timezone = 'Europe/Madrid'
