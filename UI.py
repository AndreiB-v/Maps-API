import pygame as pg
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
        self.unselect = ut.load_image('UI/checkbox/inactive.png', 'MENU')
        self.select = ut.load_image('UI/checkbox/active.png', 'MENU')
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
