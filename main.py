import pygame as pg
import utils as ut
import numpy as np
import UI

settings = ut.Settings()
geo_sagest = ut.GeoSagest('dda3ddba-c9ea-4ead-9010-f43fbc15c6e3', settings)
static_api = ut.StaticAPI('f3a0fe3a-b07e-4840-a1da-06f18b2ddf13', settings)
geocoder = ut.Geocoder('8013b162-6b42-4997-9691-77b7074026e0', settings)

# Инициализируем pygame
pg.init()
screen = pg.display.set_mode((1080, 720))
pg.display.set_caption('Yandex Maps API')
pg.display.set_icon(pg.image.load('data/icon.png'))

clock = pg.time.Clock()
running = True
fps = 60

factor = 1.7

button_layer = pg.sprite.Group()
find_layer = pg.sprite.Group()
all_sprites = pg.sprite.Group()

UI.Checkbox(6, 660,
            (all_sprites, button_layer),
            settings.change_theme,
            {'light': False, 'dark': True}[settings.theme()],
            path='theme')
UI.Checkbox(6 * 2 + 54, 660,
            (all_sprites, button_layer),
            lambda: settings.change_view('admin'),
            True if 'admin' in settings.view() else False,
            path='admin')
UI.Checkbox(6 * 3 + 54 * 2, 660, (all_sprites, button_layer),
            lambda: settings.change_view('road'),
            True if 'road' in settings.view() else False,
            path='road')
UI.Checkbox(6 * 4 + 54 * 3, 660, (all_sprites, button_layer),
            lambda: settings.change_view('transit'),
            True if 'transit' in settings.view() else False,
            path='transit')

text_input = UI.TextInput(6, 6, 217, 54)
text_field = UI.TextField(6, 12 + 54, 217, 54)


def close_open_field():
    if text_field.first_height == text_field.rect.height:
        text_field.set_text(text_field.text)
    else:
        text_field.set_text('РЕЗУЛЬТАТ ПОИСКА:')


def drop_find():
    if len(find_layer):
        find_layer.empty()
        settings.change_find_object([])
        settings.change_find_object_name('')

        text_field.set_text('')
        text_field.rect.x = 6


def change_indexing():
    global current_image
    settings.change_index()
    result = geo_sagest.get_json(**{"text": settings.find_object_name(), "type": "geo"})
    name = list(map(lambda x: f'Адрес: "{x}"', ut.json_value('text', result, [])))
    set_find(name, settings.organization())


def set_find(name: list, org: bool):
    """
    Функция ставит текущее значение поиска
    list - все найденные объекты (объект поиска - 1 значение)
    org - являются ли объекты поиска организациями
    """
    global current_image
    if name:
        if settings.index():
            for n in range(len(name)):
                index = ut.json_value('postal_code', geocoder.get_json(**{'geocode': name[n]}), [])
                if index:
                    name[n] += f', Почтовый индекс: {index[0]}'
                else:
                    name[n] += ', Почтовый индекс: нет'
        string = '\n'.join(['РЕЗУЛЬТАТ ПОИСКА:'] + ['• ' + '\n• '.join(name)])
        text_field.set_text(string)
        text_field.text = string
        text_field.rect.x = 12 + 54
        settings.change_find_object_name(name[0])

        if org:
            settings.change_organization(True)
        else:
            settings.change_organization(False)

        find_layer.empty()
        UI.Checkbox(6, 54 + 6 * 2, find_layer,
                    close_open_field,
                    True, path='arrow')
        UI.Button(6, 54 * 2 + 6 * 3, drop_find,
                  ut.load_image(f'UI/buttons/drop.png'), find_layer)
        UI.Checkbox(6, 54 * 3 + 6 * 4, find_layer,
                    change_indexing,
                    settings.index(), path='index')
    else:
        drop_find()
        text_field.set_text('Ничего не нашлось')
        text_field.text = 'Ничего не нашлось'


if settings.find_object():
    result = geo_sagest.get_json(**{"text": settings.find_object_name(), "type": "geo"})
    name = list(map(lambda x: f'Адрес: "{x}"', ut.json_value('text', result, [])))
    set_find(name, settings.organization())

current_image = pg.transform.scale(static_api.get_image(), (screen.get_size()))

