from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
import PIL
from typing import Tuple
from pydrm import SimpleDrm  # https://github.com/notro/pydrm
import evdev  # https://python-evdev.readthedocs.io/en/latest/usage.html#listing-accessible-event-devices
import asyncio
from evdev import InputDevice, categorize, ecodes, KeyEvent


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


class Button:
    def __init__(self, frame: Rectangle, color):
        self.frame = frame
        self.color = color
        self.pressed = False
        self.label = None
        self.id = None

    def draw(self, draw: PIL.ImageDraw):
        if self.pressed:
            color = "white"
        else:
            color = self.color
        draw.rectangle(self.frame.abs_tuple, fill=color)

    def touch_down(self, location: Tuple[int, int]):
        self.pressed = True
        print("TOUCH_DOWN", self.id)

    def touch_up(self, location: Tuple[int, int]):
        self.pressed = False
        print("TOUCH_UP", self.id)


class View:
    def __init__(self, frame: Rectangle):
        self.frame = frame
        self.children = []

    def draw(self, draw: PIL.ImageDraw):
        for child in self.children:
            child.draw(draw)

    def resolve(self, location: Tuple[int, int]):
        for child in self.children:
            if child.frame.contains(location):
                return child
        return None

    def touch_down(self, location: Tuple[int, int]):
        view = self.resolve(location)
        if view:
            view.touch_down(location)

    def touch_up(self, location: Tuple[int, int]):
        view = self.resolve(location)
        if view:
            view.touch_up(location)


class Screen:
    def __init__(self):
        self.drm = SimpleDrm()
        # print(self.drm.inspect(True))
        # print(self.drm.inspect())

        self.image = Image.new("RGBX", self.drm.image.size)
        self.imageDraw = ImageDraw.Draw(self.image)
        self.width, self.height = self.drm.image.size

        self.view = View(Rectangle(0, 0, self.width, self.height))

        self.touchscreenDevice = InputDevice("/dev/input/event1")
        self.touch = (0, 0)
        # devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
        # for device in devices:
        #     print(device.path, device.name, device.phys)
        # /dev/input/event1 EP0110M09 -- Capacitive Touchscreen
        # /dev/input/event0 vc4 vc4/input0
        # print(dir(ecodes))
        # print(dev.capabilities())
        # print(dev.capabilities(verbose=True))
        # print(dev.capabilities(absinfo=True))

    def redraw(self):
        self.imageDraw.rectangle(
            (0, 0, self.width, self.height), fill="black", outline="black"
        )
        self.view.draw(self.imageDraw)
        self.drm.enable()
        self.image.convert("RGBX")
        self.drm.image.paste(self.image)
        self.drm.flush()
        self.drm.disable()

    def touch_down(self, location: Tuple[int, int]):
        self.view.touch_down(location)

    def touch_up(self, location: Tuple[int, int]):
        self.view.touch_up(location)

    def handle_event(self, event):
        if event.type == evdev.ecodes.EV_ABS:
            if event.code == 1:
                self.touch = (self.touch[0], event.value)
            elif event.code == 0:
                self.touch = (event.value, self.touch[1])
        elif event.type == evdev.ecodes.EV_KEY:
            event = evdev.util.categorize(event)
            if event.keystate == KeyEvent.key_down:
                self.touch_down(self.touch)
            elif event.keystate == KeyEvent.key_up:
                self.touch_up(self.touch)
