#!/usr/bin/python
# -*- encoding: utf-8 -*-

"""
chains.py

Chains Game - build chains of similar fruits
"""

__version__ = "1.0"
__author__ = "Michael Richter"
__copyright__ = "Copyright 2017, Michael Richter"

import pygame
import pygame.locals
import random
from math import floor

pygame.init()

"""
Configuration part
"""


class Config:
    """
    Configuration
    """
    left = 0
    top = 0
    fruitCount = 8
    fruitSize = 48
    fruitMargin = 8
    margin = 8
    size = [0, 0]
    fruitsDef = []
    fps = 30
    fallSpeed = 8  # 2 pixel per frame
    scoreBase = 1
    scoreFontSize = 32
    sounds = {}


Config.size = [
    (Config.fruitSize + Config.fruitMargin) * Config.fruitCount + Config.margin,
    (Config.fruitSize + Config.fruitMargin) * Config.fruitCount + Config.margin
]
Config.fruitsDef = [
    {'image': pygame.image.load('graphics/apple.png'), 'color': pygame.Color(255, 0, 0), 'size': Config.fruitSize},
    {'image': pygame.image.load('graphics/kiwi.png'), 'color': pygame.Color(0, 255, 0), 'size': Config.fruitSize},
    {'image': pygame.image.load('graphics/grape.png'), 'color': pygame.Color(0, 0, 255), 'size': Config.fruitSize},
    {'image': pygame.image.load('graphics/banana.png'), 'color': pygame.Color(255, 255, 0), 'size': Config.fruitSize}
]
Config.sounds = {
    'cleared': pygame.mixer.Sound('sounds/pling.wav'),
    'chaining': pygame.mixer.Sound('sounds/plop.wav')
}

"""
Game code part
"""


# TODO: Implement "no moves left" detection
# TODO: Implement not so ugly line drawing (Graphics class)

class Graphics:
    """
    Graphics helper
    """

    @staticmethod
    def line(start, end):
        pass


class Fruit(pygame.sprite.Sprite):
    """
    A fruit Sprite
    """

    def __init__(self, image, color, size):
        pygame.sprite.Sprite.__init__(self)
        self.image = image
        self.image = pygame.transform.scale(self.image, (size, size))
        self.color = color
        self.rect = self.image.get_rect()


class FruitFactory:
    """
    Create a random fruit
    """

    @staticmethod
    def create_fruit(config):
        tdef = config.fruitsDef[random.randint(0, len(config.fruitsDef) - 1)]
        fruit = Fruit(tdef['image'], tdef['color'], tdef['size'])
        return fruit


