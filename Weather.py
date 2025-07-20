import requests

city = input('Input the city name: ')
print(city)
print(f'Displaying weather report for {city} city')

url = 'https://wttr.in/{}'.format(city)
res = requests.get(url)

print(res.text)
