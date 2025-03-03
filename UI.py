import re

import pygame as pg
import pyperclip

import utils as ut


# Класс кнопки
class Button(pg.sprite.Sprite):
    def __init__(self, x, y, function, image, groups):
        super().__init__(groups)
        self.backup_image = image
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.function = function

        self.size_factor = (self.rect.width / 15, self.rect.height / 15)

    def update(self, *args):
        x, y = args[0]
        pressed = (self.rect.x <= x <= self.rect.x + self.rect.width
                   and self.rect.y <= y <= self.rect.y + self.rect.height)
        if self.image != self.backup_image and args[1] == 'up':
            self.image = self.backup_image
            self.rect.x -= self.size_factor[0] / 2
            self.rect.y -= self.size_factor[1] / 2
            if pressed:
                return self.function
        if pressed:
            if args[1] == 'down':
                self.image = pg.transform.scale(self.image,
                                                (self.rect.width - self.size_factor[0],
                                                 self.rect.height - self.size_factor[1]))
                self.rect.x += self.size_factor[0] / 2
                self.rect.y += self.size_factor[1] / 2
                return 'pressed'


# Класс чекбокса
class Checkbox(Button, pg.sprite.Sprite):
    """
    groups - группы для спрайта
    function - функция для изменения параметра на противоположный
    is_check - активна ли сейчас
    path - UI/checkbox/{path}/(inactive or active).png
    """

    def __init__(self, x, y, groups, function, is_check, path='default'):
        self.unselect = ut.load_image(f'UI/checkbox/{path}/inactive.png')
        self.select = ut.load_image(f'UI/checkbox/{path}/active.png')
        Button.__init__(self, x, y, function,
                        {True: self.select, False: self.unselect}[is_check], groups)
        self.function = function
        self.is_check = is_check

    def update(self, *args):
        function = Button.update(self, *args)
        if args[1] == 'up':
            if function is not None:
                self.is_check = not self.is_check
                self.backup_image = self.image = {True: self.select, False: self.unselect}[self.is_check]
                return function
        else:
            return function


