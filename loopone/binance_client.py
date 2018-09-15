import aiohttp
import asyncio

loop = asyncio.get_event_loop()
# loop.run_until_complete(main())
STREAM_URL = "wss://stream.binance.com:9443/"


async def fetch(session, url):
    async with session.get(url) as response:
        return await response.text()


async def gener():
    for i in range(10):
        yield i
        await asyncio.sleep(3)


# TODO check 24hr, restart if websocket stops
async def get_python():
    # session = aiohttp.ClientSession(loop=loop)
    # async with session.ws_connect(
    #     f"{STREAM_URL}stream?streams=ethbtc@ticker/ethbtc@kline_1h"
    # ) as ws:
    #     # async for msg in ws:
    #     #     print(msg)
    #     #     break
    #     while True:
    #         msg = await ws.receive()
    #         print(msg)
    # await session.close()
    async for x in gener():
        print(x)


loop.run_until_complete(get_python())
loop.close()
