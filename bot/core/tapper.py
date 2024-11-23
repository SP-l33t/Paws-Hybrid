import aiohttp
import asyncio
import json
import re
import ssl
from urllib.parse import unquote, parse_qs
from aiocfscrape import CloudflareScraper
from aiohttp_proxy import ProxyConnector
from better_proxy import Proxy
from random import uniform, randint, shuffle
from time import time

from bot.utils.universal_telegram_client import UniversalTelegramClient

from bot.config import settings
from bot.utils import logger, log_error, config_utils, CONFIG_PATH, first_run
from bot.exceptions import InvalidSession
from .headers import headers, get_sec_ch_ua

API_ENDPOINT = "https://api.paws.community/v1"
TASKS_WL = {
    "672a933a7470fdfea331be92": "One falls, one rises",
    "6729082b93d9038819af5e77": " Put 🐾 in your name",
    "6730dc5674fd6bd0dd6904dd": "Join Tomarket Channel",
    "6730dc6e74fd6bd0dd6904df": "Join X Empire Channel",
    "6730dc3374fd6bd0dd6904db": "Join Cats Channel",
    "6727ca4c1ee144b53eb8c08a": "Join Blum Channel",
    "6714e8b80f93ce482efae727": "Follow channel",
    "671b8ee422d15820f13dc61d": "Connect wallet",
    "671b8ecb22d15820f13dc61a": "Invite 10 friends",
    "6734ef65594f8f54c07887f9": "Check PAWS TG sub",
    "67362326ce14073e9a9e0144": "Join PAWS Cult X",
    "673653c2ce14073e9a9e0153": "Share your PAWS (+image)",
    "6740b35b15bd1d26b7b7126b": "Check PAWS X",
    "6740b33415bd1d26b7b71269": "Check PAWS TG",
    "673a23760f9acd0470329409": "Study PAWS"
}
TASKS_BL = {
    "6730b42d74fd6bd0dd6904c1": "Go vote",
    "6730b44974fd6bd0dd6904c3": "Vote for a winner",
    "6730b45874fd6bd0dd6904c5": "Vote for a loser",
    "6730b47b74fd6bd0dd6904c7": "Mystery Quest",
    "6727ca831ee144b53eb8c08c": "Boost PAWS channel"
}


def sanitize_string(input_str: str):
    return re.sub(r'[<>]', '', input_str)


