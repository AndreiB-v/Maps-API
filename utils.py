import os
import sys

import pygame
import requests

# Геокодер
server_address_geocode = 'http://geocode-maps.yandex.ru/1.x/?'
api_key_geocode = '8013b162-6b42-4997-9691-77b7074026e0'
# Яндекс карты
server_address_card = 'https://static-maps.yandex.ru/v1?'
api_key_card = 'f3a0fe3a-b07e-4840-a1da-06f18b2ddf13'


def get_coord_by_name(object_name) -> str:
    '''Функция для получения координат объекта по его названию'''
    try:
        geocoder_request = f'{server_address_geocode}apikey={api_key_geocode}&geocode={object_name}&format=json'
        response = requests.get(geocoder_request)

        # Получаем координаты объекта
        json_response = response.json()
        toponym = json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
        toponym_coodrinates = toponym["Point"]["pos"]

        return type(toponym_coodrinates)

    except Exception:
        return "Название объекта на карте задано не верно"


def get_image(coord=tuple, spn=tuple) -> pygame.surface.Surface:
    map_request = f"{server_address_card}apikey={api_key_card}" \
                  f"&ll={coord[1]},{coord[0]}&spn={spn[0]},{spn[1]}"
    response = requests.get(map_request)

    if not response:
        print("Ошибка выполнения запроса:")
        print(map_request)
        print("Http статус:", response.status_code, "(", response.reason, ")")
        sys.exit(1)

    # Запишем полученное изображение в файл.
    map_file = "map.png"
    with open(map_file, "wb") as file:
        file.write(response.content)
    current_image = pygame.image.load(map_file)
    os.remove(map_file)
    return current_image
