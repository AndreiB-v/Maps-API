import pygame
import utils as ut

server_address = 'https://static-maps.yandex.ru/v1?'
api_key = 'f3a0fe3a-b07e-4840-a1da-06f18b2ddf13'

spn = '&spn='
coordinates = [29.975970, 31.130784]
current_spn = [0.003, 0.003]
factor = 1

# Инициализируем pygame
pygame.init()
screen = pygame.display.set_mode((600, 450))

clock = pygame.time.Clock()
running = True
fps = 60

current_image = ut.get_image(coordinates, current_spn)


while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                current_spn[0] += 2 ** factor * 0.0005
                current_spn[1] += 2 ** factor * 0.0005
                factor += 1
            if event.key == pygame.K_DOWN:
                current_spn[0] -= 2 ** factor * 0.0005
                current_spn[1] -= 2 ** factor * 0.0005
                factor -= 1
            current_image = ut.get_image(coordinates, current_spn)
    screen.blit(current_image, (0, 0))
    pygame.display.flip()
    clock.tick(fps)
pygame.quit()
