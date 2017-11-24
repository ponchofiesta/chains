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

"""
Configuration
"""


class Config:
    left = 0
    top = 0
    fruitCount = 8
    fruitSize = 48
    fruitMargin = 8
    margin = 8
    size = (0, 0)
    fruitsDef = []
    fps = 30
    fallSpeed = 8 # 2 pixel per frame


Config.size = (
    (Config.fruitSize + Config.fruitMargin) * Config.fruitCount + Config.margin,
    (Config.fruitSize + Config.fruitMargin) * Config.fruitCount + Config.margin
)
Config.fruitsDef = [
    {'image': pygame.image.load('graphics/apple.png'), 'color': pygame.Color(255, 0, 0), 'size': Config.fruitSize},
    {'image': pygame.image.load('graphics/kiwi.png'), 'color': pygame.Color(0, 255, 0), 'size': Config.fruitSize},
    {'image': pygame.image.load('graphics/grape.png'), 'color': pygame.Color(0, 0, 255), 'size': Config.fruitSize},
    {'image': pygame.image.load('graphics/banana.png'), 'color': pygame.Color(255, 255, 0), 'size': Config.fruitSize}
]

"""
Game code
"""


class Graphics:
    @staticmethod
    def lines(points):
        pass


class Fruit(pygame.sprite.Sprite):
    def __init__(self, image, color, size):
        pygame.sprite.Sprite.__init__(self)
        self.image = image
        self.image = pygame.transform.scale(self.image, (size, size))
        self.color = color
        self.rect = self.image.get_rect()


class FruitFactory:
    @staticmethod
    def create_fruit(config):
        tdef = config.fruitsDef[random.randint(0, len(config.fruitsDef) - 1)]
        fruit = Fruit(tdef['image'], tdef['color'], tdef['size'])
        return fruit


class Board:
    def __init__(self, config):
        self.config = config
        self.fruits = pygame.sprite.Group()
        self.matrix = []
        self.isSpawning = False
        for y in range(self.config.fruitSize):
            line = []
            for x in range(self.config.fruitSize):
                fruit = FruitFactory.create_fruit(self.config)
                fruit.rect.left = self.config.left + self.config.margin + (
                                                                              self.config.fruitMargin + self.config.fruitSize) * x
                fruit.rect.top = self.config.top + self.config.margin + (
                                                                            self.config.fruitMargin + self.config.fruitSize) * y
                line.append(fruit)
                self.fruits.add(fruit)
            self.matrix.append(line)

    def get_coord_by_pos(self, pos):
        x = floor((pos[0] - self.config.left - self.config.margin) / (self.config.fruitMargin + self.config.fruitSize))
        y = floor((pos[1] - self.config.left - self.config.margin) / (self.config.fruitMargin + self.config.fruitSize))
        return x, y

    def get_pos_by_coord(self, coord):
        x = self.config.left + self.config.margin + (self.config.fruitMargin + self.config.fruitSize) * coord[
            0]
        y = self.config.top + self.config.margin + (self.config.fruitMargin + self.config.fruitSize) * coord[
            1]
        return x, y

    def clear_fruits(self, chain):
        for coord in chain:
            fruit = self.matrix[coord[1]][coord[0]]
            self.fruits.remove(fruit)
            self.matrix[coord[1]][coord[0]] = None

    def spawn_fruits(self):
        self.isSpawning = True

        # walk through all columns
        for x in range(1, len(self.matrix[self.config.fruitCount - 1])):
            y = self.config.fruitCount - 1

            coord_ontop = -1
            # walk through all fields in this column starting at the bottom
            while y >= 0:

                # if there is no fruit in this field
                if self.matrix[y][x] is None:
                    y2 = y - 1
                    moved = False

                    # if this is the top line just spawn a new fruit
                    if y == 0:
                        fruit = FruitFactory.create_fruit(self.config)
                        posx, posy = self.get_pos_by_coord((x, coord_ontop))
                        fruit.rect.left = posx
                        fruit.rect.top = posy
                        coord_ontop -= 1
                        self.matrix[0][x] = fruit
                        self.fruits.add(fruit)

                    # search upwards for fruits
                    while y2 >= 0:

                        # if there is a fruit, move it down and spawn a new fruit
                        if not (self.matrix[y2][x] is None):
                            moved = True
                            self.matrix[y][x] = self.matrix[y2][x]
                            fruit = FruitFactory.create_fruit(self.config)
                            posx, posy = self.get_pos_by_coord((x, coord_ontop))
                            fruit.rect.left = posx
                            fruit.rect.top = posy
                            coord_ontop -= 1
                            self.move_down(x, y2)
                            self.matrix[0][x] = fruit
                            self.fruits.add(fruit)
                            break
                        y2 -= 1

                    # if there was no fruit to be moved stop walking through this column
                    if not moved:
                        break



                y -= 1

    def move_down(self, coordx, coordy):
        y = coordy
        while y >= 1:
            self.matrix[y][coordx] = self.matrix[y - 1][coordx]
            self.matrix[y - 1][coordx] = None
            y -= 1

    def spawning(self):
        if self.isSpawning:
            done = True
            for y in range(1, self.config.fruitCount):
                for x in range(1, self.config.fruitCount):
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

