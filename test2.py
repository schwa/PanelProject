import os

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"

import pygame, time

os.environ["SDL_FBDEV"] = "/dev/fb0"
os.environ["SDL_VIDEODRIVER"] = "fbcon"
os.environ["DISPLAY"] = ""

print(pygame.init())
print(pygame.get_error())
size = (pygame.display.Info().current_w, pygame.display.Info().current_h)
print("Detected screen size: {0}".format(size))
lcd = pygame.display.set_mode(size)
lcd.fill((10, 50, 100))
pygame.display.update()
time.sleep(1)
