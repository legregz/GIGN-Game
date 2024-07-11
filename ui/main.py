import pygame

def createRect(position, size):
    return [int(screen.get_width() / 100 * (position[0] - size[0] / 2)), int(screen.get_height() / 100 * (position[1] - size[1] / 2)), int(screen.get_width() / 100 * size[0]), int(screen.get_height() / 100 * size[1])]

file = open("colors.json", "r")
colorDict = eval(file.read())
file.close()

def createColor(color):
    if type(color) == str():
        return colorDict[color]
    else:
        return color

class Rect:
    def __init__(self, position, size, color, width = 0):
        self.color = color
        self.width = width
        self.position = position
        self.size = size

    def defScreen(self, screen):
        self.screen = screen

    def setPosition(self, position):
        self.position = position

    def show(self, hover = 0):
        pygame.draw.rect(self.screen, createColor(self.color), createRect(self.position, [self.size[0] + hover, self.size[1] + hover]), int(self.screen.get_height() // 100 * (self.width)))