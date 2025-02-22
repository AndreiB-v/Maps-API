import os
import sys
import json

import pygame as pg
import requests

# Геокодер
server_address_geocode = 'http://geocode-maps.yandex.ru/1.x/?'
api_key_geocode = '8013b162-6b42-4997-9691-77b7074026e0'
# Яндекс карты
server_address_card = 'https://static-maps.yandex.ru/v1?'
api_key_card = 'f3a0fe3a-b07e-4840-a1da-06f18b2ddf13'

# Теперь все get запросы делать через переменную session, если нужно часто обращаться к одному и тому же сайту!
session = requests.session()


def get_coord_by_name(object_name=str) -> str:
    """Функция для получения координат объекта по его названию"""
    try:
        geocoder_request = f'{server_address_geocode}apikey={api_key_geocode}&geocode={object_name}&format=json'
        response = requests.get(geocoder_request)

        # Получаем координаты объекта
        json_response = response.json()
        toponym = json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
        toponym_coodrinates = toponym["Point"]["pos"]

        return toponym_coodrinates

    except Exception:
        return "Название объекта на карте задано не верно"


def get_image(coord=tuple, spn=tuple) -> pg.surface.Surface:
    """Функция для отображения карты по заданным координатам"""

    # Получаем цвет темы
    theme = get_theme()

    map_request = f"{server_address_card}apikey={api_key_card}" \
                  f"&ll={coord[0]},{coord[1]}&spn={spn[0]},{spn[1]}&size=650,450&theme={theme}"
    response = session.get(map_request)

    if not response:
        print("Ошибка выполнения запроса:")
        print(map_request)
        print("Http статус:", response.status_code, "(", response.reason, ")")
        sys.exit(1)

    # Запишем полученное изображение в файл.
    map_file = "map.png"
    with open(map_file, "wb") as file:
        file.write(response.content)
    current_image = pg.image.load(map_file)
    os.remove(map_file)

    return current_image


def change_theme():
    """Функция вызываемая кнопкой изменения темы"""

    # Получаем json
    with open("settings.json") as file:
        settings = json.load(file)

    theme = settings["theme"]
    settings["theme"] = "dark" if theme == "light" else "light"

    # Записываем в json
    with open("settings.json", "w") as file:
        json.dump(settings, file)

    import screen as sc
    sc.current_image = get_image(sc.coordinates, sc.current_spn)


def get_theme():
    with open("settings.json") as file:
        settings = json.load(file)
    return settings['theme']


# Функция для добавления изображений
def load_image(filename=str, mode=str) -> pg.surface.Surface:
    """Загружает изображение"""

    fullname = os.path.join('data', filename)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pg.image.load(fullname)

    if mode:
        # мод хромакея, удаляет задний фон
        if 'CHROMAKEY' in mode:
            image = image.convert()
            if mode == -1:
                color_key = image.get_at((0, 0))
            image.set_colorkey(color_key)
        image = image.convert_alpha()
    return image
