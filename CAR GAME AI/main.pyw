import os
import math
import pygame
from pygame.locals import *
from pygame import mixer
from time import sleep
import threading
# COMPONENTS
from Components.GameMap import GameMap
from Components.Car import Car
from Components.AG import AlgorithmGenetic

class Main:
    def __init__(self):
        self.width = 900
        self.height = 600

        pygame.init()
        self.surface = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Car Game")

        # sound
        self.scoreup = pygame.mixer.Channel(2)
        self.dead = pygame.mixer.Channel(3)
        # self.surface.fill((66, 163, 60))
        self.font = pygame.font.Font("resource/PressStart2P.ttf",13)


        self.map = GameMap(pygame, self.surface)

        self.Npop = 50
        self.Pgen = 0

        self.FPS = 30
        self.FramePerSec = pygame.time.Clock()

        # DATA
        self.data = []
        self.lastMove = []

        self.AlgorithmGeneticCars = AlgorithmGenetic(self.Npop,[3,2,2])
        self.AlgorithmGeneticCars.createPopulation(True)
        self.CarsAi = self.AlgorithmGeneticCars.Pop
        self.Cars = [] 
        self.score = []
        for i in range(self.Npop):
            SELF_CAR = Car("P" + str(i),pygame, self.surface)
            self.Cars.append(SELF_CAR)
            self.lastMove.append([0,0,0,0])
            self.score.append(0)
       
        self.timeLeft = 15
        self.Highscore = 0
        self.speed = 3
        self.LostNumber = 0
        self.CountDownTime = 120

        self.lost = False
        self.pause = False
        self.threadStarted = False
        self.CountDownThread = False
        self.CarsThread = False
        self.RGen = True

    def run(self):
        self.running = True

        pygame.display.flip()
        while self.running:
            for event in pygame.event.get():
                if event.type == KEYDOWN:
                    if event.key == 27:
                        os._exit(1)
                    # elif event.key == K_SPACE:
                    #     self.dino.goUp()
                    if event.key == K_RETURN or event.key == K_KP_ENTER:
                        if self.lost:self.restart()
                if event.type == QUIT:
                    os._exit(1)
            

            if self.lost:
                waiting = self.font.render("WAITING THE NEXT GENERATION...",True,(255,255,255))
                self.surface.blit(waiting,(int(self.width / 2) - 180 ,int(self.height / 2) - 46))
                # result = self.font.render("You lost Press Entre to restart",True,(255,255,255))
                # self.surface.blit(result,(int(self.width / 2) - 200,int(self.height / 2) - 50))
                self.LostNumber = 0
                if not self.threadStarted : threading.Thread(target=self.DoAG, args=(),).start()
                pygame.display.flip()

                sleep(1)
                self.FramePerSec.tick(10)
            else:
                self.fill()
                if not self.CountDownThread:
                    self.CountDownThread = True
                    threading.Thread(target=self.CountDown, args=(),).start()
                elif self.CountDownTime <= 0:
                    self.lost = True
                    for i in range(self.Npop):
                        if not self.Cars[i].isDead:
                            self.Cars[i].killCar()
                            self.AlgorithmGeneticCars.setScore(i,self.score[i])
                            self.LostNumber += 1
                            print("PLAYER LEFT: " + str(self.Npop - self.LostNumber))

                if not self.CarsThread:
                    self.CarsThread = True
                    for i in range(self.Npop):
                        threading.Thread(target=self.CarThreading, args=(i,),).start()

                # if not self.keyThread:
                #     self.keyThread = True
                #     threading.Thread(target=self.handle_keys, args=(),).start()
                self.handle_keys()
                # self.isOneCarReachTheLine()
                # self.isOneCarLost()

                # if not self.LineThread:
                #     self.LineThread = True
                #     threading.Thread(target=self.isOneCarReachTheLine, args=(),).start()

                # if not self.CollisionThread:
                #     self.CollisionThread = True
                #     threading.Thread(target=self.isOneCarLost, args=(),).start()

                self.map.showLine(max(self.score))
                
                self.map.draw()
                for i in range(self.Npop):
                    self.Cars[i].draw()

                score = self.font.render(f"TIME LEFT: {self.CountDownTime}s ALIVE: {self.Npop - self.LostNumber} GEN {self.Pgen} Score:{max(self.score)}",True,(255,255,255))
                self.surface.blit(score,(10,10))
                if self.LostNumber >= self.Npop :self.lost = True
                # while True :
                #     if not self.LineThread and not self.CollisionThread:
                #         break
                #     sleep(0.01)
                self.FramePerSec.tick(self.FPS)
                
                
            pygame.display.flip()
    def handle_keys(self):

        for i in range(self.Npop):
            if not self.Cars[i].isDead:
                Input = self.calculateLinesCollision(i)
                currentCommand = self.CarsAi[i][0].run(Input)

                # 0.5 => 100%
                # 0.1 => 20%
                # 0.1 * 100 / 0.5 
                if currentCommand[0] >= 0.5:
                    slope = (currentCommand[0] - 0.5) / 0.5
                    self.Cars[i].goLeft(slope)
                else:
                    slope = (0.5 - currentCommand[0]) / 0.5
                    self.Cars[i].goRight(slope)
                if currentCommand[1] >= 0.5:
                    self.Cars[i].goForward(True)
        self.keyThread = False

    
    

    def CarThreading(self,index):
        while True:
            if not self.Cars[index].isDead:
                # Input = self.calculateLinesCollision(index)
                # currentCommand = self.CarsAi[index][0].run(Input)
                # if currentCommand[0] >= 0.5:
                #     self.Cars[index].goLeft()
                # else:
                #     self.Cars[index].goRight()
                # if currentCommand[1] >= 0.5:
                #     self.Cars[index].goForward(True)

                if self.isCarReachTheLine(index):
                    self.score[index] += 1
                if self.isCarsCollision(index):
                    self.Cars[index].killCar()
                    self.AlgorithmGeneticCars.setScore(index,self.score[index])
                    self.LostNumber += 1
                    print("PLAYER LEFT: " + str(self.Npop - self.LostNumber))
            else:
                break
            sleep(0.01)
        if self.LostNumber >= self.Npop :self.CarsThread = False

    def isOneCarReachTheLine(self):
        for i in range(self.Npop):
            if not self.Cars[i].isDead:
                if self.isCarReachTheLine(i):
                    self.score[i] += 5
        self.LineThread = False

    def isOneCarLost(self):
        for i in range(self.Npop):
            if not self.Cars[i].isDead:
                if self.isCarsCollision(i):
                    self.Cars[i].killCar()
                    self.AlgorithmGeneticCars.setScore(i,self.score[i])
                    self.LostNumber += 1
                    print("PLAYER LEFT: " + str(self.Npop - self.LostNumber))
        self.CollisionThread = False

    def isCarReachTheLine(self,index):
        Line = self.map.getLine(self.score[index])
        Car = self.Cars[index].getCar()
        carXY = self.Cars[index].getXY()
        for i in range(28):
            for j in range(28):
                try:
                    if Car.get_at((i,j)).a != 0:
                        if  Line.get_at((carXY[0] + i,carXY[1] + j)).a != 0:
                            return True
                except:
                    pass
        return False

    def isCarsCollision(self,index):
        Map = self.map.getMap()

        Car = self.Cars[index].getCar()
        carXY = self.Cars[index].getXY()

        for i in range(28):
            for j in range(28):
                try:
                    if Car.get_at((i,j)).a != 0:
                        if  Map.get_at((carXY[0] + i,carXY[1] + j)).a != 0:
                            return True
                except:
                    pass
        return False

    def calculateLinesCollision(self,index):
        Point = self.Cars[index].getMonitorPoint()
        Map = self.map.getMap()
        nearestCollision = [150,150,150]

        for i in range(150):
            position_right = self.calculateDisplacement(Point[0],Point[1],self.Cars[index].getAngle() + 45,i)
            position_left = self.calculateDisplacement(Point[0],Point[1],self.Cars[index].getAngle() - 45,i)
            position_forward = self.calculateDisplacement(Point[0],Point[1],self.Cars[index].getAngle(),i)

            if nearestCollision[1] == 150:
                try:
                    if  Map.get_at(position_right).a != 0:
                        nearestCollision[1] = i
                except:
                    pass

            if nearestCollision[0] == 150:
                try:
                    if  Map.get_at(position_left).a != 0:
                        nearestCollision[0] = i
                except:
                    pass
            
            if nearestCollision[2] == 150:
                try:
                    if  Map.get_at(position_forward).a != 0:
                        nearestCollision[2] = i
                except:
                    pass
        return nearestCollision

    def calculateDisplacement(self,x,y,angle,length):
        x = x + length * math.cos(math.radians(angle))
        y = y - length * math.sin(math.radians(angle))
        return int(x),int(y)

    def DoAG(self):
        self.Pgen += 1
        self.threadStarted = True
        print("change Weight")
        self.AlgorithmGeneticCars.ChangeNNWeight()
        print("change NN")
        self.CarsAi = self.AlgorithmGeneticCars.Pop
        self.CountDownTime = 120 + int(self.Pgen / 2)
        self.RGen = False
        
        print("restart game")

        self.restart()
        self.threadStarted = False

    def CountDown(self):
        while self.CountDownTime > 0:
            self.CountDownTime -= 1
            sleep(1)
        self.CountDownThread = False

    def restart(self):
        self.lost = False
        self.score = [0] * self.Npop
        self.map.generateRandomMap()
        for car in self.Cars:
            car.restart()


    def fill(self):
        self.surface.fill((10, 10, 10))
        
        
    

main_game = Main()
main_game.run()
