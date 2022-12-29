#!/usr/bin/env python

import asyncio
import websockets
import ssl
from pathlib import Path


async def echo(websocket):
    async for message in websocket:
        print(message)
        await websocket.send(message)


async def main():
    # ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    # localhost_pem = Path(__file__).with_name("localhost.pem")
    # ssl_context.load_cert_chain(localhost_pem)
    # async with websockets.serve(echo, "localhost", 8765, ssl=ssl_context):
    async with websockets.serve(echo, "localhost", 8765):
        await asyncio.Future()  # run forever


asyncio.run(main())
