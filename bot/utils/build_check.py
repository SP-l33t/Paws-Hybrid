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
    'user-agent': 'Mozilla/5.0 (Linux; Android 10.0; OnePlus 10 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.9.9622.83 Mobile Safari/537.36'
}


async def get_main_js_format(client, base_url):
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


async def get_versions(client, service):
    async with client.request(url=versions, method="GET") as response:
        if response.status in range(200, 300):
            return json.loads(await response.text()).get(service, {})


async def get_js_hash(client, url, path):
    async with client.request(url=url+path, method="GET", headers=headers) as response:
        if response.status in range(200, 300):
            return sha256((await response.text()).encode('utf-8')).hexdigest()
        else:
            logger.error(f"Failed to get hash for: {url+path}, status code: {response.status}")


async def handle_missing_js_error():
    logger.error("<lr>No main js file found. Can't continue</lr>")
    sys.exit("No main js file found. Contact me to check if it's safe to continue: https://t.me/SP_l33t")


async def check_js_updates(client, js_formats, actual_js, actual_hash, js_type):
    for js in js_formats:
        if actual_js in js or js.split('/')[-1].startswith(actual_js[0:3]):
            live_hash = await get_js_hash(client, appUrl if js_type == 'app' else webUrl.removesuffix('/app'), js)

            if live_hash == actual_hash:
                logger.success(f"No changes in {js_type} main js file: <green>{actual_js}</green>")
                return

            logger.error(f"{js_type.upper()} Main JS updated. New file name: <lr>'{js}'</lr>. "
                         f"New hash: '<lr>{live_hash}</lr>' Old hash: '<lg>{actual_hash}</lg>")
            sys.exit("Bot updates detected. Contact me to check if it's safe to continue: https://t.me/SP_l33t")


async def check_updates():
    if not settings.TRACK_BOT_UPDATES:
        return

    ssl_context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
    ssl_context.minimum_version = ssl.TLSVersion.TLSv1_3
    async with CloudflareScraper(headers=headers, connector=aiohttp.TCPConnector(ssl=ssl_context)) as client:
        app_js_formats = await get_main_js_format(client, appUrl)
        web_js_formats = await get_main_js_format(client, webUrl)

        if not (app_js_formats and web_js_formats):
            await handle_missing_js_error()

        git_versions = await get_versions(client, 'paws')

        await check_js_updates(
            client=client,
            js_formats=app_js_formats,
            actual_js=git_versions.get('main_js'),
            actual_hash=git_versions.get('js_hash'),
            js_type='app'
        )

        await check_js_updates(
            client=client,
            js_formats=web_js_formats,
            actual_js=git_versions.get('main_js_web'),
            actual_hash=git_versions.get('js_hash_web'),
            js_type='web'
        )


async def check_bot_update_loop(start_delay: 0):
    await asyncio.sleep(start_delay)
    while settings.TRACK_BOT_UPDATES:
        await check_updates()
        await asyncio.sleep(uniform(1500, 2000))
