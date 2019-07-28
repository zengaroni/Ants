# Zen Futral

from pygame_functions import *  # Created by Steve Paget
import matplotlib.pyplot as plt
import pygame as pg
from random import *
import numpy as np
from math import atan2, pi

# Changing settings may cause issues to performance
ant_pop = 75   # Number of ants 
ant_speed = 3   # Ant Speed
view_dist = 20  # Ant Sensory Range
ant_mem = 30    # Pheramone trail length
food_pop = 3    # Number of food on map
line_draw = False   # Draw Pheramone trails
real_grouping = True   # Realistic movement
'''
Enabling 'real_grouping' will cause the ants to move more realisticly.
They will start to cluster more often, and go to ghost food. This is 
similar to ant death spirals. But due to the fact that it looks like a bug
to someone who doesn't understand, I have decided to disable it by default.
'''

axis_len = 800  
# Anything outside of (400:800) may cause issues

screen = screenSize(axis_len, axis_len)

class Ant:
    def __init__(self, name):
        self.name = name
        self.sprite = makeSprite('Ants/sprites/ant.png')
        self.color = (randrange(100, 255), randrange(0, 155), randrange(100, 255))  # Color of Pheramone Trail
        
        self.food = False   # If the ant is holding food
        self.collecting = False     # If the ant knows where food is (Regardless if he is/not carrying food)
        self.path = []

        self.angle = randrange(360) # Randomly chooses starting angle
        # You will notice a bell curve arrising when watching their initial directions.

        self.coord = hive.coord #Spawns ants on hill
    
    def ActionCycle(self):
        self.VarLogic()
        self.SenseSurroundings()
        self.ReactToSurroundings()

    def SenseSurroundings(self):
        self.SenseFOV()
        self.WallDetect()

    def ReactToSurroundings(self):
        self.PointOfInterest()
        self.Wander()
        self.AngleToSlope()
        self.Move()
        self.PathUpdate()

    def VarLogic(self):
        if self.collecting == False:
            self.path = []
            self.lkfc = (0,0)   # Last Known Food Coord
            # Default is (0,0) when not in use
        
        self.neighbors = [] # Resets Neighbors, to allow creation of new list

        # Updates Axis-Coords to match self.coord
        self.x = self.coord[0]
        self.y = self.coord[1]

        # Defines View Range
        self.lx = self.x - view_dist  # Left Limit
        if self.lx < 0:
            self.lx = 0

        self.hx = self.x + view_dist  # Right Limit
        if self.hx > axis_len - 1:
            self.hx = axis_len - 1

        self.ly = self.y - view_dist  # Top Limit
        if self.ly < 0:
            self.ly = 0

        self.hy = self.y + view_dist  # Bot Limit
        if self.hy > axis_len - 1:
            self.hy = axis_len - 1
        
    def SenseFOV(self):
        for ant in ant_list:
            if ant.name == self.name:   # Skip Self
                pass

            if self.collecting == False:
                for coord in ant.path:  # Goes through pheramone trails
                    found = self.CheckFor(coord)   # Can the ant see any of them?

                    if found:   # If ant stumbles upon a pheramon trail
                        self.collecting = True  # Activates 'collection mode'
                        self.food = ant.food    # Copies ant direction, more realistic movement patterns
                        self.lkfc = ant.lkfc    # Communicates known food location
            
            found = self.CheckFor(ant.coord)   # Look For Neighbors
            if found:
                self.neighbors.append(ant) # Adds ant to neighbor list

        for food in food_list:
            found = self.CheckFor(food.coord) # Look for Food
            if found:
                if food.coord != self.lkfc: # If food is found, but 'lkfc' doesn't align
                    self.lkfc = food.coord  # Update 'lkfc' to current food location
            
            found = self.CheckFor(self.lkfc) # Look for Last Known Food Coord
            if found:
                for food in food_list:
                    if food.coord != self.lkfc: # If there isn't food at 'lkfc' anymore
                        self.collecting = False # Stop collecting, and start searching for food

                    else:
                        self.collecting = True  # If at newly discovered food, start collecting
                        if self.food == False:  # Stops glitch were ants eat lots of food at a time
                            food.Eat()

                            if not real_grouping:   # Real grouping feature
                                self.path = []

                        self.food = True    # Stops glitch were ants eat lots of food at a time
                        break         

        found = self.CheckFor(hive.coord) # Look for Hive
        if found:
            self.food = False   # If hive is found, drop food

    def CheckFor(self, targ):
        # Check surroundings for targ

        if self.lx < targ[0] < self.hx and self.ly < targ[1] < self.hy:
            return True
        
        else:
            return False

    def WallDetect(self):
        if ant_speed > int(self.x): # Left
            self.angle = choice([0, 180])   # Turn towards Y-axis
            self.coord = tuple(np.array(self.coord) + np.array([ant_speed, 0])) # Bounce away from wall
        
        if int(self.x) > axis_len - ant_speed:  # Right
            self.angle = choice([0, 180])
            self.coord = self.coord = tuple(np.array(self.coord) + np.array([-ant_speed, 0]))
        
        if ant_speed > int(self.y): # Top
            self.angle = choice([90, 270])  # Turn towards X-axis
            self.coord = tuple(np.array(self.coord) + np.array([0, ant_speed])) # Bounce awa from wall
        
        if int(self.y) > axis_len - ant_speed:  # Bottom
            self.angle = choice([90, 270])
            self.coord = self.coord = tuple(np.array(self.coord) + np.array([0, -ant_speed]))

    def PointOfInterest(self):
        if self.collecting:
            if self.food:
                poi = hive.coord    # Set's point of interest to hive
            
            else:
                poi = self.lkfc     # Set's point of interest to 'lkfc'
                                            # 'Last Known Food Coord'
        else:
            return
        
        # X & Y of POI
        px = poi[0]
        py = poi[1]

        # Finds difference in location
        x_dif = px - self.x
        y_dif = py - self.y

        # Calculates angle to POI
        rad = atan2(x_dif, y_dif)
        self.angle = rad * 180/pi

    def Wander(self):
        # Simulates an and wandering around
        self.angle += randrange(-20, 20)

        # Keeps angle within 0:360
        if self.angle > 360:
            self.angle = self.angle % 360
        if self.angle < 0:
            self.angle = 360 + self.angle

        # Floats Cause issues in AngleToSlope()
        self.angle = int(self.angle)
    
    def AngleToSlope(self):
        '''
        I could not for the life of me figure out how to convert degrees to slope.
        I decided to just to hard code it, it's a bit 'cheatsy'. But it works.
        '''

        self.dir = np.array([0,0])

        if self.angle in (range(338, 361) or range(0, 23)): # Angle Range
            self.dir = np.array([0, 1]) # Slope 

        elif self.angle in range(23, 67): # Angle Range
            self.dir = np.array([1, 1]) # Slope
            
        elif self.angle in range(67, 112):
            self.dir = np.array([1, 0])

        elif self.angle in range(112, 157):
            self.dir = np.array([1, -1])

        elif self.angle in range(157, 202):
            self.dir = np.array([0, -1])
            
        elif self.angle in range(202, 247):
            self.dir = np.array([-1, -1])

        elif self.angle in range(247, 292):
            self.dir = np.array([-1, 0])
            
        elif self.angle in range(292, 338):
            self.dir = np.array([-1, 1])

        # Scales the direction to allow faster movement
        self.dir *= ant_speed 

    def Move(self):
        # Moves sprite to knew location
        self.coord += self.dir
        moveSprite(self.sprite, self.coord[0], self.coord[1], True)
        showSprite(self.sprite)

    def PathUpdate(self):
        # Create Pheramone if collecting food
        if self.collecting:
            self.path.append(tuple(self.coord))
        
        # Defines Pheramone path length
        if len(self.path) > ant_mem:
            self.path = self.path[-ant_mem:]
        
    def drawPath(self):
        # Draws pheramone trail if enabled
        if line_draw == True:
            if self.collecting and len(self.path) > 1:
                pg.draw.lines(screen, self.color, False, self.path, 1)

