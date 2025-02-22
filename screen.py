import pygame as pg
import utils as ut
import numpy as np

from utils import get_coord_by_name

coordinates = str(get_coord_by_name("Красная площадь, 1")).split()
current_spn = np.array([0.003, 0.003])

# Инициализируем pygame
pg.init()
screen = pg.display.set_mode((650, 450))

clock = pg.time.Clock()
running = True
fps = 60

current_image = ut.get_image(coordinates, current_spn)

factor = 1.7


while running:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_w:
                print("Вверх")
                ut.change_theme() # Вызывать в чекбоксе
            if event.key == pg.K_s:
                print("Вниз")
            if event.key == pg.K_d:
                print("Вправо")
            if event.key == pg.K_a:
                print("Влево")
            current_image = ut.get_image(coordinates, current_spn)

    keys = pg.key.get_pressed()
    if keys[pg.K_UP]:
        if all(current_spn * factor < 98):
            current_spn *= factor
        current_image = ut.get_image(coordinates, current_spn)
    if keys[pg.K_DOWN]:
        if all(current_spn / factor > 0):
            current_spn /= factor
        current_image = ut.get_image(coordinates, current_spn)

    screen.blit(current_image, (0, 0))
    pg.display.flip()
    clock.tick(fps)
pg.quit()
