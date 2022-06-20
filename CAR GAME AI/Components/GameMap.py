from time import sleep
import random

class GameMap:
    def __init__(self,pygame,surface):
        self.surface = surface
        self.pygame = pygame

        # IMAGE
        self.lines = []
        for i in range(52):
            self.lines.append(self.pygame.image.load("resource/image/maps/lines2/" + str(i + 1) + ".png").convert_alpha())
    
        self.map = any
        self.generateRandomMap()
        self.draw()
        
    def getMap(self):
        return self.map

    def getLine(self,number):
        # number += 8
        number = (number % 52) + 1
        return  self.lines[number - 1]

    def showLine(self,number):
        # number += 8
        number = (number % 52) + 1
        self.line = self.lines[number - 1]

    def generateRandomMap(self):
        self.line = self.lines[0]
        self.map = self.pygame.image.load("resource/image/maps/map2.png").convert_alpha()

    def draw(self):
        self.surface.blit(self.line,(0,0))
        self.surface.blit(self.map,(0,0))

        