class Game:
    def __init__(self, config):
        self.config = config
        self.screen = pygame.display.set_mode(self.config.size)
        self.background = pygame.Surface(self.screen.get_size()).convert()
        self.board = Board(self.config)
        self.keepGoing = True
        self.isMouseDown = False
        self.chain = []

    def get_chain_points(self):
        points = []
        for coord in self.chain:
            posx, posy = self.board.get_pos_by_coord(coord)
            posx += self.config.fruitSize / 2
            posy += self.config.fruitSize / 2
            points.append((posx, posy))
        points.append(pygame.mouse.get_pos())
        return points

    def mouse_down(self):
        if not self.board.isSpawning:
            self.isMouseDown = True
            pos = pygame.mouse.get_pos()
            x, y = self.board.get_coord_by_pos(pos)
            self.chain.append((x, y))

    def mouse_up(self):
        if not self.board.isSpawning:
            if len(self.chain) > 1:
                self.board.clear_fruits(self.chain)
                self.board.spawn_fruits()
            self.isMouseDown = False
            self.chain = []

    def chaining(self):
        if self.isMouseDown:
            pos = pygame.mouse.get_pos()
            x, y = self.board.get_coord_by_pos(pos)
            removed = False

            if len(self.chain) > 1:
                forelast_coord = self.chain[len(self.chain) - 2]
                if forelast_coord[0] == x and forelast_coord[1] == y:
                    self.chain.pop()
                    removed = True

            start_fruit = self.board.matrix[self.chain[0][1]][self.chain[0][0]]
            last_coord = self.chain[len(self.chain) - 1]
            if not removed \
                    and ((last_coord[0] == x and (last_coord[1] == y + 1 or last_coord[1] == y - 1)) \
                                 or (last_coord[1] == y and (last_coord[0] == x + 1 or last_coord[0] == x - 1))) \
                    and start_fruit.color == self.board.matrix[y][x].color:
                self.chain.append((x, y))

    def render(self):
        self.screen.blit(self.background, (0, 0))
        self.board.fruits.draw(self.screen)

        if self.isMouseDown:
            start_fruit = self.board.matrix[self.chain[0][1]][self.chain[0][0]]
            points = self.get_chain_points()
            pygame.draw.lines(self.screen, start_fruit.color, True, points, 32)

        # screen.blit(lbl, (100, 100))
        pygame.display.flip()

    def run(self):

        pygame.init()

        pygame.display.set_caption("Chains")

        self.background.fill(pygame.Color(255, 255, 255))

        clock = pygame.time.Clock()

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
