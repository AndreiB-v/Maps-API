import math
import os
import sys
import json

import pygame as pg
import requests
import numpy as np

# Теперь все get запросы делать через переменную session, если нужно часто обращаться к одному и тому же сайту!!
session = requests.session()


class Settings:
    def __init__(self):
        with open("settings.json", encoding='utf8') as file:
            self.settings = json.load(file)

    def save(self) -> None:
        with open("settings.json", "w", encoding='utf8') as file:
            json.dump(self.settings, file, ensure_ascii=False, indent=2)

    # ___ПОЧТОВЫЙ ИНДЕКС___ #
    def index(self) -> bool:
        return self.settings['is_index']

    def change_index(self) -> None:
        self.settings["is_index"] = True if self.index() is False else False

    # ___ВИД КАРТЫ___ #
    def view(self) -> list:
        return self.settings['view']

    def change_view(self, param: str) -> None:
        """Sender in ('road', 'transit', 'admin')"""

        if param in self.settings["view"]:
            self.settings["view"].remove(param)
        else:
            self.settings["view"].append(param)

    # ___ТЕМА КАРТЫ___ #
    def theme(self) -> str:
        return self.settings['theme']

    def change_theme(self) -> None:
        self.settings["theme"] = "dark" if self.theme() == "light" else "light"

    # ___ЦЕНТР КАРТЫ___ #
    def center(self) -> list[int, int]:
        return self.settings['center']

    def change_center(self, new_center: np.array or list):
        self.settings["center"] = list(new_center)

    # ___РАЗМЕР КАРТЫ___ #
    def spn(self) -> list[list[int, int], list[int, int]]:
        return self.settings['spn']

    def change_spn(self, new_spn: np.array or list):
        self.settings["spn"] = list(new_spn)

    # ___ТЕКУЩИЙ ОБЪЕКТ ПОИСКА___ #
    def find_object(self):
        return self.settings['object']

    def find_object_name(self):
        return self.settings['object_name']

    def change_find_object(self, new_position: list):
        self.settings['object'] = new_position

    def change_find_object_name(self, new_name: str):
        self.settings['object_name'] = new_name

    # ___ЯВЛЯЕТСЯ ЛИ ОБЪЕКТ ПОИСКА ОРГАНИЗАЦИЕЙ___ #
    def organization(self):
        return self.settings['is_organization']

    def change_organization(self, value: bool):
        self.settings['is_organization'] = value


class GeoSagest:
    def __init__(self,
                 api_key: str,
                 settings: Settings):
        self.api_key = api_key
        self.server = "https://search-maps.yandex.ru/v1/"

    def get_json(self, **params) -> dict:
        """
        Получить ближайшие географические объекты
        Подробнее: https://yandex.ru/maps-api/docs/suggest-api/request.html
        """
        search_params = {"apikey": self.api_key,
                         "text": "организация",
                         "lang": "ru_RU"}
        for key, param in params.items():
            search_params[key] = param
        response = session.get(self.server, params=search_params)
        return response.json()


class Geocoder:
    def __init__(self,
                 api_key: str,
                 settings: Settings):
        self.api_key = api_key
        self.server = 'http://geocode-maps.yandex.ru/1.x/?'
        self.settings = settings

    def get_json(self, **params) -> dict:
        """
        Получить ближайшие географические объекты по адресу
        Подробнее: https://yandex.ru/maps-api/docs/geocoder-api/response.html
        """
        search_params = {"apikey": self.api_key,
                         "lang": "ru_RU",
                         "format": "json"}
        for key, param in params.items():
            search_params[key] = param
        response = session.get(self.server, params=search_params)
        return response.json()


class StaticAPI:
    def __init__(self,
                 api_key: str,
                 settings: Settings):
        self.api_key = api_key
        self.server = 'https://static-maps.yandex.ru/v1?'

        self.settings = settings

    def get_image(self) -> pg.surface.Surface:
        # ___ПАРАМЕТРЫ ПОИСКА___ #
        coord = self.settings.center()
        spn = self.settings.spn()
        view = self.settings.view()
        find_object = self.settings.find_object()
        search_params = {'apikey': self.api_key,
                         'theme': self.settings.theme(),
                         'll': f'{coord[0]},{coord[1]}',
                         'spn': f'{spn[0]},{spn[1]}',
                         'size': f'650,450'}

        if find_object:
            search_params['pt'] = f'{find_object[0]},{find_object[1]},ya_ru'

        # ___ВИД КАРТЫ___ #
        style = []
        if "road" in view:
            style.append(
                'tags.all:road|elements:geometry.fill|stylers.color:32CD32~tags.all:poi|elements:label|stylers.visibility:off~tags.all:transit|elements:label|stylers.visibility:off')
        if 'admin' in view:
            style.append(
                'tags.any:road;poi;transit|elements:geometry|stylers.visibility:off~tags.any:road;poi;transit|elements:label|stylers.visibility:off')
        if "transit" in view:
            style.append(
                'tags.any:road;poi;admin|elements:geometry|stylers.visibility:off~tags.any:road;poi|elements:label|stylers.visibility:off')
        if style:
            search_params['style'] = '~'.join(style)

        # ___ПОЛУЧАЕМ КАРТУ___ #
        response = session.get(self.server, params=search_params)
        map_file = "map.png"
        with open(map_file, "wb") as file:
            file.write(response.content)
        current_image = pg.image.load(map_file)
        os.remove(map_file)

        return current_image


def get_bbox_by_name(object_name: str) -> tuple:
    """Возвращает границы области, в которую входит объект"""

    toponym = get_object_json(object_name)
    if toponym is not None:
        bbox = toponym['featureMember'][0]['GeoObject']['boundedBy']['Envelope']
        x1, y1 = (float(i) for i in bbox['lowerCorner'].split())
        x2, y2 = (float(i) for i in bbox['upperCorner'].split())
        return (x1, y1), (x2, y2)


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


def json_value(find_key: str, json_items: dict or list, result, non_key=''):
    if type(json_items) == dict:
        if find_key in json_items.keys():
            result.append(json_items[find_key])
        for key in json_items.keys():
            if key not in non_key:
                json_value(find_key, json_items[key], result, non_key)
    elif type(json_items) == list:
        for item in json_items:
            if type(item) == dict:
                json_value(find_key, item, result, non_key)
    return result


def lonlat_distance(a, b):
    degree_to_meters_factor = 111 * 1000  # 111 километров в метрах
    a_lon, a_lat = a
    b_lon, b_lat = b

    # Берем среднюю по широте точку и считаем коэффициент для нее.
    radians_lattitude = math.radians((a_lat + b_lat) / 2.)
    lat_lon_factor = math.cos(radians_lattitude)

    # Вычисляем смещения в метрах по вертикали и горизонтали.
    dx = abs(a_lon - b_lon) * degree_to_meters_factor * lat_lon_factor
    dy = abs(a_lat - b_lat) * degree_to_meters_factor

    # Вычисляем расстояние между точками.
    distance = math.sqrt(dx * dx + dy * dy)

    return distance