class Board:
    """
    The game board holding the fruits
    """

    def __init__(self, config):
        self.config = config
        self.fruits = pygame.sprite.Group()
        self.matrix = []
        self.isSpawning = False
        self.cleared_callback = None

        # create an empty board matrix
        self.matrix = [[None for x in range(self.config.fruitCount)] for y in range(self.config.fruitCount)]

    def on_cleared(self, len):
        """
        fired when fruits were cleared from the board
        :param len: count of ceared fruits
        """
        if not (self.cleared_callback is None):
            self.cleared_callback(len)

    def get_coord_by_pos(self, pos):
        """
        Get matrix coordinates by point
        :param pos: point tuple (x, y)
        :return: coordinates tuple (x, y)
        """
        x = floor((pos[0] - self.config.left - self.config.margin) / (self.config.fruitMargin + self.config.fruitSize))
        y = floor((pos[1] - self.config.left - self.config.margin) / (self.config.fruitMargin + self.config.fruitSize))
        if x < 0:
            x = 0
        elif x > self.config.fruitCount - 1:
            x = self.config.fruitCount - 1
        if y > self.config.fruitCount - 1:
            y = self.config.fruitCount - 1
        return x, y

    def get_pos_by_coord(self, coord):
        """
        Get points by matrix coordinates
        :param coord: coordinates tuple (x, y)
        :return: point tuple (x, y)
        """
        x = self.config.left + self.config.margin + (self.config.fruitMargin + self.config.fruitSize) * coord[
            0]
        y = self.config.top + self.config.margin + (self.config.fruitMargin + self.config.fruitSize) * coord[
            1]
        return x, y

    def clear_fruits(self, chain):
        """
        Remove fruits from board
        :param chain: a list of coordinates of the selected fruits
        """
        for coord in chain:
            fruit = self.matrix[coord[1]][coord[0]]
            self.fruits.remove(fruit)
            self.matrix[coord[1]][coord[0]] = None
        self.on_cleared(len(chain))

    def spawn_fruits(self):
        """
        Spawn new fruits for every empty field and move fruits down
        """
        self.isSpawning = True

        # walk through all columns
        for x in range(self.config.fruitCount):
            y = self.config.fruitCount - 1

            coord_ontop = -1
            # walk through all fields in this column starting at the bottom
            while y >= 0:

                # if there is no fruit in this field
                if self.matrix[y][x] is None:
                    y2 = y - 1
                    self.move_down(x, y2)
                    self.spawn_fruit(x, coord_ontop)
                    coord_ontop -= 1
                    continue

                y -= 1

    def spawn_fruit(self, x, coord_ontop):
        """
        Spawn one new fruit on top of the board
        :param x: column coordinate
        :param coord_ontop: position in queue (negative counting)
        """
        fruit = FruitFactory.create_fruit(self.config)
        posx, posy = self.get_pos_by_coord((x, coord_ontop))
        fruit.rect.left = posx
        fruit.rect.top = posy
        self.matrix[0][x] = fruit
        self.fruits.add(fruit)

    def move_down(self, coordx, coordy):
        """
        Move fruits in the column one field down
        :param coordx: column coordinate
        :param coordy: start field and going upwards
        """
        y = coordy
        while y >= 0:
            self.matrix[y + 1][coordx] = self.matrix[y][coordx]
            self.matrix[y][coordx] = None
            y -= 1

    def spawning(self):
        """
        Fruits are falling from above animation
        :return:
        """
        if self.isSpawning:
            done = True
            for y in range(self.config.fruitCount):
                for x in range(self.config.fruitCount):
                    fruit = self.matrix[y][x]
                    coordx, coordy = self.get_coord_by_pos((fruit.rect.left, fruit.rect.top))
                    if coordy != y:
                        done = False
                        fruit.rect.top += self.config.fallSpeed
                        posx, posy = self.get_pos_by_coord((coordx, coordy + 1))
                        if fruit.rect.top >= posy:
                            fruit.rect.top = posy
            if done:
                self.isSpawning = False


class Score:
    """
    Game score
    """

    def __init__(self, config):
        self.config = config
        self.scoreBase = self.config.scoreBase
        self.score = 0
        self.turns = 0

    def cleared(self, len):
        """
        Calculate score
        Fired when fruits are cleared from the board
        :param len: count of cleared fruits
        """
        self.score += (self.scoreBase * len) ** 2
        self.turns += 1


class Sound:
    """
    Game sounds
    """

    def __init__(self, config):
        self.config = config

    def play(self, sound):
        """
        Play sound effect
        :param sound: key of the sound
        """
        if sound in self.config.sounds:
            self.config.sounds[sound].play()


