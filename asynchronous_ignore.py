import asyncio
import websockets

async def hello_world(websocket, path):
    print("Goodbye world")
    await websocket.wait_closed()  # Wait for the client to close the connection

async def normal():
    loopCount = 10
    while loopCount > 0:
        print("hello world")
        print(loopCount)
        start_server = websockets.serve(hello_world, "localhost", 8765)
        await start_server  # Start the server
        await asyncio.sleep(0.1)  # Optional: Add a short delay to allow server startup
        loopCount -= 1

asyncio.run(normal())