class Tapper:
    def __init__(self, tg_client: UniversalTelegramClient):
        self.tg_client = tg_client
        self.session_name = tg_client.session_name

        session_config = config_utils.get_session_config(self.session_name, CONFIG_PATH)

        if not all(key in session_config for key in ('api', 'user_agent')):
            logger.critical(self.log_message('CHECK accounts_config.json as it might be corrupted'))
            exit(-1)

        self.headers = headers
        user_agent = session_config.get('user_agent')
        self.headers['user-agent'] = user_agent
        self.headers.update(**get_sec_ch_ua(user_agent))

        self.proxy = session_config.get('proxy')
        if self.proxy:
            proxy = Proxy.from_str(self.proxy)
            self.tg_client.set_proxy(proxy)

        self.ref_id = None
        self.access_token = None
        self.user_data = None
        self.ref_count = 0
        self.wallet = session_config.get('ton_address')

    def log_message(self, message) -> str:
        return f"<ly>{self.session_name}</ly> | {message}"

    async def get_tg_web_data(self) -> str:
        webview_url = await self.tg_client.get_app_webview_url('PAWSOG_bot', "PAWS", "uLnYLVgv")

        tg_web_data = unquote(string=webview_url.split('tgWebAppData=')[1].split('&tgWebAppVersion')[0])
        query_params = parse_qs(tg_web_data)
        self.user_data = json.loads(query_params.get('user', [''])[0])
        self.ref_id = query_params.get('start_param', [''])[0]

        return tg_web_data

    async def check_proxy(self, http_client: CloudflareScraper) -> bool:
        proxy_conn = http_client.connector
        if proxy_conn and not hasattr(proxy_conn, '_proxy_host'):
            logger.info(self.log_message(f"Running Proxy-less"))
            return True
        try:
            response = await http_client.get(url='https://ifconfig.me/ip', timeout=aiohttp.ClientTimeout(15))
            logger.info(self.log_message(f"Proxy IP: {await response.text()}"))
            return True
        except Exception as error:
            proxy_url = f"{proxy_conn._proxy_type}://{proxy_conn._proxy_host}:{proxy_conn._proxy_port}"
            log_error(self.log_message(f"Proxy: {proxy_url} | Error: {type(error).__name__}"))
            return False

    async def login(self, http_client: CloudflareScraper, init_data: str):
        ref_code = {"referralCode": self.ref_id} if self.ref_id else {}
        payload = {"data": init_data, **ref_code}

        response = await http_client.post(f"{API_ENDPOINT}/user/auth", json=payload)

        if response.status in range(200, 300):
            res_data = (await response.json()).get('data')
            if res_data:
                self.access_token = res_data[0]
                if 'authorization' in http_client.headers:
                    http_client.headers.pop('authorization')
                http_client.headers['authorization'] = f"Bearer {self.access_token}"
                if None in res_data:
                    balance = res_data[1].get('gameData', {}).get('balance')
                    self.ref_count = res_data[1].get('referralData', {}).get('referralsCount', 0)
                    logger.success(self.log_message(f"Logged in Successfully | Balance {balance}"))
                else:
                    balance = res_data[2].get('total')
                    logger.success(self.log_message(f"Registered successfully | Balance {balance}"))
                return True

        logger.warning(self.log_message(f"Failed to login. {response.status}"))
        return False

    async def get_quests(self, http_client: CloudflareScraper):
        response = await http_client.get(f"{API_ENDPOINT}/quests/list")
        if response.status in range(200, 300):
            data = (await response.json()).get('data', {})
            return data
        else:
            logger.warning(self.log_message(f"Failed to get quests: {response.status}"))
            return None

    async def complete_quest(self, http_client: CloudflareScraper, quest_id: str):
        payload = {"questId": quest_id}
        response = await http_client.post(f"{API_ENDPOINT}/quests/completed", json=payload)
        if response.status in range(200, 300):
            resp_json = await response.json()
            return resp_json.get('success')
        else:
            logger.warning(self.log_message(f"Failed to complete quest: {response.status}"))
            return None

    async def claim_quest_reward(self, http_client: CloudflareScraper, quest_id: str):
        payload = {"questId": quest_id}
        response = await http_client.post(f"{API_ENDPOINT}/quests/claim", json=payload)
        if response.status in range(200, 300):
            resp_json = await response.json()
            return resp_json.get('success') and resp_json.get('data')
        else:
            logger.warning(self.log_message(f"Failed to claim quest: {response.status}"))
            return None

    async def connect_wallet(self, http_client: CloudflareScraper):
        if not self.wallet:
            return
        wallet = {"wallet": self.wallet}
        resp = await http_client.post(f"{API_ENDPOINT}/user/wallet", json=wallet)
        if resp.status in range(200, 300):
            resp_json = await resp.json()
            return resp_json.get('success')

    async def add_emoji_to_first_name(self):
        if '🐾' not in self.user_data.get('first_name'):
            await self.tg_client.update_profile(first_name=f"{self.user_data.get('first_name')} 🐾")

    async def run(self) -> None:
        random_delay = uniform(1, settings.SESSION_START_DELAY)
        logger.info(self.log_message(f"Bot will start in <lr>{int(random_delay)}s</lr>"))
        await asyncio.sleep(delay=random_delay)

        access_token_created_time = 0
        sleep_time = 0

        ssl_context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
        ssl_context.minimum_version = ssl.TLSVersion.TLSv1_3
        proxy_conn = ProxyConnector.from_url(self.proxy, ssl=ssl_context) if self.proxy \
            else aiohttp.TCPConnector(ssl_context=ssl_context)
        async with CloudflareScraper(headers=self.headers, timeout=aiohttp.ClientTimeout(60),
                                     connector=proxy_conn) as http_client:
            while True:
                if not await self.check_proxy(http_client=http_client):
                    logger.warning(self.log_message('Failed to connect to proxy server. Sleep 150 seconds.'))
                    await asyncio.sleep(150)
                    continue

                refresh_webview_time = randint(3400, 3600)
                try:
                    if time() - access_token_created_time >= refresh_webview_time:
                        tg_web_data = await self.get_tg_web_data()

                        if not tg_web_data:
                            logger.warning(self.log_message('Failed to get webview URL'))
                            await asyncio.sleep(300)
                            continue

                        access_token_created_time = time()

                    if not await self.login(http_client, tg_web_data):
                        sleep_time = uniform(60, 600)
                        logger.info(self.log_message(f"Going to sleep for {int(sleep_time)} seconds"))
                        await asyncio.sleep(sleep_time)
                        continue

                    if self.tg_client.is_fist_run:
                        await first_run.append_recurring_session(self.session_name)
                    await asyncio.sleep(uniform(3, 10))

                    if settings.PERFORM_EMOJI_TASK:
                        await self.add_emoji_to_first_name()

                    if settings.PERFORM_TASKS:
                        tasks = await self.get_quests(http_client)
                        channel_subs = 0
                        shuffle(tasks)
                        for task in tasks:
                            if task.get('progress', {}).get('claimed'):
                                continue
                            if task.get('_id') not in TASKS_WL and task.get('_id') not in TASKS_BL:
                                logger.info(self.log_message(
                                    f"Quest with id: <lc>{task.get('_id')}</lc> and Title: <lc>{task.get('title')}</lc>"
                                    f" is not present in the white and black lists"))
                                continue
                            elif task.get('_id') in TASKS_BL:
                                continue

                            task_id = task.get('_id')
                            if task.get("checkRequirements", True) is False and task.get('code') != "emojiName":
                                pass
                            elif task.get('code') == "wallet":
                                await self.connect_wallet(http_client)
                            elif task.get('code') == "invite":
                                progress = task.get('progress', {})
                                if progress.get('current', 0) < progress.get('total', 100):
                                    continue
                            elif task.get('code') == "emojiName" and not settings.PERFORM_EMOJI_TASK:
                                continue
                            elif task.get('code') == 'telegram' and channel_subs < settings.SUBSCRIPTIONS_PER_CYCLE:
                                if task.get('progress', {}).get('status') != 'claimable':
                                    await self.tg_client.join_and_mute_tg_channel(task.get('data'))
                                    channel_subs += 1
                                    await asyncio.sleep(10)
                            status = await self.complete_quest(http_client, task_id)
                            if status:
                                await asyncio.sleep(uniform(2, 5))
                                status = await self.claim_quest_reward(http_client, task_id)
                                if status:
                                    logger.success(self.log_message(
                                        f"Successfully completed task <lg>{task.get('title')}</lg> and got "
                                        f"<lg>{task.get('rewards', [{}])[0].get('amount')}</lg> Paws"))

                            await asyncio.sleep(uniform(2, 5))

                    sleep_time = uniform(settings.SLEEP_TIME[0], settings.SLEEP_TIME[1])
                    logger.info(self.log_message(f"Nothing else to do. Gonna sleep for {int(sleep_time)}s..."))
                    await asyncio.sleep(sleep_time)

                except InvalidSession as error:
                    raise error

                except Exception as error:
                    sleep_time = uniform(60, 120)
                    log_error(self.log_message(f"Unknown error: {error} Retry in {int(sleep_time)}s"))
                    await asyncio.sleep(sleep_time)


async def run_tapper(tg_client: UniversalTelegramClient):
    runner = Tapper(tg_client=tg_client)
    try:
        await runner.run()
    except InvalidSession as e:
        logger.error(runner.log_message(f"Invalid Session: {e}"))
