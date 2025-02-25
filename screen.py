import pygame as pg
import utils as ut
import numpy as np
import UI
from utils import get_full_address

coordinates = ut.get_coord_by_name("Красная площадь, 1")
current_spn = np.array([0.003, 0.003])
current_image = ut.get_image(coordinates, current_spn)

# Инициализируем pygame
pg.init()
screen = pg.display.set_mode((650, 450))

clock = pg.time.Clock()
running = True
fps = 60

factor = 1.7

button_layer = pg.sprite.Group()
all_sprites = pg.sprite.Group()

UI.Checkbox(6, 390, (all_sprites, button_layer), ut.change_theme, {'light': False, 'dark': True}[ut.get_theme()])
text_input = UI.TextInput(6, 6, 74, 54)

while running:
    events = pg.event.get()
    for event in events:
        if event.type == pg.QUIT:
            running = False

        # Поиск по результатам из text_input
        text = text_input.handle_event(event)
        if text is not None and text != "":
            coordinates = ut.get_coord_by_name(text)
            bbox = ut.get_bbox_by_name('+'.join(text.split()))
            x1, y1 = bbox[0]
            x2, y2 = bbox[1]
            current_spn = np.array([(x2 - x1) * 0.36, (y2 - y1) * 0.36])
            ut.change_is_mark()
            current_image = ut.get_image(coordinates, current_spn)
            print(get_full_address(text))

        if not text_input.active:
            if event.type == pg.KEYDOWN:

                # Перемещение по Y
                if event.key == pg.K_w:
                    if -80 < coordinates[1] + current_spn[1] / 2 < 80:
                        coordinates[1] += current_spn[1] / 2
                    else:
                        coordinates[1] = 80
                if event.key == pg.K_s:
                    if -80 < coordinates[1] - current_spn[1] / 2 < 80:
                        coordinates[1] -= current_spn[1] / 2
                    else:
                        coordinates[1] = - 80

                # Перемещение по X
                if event.key == pg.K_d:
                    if -179 < coordinates[0] + current_spn[0] / 2 < 179:
                        coordinates[0] += current_spn[0] / 2
                    elif coordinates[0] == 179:
                        coordinates[0] = - 179
                    else:
                        coordinates[0] = 179
                if event.key == pg.K_a:
                    if -179 < coordinates[0] - current_spn[0] / 2 < 179:
                        coordinates[0] -= current_spn[0] / 2
                    elif coordinates[0] == - 179:
                        coordinates[0] = 179
                    else:
                        coordinates[0] = - 179

                # Общая проверка
                if event.key in (pg.K_w, pg.K_s, pg.K_d, pg.K_a):
                    current_image = ut.get_image(coordinates, current_spn)
                    print(current_spn)

            if event.type == pg.MOUSEBUTTONDOWN:
                button_layer.update(event.pos, 'down')
            if event.type == pg.MOUSEBUTTONUP:
                for sprite in button_layer:
                    func = sprite.update(event.pos, 'up')
                    if func == ut.change_theme:
                        func()
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

    screen.fill((0, 0, 0))
    screen.blit(current_image, (0, 0))
    text_input.draw(screen)
    button_layer.draw(screen)
    pg.display.flip()
    clock.tick(fps)
pg.quit()
