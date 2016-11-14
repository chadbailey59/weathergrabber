web: gunicorn weathergrabber.wsgi --log-file -
worker: celery -A tasks worker --loglevel=info
