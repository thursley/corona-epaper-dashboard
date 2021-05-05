import json
import requests
import os

api_key = os.environ.get('OWM_API_KEY')

kelvin_offset = -273.15
city = 'Jena'

rsp = requests.get(f'https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}')
if not rsp.ok:
    print(f'could not retrieve weather data for {city}. abort.')
    exit(1)

data = json.loads(rsp.content)
print(data)

def get_temperature():
    temperature_c = round(data['main']['temp'] + kelvin_offset, 1)
    return temperature_c

def get_icon_name():
    try:
        return data['weather'][0]['icon']
    except:
        return 'alien'

if __name__ == '__main__':
    print(f'{get_temperature()} °C')

