import os
import random
import math
import pygame

from os import listdir
from os.path import isfile, join

pygame.init()
pygame.display.set_caption("Platformer")

WIDTH, HEIGHT = 1000, 800
FPS = 120
PLAYER_VEL = 5

window = pygame.display.set_mode((WIDTH, HEIGHT))

def main(window):
    clock = pygame.time.Clock()
    block_size = 96

    background, bg_image = get_background("Blue.png")
    player = Player(100, 100, 50, 50)

    fire = Fire(150, HEIGHT - block_size - 64, 16, 32)
    fire.on()

    floor = [Block(i * block_size, HEIGHT - block_size, block_size) for i in range(-WIDTH // block_size, (WIDTH*5) // block_size)]
    objects = [*floor, fire]

    offset_x = 0
    scroll_area_width = 200

    run = True
    while run:
        # To regulate the frame rate accross different devices
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and player.jump_count < 2:
                    player.jump()

        player.loop(FPS)
        fire.loop()
        handle_move(player, objects)
        draw(window, background, bg_image, player, objects, offset_x)

        if((player.rect.right - offset_x >= WIDTH - scroll_area_width) and player.x_vel > 0) or (
            (player.rect.left - offset_x <= scroll_area_width) and player.x_vel < 0):
            offset_x += player.x_vel

    pygame.quit()
    quit()