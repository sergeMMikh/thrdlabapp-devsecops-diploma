import requests
from pprint import pprint

url = 'http://127.0.0.1:8000/api/v1/'
TOKEN = None

# Регистрация

request = requests.post(f'{url}user/register',
                        data={
                            "first_name": "magaz",
                            "last_name": "magaz7",
                            "email": "student@mail.ru",
                            "password": "qwer2345",
                        })
if request.status_code == 200:
    data_str = request.json()
    print("request:")
    pprint(data_str)
else:
    print(f'request: {request}')

# Вход
request = requests.post(f'{url}user/login',
                        data={
                            "email": "student@mail.ru",
                            "password": "qwer2345",
                        },
                        )
if request.status_code == 200:
    data_str = request.json()
    print("request:")
    pprint(data_str)

    TOKEN = data_str.get('Token')
    print(f'TOKEN: {TOKEN}')
else:

    print(f'request: {request.status_code}')
    data_str = request.raw


