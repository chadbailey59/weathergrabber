# WEATHERGRABBER

## Try it at http://weathergrabber.herokuapp.com/weather/

The file you probably want to see is [rate_limiter.py](rate_limiter.py).

I might have gone a little overboard with this. This is a Django app that uses Celery workers to hit the Dark Sky API in parallel (using `requests`, of course) to get the temperature in a few different places. You can control the rate limiting with the `RATE_LIMIT_PERIOD_SECONDS` and `RATE_LIMIT_PER_PERIOD` environment variables. It's configured out of the box to only allow 2 requests every 10 seconds.

When you load [the demo page](http://weathergrabber.herokuapp.com/weather/), the app queues up 4 celery tasks to fetch the weather in Austin, SF, Vancouver, and New York. Based on the rate limiting settings, you'll either see temperatures or "None".

I'm sort of blowing away the whole notion of "asynchronous" by waiting for the celery tasks to complete to get the data for demo purposes. But hey, at least they run in parallel!

You can see a bit more of what's happening by tailing the app's logs. Feel free to also play around with the config vars to set different rate limits.

## A Brief Design Spec

Rate limiting across processes requires a shared external resource for coordination. Ideally, this resource would be accessible (1) atomically and (2) with relatively low latency by the rate-limited processes.

Fortunately, redis is about as low-latency as we can get on a platform like Heroku, and it has an atomic `INCR` operation which is pretty much perfect for what we need. `INCR` increments a counter and returns the value in a single operation. By creating a redis key based on the current unix time, we can monitor the counter and prevent API calls if the count goes too high. Additionally, we can send an extra command to automatically expire the counters after they're no longer needed.

The pattern I chose uses simple integer division to create redis keys. This allows for arbitrary reset periods from 1 second upwards. The main weakness with this particular approach is a first-time premature reset. Say the UNIX time of the first request is `1479104633` and we've set the reset period to 10 seconds. Since I chose integer division, the period will next reset at `1479104640` and every 10 seconds thereafter. But the first window is only 7 seconds long, which means it would be possible to send the maximum number of requests in only 7 seconds, reset the counter, and send the maximum number again in the next 3 seconds.

There are a variety of ways to design around this. For example, I could choose to store the initial counter time in redis and use it to calculate an offset. For example, using something like `offset = current_time % period` would give me an offset of `3` in the above example. Subsequent iterations could use `current_time - offset` as the redis key to ensure all periods are 10 seconds.

I considered setting the redis key expiration to the rate limiting period whenever the counter returned 1, but I think there are some edge cases that could prove unreliable.

Of course, all of the above solutions might be preferred depending on the fine-grained specifics of how the rate limiting is implemented on the API side. For this example, I chose a solution that I think would be acceptable in the vast majority of cases, since it only introduces the possibility for error in the first period of the rate limiter running.
