from prometheus_client import start_http_server, Gauge, Counter, Histogram, Info
import requests
import time
import random
from datetime import datetime

API_KEY = "b07973546d5ae189e0c06d8f92629a7e"
CITY = "Almaty"
WEATHER_URL = f"http://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={API_KEY}&units=metric"

temperature = Gauge('weather_temperature_celsius', 'Current temperature in Celsius')
humidity = Gauge('weather_humidity_percent', 'Current humidity in %')
pressure = Gauge('weather_pressure_hpa', 'Current pressure in hPa')
wind_speed = Gauge('weather_wind_speed_mps', 'Wind speed in m/s')
cloudiness = Gauge('weather_cloudiness_percent', 'Cloudiness in %')
visibility = Gauge('weather_visibility_m', 'Visibility in meters')
feels_like = Gauge('weather_feels_like_celsius', 'Feels like temperature')
temp_min = Gauge('weather_temp_min_celsius', 'Minimum temperature')
temp_max = Gauge('weather_temp_max_celsius', 'Maximum temperature')
wind_direction = Gauge('weather_wind_direction_degrees', 'Wind direction in degrees')

# Additional custom metrics
api_response_time = Histogram('api_response_time_seconds', 'API response time')
weather_requests_total = Counter('weather_requests_total', 'Total weather API requests')
failed_requests = Counter('failed_requests_total', 'Total failed API requests')
system_uptime = Gauge('exporter_uptime_seconds', 'Exporter uptime in seconds')
random_metric = Gauge('random_metric_value', 'Random metric for testing')
timestamp = Gauge('last_successful_update_timestamp', 'Timestamp of last successful update')

start_time = time.time()

def fetch_weather():
    try:
        start_request = time.time()
        response = requests.get(WEATHER_URL, timeout=10)
        api_response_time.observe(time.time() - start_request)
        
        weather_requests_total.inc()
        data = response.json()

        main = data['main']
        wind = data['wind']
        clouds = data['clouds']
        weather_info = data['weather'][0]

        # Set all weather metrics
        temperature.set(main['temp'])
        humidity.set(main['humidity'])
        pressure.set(main['pressure'])
        wind_speed.set(wind['speed'])
        cloudiness.set(clouds['all'])
        visibility.set(data.get('visibility', 0))
        feels_like.set(main['feels_like'])
        temp_min.set(main['temp_min'])
        temp_max.set(main['temp_max'])
        wind_direction.set(wind.get('deg', 0))
        
        # Set additional metrics
        random_metric.set(random.uniform(0, 100))
        system_uptime.set(time.time() - start_time)
        timestamp.set(time.time())
        
        print(f"Updated weather metrics for {CITY} at {datetime.now()}")
        
    except Exception as e:
        failed_requests.inc()
        print(f"Error fetching weather data: {e}")

if __name__ == "__main__":
    start_http_server(8010)
    print("Custom exporter running at http://localhost:8010/metrics")
    print(f"Monitoring weather for: {CITY}")

    while True:
        fetch_weather()
        time.sleep(20)