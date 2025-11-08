from prometheus_client import start_http_server, Gauge, Counter, Histogram
import requests
import time
import random
from datetime import datetime

CITIES = {
    'Almaty': {'lat': '43.2567', 'lon': '76.9286'},
    'Astana': {'lat': '51.1694', 'lon': '71.4491'},
    'Moscow': {'lat': '55.7558', 'lon': '37.6173'},
    'London': {'lat': '51.5074', 'lon': '-0.1278'}
}

API_KEY = "b07973546d5ae189e0c06d8f92629a7e"

temperature = Gauge('weather_temperature_celsius', 'Temperature in Celsius', ['city'])
humidity = Gauge('weather_humidity_percent', 'Humidity percentage', ['city'])
pressure = Gauge('weather_pressure_hpa', 'Pressure in hPa', ['city'])
wind_speed = Gauge('weather_wind_speed_mps', 'Wind speed in m/s', ['city'])
cloudiness = Gauge('weather_cloudiness_percent', 'Cloudiness percentage', ['city'])
visibility = Gauge('weather_visibility_m', 'Visibility in meters', ['city'])
feels_like = Gauge('weather_feels_like_celsius', 'Feels like temperature', ['city'])
temp_min = Gauge('weather_temp_min_celsius', 'Minimum temperature', ['city'])
temp_max = Gauge('weather_temp_max_celsius', 'Maximum temperature', ['city'])
wind_direction = Gauge('weather_wind_direction_degrees', 'Wind direction', ['city'])

api_response_time = Histogram('api_response_time_seconds', 'API response time', ['city'])
weather_requests_total = Counter('weather_requests_total', 'Total weather API requests', ['city'])
failed_requests = Counter('failed_requests_total', 'Total failed API requests', ['city'])
temperature_change = Gauge('weather_temperature_change_5m', 'Temperature change over 5 minutes', ['city'])
pressure_trend = Gauge('weather_pressure_trend_hpa', 'Pressure trend per hour', ['city'])

def fetch_weather_for_city(city_name, lat, lon):
    try:
        start_request = time.time()
        url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"
        response = requests.get(url, timeout=10)
        api_response_time.labels(city=city_name).observe(time.time() - start_request)
        
        weather_requests_total.labels(city=city_name).inc()
        data = response.json()

        main = data['main']
        wind = data['wind']
        clouds = data['clouds']

        temperature.labels(city=city_name).set(main['temp'])
        humidity.labels(city=city_name).set(main['humidity'])
        pressure.labels(city=city_name).set(main['pressure'])
        wind_speed.labels(city=city_name).set(wind['speed'])
        cloudiness.labels(city=city_name).set(clouds['all'])
        visibility.labels(city=city_name).set(data.get('visibility', 0))
        feels_like.labels(city=city_name).set(main['feels_like'])
        temp_min.labels(city=city_name).set(main['temp_min'])
        temp_max.labels(city=city_name).set(main['temp_max'])
        wind_direction.labels(city=city_name).set(wind.get('deg', 0))
        current_time = time.time()
        if hasattr(fetch_weather_for_city, 'last_temps'):
            if city_name in fetch_weather_for_city.last_temps:
                change = main['temp'] - fetch_weather_for_city.last_temps[city_name]['temp']
                temperature_change.labels(city=city_name).set(change)
         
                pressure_trend_value = (main['pressure'] - 1013) / 10
                pressure_trend.labels(city=city_name).set(pressure_trend_value)
        
        if not hasattr(fetch_weather_for_city, 'last_temps'):
            fetch_weather_for_city.last_temps = {}
        fetch_weather_for_city.last_temps[city_name] = {'temp': main['temp'], 'time': current_time}
        
        print(f"Updated {city_name} weather: {main['temp']}°C at {datetime.now().strftime('%H:%M:%S')}")
        return True
        
    except Exception as e:
        failed_requests.labels(city=city_name).inc()
        print(f"Error fetching {city_name} weather: {e}")
        return False

def fetch_all_weather():
    for city, coords in CITIES.items():
        fetch_weather_for_city(city, coords['lat'], coords['lon'])
        time.sleep(2) 
if __name__ == "__main__":
    start_http_server(8010)
    print("Custom exporter running at http://localhost:8010/metrics")
    print(f"Monitoring weather for: {', '.join(CITIES.keys())}")

    while True:
        fetch_all_weather()
        time.sleep(20)