import asyncio, aiohttp, json
from config import *

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


# Config semaphore to control max # of requests sent at the same time
semaphore = asyncio.Semaphore(CONCURRENCY)
# aiohttp session
session = None


async def fetch_examples():
    # Schedule three calls *concurrently*:
    tasks = [fetch_url('https://httpbin.org/delay/5', params={f'greeting {i}': 'hello'}, fetch_field='args') for i in range(20)]
    results = await asyncio.gather(*tasks)

    # results = await asyncio.gather(fetch_url('https://httpbin.org/post', data={"greeting": 'Hello!'},
    #                                    http_method='post',
    #                                    fetch_field='form'), # Post a form
    #                          fetch_url('https://httpbin.org/delay/2', params={"location": 'Austin,TX'},
    #                                    http_method='get',
    #                                    fetch_field='args'), # Get request with params
    #                          fetch_url('https://httpbin.org/post', json={"json": 'Hello json!'},
    #                                    http_method='post',
    #                                    fetch_field='json') # Post a form with data in json
    #                          )
    print("Results => ", results)


async def fetch_url(url, http_method='get', fetch_field='all', **kwargs):
    """
    Send an asynchronous GET request and await for the response.
    :param url:
    :param http_method: HTTP method (i.e. 'get', 'post','put', 'delete')
    :param fetch_field: Specify the field name of the returned value in the response. Default is 'all'
    :param kwargs:
    :return:
    """
    async with semaphore:
        # Get the function by its name. i.e. session.get()
        method_to_call = getattr(session, http_method)
        try:
            async with method_to_call(url, **kwargs) as resp:
                logging.info("Fetch URL=> %s", url)
                resp, status = await resp.json(), resp.status

                if fetch_field == 'all':
                    return resp
                else:
                    # Convert string to json
                    js_result = json.loads(resp)
                    return js_result.get(fetch_field)

        except aiohttp.ClientError:
            logging.error("Error occurred while scrapping url => %s", url, exc_info=True)


async def save_data(data):
    """
    Save the parsed data to the database.
    :param data:
    :return:
    """
    logging.info("Saving data to db. data=> %s", data)
    if data:
        return await db_coll.update_one({
            'id': data.get('id')
        }, {'$set': data},
            upsert=True)


async def fetch_book_details_then_save_to_db(book_id):
    """
    Fetch the book details and save to the db.
    :param book_id:
    :return:
    """
    url = DETAILS_URL.format(book_id=book_id)
    book_details = await fetch_url(url)
    await save_data(book_details)


async def main():
    global session
    timeout = 10  # seconds
    client_timeout = aiohttp.ClientTimeout(total=timeout)
    session = aiohttp.ClientSession(timeout=client_timeout)

    # Make requests to the target website and retrieve the book ids
    scrap_urls = [INDEX_URL.format(offset=ITEMS_PER_PAGE * (page-1)) for page in range(1, PAGE_NUMBER+1)]
    tasks = [fetch_url(url) for url in scrap_urls]
    results = await asyncio.gather(*tasks)
    logging.info('Results %s', json.dumps(results, ensure_ascii=False, indent=2))

    # Retrieve the details of books with given ids and save the parsed data to database
    book_ids = [item.get('id') for book_data in results for item in book_data.get('results') if book_data]
    fetch_details_and_save_tasks = [fetch_book_details_then_save_to_db(id) for id in book_ids]
    await asyncio.gather(*fetch_details_and_save_tasks)

if __name__ == '__main__':
    # For Windows only. To suppress warning of event loop closed earlier
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    asyncio.run(main())