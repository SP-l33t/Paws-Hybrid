import asyncio
import re
import aiohttp
import sys
import ssl
import json
from aiocfscrape import CloudflareScraper
from random import uniform
from bot.utils import logger
from bot.config import settings
from hashlib import sha256

appUrl = "https://app.paws.community"
webUrl = "https://paws.community/app"
versions = "https://github.com/SP-l33t/Auxiliary-Data/raw/refs/heads/main/version_track.json"

headers = {
    'accept': '*/*',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36 Edg/129.0.0.0'
}


async def get_main_js_format(base_url):
    ssl_context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
    ssl_context.minimum_version = ssl.TLSVersion.TLSv1_3
    async with CloudflareScraper(headers=headers, connector=aiohttp.TCPConnector(ssl=ssl_context)) as client:
        async with client.request(url=base_url, method="GET", headers=headers) as response:
            try:
                response.raise_for_status()
                content = (await response.text()).replace("/script>", "/script>\n")
                matches = re.findall(r'src="(/.+?\.js)', content)
                return sorted(set(matches), key=len, reverse=True) if matches else None
            except Exception as e:
                if response.status == 403:
                    logger.warning(f"Cloudflare 403: {e}")
                else:
                    logger.warning(f"Error fetching the base URL: {e}")
                return None


async def get_versions(service):
    async with aiohttp.request(url=versions, method="GET") as response:
        if response.status in range(200, 300):
            return json.loads(await response.text()).get(service, {})


async def get_js_hash(path):
    async with aiohttp.request(url=appUrl+path, method="GET", headers=headers) as response:
        if response.status in range(200, 300):
            return sha256((await response.text()).encode('utf-8')).hexdigest()


async def check_base_url():
    not_updated = False
    if settings.TRACK_BOT_UPDATES:
        main_js_formats_app = await get_main_js_format(appUrl)
        main_js_formats_web = await get_main_js_format(webUrl)
        if main_js_formats_app:
            last_actual_files = await get_versions('paws')
            last_actual_js = last_actual_files.get('main_js')
            last_actual_hash = last_actual_files.get('js_hash')
            for js in main_js_formats_app:
                if last_actual_js in js:
                    live_hash = await get_js_hash(js)
                    if live_hash == last_actual_hash:
                        logger.success(f"No changes in main js file: <green>{last_actual_js}</green>")
                        not_updated = True
            if not not_updated:
                logger.error(f"Main JS updated. New file name: <lr>'{js}'</lr>. Hash: '<lr>{await get_js_hash(js)}</lr>'")
        else:
            logger.error("<lr>No main js file found. Can't continue</lr>")
            sys.exit("No main js file found. Contact me to check if it's safe to continue: https://t.me/SP_l33t")

        if main_js_formats_web:
            last_actual_files = await get_versions('paws')
            last_actual_js = last_actual_files.get('main_js_web')
            last_actual_hash = last_actual_files.get('js_hash_web')
            for js in main_js_formats_web:
                if last_actual_js in js:
                    live_hash = await get_js_hash(js)
                    if live_hash == last_actual_hash:
                        logger.success(f"No changes in web main js file: <green>{last_actual_js}</green>")
                    else:
                        logger.error(
                            f"WEB Main JS updated. New file name: <lr>'{js}'</lr>. Hash: '<lr>{await get_js_hash(js)}</lr>'")
                        sys.exit("Bot updates detected. Contact me to check if it's safe to continue: https://t.me/SP_l33t")
                elif js.split('/')[-1].startswith(last_actual_js[0:3]):
                    logger.error(f"WEB Main JS updated. New file name: <lr>'{js}'</lr>. Hash: '<lr>{await get_js_hash(js)}</lr>'")
                    sys.exit("Bot updates detected. Contact me to check if it's safe to continue: https://t.me/SP_l33t")
        else:
            logger.error("<lr>No main js file found. Can't continue</lr>")
            sys.exit("No main js file found. Contact me to check if it's safe to continue: https://t.me/SP_l33t")


async def check_bot_update_loop(start_delay: 0):
    await asyncio.sleep(start_delay)
    while settings.TRACK_BOT_UPDATES:
        await check_base_url()
        await asyncio.sleep(uniform(1500, 2000))
