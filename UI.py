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


# Класс чекбокса?
class Checkbox(Button, pg.sprite.Sprite):
    def __init__(self, x, y, groups, function, is_check=False):
        self.unselect = ut.load_image('UI/checkbox/inactive.png')
        self.select = ut.load_image('UI/checkbox/active.png')
        Button.__init__(self, x, y, function,
                        {True: self.select, False: self.unselect}[is_check], groups)
        self.function = function
        self.is_check = is_check

    def update(self, *args):
        function = Button.update(self, *args)
        if function is not None:
            self.is_check = not self.is_check
            self.backup_image = self.image = {True: self.select, False: self.unselect}[self.is_check]
            return function


class TextInput:
    def __init__(self, x, y, width, height):
        # Инициализация
        self.rect = pg.Rect(x, y, width, height)
        self.text = ""
        self.active = False  # Активное состояние поля ввода

        self.first_x = self.rect.x
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
        width = max(self.first_x,
                    txt_surface.get_width() + self.rect.height + 10)
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