while running:
    events = pg.event.get()
    for event in events:
        if event.type == pg.QUIT:
            running = False
        # Поиск по результатам из text_input
        text = text_input.handle_event(event)
        if text is not None and text != "":
            result = geo_sagest.get_json(**{"text": text, "type": "geo"})
            name = list(map(lambda x: f'Адрес: "{x}"', ut.json_value('text', result, [])))
            set_find(name, False)

            if ut.json_value('found', result, [])[0]:
                coordinates = ut.json_value('coordinates', result, [])[0]
                settings.change_find_object(coordinates)
                settings.change_center(coordinates)
                bbox = ut.json_value('boundedBy', result, [])[0]
                x1, y1 = bbox[0]
                x2, y2 = bbox[1]
                settings.change_spn([(x2 - x1) * 0.36, (y2 - y1) * 0.36])
            current_image = pg.transform.scale(static_api.get_image(), (screen.get_size()))

        if not text_input.active:
            if event.type == pg.MOUSEBUTTONDOWN:
                for sprite in list(button_layer) + list(find_layer):
                    if sprite.update(event.pos, 'down') == 'pressed':
                        break
                else:
                    spn = settings.spn()
                    size = screen.get_size()
                    pos = event.pos
                    center = settings.center()
                    click = [center[0] + (spn[0] / (size[0] / 2)) * (pos[0] - size[0] / 2),
                             center[1] + (spn[1] / (size[1] / 2)) * (size[1] / 2 - pos[1])]
                    if event.button == 3:
                        result = geo_sagest.get_json(**{"type": "biz",
                                                        "ll": f'{click[0]},{click[1]}'})
                        values = list(zip(ut.json_value('name', ut.json_value('CompanyMetaData', result, []), [],
                                                        non_key=['Categories', 'Hours', 'Features']),
                                          ut.json_value('address', result, []),
                                          ut.json_value('coordinates', result, [])))
                        name = list(map(lambda x: f'Организация: "{x[0]}", Адрес: "{x[1]}"',
                                        filter(lambda x: ut.lonlat_distance(x[-1], click) <= 50, values)))
                        set_find(name, True)
                        settings.change_find_object(click)
                        current_image = pg.transform.scale(static_api.get_image(), (screen.get_size()))
                    elif event.button == 1:
                        result = geocoder.get_json(**{"geocode": f'{click[0]},{click[1]}'})
                        name = list(map(lambda x: f'Адрес: "{x}"', ut.json_value('formatted', result, [])))
                        set_find(name, False)

                        if ut.json_value('found', result, [])[0]:
                            coordinates = ut.json_value('pos', result, [])[0]
                            settings.change_find_object(list(map(lambda x: float(x), coordinates.split())))
                        current_image = pg.transform.scale(static_api.get_image(), (screen.get_size()))

            if event.type == pg.MOUSEBUTTONUP:
                for sprite in list(button_layer) + list(find_layer):
                    func = sprite.update(event.pos, 'up')
                    if func:
                        func()
                        current_image = pg.transform.scale(static_api.get_image(), (screen.get_size()))

    if not text_input.active:
        keys = pg.key.get_pressed()
        if keys[pg.K_PAGEUP] or keys[1073741921] or keys[pg.K_q]:
            if all(np.array(settings.spn()) * factor < 98):
                settings.change_spn(np.array(settings.spn()) * factor)
            current_image = pg.transform.scale(static_api.get_image(), (screen.get_size()))
        if keys[pg.K_PAGEDOWN] or keys[1073741915] or keys[pg.K_e]:
            if all(np.array(settings.spn()) / factor > 0):
                settings.change_spn(np.array(settings.spn()) / factor)
            current_image = pg.transform.scale(static_api.get_image(), (screen.get_size()))
        if keys[pg.K_RIGHT] or keys[pg.K_d]:
            if -179 < settings.center()[0] + settings.spn()[0] / 2 < 179:
                settings.settings['center'][0] += settings.spn()[0] / 2
            elif settings.center()[0] == 179:
                settings.settings['center'][0] = - 179
            else:
                settings.settings['center'][0] = 179
        if keys[pg.K_LEFT] or keys[pg.K_a]:
            if -179 < settings.center()[0] - settings.spn()[0] / 2 < 179:
                settings.settings['center'][0] -= settings.spn()[0] / 2
            elif settings.center()[0] == - 179:
                settings.settings['center'][0] = 179
            else:
                settings.settings['center'][0] = - 179
        if keys[pg.K_UP] or keys[pg.K_w]:
            if -80 < settings.center()[1] + settings.spn()[1] / 2 < 80:
                settings.settings['center'][1] += settings.spn()[1] / 2
            else:
                settings.settings['center'][1] = 80
        if keys[pg.K_DOWN] or keys[pg.K_s]:
            if -80 < settings.center()[1] - settings.spn()[1] / 2 < 80:
                settings.settings['center'][1] -= settings.spn()[1] / 2
            else:
                settings.settings['center'][1] = - 80
        # Общая проверка
        if any([keys[key] for key in [pg.K_PAGEUP, 1073741921, pg.K_PAGEDOWN, 1073741915, pg.K_RIGHT, pg.K_d,
                                      pg.K_LEFT, pg.K_a, pg.K_UP, pg.K_w, pg.K_DOWN, pg.K_s, pg.K_q, pg.K_e]]):
            current_image = pg.transform.scale(static_api.get_image(), (screen.get_size()))

    screen.fill((0, 0, 0))
    screen.blit(current_image, (0, 0))
    text_input.draw(screen)
    text_field.draw(screen)
    button_layer.draw(screen)
    find_layer.draw(screen)
    pg.display.flip()
    clock.tick(fps)
# Сохраняем настройки
settings.save()
pg.quit()
