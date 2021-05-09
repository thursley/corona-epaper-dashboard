import json
import requests
import os

api_key = os.environ.get('OWM_API_KEY')

kelvin_offset = -273.15
city = 'Jena'

rsp = requests.get(f'https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}')
if not rsp.ok:
    print(f'warning: could not retrieve weather data for {city}.')
    data = None
else:
    data = json.loads(rsp.content)

def get_temperature():
    if None == data:
        return -99.0
    else:
        temperature_c = round(data['main']['temp'] + kelvin_offset, 1)
        return temperature_c

def get_icon_name():
    try:
        return data['weather'][0]['icon']
    except:
        return 'alien'

if __name__ == '__main__':
    print(f'{get_temperature()} °C')

