import pygame
import utils as ut


coordinates = str(ut.get_coord_by_name("Красная площадь, 1")).split()
current_spn = [0.001, 0.001]
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
            if event.key == pygame.K_w:
                 if factor < 15:
                    current_spn[0] += 2 ** factor * 0.0005
                    current_spn[1] += 2 ** factor * 0.0005
                    factor += 1
            if event.key == pygame.K_s:
                if factor > 0:
                    current_spn[0] = 2 ** factor * 0.0005
                    current_spn[1] = 2 ** factor * 0.0005
                    factor -= 1
            if event.key == pygame.K_UP:
                print("Вверх")
                ut.change_theme()
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