class Game:
    """
    Main game class
    """

    def __init__(self, config):

        self.config = config
        self.size = self.config.size[:]
        self.scoreFont = pygame.font.SysFont(None, self.config.scoreFontSize)
        self.size[1] += self.scoreFont.get_height() + self.config.margin
        self.screen = pygame.display.set_mode(self.size)
        self.background = pygame.Surface(self.screen.get_size()).convert()
        self.background.fill(pygame.Color(255, 255, 255))

        self.keepGoing = True
        self.isMouseDown = False
        self.chain = []

        self.board = Board(self.config)
        self.score = Score(self.config)
        self.sound = Sound(self.config)
        self.board.cleared_callback = self.on_cleared

    def on_cleared(self, len):
        """
        Fired when fruits are cleared from the board
        :param len: count of cleared fruits
        """
        self.score.cleared(len)
        self.sound.play('cleared')

    def on_chaining(self):
        """
        Fired when fruits are selected with mouse
        """
        self.sound.play('chaining')

    def get_chain_points(self):
        """
        Calculate points from the selected fruits
        :return: list of points (x, y)
        """
        points = []
        for coord in self.chain:
            posx, posy = self.board.get_pos_by_coord(coord)
            posx += self.config.fruitSize / 2
            posy += self.config.fruitSize / 2
            points.append((posx, posy))
        points.append(pygame.mouse.get_pos())
        return points

    def mouse_down(self):
        """
        Fired when mouse button was pressed down
        Start chaining
        """
        if not self.board.isSpawning:
            self.isMouseDown = True
            pos = pygame.mouse.get_pos()
            x, y = self.board.get_coord_by_pos(pos)
            self.chain.append((x, y))

    def mouse_up(self):
        """
        Fired when mouse button was released
        Stop chaining and handle chain
        """
        if not self.board.isSpawning:
            if len(self.chain) > 1:
                self.board.clear_fruits(self.chain)
                self.board.spawn_fruits()
            self.isMouseDown = False
            self.chain = []

    def chaining(self):
        """
        Add or remove fruits to the chain
        :return:
        """
        if self.isMouseDown:
            pos = pygame.mouse.get_pos()
            x, y = self.board.get_coord_by_pos(pos)
            removed = False

            if len(self.chain) > 1:
                # Go backwards and remove a fruit from chain
                forelast_coord = self.chain[len(self.chain) - 2]
                if forelast_coord[0] == x and forelast_coord[1] == y:
                    self.chain.pop()
                    removed = True
                    self.on_chaining()

            start_fruit = self.board.matrix[self.chain[0][1]][self.chain[0][0]]
            last_coord = self.chain[len(self.chain) - 1]
            if not removed \
                    and ((last_coord[0] == x and (last_coord[1] == y + 1 or last_coord[1] == y - 1)) \
                                 or (last_coord[1] == y and (last_coord[0] == x + 1 or last_coord[0] == x - 1))) \
                    and start_fruit.color == self.board.matrix[y][x].color:
                # Go forwards and add a fruit to the chain
                self.chain.append((x, y))
                self.on_chaining()

    def render(self):
        """
        Render the screen
        """

        # draw background
        self.screen.blit(self.background, (0, 0))
        # draw fruits
        self.board.fruits.draw(self.screen)

        if self.isMouseDown:
            # draw the chain line
            start_fruit = self.board.matrix[self.chain[0][1]][self.chain[0][0]]
            points = self.get_chain_points()
            line_color = pygame.Color(start_fruit.color.r, start_fruit.color.g, start_fruit.color.b, 128)
            for i in range(len(points) - 1):
                pygame.draw.line(self.screen, line_color, points[i], points[i + 1], 32)

        # draw score
        label = self.scoreFont.render(
            'Punkte: ' + str(self.score.score) + '    Züge: ' + str(self.score.turns), 1, (0, 0, 0))
        self.screen.blit(label, (self.config.margin, self.config.size[1]))

        pygame.display.flip()

    def run(self):
        """
        Run the game
        """
        pygame.display.set_caption("Chains")

        clock = pygame.time.Clock()

        self.board.spawn_fruits()

        while self.keepGoing:

            clock.tick(self.config.fps)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.keepGoing = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.mouse_down()
                if event.type == pygame.MOUSEBUTTONUP:
                    self.mouse_up()

            self.board.spawning()
            self.chaining()
            self.render()


if __name__ == "__main__":
    game = Game(Config)
    game.run()