class Food:
    def __init__(self, name):
        self.name = name
        self.sprite = makeSprite('Ants/sprites/food.png')
        self.quant = 0  # How much food contained

    def ActionCycle(self):
        self.VarLogic()
        if self.eaten:
            self.spawn()

    def VarLogic(self):
        # Initiates respawn when needed
        if self.quant <= 0:
            self.quant = randrange(30, 50)
            self.eaten = True

    def spawn(self):
        # Spawns the food
        while True:
            self.x = randrange(20, axis_len - 20)
            self.y = randrange(20, axis_len - 20)
            self.coord = (self.x, self.y)

            if hive.lx < self.x < hive.hx and hive.ly < self.y < hive.hy:
                pass
            
            else:
                moveSprite(self.sprite, self.x, self.y, True)
                showSprite(self.sprite)
                self.eaten = False
                return

    def Eat(self):
        self.quant -= 1

class Hive:
    def __init__(self):
        self.sprite = makeSprite('Ants/sprites/hole.png')
    
    def ActionCycle(self):
        self.spawn()
        self.FoodBoarder()

    def spawn(self):
        LorU = axis_len/4    # Left & Up Limit
        RorD = axis_len - LorU   # Right & Down Limit

        self.x = randrange(LorU, RorD)
        self.y = randrange(LorU, RorD)

        self.coord = (self.x, self.y)

        moveSprite(self.sprite, self.x, self.y, True)
        showSprite(self.sprite)
        
    def FoodBoarder(self):
        # Prevents food from spawning to close
        self.x = self.coord[0]
        self.y = self.coord[1]

        self.lx = self.x - 100
        self.hx = self.x + 100
        self.ly = self.y - 100
        self.hy = self.y + 100

hive = Hive()
hive.ActionCycle()

# Creates food
food_list = []
for food in range(food_pop):
    food_name = 'food_' + str(food)
    food_name = Food(food_name)
    food_list.append(food_name)

# Creates the ants
ant_list = []
for ant in range(ant_pop):
    ant_name = 'ant_' + str(ant)
    ant_name = Ant(ant_name)
    ant_list.append(ant_name)

def run():
    while True:
        setBackgroundImage('Ants/sprites/grass.png')
        for food in food_list:
            food.ActionCycle()

        for ant in ant_list:    # This prevents the paths from flickering
            ant.drawPath()

        for ant in ant_list:    # Action cycle
            ant.ActionCycle()

        tick(1000)

run()
