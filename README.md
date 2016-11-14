# WEATHERGRABBER

The file you probably want is [rate_limiter.py](rate_limiter.py).

I might have gone a little overboard with this. This is a Django app that uses Celery workers to hit the Dark Sky API in parallel (using `requests`, of course) to get the temperature in a few different places. You can control the rate limiting with the 
