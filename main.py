import asyncio
import datetime
from bs4.element import Tag
import aiohttp
import async_timeout
# https://www.crummy.com/software/BeautifulSoup/bs4/doc/
from bs4 import BeautifulSoup
import logging
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s',
                    filename='feching.log', level=logging.DEBUG)

URL = "https://eatapplepies.com/tcf-chapter-712/"
INTERVAL = datetime.timedelta(seconds=60)
ASYNC_TIMEOUT = max(10, INTERVAL.total_seconds()/2)


async def try_get_article():
    async with aiohttp.ClientSession() as session:
        try:
            async with async_timeout.timeout(ASYNC_TIMEOUT):
                async with session.get(URL) as response:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    result = soup.find("article")
                    if isinstance(result, Tag) and 'id' in result.attrs:
                        logging.debug("try update")
                        return result["id"] != "post-0"
                    else:
                        raise NotImplementedError(
                            "Page without article or without article id")
        except asyncio.TimeoutError:
            logging.warning("timeout")
            return False


async def main():
    next_update = datetime.datetime.now()+INTERVAL
    error_counter = 3
    while True:
        try:
            if await try_get_article():
                break
        except Exception as ex:
            logging.error("%s", str(ex))
            error_counter -= 1
            if error_counter > 0:
                continue
            logging.error("Exit because of errors")
            break
        await asyncio.sleep(max(0, (next_update-datetime.datetime.now()).total_seconds()))
        next_update += INTERVAL
        error_counter = 3
    got_article_time = datetime.datetime.now()
    logging.info("Got article!")
    with open("result.txt", 'a+') as out_file:
        out_file.write(str(got_article_time)+"\n")


if __name__ == "__main__":
    asyncio.run(main())
