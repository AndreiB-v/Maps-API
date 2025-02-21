import sys

import pygame
import requests

server_address = 'https://static-maps.yandex.ru/v1?'
api_key = 'f3a0fe3a-b07e-4840-a1da-06f18b2ddf13'

spn = '&spn='
coordinates = (29.975970, 31.130784)
current_spn = 0.003

# Инициализируем pygame
pygame.init()
screen = pygame.display.set_mode((600, 450))
n = 0

clock = pygame.time.Clock()
running = True
fps = 60

current_image = pygame.surface.Surface(screen.get_size())


while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                print(pygame.K_UP)
            n += 1
        else:
            map_request = f"{server_address}ll={coordinates[1]},{coordinates[0]}&spn={current_spn},{current_spn}&apikey={api_key}"
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
            print(current_image.__class__)
    screen.blit(current_image, (0, 0))
    pygame.display.flip()
    clock.tick(fps)
pygame.quit()
