import asyncio, time, requests, aiohttp, json

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


async def factorial(name, number):
    f = 1
    for i in range(2, number + 1):
        print(f"Task {name}: Compute factorial({number}), currently i={i}...")
        await asyncio.sleep(1)
        f *= i
    print(f"Task {name}: factorial({number}) = {f}")
    return f


async def fetch_url(url, http_method='get', fetch_field='args', **kwargs):
    """
    Send an asynchronous GET request and await for the response.
    :param url:
    :param http_method: HTTP method (i.e. 'get', 'post','put', 'delete')
    :param fetch_field: the field name of the returned value in the response
    :param kwargs:
    :return:
    """
    async with aiohttp.ClientSession() as session:
        # Get the function by its name. i.e. session.get()
        method_to_call = getattr(session, http_method)
        async with method_to_call(url, **kwargs) as resp:
            print("Fetch URL=> ", url)
            resp, status = await resp.text(), resp.status
            print("Response is ", resp, " Status code is ", status)
            # Convert string to json
            js_result = json.loads(resp)
            return js_result.get(fetch_field)


async def main():
    # Schedule three calls *concurrently*:
    # tasks = [get_url('https://httpbin.org/delay/5') for i in range(5)]
    L = await asyncio.gather(fetch_url('https://httpbin.org/delay/5', data={"greeting": 'Hello!'},
                                       http_method='post',
                                       fetch_field='form'),
                             fetch_url('https://httpbin.org/delay/5', params={"location": 'Austin,TX'},
                                       http_method='get',
                                       fetch_field='args'))
    print("Results => ", L)


if __name__ == '__main__':
    # For Windows only. To suppress warning of event loop closed earlier
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    asyncio.run(main())