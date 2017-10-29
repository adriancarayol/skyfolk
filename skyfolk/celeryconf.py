import os

RABBIT_HOSTNAME = os.environ.get('RABBIT_PORT_5672_TCP', 'rabbit')

RABBIT_HOSTNAME = 'rabbit'

if RABBIT_HOSTNAME.startswith('tcp://'):
    RABBIT_HOSTNAME = RABBIT_HOSTNAME.split('//')[1]

broker_url = os.environ.get('BROKER_URL',
                            '')

if not broker_url:
    broker_url = 'amqp://{user}:{password}@{hostname}/{vhost}/'.format(
        user=os.environ.get('RABBIT_ENV_USER', 'guest'),
        password=os.environ.get('RABBIT_ENV_RABBITMQ_PASS', 'guest'),
        hostname=RABBIT_HOSTNAME,
        vhost=os.environ.get('RABBIT_ENV_VHOST', ''))


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
