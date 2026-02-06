import pygame
import os
from settings import *

class Pot(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        super().__init__()
        self.game = game
        
        # Load Pot Body
        self.image = pygame.image.load(os.path.join("assets", "images", "pot.png")).convert_alpha()
        self.image = pygame.transform.smoothscale(self.image, (300, 300))
        
        # Load Pot Lid
        try:
            self.lid_image = pygame.image.load(os.path.join("assets", "images", "pot_lid.png")).convert_alpha()
            self.lid_image = pygame.transform.smoothscale(self.lid_image, (300, 300))
        except:
            self.lid_image = None # Fallback if lid missing

        self.rect = self.image.get_rect(center=(x, y))
        
        # Cooking State
        self.is_cooking = False
        self.cook_start_time = 0
        self.cook_duration = 3000 # 3 seconds

    def update(self):
        # Check if 3 seconds have passed
        if self.is_cooking:
            now = pygame.time.get_ticks()
            if now - self.cook_start_time > self.cook_duration:
                self.is_cooking = False # Open the lid!

    def start_cooking(self):
        self.is_cooking = True
        self.cook_start_time = pygame.time.get_ticks()

# You can add Ingredient classes here later!
# class Ingredient(pygame.sprite.Sprite): ...