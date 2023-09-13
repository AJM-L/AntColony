#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 18 13:35:52 2023

@author: ajmatheson-lieber
"""

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan 10 08:21:20 2023

@author: ajmatheson-lieber
"""
import numpy as np
import random
import pygame
from collections import deque

dispersion = 100
pheremones = deque()
foods = set()
food_count = 0
colony_position = (200, 200)
ants = []
global food
food = 0


class ant ():
    def __init__(self, position, pheremone_detection, food_desire, random_movement, direction, speed, carrying_food = False):
        self.position = position
        self.pheremone_detection = pheremone_detection
        self.food_desire = food_desire
        self.random_movement = random_movement
        self.carrying_food = carrying_food
        self.direction = direction
        self.speed = speed
        self.threshold = 0
        
    
    def sense_food (self, radius = 5):
        if not self.carrying_food:
            for i in range(int(self.position[0])-radius, int(self.position[0]) + radius + 1):
                for j in range(int(self.position[1])-radius, int(self.position[1]) + radius +1):
                    try:
                        if (i, j) in foods:
                            foods.remove((i, j))
                            self.postition = (i, j)
                            pheremones.append([(i, j), dispersion])
                            self.carrying_food = True
                            return True
                    except KeyError:
                        continue
        return False
    
    def pheremone_sense (self):
        movement_vectors = [0, 0]
        X, Y = (0, 0)
        for item in pheremones:
            x, y = item[0]
            try:
                X += (x - self.position[0])/((y - self.position[1])**2 + (x - self.position[0])**2)
            except ZeroDivisionError:
                X += 0
            try:
                Y += (y - self.position[1])/((y - self.position[1])**2 + (x - self.position[0])**2)
            except ZeroDivisionError:
                Y += 0
        if X + Y > self.threshold * 2:
            if X > self.speed:
                X = self.speed
            if Y > self.speed:
                Y = self.speed
            movement_vectors[0] = X
            movement_vectors[1] = Y
            if X + Y > self.threshold * 10:
                self.direction = 0
                if X == 0:
                    if Y > 0:
                        self.direction = np.pi/2
                    elif Y < 0:
                        self.direction = 3*np.pi/2
                elif Y ==0:
                    if X > 0:
                        self.direction = 0
                    elif X < 0:
                        self.direction = np.pi
                elif X > 0 and Y > 0:
                    self.direction = np.arctan(Y/X)
                elif X < 0 and Y > 0:
                    self.direction = np.pi - np.arctan(-Y/X)
                elif X > 0 and Y < 0:
                    self.direction = 2 * np.pi - np.arctan(-Y/X)
                elif X < 0 and Y < 0:
                    self.direction = np.pi - np.arctan(Y/X)
            self.position = self.combine_vectors(self.position, tuple(movement_vectors))
            return X + Y
        else:
            movement_vectors[0] = 0
            movement_vectors[1] = 0
            self.position = self.combine_vectors(self.position, tuple(movement_vectors))
            return 0
            
        
    
    def move (self, position):
        self.position = position
        return
    
    def combine_vectors (self, *vector):
        movement_vector = [0, 0]
        for i in vector:
            movement_vector[0] += i[0]
            movement_vector[1] += i[1]
        return tuple(movement_vector)
    
    def normalize (self, vector):
        x, y = vector
        heavy = max(vector)
        if heavy == 0:
            inv = 0
        else:
            inv = 1 / heavy
        return (x*inv, y*inv)
    
    def normal_nest_vector (self):
        x = colony_position[0] - self.position[0]
        y = colony_position[1] - self.position[1]
        try:
            inv = 1/max([abs(x), abs(y)])
        except ZeroDivisionError:
            inv = 0
        self.position = self.combine_vectors(self.position, (x * inv, y * inv))
        return 
    
    def generate_random_movement (self, movement_val):
        self.direction += np.random.randn() * (movement_val + 0.1)
        pos = self.combine_vectors((np.cos(self.direction) * self.speed, np.sin(self.direction) * self.speed), self.position)
        if pos[0] <= 0 or pos[1] <= 0 or pos[0] >= 500 or pos[1] > 500:
            self.direction += 2*np.pi
        pos = self.combine_vectors((np.cos(self.direction) * self.speed, np.sin(self.direction) * self.speed), self.position)
        self.position = pos
        return
        
    
    def generate_movement (self):
        if not self.carrying_food:
            if self.sense_food():
                return
            else:
                self.generate_random_movement(self.pheremone_sense())
                return
        else:
            if abs(self.position[0] - colony_position[0]) + abs(self.position[1] - colony_position[1]) < 5:
                self.carrying_food = False
                global food
                food +=1
            self.normal_nest_vector()
            return
            
        
        
    def leave_pheremone (self):
        pheremones.append([self.position, dispersion])
        return




def generate_colony (x = 20, size = 300, position = (200, 200), turns = 1000, direction = None, speed = 1):
    for i in range(size):
        direction = random.randint(0, 200) * 0.01 * np.pi
        pheremone_detection_val = random.randint(0, x) * 0.5
        food_desire_val = random.randint(0, x) * .1
        random_movement_val = random.randint(0, x) * .1
        ants.append(ant(position, pheremone_detection_val, food_desire_val, random_movement_val, direction, speed))
    return ants

def generate (x = 20):
    generate_colony()
    global food
    global foods
    screen = pygame.display.set_mode((500, 500))
    for turn in range(10000):
        while len(pheremones) > 100:
            pheremones.popleft()
        while len(foods) < 3000:
            if len(foods) < 8 or random.choices([True, False], weights = (0.1, 0.9))[0]:
                foods = foods | {(random.randint(0, 500), random.randint(0, 500))}
            origin = random.choice(tuple(foods))
            new_node = (origin[0] + random.randint(-2, 2), origin[1] + random.randint(-2, 2))
            if (new_node[0] > 0 and new_node[0] < 500) and (new_node[1] > 0 and new_node[1] < 500):
                foods = foods | {new_node}
        for a in ants:
            a.generate_movement()
            if a.carrying_food:
                screen.set_at((int(a.position[0]), int(a.position[1])), [0, 155, 255])
            else:
                screen.set_at((int(a.position[0]), int(a.position[1])), [0, 0, 0])
        for item in tuple(foods):
            screen.set_at(item, [255, 155, 0])
        spoiled = []
        for p in pheremones:
            item = p[0]
            if p[1] < 0:
                spoiled.append(p)
            else:
                p[1] -= 1
                screen.set_at((int(item[0]), int(item[1])), [160,32,240])
        for i in spoiled:
            pheremones.popleft()
        screen.set_at((200, 200), [0, 0, 0])
        pygame.display.update()
        screen.fill([255, 255, 255])
        
    pygame.quit()
    return food

generate()

        