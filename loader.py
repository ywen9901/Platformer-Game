import os
import random
import math
import pygame

from os import listdir
from os.path import isfile, join

pygame.init()
pygame.display.set_caption("Platformer")

WIDTH, HEIGHT = 1000, 800
FPS = 60
PLAYER_VEL = 5

window = pygame.display.set_mode((WIDTH, HEIGHT))

def get_background(name):
    image = pygame.image.load(join("assets", "Background", name))
    _, _, width, height = image.get_rect()
    tiles = []

    for i in range(WIDTH // width + 1):
        for j in range(HEIGHT // height + 1):
            # From top left, make tuple
            pos = (i*width, j*height)
            tiles.append(pos)

    return tiles, image

def draw(window, background, bg_image):
    for tile in background:
        window.blit(bg_image, tile)

    pygame.display.update()

def main(window):
    clock = pygame.time.Clock()
    background, bg_image = get_background("Yellow.png")

    run = True
    while run:
        # To regulate the frame rate accross different devices
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break
        
        draw(window, background, bg_image)
    
    pygame.quit()
    quit()

# Only call the function when the file is runned directly
# So importing something from the file won't run the game code
if __name__ == "__main__":
    main(window)