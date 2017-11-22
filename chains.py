#!/usr/bin/python
# -*- encoding: utf-8 -*-

# Import and initialize
import pygame
import pygame.locals
import random
from math import floor

pygame.init()

# Display
pygame.display.set_caption("Chains")


# Entities
class Config:
    left = 0
    top = 0
    tileCount = 8
    tileSize = 48
    tileMargin = 8
    margin = 8
    size = (0, 0)

Config.size = (
    (Config.tileSize + Config.tileMargin) * Config.tileCount + Config.margin,
    (Config.tileSize + Config.tileMargin) * Config.tileCount + Config.margin
)

tilesDef = [
    { 'image': pygame.image.load('graphics/apple.png'), 'color': pygame.Color(255, 0, 0), 'size': Config.tileSize },
    { 'image': pygame.image.load('graphics/kiwi.png'), 'color': pygame.Color(0, 255, 0), 'size': Config.tileSize },
    { 'image': pygame.image.load('graphics/grape.png'), 'color': pygame.Color(0, 0, 255), 'size': Config.tileSize },
    { 'image': pygame.image.load('graphics/banana.png'), 'color': pygame.Color(255, 255, 0), 'size': Config.tileSize }
]

class Tile(pygame.sprite.Sprite):
    def __init__(self, image, color, size):
        pygame.sprite.Sprite.__init__(self)
        self.image = image
        self.image = pygame.transform.scale(self.image, (size, size))
        self.color = color
        self.rect = self.image.get_rect()

def getCoordByPos(pos):
    x = floor((pos[0] - Config.left - Config.margin) / (Config.tileMargin + Config.tileSize))
    y = floor((pos[1] - Config.left - Config.margin) / (Config.tileMargin + Config.tileSize))
    return (x, y)

screen = pygame.display.set_mode(Config.size)

allTiles = pygame.sprite.Group()
matrix = []
for y in range(Config.tileCount):
    line = []
    for x in range(Config.tileCount):
        tDef = tilesDef[random.randint(0, len(tilesDef) - 1)]
        tile = Tile(tDef['image'], tDef['color'], tDef['size'])
        tile.rect.left = Config.left + Config.margin + (Config.tileMargin + Config.tileSize) * x
        tile.rect.top = Config.top + Config.margin + (Config.tileMargin + Config.tileSize) * y
        line.append(tile)
        allTiles.add(tile)
    matrix.append(line)

background = pygame.Surface(screen.get_size()).convert()
background.fill(pygame.Color(255, 255, 255))
# fnt = pygame.font.SysFont("None", 24)
# lbl = fnt.render("IDEA-ALTER", 1, (255, 255, 0))

# Action -> ALTER
################

# Assign values
clock = pygame.time.Clock()
keepGoing = True

# Loop
while keepGoing:

    # Timing
    clock.tick(30)

    # Events
    for evnt in pygame.event.get():
        if evnt.type == pygame.QUIT:
            keepGoing = False
        if evnt.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()
            x, y = getCoordByPos(pos)
            print(matrix[y][x].color)


    # Refresh display
    screen.blit(background, (0, 0))
    allTiles.draw(screen)
            # screen.blit(matrix[y][x], (x, y))

    # screen.blit(lbl, (100, 100))
    pygame.display.flip()
