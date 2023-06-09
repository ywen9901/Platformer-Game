import os
import random
import math
import pygame

from os import listdir
from os.path import isfile, join

pygame.init()
pygame.display.set_caption("Platformer")

WIDTH, HEIGHT = 1000, 800
FPS = 30
PLAYER_VEL = 4

window = pygame.display.set_mode((WIDTH, HEIGHT))

def flip(sprites):
    return [pygame.transform.flip(sprite, True, False) for sprite in sprites]

def load_sprite_sheets(dir1, dir2, width, height, direction=False):
    path = join("assets", dir1, dir2)
    images = [f for f in listdir(path) if isfile(join(path, f))]

    all_sprites = {}

    for image in images:
        sprite_sheet = pygame.image.load(join(path, image)).convert_alpha()

        sprites = []
        for i in range(sprite_sheet.get_width() // width):
            surface = pygame.Surface((width, height), pygame.SRCALPHA, 32)
            rect = pygame.Rect(i * width, 0, width, height)
            surface.blit(sprite_sheet, (0, 0), rect)
            sprites.append(pygame.transform.scale2x(surface))
        
        if direction:
            all_sprites[image.replace(".png", "") + "_right"] = sprites
            all_sprites[image.replace(".png", "") + "_left"] = flip(sprites)
        else:
            all_sprites[image.replace(".png", "")] = sprites

    return all_sprites

def load_block(size):
    path = join("assets", "Terrain", "Terrain.png")
    image = pygame.image.load(path).convert_alpha()
    surface = pygame.Surface((size, size), pygame.SRCALPHA, 32)
    rect = pygame.Rect(96, 0, size, size)
    surface.blit(image, (0, 0), rect)
    return pygame.transform.scale2x(surface)

class Player(pygame.sprite.Sprite):
    # Use Sprite for pixel collision
    COLOR = (255, 0, 0)
    GRAVITY = 8
    SPRITES = load_sprite_sheets("MainCharacters", "VirtualGuy", 32, 32, True)
    ANIMATION_DELAY = 2

    def __init__(self, x, y, width, height):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        # Velocity here denotes the speed we move our player in every frame
        self.x_vel = 0
        self.y_vel = 0
        self.mask = None
        self.direction = "left"
        self.animation_count = 0
        self.fall_count = 0
        self.jump_count = 0
        self.hit = False
        self.hit_count = 0
        self.health = 5
        self.win = False

    def jump(self):
        self.y_vel = -self.GRAVITY * 2
        self.animation_count = 0
        self.jump_count += 1
        if self.jump_count == 1:
            self.fall_count = 0
    
    def move(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy

    def make_hit(self):
        if self.hit is False:
            self.hit = True
            self.health -= 1
        self.hit_count = 0

    def move_left(self, vel):
        self.x_vel = -vel
        if self.direction != "left":
            self.direction = "left"
            self.animation_count = 0

    def move_right(self, vel):
        self.x_vel = vel
        if self.direction != "right":
            self.direction = "right"
            self.animation_count = 0

    def loop(self, fps):
        self.y_vel += min(1, (self.fall_count / fps) * self.GRAVITY)
        self.move(self.x_vel, self.y_vel)

        if self.hit:
            self.hit_count += 1
        if self.hit_count > fps * 0.3:
            self.hit = False

        self.fall_count += 1
        self.update_sprite()

    def landed(self):
        self.fall_count = 0
        self.y_vel = 0
        self.jump_count = 0
    
    def hit_head(self):
        self.count = 0
        self.y_vel *= -1

    def update_sprite(self):
        sprite_sheet = "run"
        if self.hit:
            sprite_sheet = "hit"
        if self.x_vel == 0:
            sprite_sheet = "idle"
        elif self.y_vel != 0:
            if self.jump_count == 1:
                sprite_sheet = "jump"
            elif self.jump_count == 2:
                sprite_sheet = "double_jump"
        elif self.y_vel > self.GRAVITY * 2:
            sprite_sheet = "fall"

        sprite_sheet_name = sprite_sheet + "_" + self.direction
        sprites = self.SPRITES[sprite_sheet_name]
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)
        self.sprite = sprites[sprite_index]
        self.animation_count += 1
        self.update()
    
    def update(self):
        self.rect = self.sprite.get_rect(topleft = (self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.sprite)

    def draw_health(self, window, offset_x):
        pos = (self.rect.topleft[0] + 5 - offset_x, self.rect.top - 10)
        size = (50, 10)
        pygame.draw.rect(window, (0, 0, 0), (pos[0] - 2, pos[1] - 2, size[0] + 4, size[1] + 4), 1)
        pygame.draw.rect(window, (255, 0, 0), (pos[0], pos[1], size[0], size[1]))
        pygame.draw.rect(window, (0, 128, 0), (pos[0] + self.health * 10, pos[1], size[0] - self.health * 10, size[1]))

    def draw(self, window, offset_x):
        window.blit(self.sprite, (self.rect.x - offset_x, self.rect.y))
        self.draw_health(window, offset_x)

class Object(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, name = None):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        self.width = width
        self.height = height
        self.name = name
    
    def draw(self, window, offset_x):
        window.blit(self.image, (self.rect.x - offset_x, self.rect.y))

class Block(Object):
    def __init__(self, x, y, size):
        super().__init__(x, y, size, size)
        block = load_block(size)
        self.image.blit(block, (0, 0))
        self.mask = pygame.mask.from_surface(self.image)

class Box(Object):
    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height)
        path = join("assets", "Items", "Boxes", "Box2", "Idle.png")
        image = pygame.image.load(path).convert_alpha()
        surface = pygame.Surface((width, height), pygame.SRCALPHA, 32)
        rect = pygame.Rect(0, 0, width, height)
        surface.blit(image, (0, 0), rect)
        box = pygame.transform.scale2x(pygame.transform.scale2x(surface))
        self.image.blit(box, (0, 0))
        self.mask = pygame.mask.from_surface(self.image)

class Flag(Object):
    ANIMATION_DELAY = 5

    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, "flag")

        path = join("assets", "Items", "Checkpoints", "Checkpoint")
        images = [f for f in listdir(path) if isfile(join(path, f))]

        all_sprites = {}

        for image in images:
            sprite_sheet = pygame.image.load(join(path, image)).convert_alpha()

            sprites = []
            for i in range(sprite_sheet.get_width() // width):
                surface = pygame.Surface((width, height), pygame.SRCALPHA, 32)
                rect = pygame.Rect(i * width, 0, width, height)
                surface.blit(sprite_sheet, (0, 0), rect)
                sprites.append(pygame.transform.scale2x(surface))
                all_sprites[image.replace(".png", "")] = sprites
        
        self.flag = all_sprites
        self.image = self.flag["Checkpoint (Flag Idle)(64x64)"][0]
        self.mask = pygame.mask.from_surface(self.image)
        self.animation_count = 0
    
    def loop(self):
        sprites = self.flag["Checkpoint (Flag Idle)(64x64)"]
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)
        self.image = sprites[sprite_index]
        self.animation_count += 1

        self.rect = self.image.get_rect(topleft = (self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.image)

class RockHead(Object):
    ANIMATION_DELAY = 5
    spd = 5

    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, "rock_head")
        self.rock_head = load_sprite_sheets("Traps", "Rock Head", width, height)
        self.image = self.rock_head["Blink (42x42)"][0]
        self.mask = pygame.mask.from_surface(self.image)
        self.animation_count = 0

    def loop(self):
        sprites = self.rock_head["Blink (42x42)"]
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)
        self.image = sprites[sprite_index]
        self.animation_count += 1
        self.rect.y += self.spd

        self.rect = self.image.get_rect(topleft = (self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.image)

        if self.animation_count // self.ANIMATION_DELAY > len(sprites):
            self.animation_count = 0

        if self.rect.y >= 600 or self.rect.y <= 150:
            self.spd = -self.spd

class Spikes(Object):
    ANIMATION_DELAY = 2

    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, "spikes")
        self.spikes = load_sprite_sheets("Traps", "Spikes", width, height)
        self.image = self.spikes["Idle"][0]
        self.mask = pygame.mask.from_surface(self.image)
        self.animation_count = 0
    
    def loop(self):
        sprites = self.spikes["Idle"]
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)
        self.image = sprites[sprite_index]
        self.animation_count += 1

        self.rect = self.image.get_rect(topleft = (self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.image)

        if self.animation_count // self.ANIMATION_DELAY > len(sprites):
            self.animation_count = 0

class SpikeHead(Object):
    ANIMATION_DELAY = 5

    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, "spike_head")
        self.spike_head = load_sprite_sheets("Traps", "Spike Head", width, height)
        self.image = self.spike_head["Blink (54x52)"][0]
        self.mask = pygame.mask.from_surface(self.image)
        self.animation_count = 0

    def loop(self):
        # sprite_sheet_name = sprite_sheet + "_" + self.direction
        sprites = self.spike_head["Blink (54x52)"]
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)
        self.image = sprites[sprite_index]
        self.animation_count += 1

        self.rect = self.image.get_rect(topleft = (self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.image)

        if self.animation_count // self.ANIMATION_DELAY > len(sprites):
            self.animation_count = 0

class Fire(Object):
    ANIMATION_DELAY = 2

    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, "fire")
        self.fire = load_sprite_sheets("Traps", "Fire", width, height)
        self.image = self.fire["off"][0]
        self.mask = pygame.mask.from_surface(self.image)
        self.animation_count = 0
        self.animation_name = "off"

    def on(self):
        self.animation_name = "on"

    def off(self):
        self.animation_name = "off"

    def loop(self):
        # sprite_sheet_name = sprite_sheet + "_" + self.direction
        sprites = self.fire[self.animation_name]
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)
        self.image = sprites[sprite_index]
        self.animation_count += 1

        self.rect = self.image.get_rect(topleft = (self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.image)

        if self.animation_count // self.ANIMATION_DELAY > len(sprites):
            self.animation_count = 0

def get_background(name):
    image = pygame.image.load(join("assets", "Background", name))
    _, _, width, height = image.get_rect()
    tiles = []

    for i in range(WIDTH // width + 2):
        for j in range(HEIGHT // height + 1):
            # From top left, make tuple
            pos = (i*width, j*height)
            tiles.append(pos)

    return tiles, image

def draw(window, background, bg_image, player, objects, offset_x, scroll):
    for tile in background:
        window.blit(bg_image, (tile[0] + scroll, tile[1]))
    
    for obj in objects:
        obj.draw(window, offset_x)

    player.draw(window, offset_x)

    pygame.display.update()

def handle_vertical_collision(player, objects, dy):
    collided_objects = []
    for obj in objects:
        if pygame.sprite.collide_mask(player, obj):
            if dy > 0:
                player.rect.bottom = obj.rect.top
                player.landed()
            elif dy < 0:
                player.rect.top = obj.rect.bottom
                player.hit_head()
        
            collided_objects.append(obj)
    
    return collided_objects

def collide(player, objects, dx):
    player.move(dx, 0)
    player.update()
    collided_object = None
    for obj in objects:
        if pygame.sprite.collide_mask(player, obj):
            collided_object = obj
            break
    
    player.move(-dx, 0)
    player.update()
    return collided_object

def handle_move(player, objects):
    keys = pygame.key.get_pressed()

    player.x_vel = 0
    collide_left = collide(player, objects, -PLAYER_VEL * 2)
    collide_right = collide(player, objects, PLAYER_VEL * 2)

    if keys[pygame.K_LEFT] and not collide_left:
        player.move_left(PLAYER_VEL)
    if keys[pygame.K_RIGHT] and not collide_right:
        player.move_right(PLAYER_VEL)

    vertical_collide = handle_vertical_collision(player, objects, player.y_vel)
    to_check = [collide_left, collide_right, *vertical_collide]
    trap_name = ["fire", "spikes", "spike_head"]
    for obj in to_check:
        if obj and obj.name in trap_name:
            player.make_hit()
        if obj and obj.name == "flag":
            player.win = True 

def draw_start_menu():
    window.fill((255, 255, 255))
    image = pygame.image.load(join("assets", "Sign", "ToBegin.png")).convert_alpha()
    window.blit(image, (WIDTH/2 - image.get_width()/2, HEIGHT/2 - image.get_height()/2))
    pygame.display.update()

def draw_game_over():
    window.fill((255, 255, 255))
    image = pygame.image.load(join("assets", "Sign", "GameOver.png")).convert_alpha()
    window.blit(image, (WIDTH/2 - image.get_width()/2, HEIGHT/2 - image.get_height()/2))
    pygame.display.update()

def draw_win():
    window.fill((255, 255, 255))
    image = pygame.image.load(join("assets", "Sign", "YouWin.jpg")).convert_alpha()
    window.blit(image, (WIDTH/2 - image.get_width()/2, HEIGHT/2 - image.get_height()/2))
    pygame.display.update()

def main(window):
    game_state = "start_menu"

    clock = pygame.time.Clock()
    block_size = 96

    background, bg_image = get_background("Cloud.jpg")
    player = Player(100, 100, 50, 50)
   
    wall = [Block(0, HEIGHT - block_size*(i+1), block_size) for i in range(HEIGHT // block_size + 1)]
    floor = [Block(i*block_size, HEIGHT - block_size, block_size) for i in range(0, (WIDTH*2) // block_size + 3)]

    boxes = []
    for i in range(7):
        for j in range(i):
            boxes.append(Box(block_size*14 + 80*j, HEIGHT - block_size - 75*(8-i-1) - 12, 112, 96))
    
    platform1 = [Block(block_size*2 + block_size*i, HEIGHT - block_size*3.6, block_size) for i in range(3)]
    platform2 = [Block(block_size*7 + block_size*i, HEIGHT - block_size*5.5, block_size) for i in range(3)]
    platform3 = [Block(block_size*7 + block_size*i, HEIGHT - block_size*3, block_size) for i in range(3)]

    rock_heads = [RockHead(block_size*10.5 + 64, 550, 42, 42), RockHead(block_size*10.5 + 128, 200, 42, 42), RockHead(block_size*10.5 + 192, 350, 42, 42)]

    fires = [Fire(block_size*7, HEIGHT - block_size*5.5 - 64, 16, 32), Fire(block_size*15.5 - 16, HEIGHT - block_size*4 - 64, 16, 32)]
    
    spikes1 = [Spikes(block_size + 16*i, HEIGHT - block_size - 32, 8, 16) for i in range(100)]
    traps = [*spikes1, SpikeHead(block_size*5 + 20, HEIGHT - block_size*4, 54, 52)]

    flag = Flag(block_size*14 + 640, HEIGHT - block_size - 128, 64, 64)

    for fire in fires:
        fire.on()

    objects = [*floor, *wall, *platform1, *platform2, *platform3, *fires, *traps, *rock_heads, *boxes, flag]

    run = True

    offset_x = 0
    scroll_area_width = 200
    scroll = 0

    while run:
        # To regulate the frame rate accross different devices
        clock.tick(FPS)

        # event handler
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and player.jump_count < 2:
                    player.jump()

        if game_state == "start_menu":
            draw_start_menu()
            keys = pygame.key.get_pressed()
            if keys[pygame.K_SPACE]:
                game_state = "game"
        
        if game_state == "game_over":
            draw_game_over()
            keys = pygame.key.get_pressed()
            if keys[pygame.K_q]:
                pygame.quit()
                quit()

        if player.win:
            game_state = "win"
            draw_win()
            keys = pygame.key.get_pressed()
            if keys[pygame.K_q]:
                pygame.quit()
                quit()

        if game_state == "game":
            if player.health <= 0:
                game_state = "game_over"

            scroll -= 3
            # reset scroll
            if abs(scroll) > WIDTH:
                scroll = 0

            player.loop(FPS)
            flag.loop()
            for fire in fires:
                fire.loop()
            for trap in traps:
                trap.loop()
            for rock_head in rock_heads:
                rock_head.loop()

            if((player.rect.right - offset_x >= WIDTH - scroll_area_width) and player.x_vel > 0) or (
                (player.rect.left - offset_x <= scroll_area_width) and player.x_vel < 0):
                offset_x += player.x_vel
                
            handle_move(player, objects)
            draw(window, background, bg_image, player, objects, offset_x, scroll)

    pygame.quit()
    quit()

# Only call the function when the file is runned directly
# So importing something from the file won't run the game code
if __name__ == "__main__":
    main(window)