import pygame
import utils as ut

from utils import get_coord_by_name

coordinates = str(get_coord_by_name("Красная площадь, 1")).split()
current_spn = [0.003, 0.003]

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
            if event.key == pygame.K_w:
                current_spn[0] += 2 * 0.0005
                current_spn[1] += 2 * 0.0005
            if event.key == pygame.K_s:
                current_spn[0] -= 2 * 0.0005
                current_spn[1] -= 2 * 0.0005
            if event.key == pygame.K_UP:
                print("Вверх")
            if event.key == pygame.K_DOWN:
                print("Вниз")
            if event.key == pygame.K_RIGHT:
                print("Вправо")
            if event.key == pygame.K_LEFT:
                print("Влево")
            current_image = ut.get_image(coordinates, current_spn)
    screen.blit(current_image, (0, 0))
    pygame.display.flip()
    clock.tick(fps)
pygame.quit()
