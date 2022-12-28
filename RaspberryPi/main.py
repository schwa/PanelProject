import asyncio
import random
from gui import *

screen = Screen()

rows = 4
cols = 4
cell_width = screen.width // cols
cell_height = screen.height // rows
for row in range(rows):
    for col in range(cols):
        r = Rectangle(col * cell_width, row * cell_height, cell_width, cell_height)
        hue = random.randrange(0, 360)
        button = Button(r, f"hsl({hue}, 100%, 50%)")
        button.id = (col, row)
        screen.view.children.append(button)


async def helper(device):
    async for event in device.async_read_loop():
        screen.redraw()
        screen.handle_event(event)


async def main():
    await asyncio.gather(helper(screen.touchscreenDevice))


screen.redraw()
asyncio.run(main())