class TextInput:
    def __init__(self, x, y, width, height):
        # Инициализация
        self.rect = pg.Rect(x, y, width, height)
        self.text = ""
        self.active = False  # Активное состояние поля ввода

        self.first_width = self.rect.width
        self.image = ut.load_image('UI/text_input/lens.png')

        try:
            self.font = pg.font.SysFont("notosansmonocjkjp", 24)
        except:
            print("Warninig: Japanese font not found. Using default font.")
            self.font = pg.font.Font(None, 24)

        self.color_inactive = pg.Color('gray')
        self.color_active = pg.Color('black')
        self.color = self.color_inactive

        self.barrier = ut.load_image('UI/text_input/barrier.png')
        self.barrier = pg.transform.scale(self.barrier, (self.barrier.get_width(), self.rect.height))
        self.background = ut.load_image('UI/text_input/background.png')
        self.background = pg.transform.scale(self.background, (self.background.get_width(), self.rect.height))

        # Для ввода IME
        self.composition = ""
        pg.key.start_text_input()
        pg.key.set_text_input_rect(self.rect)

    def handle_event(self, event):
        # Обработка щелчков мыши
        if event.type == pg.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.active = True
                pg.key.set_text_input_rect(self.rect)
            else:
                self.active = False
            self.color = self.color_active if self.active else self.color_inactive

        # Ограничить ширину текста
        if self.active:
            if event.type == pg.KEYDOWN:
                if event.key in (pg.K_RETURN, pg.K_KP_ENTER):
                    self.active = False
                    text = self.text
                    self.text = ""
                    return text
                if event.mod & pg.KMOD_CTRL:
                    if event.key == pg.K_v:
                        self.text += pyperclip.paste()
                if event.key == pg.K_BACKSPACE:
                    # Для быстрого удаления ctrl
                    if event.mod & pg.KMOD_CTRL:
                        with_sep = re.split('( )', self.text)
                        if with_sep[:-1]:
                            self.text = self.text[:-len(''.join(with_sep[-2:]))]
                        elif self.text.split():
                            self.text = self.text[:-len(with_sep[-1])]
                    else:
                        self.text = self.text[:-1]

            elif event.type == pg.TEXTINPUT:
                # Обычный ввод символов
                self.text += event.text

            elif event.type == pg.TEXTEDITING:
                # Текст вводится с помощью IME
                self.composition = event.text

    def draw(self, screen):
        # Нарисовать текст
        display_text = self.text + self.composition
        txt_surface = self.font.render(display_text, True, self.color)

        # Ограничить ширину текста
        width = max(self.first_width,
                    txt_surface.get_width() + self.rect.height + 20)
        self.rect.w = width

        # Рисунок
        self.background = pg.transform.scale(self.background,
                                             (self.rect.width - self.barrier.get_width() * 2,
                                              self.rect.height))

        screen.blit(self.barrier, (self.rect.x, self.rect.y))
        screen.blit(pg.transform.flip(self.barrier, True, False),
                    (self.rect.x + self.rect.width - self.barrier.get_width(), self.rect.y))
        screen.blit(self.background, (self.rect.x + self.barrier.get_width(), self.rect.y))
        screen.blit(self.image, (self.rect.x + 10, self.rect.y + 10))

        # blit текста
        screen.blit(txt_surface,
                    (self.rect.x + self.image.get_width() + 20,
                     self.rect.y + self.rect.height // 2 - txt_surface.get_height() // 2))


class TextField:
    def __init__(self, x, y, width, height):
        self.rect = pg.Rect(x, y, width, height)
        self.font = pg.font.SysFont("notosansmonocjkjp", 20)

        self.color_inactive = pg.Color('gray')
        self.color_active = pg.Color('black')
        self.color = self.color_active

        self.first_width = self.rect.width
        self.first_height = self.rect.height

        self.image = None

        self.text = ''
        self.set_text(self.text)

    def set_text(self, text) -> pg.surface.Surface:
        text = text.split('\n')
        surfaces = []
        height = 0
        width = 0
        for line in text:
            surface = self.font.render(line, True, self.color)
            if surface.get_width() > 200:
                string = line.split(' ')
                surface1 = self.font.render(' '.join(string[:len(string) // 2]), True, self.color)
                surface2 = self.font.render(' '.join(string[len(string) // 2:]), True, self.color)
                height += surface1.get_height() + surface2.get_height() + 20
                if surface1.get_width() > width:
                    width = surface1.get_width()
                if surface2.get_width() > width:
                    width = surface2.get_width()
                surfaces.append(surface1)
                surfaces.append(surface2)
            else:
                if surface.get_width() > width:
                    width = surface.get_width()
                height += surface.get_height() + 10
                surfaces.append(surface)

        self.rect.height = max(self.first_height, height + 20)
        self.rect.width = max(self.first_width, width + 40)
        self.image = pg.surface.Surface((self.rect.width, self.rect.height), pg.SRCALPHA)

        edge = ut.load_image('UI/text_field/edge.png')
        background = ut.load_image('UI/text_field/background.png')
        background = pg.transform.scale(background, (self.rect.width - edge.get_width() * 2,
                                                     self.rect.height - edge.get_height() * 2))
        horizontal = ut.load_image('UI/text_field/horizontal_barrier.png')
        horizontal = pg.transform.scale(horizontal, (self.rect.width - edge.get_width() * 2, horizontal.get_height()))
        vertical = ut.load_image('UI/text_field/vertical_barrier.png')
        vertical = pg.transform.scale(vertical, (vertical.get_width(), self.rect.height - edge.get_height() * 2))

        # Рисуем края
        self.image.blit(edge, (0, 0))
        self.image.blit(pg.transform.flip(edge, True, False), (self.rect.width - edge.get_width(), 0))
        self.image.blit(pg.transform.flip(edge, False, True), (0, self.rect.height - edge.get_height()))
        self.image.blit(pg.transform.flip(edge, True, True), (self.rect.width - edge.get_width(),
                                                              self.rect.height - edge.get_height()))

        # Рисуем бортики
        self.image.blit(horizontal, (edge.get_width(), 0))
        self.image.blit(pg.transform.flip(horizontal, False, True),
                        (edge.get_width(), self.rect.height - edge.get_height()))

        self.image.blit(vertical, (0, edge.get_height()))
        self.image.blit(pg.transform.flip(vertical, True, False),
                        (self.rect.width - edge.get_width(), edge.get_height()))

        self.image.blit(background, (edge.get_width(), edge.get_height()))

        # blit текста
        indent = 10
        for surface in surfaces:
            self.image.blit(surface, (20, indent))
            indent += surface.get_height() + 10

    def draw(self, screen):
        screen.blit(self.image, (self.rect.x, self.rect.y))
