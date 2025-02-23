import os
import sys
import json

import pygame as pg
import requests
import numpy as np

# Геокодер
server_address_geocode = 'http://geocode-maps.yandex.ru/1.x/?'
api_key_geocode = '8013b162-6b42-4997-9691-77b7074026e0'
# Геосаджет
server_address_geosadjet = 'https://search-maps.yandex.ru/v1/?'
api_key_geosadjet = 'dda3ddba-c9ea-4ead-9010-f43fbc15c6e3'
# Яндекс карты
server_address_card = 'https://static-maps.yandex.ru/v1?'
api_key_card = '096cd594-8239-4812-a4a9-176415d47f14'

# Теперь все get запросы делать через переменную session, если нужно часто обращаться к одному и тому же сайту!
session = requests.session()


def get_coord_by_name(object_name: str) -> np.array:
    """Функция для получения координат объекта по его названию"""

    toponym = get_object_json(object_name)
    if toponym is not None:
        toponym_coordinates = toponym["featureMember"][0]["GeoObject"]["Point"]["pos"]
        return np.array([float(i) for i in toponym_coordinates.split()])
    else:
        print(f'Не найдены координаты для {object_name}')


def get_bbox_by_name(object_name: str) -> tuple:
    """Возвращает границы области, в которую входит объект"""

    toponym = get_object_json(object_name)
    if toponym is not None:
        bbox = toponym['featureMember'][0]['GeoObject']['boundedBy']['Envelope']
        x1, y1 = (float(i) for i in bbox['lowerCorner'].split())
        x2, y2 = (float(i) for i in bbox['upperCorner'].split())
        return (x1, y1), (x2, y2)


def get_organization_json(object_name: str) -> dict or None:
    """Получить JSON объекта из геокодера на уровне GeoObjectCollection"""
    # https://yandex.ru/maps-api/docs/geosearch-api/response.html

    try:
        request = f'{server_address_geosadjet}apikey={api_key_geosadjet}&text={object_name}&format=json&type=biz&lang=ru_RU'
        print(request)
        response = requests.get(request)
        json_response = response.json()
        print(json_response)
        # return toponym
    except Exception:
        return None


def get_object_json(object_name: str) -> dict or None:
    """Получить JSON объекта из геокодера на уровне GeoObjectCollection"""

    try:
        geocoder_request = f'{server_address_geocode}apikey={api_key_geocode}&geocode={object_name}&format=json'
        response = requests.get(geocoder_request)

        # Получаем координаты объекта
        json_response = response.json()
        toponym = json_response["response"]["GeoObjectCollection"]
        return toponym
    except Exception:
        return None


def get_image(coord: tuple, spn: tuple, bbox=None, is_mark=None) -> pg.surface.Surface:
    """Функция для отображения карты по заданным координатам"""

    # Получаем цвет темы
    theme = get_theme()

    map_request = f"{server_address_card}apikey={api_key_card}" \
                  f"&ll={coord[0]},{coord[1]}&spn={spn[0]},{spn[1]}&size=650,450&theme={theme}"

    # is_mark - нужна ли метка на карте или нет
    if is_mark is not None:
        map_request += f"&pt={coord[0]},{coord[1]},pm2vvl1"

    if bbox is not None:
        x1, y1 = bbox[0]
        x2, y2 = bbox[1]
        map_request += f'&bbox={x1},{y1}~{x2},{y2}'

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


def change_theme() -> None:
    """Функция вызываемая кнопкой изменения темы"""

    # Получаем json
    with open("settings.json") as file:
        settings = json.load(file)

    theme = settings["theme"]
    settings["theme"] = "dark" if theme == "light" else "light"

    # Записываем в json
    with open("settings.json", "w") as file:
        json.dump(settings, file)


def get_theme() -> str:
    """Получить текущую тему"""

    with open("settings.json") as file:
        settings = json.load(file)
    return settings['theme']


# Функция для добавления изображений
def load_image(filename=str, mode=()) -> pg.surface.Surface:
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
