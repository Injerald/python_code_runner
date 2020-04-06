# python_code_runner
Flask application to run python code using Celery, RabbitMQ, Websockets and docker SDK

# To run application
Flask - python python_code_runner/app.py
Websocket server - python python_code_runner/web_sockets.py
Celery worker - from project base directory celery -A python_code_runner.celery_tasks worker --loglevel=info (include -P eventlet if running on Windows)