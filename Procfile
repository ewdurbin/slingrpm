redis: redis-server
worker: celery -A slingrpm.celery worker --loglevel=info
http: gunicorn --access-logfile - --error-logfile - slingrpm.server:APP
