import requests

params = {'v': '5.81',
          'access_token': '*',
          'extended': '1'}

url = "https://api.vk.com/method/groups.get?"
response = requests.get(url, params=params)
j_data = response.json()

for i in j_data["response"]["items"]:
    print(f"{i['name']}")
