import os
import sys
import pygame
import requests
import math

server_address = 'https://static-maps.yandex.ru/v1?'
api_key = 'f3a0fe3a-b07e-4840-a1da-06f18b2ddf13'
ll_spn = 'll=135.746182,-27.483765&spn=20,20'


def get_map_image():
    map_request = f"{server_address}{ll_spn}&apikey={api_key}"
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

    return map_file


def get_organizations(lon, lat):
    # Здесь Вы можете использовать API для поиска организаций
    # Например, используя Yandex Places API
    # В этом примере мы просто вернем фиктивные данные
    # Замените этот код на реальный запрос к API
    return [{"name": "Организация 1", "lon": lon, "lat": lat}]


def distance(lat1, lon1, lat2, lon2):
    # Функция для вычисления расстояния между двумя точками
    R = 6371000  # Радиус Земли в метрах
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = math.sin(delta_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c  # Возвращаем расстояние в метрах


# Инициализируем pygame
pygame.init()
screen = pygame.display.set_mode((600, 450))
map_file = get_map_image()
screen.blit(pygame.image.load(map_file), (0, 0))
pygame.display.flip()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            os.remove(map_file)
            sys.exit()

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 3:  # Правая кнопка мыши
                x, y = event.pos
                # Преобразуем координаты пикселя в долготу и широту
                lon = 135.746182 + (x / 600) * 20  # Пример преобразования
                lat = -27.483765 - (y / 450) * 20  # Пример преобразования

                organizations = get_organizations(lon, lat)
                found_org = None

                for org in organizations:
                    if distance(lat, lon, org["lat"], org["lon"]) <= 50:
                        found_org = org
                        break

                if found_org:
                    print(f"Найдена организация: {found_org['name']}")
                else:
                    print("Организация не найдена в пределах 50 метров.")

    pygame.display.flip()
