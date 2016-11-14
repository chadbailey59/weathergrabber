from django.shortcuts import render
from django.template import loader
from tasks import get_weather

def index(request):
    cities_list = [
        {'name': 'Austin, TX', 'lat': 30.2672, 'long': -97.7431 },
        {'name': 'San Francisco, CA', 'lat': 37.7749, 'long': -122.4194 },
        {'name': 'Vancouver, BC', 'lat': 49.2827, 'long': 123.1207 },
        {'name': 'New York, NY', 'lat': 40.7128, 'long': -74.0059 },
    ]
    city_tasks = [get_weather.delay(city['lat'], city['long']) for city in cities_list]
    for index, city in enumerate(cities_list):
        cities_list[index]['temperature'] = city_tasks[index].get(timeout=2)

    template = loader.get_template('weather/index.html')
    context = {'cities_list': cities_list}
    return render(request, 'weather/index.html', context)

# Create your views here.
