import sys
import os
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from datetime import datetime
import time
from pydrm import *  # https://github.com/notro/pydrm
import evdev  # https://python-evdev.readthedocs.io/en/latest/usage.html#listing-accessible-event-devices
import asyncio
from evdev import InputDevice, categorize, ecodes, KeyEvent
import random


class Button:
    def __init__(self, frame, color):
        self.frame = frame
        self.color = color
        self.pressed = False
        self.label = None
        self.id = None

    def draw(self, draw):
        if self.pressed:
            color = "white"
        else:
            color = self.color
        draw.rectangle(self.frame.abs_tuple, fill=color)

    def touch_down(self, location):
        self.pressed = True
        print("TOUCH_DOWN", self.id)

    def touch_up(self, location):
        self.pressed = False
        print("TOUCH_UP", self.id)


class Rectangle:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    @property
    def abs_tuple(self):
        return (self.x, self.y, self.x + self.width, self.y + self.height)

    @property
    def min_x(self):
        return self.x

    @property
    def min_y(self):
        return self.y

    @property
    def max_x(self):
        return self.x + self.width

    @property
    def max_y(self):
        return self.y + self.height

    def contains(self, point):
        return (
            point[0] >= self.min_x
            and point[0] < self.max_x
            and point[1] >= self.min_y
            and point[1] < self.max_y
        )


class View:
    def __init__(self, frame):
        self.frame = frame
        self.children = []

    def draw(self, draw):
        for child in self.children:
            child.draw(draw)

    def resolve(self, point):
        for child in self.children:
            if child.frame.contains(point):
                return child
        return None

    def touch_down(self, location):
        view = self.resolve(location)
        if view:
            view.touch_down(location)

    def touch_up(self, location):
        view = self.resolve(location)
        if view:
            view.touch_up(location)


drm = SimpleDrm()
print(drm.inspect(True))
print(drm.inspect())

image = Image.new("RGBX", drm.image.size)
draw = ImageDraw.Draw(image)
width, height = drm.image.size

view = View(Rectangle(0, 0, width, height))

rows = 4
cols = 4
cell_width = width // cols
cell_height = height // rows
for row in range(rows):
    for col in range(cols):
        r = Rectangle(col * cell_width, row * cell_height, cell_width, cell_height)
        hue = random.randrange(0, 360)
        button = Button(r, f"hsl({hue}, 100%, 50%)")
        button.id = (col, row)
        view.children.append(button)


devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
for device in devices:
    print(device.path, device.name, device.phys)
# /dev/input/event1 EP0110M09 -- Capacitive Touchscreen
# /dev/input/event0 vc4 vc4/input0

# print(dir(ecodes))
dev = InputDevice("/dev/input/event1")
print(dev.capabilities())
print(dev.capabilities(verbose=True))
print(dev.capabilities(absinfo=True))


def redraw():
    draw.rectangle((0, 0, width, height), fill="black", outline="black")
    view.draw(draw)
    drm.enable()
    image.convert("RGBX")
    drm.image.paste(image)
    drm.flush()
    drm.disable()


redraw()


async def helper(dev):
    X = 0
    Y = 0
    async for event in dev.async_read_loop():
        redraw()
        if event.type == evdev.ecodes.EV_ABS:
            if event.code == 1:
                X = event.value
            elif event.code == 0:
                Y = event.value
        elif event.type == evdev.ecodes.EV_KEY:
            event = evdev.util.categorize(event)
            if event.keystate == KeyEvent.key_down:
                view.touch_down((Y, X))
            elif event.keystate == KeyEvent.key_up:
                view.touch_up((Y, X))


loop = asyncio.get_event_loop()
loop.run_until_complete(helper(dev))
