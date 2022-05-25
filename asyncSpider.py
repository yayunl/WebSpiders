import asyncio, time, requests, aiohttp

# Silence the event loop is closed message
from functools import wraps
from asyncio.proactor_events import _ProactorBasePipeTransport

def silence_event_loop_closed(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except RuntimeError as e:
            if str(e) != 'Event loop is closed':
                raise
    return wrapper

_ProactorBasePipeTransport.__del__ = silence_event_loop_closed(_ProactorBasePipeTransport.__del__)
# Silence the event loop is closed message


async def execute(x, y=20):
    print("Sum:", x+y)
    # await asyncio.sleep(2)
    time.sleep(2)
    return x+y


async def get_url(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            print("ULR=> ", url)
            resp =  await resp.text()
            print("Response is ", resp)


async def factorial(name, number):
    f = 1
    for i in range(2, number + 1):
        print(f"Task {name}: Compute factorial({number}), currently i={i}...")
        await asyncio.sleep(1)
        f *= i
    print(f"Task {name}: factorial({number}) = {f}")
    return f


async def main():
    # Schedule three calls *concurrently*:
    # tasks = [get_url('https://httpbin.org/delay/5') for i in range(5)]
    L = await asyncio.gather(get_url('https://httpbin.org/delay/5'),
                             get_url('https://httpbin.org/delay/5'))
    print("Results=> ",L)


if __name__ == '__main__':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    asyncio.run(main())