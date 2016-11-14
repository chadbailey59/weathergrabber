from celery import Celery
import requests
import os
from rate_limiter import rate_limit

app = Celery('tasks', backend=os.environ.get('REDIS_URL'), broker=os.environ.get('REDIS_URL'))

# 37.8267,-122.4233
# os.environ.get('DARK_SKY_API_KEY'),

@app.task
@rate_limit
def get_weather(lat, long):
    r = requests.get("https://api.darksky.net/forecast/{0}/{1},{2}".format(os.environ.get('DARK_SKY_API_KEY'), lat, long))
    r.raise_for_status()
    return r.json()['currently']['temperature']
