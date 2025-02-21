import os
import sys
import pygame
import requests
import math

server_address = 'https://static-maps.yandex.ru/v1?'
api_key = 'f3a0fe3a-b07e-4840-a1da-06f18b2ddf13'
ll_spn = 'll=135.746182,-27.483765&spn=20,20'


def get_organizations(lon, lat):
    url = f"https://search-maps.yandex.ru/v1/?text=организация&ll={lon},{lat}&spn=0.01,0.01&apikey={api_key}&results=1"
    response = requests.get(url)

    if response.status_code == 200:
        return response.json().get('features', [])
    else:
        print("Ошибка выполнения запроса к Yandex Places API:", response.status_code)
        return []

def calculate_distance(lon1, lat1, lon2, lat2):
    R = 6371000
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = math.sin(delta_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c


pygame.init()
screen = pygame.display.set_mode((600, 450))

map_request = f"{server_address}{ll_spn}&apikey={api_key}"
response = requests.get(map_request)

if not response:
    print("Ошибка выполнения запроса:")
    print(map_request)
    print("Http статус:", response.status_code, "(", response.reason, ")")
    sys.exit(1)

map_file = "map.png"
with open(map_file, "wb") as file:
    file.write(response.content)

screen.blit(pygame.image.load(map_file), (0, 0))
pygame.display.flip()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            os.remove(map_file)
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 3:
                mouse_x, mouse_y = event.pos
                lon = 135.746182 + (mouse_x / 600) * 20
                lat = -27.483765 + (mouse_y / 450) * 20

                organizations = get_organizations(lon, lat)
                found = False

                for org in organizations:
                    org_lon = org['geometry']['coordinates'][0]
                    org_lat = org['geometry']['coordinates'][1]
                    distance = calculate_distance(lon, lat, org_lon, org_lat)

                    if distance <= 50:
                        print(f"Найдена организация: {org['properties']['name']}")
                        found = True
                        break

                if not found:
                    print("Организации не найдены в пределах 50 метров.")

pygame.quit()
os.remove(map_file)
