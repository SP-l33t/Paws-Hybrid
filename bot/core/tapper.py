import aiohttp
import asyncio
import concurrent.futures
import json
import re
import ssl
from urllib.parse import unquote, parse_qs
from aiocfscrape import CloudflareScraper
from aiohttp_proxy import ProxyConnector
from better_proxy import Proxy
from random import uniform, shuffle, randint
from time import time
from twocaptcha import TwoCaptcha

from bot.utils.universal_telegram_client import UniversalTelegramClient

from bot.config import settings
from bot.utils import logger, log_error, config_utils, CONFIG_PATH, first_run, sol, ton
from bot.exceptions import InvalidSession
from .headers import headers_app, headers_pwa, get_sec_ch_ua

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
    "673a23760f9acd0470329409": "Study PAWS",
    "674b1f0c30dc53f7e9aec46a": "Mystery Quest: Scroll",
    "674dcb4b30dc53f7e9aec470": "Mystery Quest: Tabs",
    "674f45e99bfbbe63fab834f2": "Get Lucky",
    "675067faaae81a10ba5a3c4f": "GET PAWSED",
    "6751e24d561ee9de322ef182": "Check PAWS TG",
    "6751e267561ee9de322ef184": "Check PAWS X",
    "67532ea5a3770d4f94e38f6f": "REACT HARDER",
    "675729bc8a00f11f8cf8c1fd": "Reach 1st Milestone",
    "67572a2c8a00f11f8cf8c1ff": "Reach 2nd Milestone",
    "6757a207ec9bc04f1beb0e75": "Reach 3nd Milestone",
    "6757a21dec9bc04f1beb0e77": "Reach 4nd Milestone",
    "6757a232ec9bc04f1beb0e79": "Reach 5nd Milestone",
    "6758d84842df2161c728c742": "Reach 6nd Milestone",
    "675adeb56fe975fdde798265": "Infinite Milestone",
    "675dbe20995e9832d3ebb8ee": "heck PAWS TG",
    "675dbe36995e9832d3ebb8f0": "Check PAWS X",
    "675c65a74d9b0f56a8bb99f1": "Join Streaks from @tapps",
    "676467f28eb5e1e35f033d63": "Mystery Quest",
    "67654a381b49f3cc132b80cb": "Join Y Twitter",
    "6766eceedf75d42c3fff4cbc": "Wen TGE?",
    "6768c21f2e171c1a4d8e3df1": "MY PAWS GONE!!!",
    "6768c22d2e171c1a4d8e3df3": "PAWS lost, report it!",
    "6768c30f2e171c1a4d8e3df5": "#PAWSMAS COMING 🐾",
    "6768c3242e171c1a4d8e3df8": "Lil buddy almost had’em, go help!",
    "6768c3312e171c1a4d8e3dfa": "Well done, bud!",
    "6768c3402e171c1a4d8e3dfc": "Christmas Miracle",
    "67703cd95a4eb56c5f81a6e9": "Check PAWS TG",
    "67703cf45a4eb56c5f81a6eb": "Check PAWS X",
    "67797ea7df75d42c3fff4cc4": "EASY PAWS WEB Access",
    "677e875ddf75d42c3fff4cc7": "Hide & Seek",
    "677faa8e2cd0f9fc21b34d84": "Follow REP X",
    "677faa722cd0f9fc21b34d83": "Follow REP TG",
    "677faac52cd0f9fc21b34d85": "Follow Tonkeeper's TG",
    "677faaef2cd0f9fc21b34d86": "Download Tonkeeper",
    "67717bfb067c823d800e5a14": "Verify via PAWS Web",
    "678556b8ed515bd1fbea8147": "NO TIME TO RUSH",
    "67867e662397c64561caa4f6": "FIND ME PAWS",
    "67898a6b31c13aecab68289c": "Check PAWS TG",
    "67814ddc6806dce25e57fe20": "Connect wallets via Web",
    "6793b2731c49bcc7f16aa817": "Join DONOT community in X",
    "6798d977ff2e2506ca57b3e8": "Follow Buzzit X",
    "679a306ca30cce7d9db598dc": "Follow Roko",
    "6798d93aff2e2506ca57b3e5": "Follow Buzzit Channel",
    "679bc06e70efab8b96d0efdf": "Join PAWS Discord!",
    "679bcd2270efab8b96d0efe1": "Follow ARMIN",
    "67a52a71df75d42c3fff4cd7": "Follow DUDE",
    "67ace20fb2da260fdacba414": "Follow PAWS YouTube",
    "67ace1f8b2da260fdacba412": "Follow PAWS TikTok"
}
TASKS_BL = {
    "6730b42d74fd6bd0dd6904c1": "Go vote",
    "6730b44974fd6bd0dd6904c3": "Vote for a winner",
    "6730b45874fd6bd0dd6904c5": "Vote for a loser",
    "6730b47b74fd6bd0dd6904c7": "Mystery Quest",
    "6727ca831ee144b53eb8c08c": "Boost PAWS channel",
    "6740b2cb15bd1d26b7b71266": "Add PAWS emoji",  # Only Premium
    "6754c09b5de2c352526ab323": "Explore TON",
    "6754c1065de2c352526ab324": "Mystery Quest",
    "6756c53f0284d9d7b208dd50": "Lucky Block"
}

NO_ADDITIONAL_DATA = ["67867e662397c64561caa4f6"]
NO_TG_SUB_NEEDED = ["6798d977ff2e2506ca57b3e8",
                    "679a306ca30cce7d9db598dc",
                    "679bc06e70efab8b96d0efdf",
                    "67a52a71df75d42c3fff4cd7",
                    "67ace20fb2da260fdacba414",
                    "67ace1f8b2da260fdacba412"]

AIRDROP_CRITERIAS = ["completedQuestsCounter",
                     "userReferrals",
                     "verifiedOnWebsite",
                     "grinchRemoved",
                     "activityCheck"]

CODE = "oSmGOqWsuFNw"


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

        self.headers = headers_app.copy()
        self.headers_pwa = headers_pwa.copy()
        user_agent = session_config.get('user_agent')
        self.headers['user-agent'] = user_agent
        self.headers_pwa['user-agent'] = user_agent
        self.headers_pwa.update(**get_sec_ch_ua(user_agent, False))
        self.headers.update(**get_sec_ch_ua(user_agent))

        self.proxy = session_config.get('proxy')
        if self.proxy:
            proxy = Proxy.from_str(self.proxy)
            self.tg_client.set_proxy(proxy)

        self.ton_wallet = session_config.get('ton')
        self.sol_wallet = session_config.get('sol')

        self.sol_connected = None
        self.ton_connected = None

        self.ref_id = None
        self.access_token = None
        self.access_token_pwa = None
        self.user_data = None
        self.ref_count = 0
        self.wallet = session_config.get('ton', {}).get('wallet_address')

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
                if len(res_data) > 1:
                    self.sol_connected = res_data[1].get('userData', {}).get('proofSolanaWallet')
                    ton_hex_addr = res_data[1].get('userData', {}).get('proofTonWallet')
                    self.ton_connected = ton.hex_to_uf_address(ton_hex_addr) if ton_hex_addr else ton_hex_addr
                if 'authorization' in http_client.headers:
                    http_client.headers.pop('authorization')
                http_client.headers['authorization'] = f"Bearer {self.access_token}"
                if None in res_data:
                    balance = res_data[1].get('gameData', {}).get('balance')
                    self.ref_count = res_data[1].get('referralData', {}).get('referralsCount', 0)
                    logger.success(self.log_message(f"Logged in Successfully | Balance: <lc>{balance}</lc> | "
                                                    f"SOL: <lc>{self.sol_connected}</lc> | "
                                                    f"TON: <lc>{self.ton_connected}</lc>"))
                else:
                    balance = res_data[2].get('total')
                    logger.success(self.log_message(f"Registered successfully | Balance {balance}"))
                return True

        logger.warning(self.log_message(f"Failed to login. {response.status}"))
        return False

    async def login_pwa(self, http_client: CloudflareScraper, init_data: str):
        payload = {"data": init_data}

        response = await http_client.post(f"{API_ENDPOINT}/user/auth", json=payload)

        if response.status in range(200, 300):
            res_data = (await response.json()).get('data')
            if res_data:
                self.access_token_pwa = res_data[0]
                if len(res_data) > 1:
                    self.sol_connected = res_data[1].get('userData', {}).get('proofSolanaWallet')
                    ton_hex_addr = res_data[1].get('userData', {}).get('proofTonWallet')
                    self.ton_connected = ton.hex_to_uf_address(ton_hex_addr) if ton_hex_addr else ton_hex_addr
                if 'authorization' in http_client.headers:
                    http_client.headers.pop('authorization')
                http_client.headers['authorization'] = f"Bearer {self.access_token_pwa}"
                return True

        logger.warning(self.log_message(f"Failed to login in pwa. {response.status}"))
        return False

    async def get_user_pwa(self, http_client: CloudflareScraper):
        resp = await http_client.get(f"{API_ENDPOINT}/user")
        if resp.status in range(200, 300):
            resp = await resp.json()
            return resp.get('success')

    async def get_quests(self, http_client: CloudflareScraper):
        response = await http_client.get(f"{API_ENDPOINT}/quests/list")
        if response.status in range(200, 300):
            data = (await response.json()).get('data', {})
            return data
        else:
            logger.warning(self.log_message(f"Failed to get quests: {response.status}"))
            return None

    async def complete_quest(self, http_client: CloudflareScraper, quest_id: str, x: int = None, y: int = None):
        payload = {"questId": quest_id}
        if x and y:
            payload["additionalData"] = {
                "x": x,
                "y": y,
                "timestamp": int(time() * 1000)
            }
        response = await http_client.post(f"{API_ENDPOINT}/quests/completed", json=payload)
        if response.status in range(200, 300):
            resp_json = await response.json()
            return resp_json.get('success')
        else:
            logger.warning(self.log_message(f"Failed to complete quest: {response.status}"))
            return None

    async def custom_complete_quest(self, http_client: CloudflareScraper, quest_id: str, code: str):
        payload = {"questId": quest_id, "code": code}
        response = await http_client.post(f"{API_ENDPOINT}/quests/custom", json=payload)
        if response.status in range(200, 300):
            resp_json = await response.json()
            return resp_json.get('success') and resp_json.get('data')
        else:
            logger.warning(self.log_message(f"Failed to complete quest: {response.status}"))
            return None

    async def claim_quest_reward(self, http_client: CloudflareScraper, quest_id: str, additional_data: bool = True):
        payload = {"questId": quest_id}
        if additional_data:
            payload["additionalData"] = {
                "x": randint(300, 450),
                "y": randint(300, 450),
                "timestamp": int(time() * 1000)
            }
        response = await http_client.post(f"{API_ENDPOINT}/quests/claim", json=payload)
        if response.status in range(200, 300):
            resp_json = await response.json()
            data = resp_json.get('data')
            is_success = resp_json.get('success', False)
            return (data or resp_json) if is_success else False
        else:
            logger.warning(self.log_message(f"Failed to claim quest: {response.status}"))
            return False

    async def connect_ton_wallet_app(self, http_client: CloudflareScraper):
        if not self.wallet:
            return
        wallet = {"wallet": self.wallet}
        resp = await http_client.post(f"{API_ENDPOINT}/user/wallet", json=wallet)
        if resp.status in range(200, 300):
            resp_json = await resp.json()
            return resp_json.get('success')

    async def get_ton_payload(self, http_client: CloudflareScraper):
        resp = await http_client.get(f"{API_ENDPOINT}/wallet/ton/payload")
        if resp.status in range(200, 300):
            return (await resp.json()).get('data')

    async def get_sol_payload(self, http_client: CloudflareScraper):
        resp = await http_client.get(f"{API_ENDPOINT}/wallet/solana/payload")
        if resp.status in range(200, 300):
            return (await resp.json()).get('data')

    async def check_eligibility(self, http_client: CloudflareScraper) -> list[dict]:
        resp = await http_client.get(f"{API_ENDPOINT}/eligibility")
        if resp.status in range(200, 300):
            return (await resp.json()).get('data')
        return []

    async def solve_captcha(self) -> dict:
        solver = TwoCaptcha(settings.TWOCAPTCHA_API)
        for i in range(5):
            try:
                balance = solver.balance()
                if balance > 0.1:
                    logger.info(self.log_message(f'2Captcha Balance: {solver.balance()}'))
                else:
                    logger.warning(self.log_message(f'2Captcha Balance is too low: {balance}'))
                    return {}
                loop = asyncio.get_running_loop()
                with concurrent.futures.ThreadPoolExecutor() as pool:
                    return await loop.run_in_executor(pool,
                                                      lambda: solver.recaptcha(sitekey="6Lda_s0qAAAAAItgCSBeQN_DVlM9YOk9MccqMG6_",
                                                                               url="https://paws.community/app?tab=claim",
                                                                               version='v2',
                                                                               enterprise=1,
                                                                               userAgent=self.headers['user-agent'],
                                                                               action="submit",
                                                                               softId=4801))
            except Exception as e:
                logger.warning(self.log_message(f'Failed to solve captcha. Retrying {e}'))
                await asyncio.sleep(uniform(5, 10))
                return await self.solve_captcha()

    async def complete_activity_check(self, http_client: CloudflareScraper):
        recap = await self.solve_captcha()
        if not recap.get('code'):
            return False
        payload = {"recaptchaToken": recap.get('code')}
        resp = await http_client.post(f"{API_ENDPOINT}/user/activity", json=payload)
        if resp.status in range(200, 300):
            resp = await resp.json()
            return resp.get('success') and resp.get('data')

    async def connect_sol_web(self, http_client: CloudflareScraper, token: str):
        keypair = sol.import_sol_wallet(self.sol_wallet.get('private_key'))
        signature = sol.generate_sol_signature(keypair, token.encode("utf-8"))
        payload = {
            "signature": str(signature),
            "publicKey": str(keypair.pubkey()),
            "token": token
        }
        resp = await http_client.post(f"{API_ENDPOINT}/wallet/solana/check_proof", json=payload)
        if resp.status in range(200, 300):
            resp_json = await resp.json()
            return resp_json.get('success') and resp_json.get('data')

    async def connect_ton_web(self, http_client: CloudflareScraper, token: str):
        payload = ton.generate_ton_proof_v2(self.ton_wallet.get("mnemonic_phrase"), "app.paws.community", token)
        resp = await http_client.post(f"{API_ENDPOINT}/wallet/ton/check_proof", json=payload)
        if resp.status in range(200, 300):
            resp_json = await resp.json()
            return resp_json.get('success') and resp_json.get('data')

    async def disconnect_sol_web(self, http_client: CloudflareScraper):
        resp = await http_client.post(f"{API_ENDPOINT}/wallet/solana/reset", data="")
        if resp.status in range(200, 300):
            return (await resp.json()).get('success')

    async def disconnect_ton_web(self, http_client: CloudflareScraper):
        resp = await http_client.post(f"{API_ENDPOINT}/wallet/ton/reset", data="")
        if resp.status in range(200, 300):
            return (await resp.json()).get('success')

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
        async with CloudflareScraper(headers=self.headers, timeout=aiohttp.ClientTimeout(60), connector=proxy_conn) as http_client,\
                CloudflareScraper(headers=self.headers_pwa, timeout=aiohttp.ClientTimeout(60), connector=proxy_conn) as http_client_pwa:
            while True:
                if not await self.check_proxy(http_client=http_client):
                    logger.warning(self.log_message('Failed to connect to proxy server. Sleep 150 seconds.'))
                    await asyncio.sleep(150)
                    continue

                refresh_webview_time = uniform(3400, 3600)
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
                            task_id = task.get('_id')
                            task_title = sanitize_string(task.get('title'))
                            if task.get('progress', {}).get('claimed') or task.get('progress', {}).get('status') == "waiting":
                                continue
                            if task_id == "67814ddc6806dce25e57fe20" and not (self.sol_connected and self.ton_connected):
                                continue

                            if task_id not in TASKS_WL and task_id not in TASKS_BL:
                                logger.info(self.log_message(
                                    f"Quest with id: <lc>{task_id}</lc> and Title: <lc>{task_title}</lc>"
                                    f" is not present in the white and black lists"))
                                continue
                            elif task_id in TASKS_BL:
                                continue

                            if task.get("checkRequirements", True) is False and task.get('code') != "emojiName":
                                pass
                            elif task.get('code') == "wallet":
                                await self.connect_ton_wallet_app(http_client)
                            elif task.get('code') == "invite":
                                progress = task.get('progress', {})
                                if progress.get('current', 0) < progress.get('total', 100):
                                    continue
                            elif task.get('code') == "emojiName" and not settings.PERFORM_EMOJI_TASK:
                                continue
                            elif task.get('code') == 'telegram' and task_id not in NO_TG_SUB_NEEDED and channel_subs < settings.SUBSCRIPTIONS_PER_CYCLE:
                                if task.get('progress', {}).get('status') != 'claimable':
                                    await self.tg_client.join_and_mute_tg_channel(task.get('data'))
                                    channel_subs += 1
                                    await asyncio.sleep(10)

                            if task.get('type') == "pwa":
                                if not http_client_pwa.headers.get('authorization') and task.get('progress', {}).get('status', "") != "claimable":
                                    await self.login_pwa(http_client_pwa, tg_web_data)
                                    await asyncio.sleep(uniform(2, 5))
                                    pwa_user = await self.get_user_pwa(http_client_pwa)
                                    if pwa_user:
                                        if task_id == "67867e662397c64561caa4f6":
                                            status = await self.custom_complete_quest(http_client_pwa, task_id, CODE) if \
                                                task.get('progress', {}).get('status', "") != "claimable" else True
                                            continue
                                        else:
                                            status = await self.complete_quest(http_client_pwa, task_id) if \
                                                task.get('progress', {}).get('status', "") != "claimable" else True
                                    await asyncio.sleep(uniform(5, 15))
                                else:
                                    status = True
                            else:
                                additional_data = {} if task_id == "677e875ddf75d42c3fff4cc7" else \
                                    {'x': -1, 'y': -1} if task_id == "67814ddc6806dce25e57fe20" else \
                                    {'x': randint(300, 450), 'y': randint(300, 450)}
                                status = await self.complete_quest(http_client, task_id, **additional_data) if \
                                    task.get('progress', {}).get('status', "") != "claimable" else True

                            if task_id == "678556b8ed515bd1fbea8147" and task.get('progress', {}).get('status', "") != "claimable":
                                if status:
                                    logger.info(self.log_message(f"Successfully started task: <lg>{task_title}</lg>."))
                                continue
                            elif task_id == "67814ddc6806dce25e57fe20" and status:
                                logger.info(self.log_message(f"Successfully completed task: <lg>{task_title}</lg>."))
                                continue

                            if status:
                                await asyncio.sleep(uniform(2, 5))
                                status = await self.claim_quest_reward(http_client, task_id) if task_id not in NO_ADDITIONAL_DATA else await self.claim_quest_reward(http_client, task_id, False)
                                reward = status.get('amount', 0) if isinstance(status, dict) else \
                                    task.get('rewards', [{}])[0].get('amount') if len(task.get('rewards', [{}])) else 0
                                if status:
                                    logger.success(self.log_message(
                                        f"Successfully completed task <lg>{task_title}</lg>"
                                        f"{f' and got <lg>{reward}</lg> Paws' if reward else ''}"))

                            await asyncio.sleep(uniform(2, 5))

                    if not http_client_pwa.headers.get('authorization'):
                        await self.login_pwa(http_client_pwa, tg_web_data)
                        await asyncio.sleep(uniform(2, 5))

                    if settings.CONNECT_WALLETS_WEB:
                        if settings.OVERWRITE_WALLETS:
                            if self.sol_connected and self.sol_connected != self.sol_wallet.get('public_key'):
                                logger.warning(self.log_message(f"SOL Wallets mismatch: "
                                                                f"Connected: <ly>{self.sol_connected}</ly>. "
                                                                f"Config <ly>{self.sol_wallet.get('public_key')}</ly>"))
                                if await self.disconnect_sol_web(http_client_pwa):
                                    logger.info(self.log_message("Successfully disconnected wallet"))
                                    await asyncio.sleep(2, 4)
                                    self.sol_connected = None

                            if self.ton_connected and self.ton_connected != self.ton_wallet.get('wallet_address'):
                                logger.warning(self.log_message(f"TON Wallets mismatch: "
                                                                f"Connected: <ly>{self.ton_connected}</ly>. "
                                                                f"Config <ly>{self.ton_wallet.get('wallet_address')}</ly>"))
                                if await self.disconnect_ton_web(http_client_pwa):
                                    logger.info(self.log_message("Successfully disconnected wallet"))
                                    await asyncio.sleep(2, 4)
                                    self.ton_connected = None

                        if not self.sol_connected:
                            payload = await self.get_sol_payload(http_client_pwa)
                            await asyncio.sleep(uniform(15, 30))
                            if payload and await self.connect_sol_web(http_client_pwa, payload):
                                logger.success(self.log_message(f"Successfully connected SOL wallet: "
                                                                f"<ly>{self.sol_wallet.get('public_key')}</ly>"))

                        if not self.ton_connected:
                            if not self.ton_wallet.get('mnemonic_phrase'):
                                logger.info(self.log_message("No Mnemonic found in config. "
                                                             "Edit config and restart the script"))
                            else:
                                payload = await self.get_ton_payload(http_client_pwa)
                                await asyncio.sleep(uniform(15, 30))
                                if payload and await self.connect_ton_web(http_client_pwa, payload):
                                    logger.success(self.log_message(f"Successfully connected TON wallet: "
                                                                    f"<ly>{self.ton_wallet.get('wallet_address')}</ly>"))

                    if settings.TWOCAPTCHA_API:

                        elig = (await self.check_eligibility(http_client_pwa))
                        elig = list(filter(lambda x: x.get('criteriaName') in AIRDROP_CRITERIAS, elig)) if len(elig) else []
                        elig = {x.get('criteriaName'): x for x in elig}
                        all_other_criteria_met = all(
                            value["meetsCriteria"]
                            for key, value in elig.items() if key not in {"completedQuestsCounter", "userReferrals"}
                        )

                        at_least_one_quest_or_referral_met = any(
                            elig[key]["meetsCriteria"]
                            for key in {"completedQuestsCounter", "userReferrals"}
                        )

                        result = all_other_criteria_met and at_least_one_quest_or_referral_met

                        failed_criteria = []
                        if not result:
                            if not all_other_criteria_met:
                                failed_criteria.extend([
                                    value["criteriaName"]
                                    for key, value in elig.items()
                                    if key not in {"completedQuestsCounter", "userReferrals"} and not value["meetsCriteria"]
                                ])
                            if not at_least_one_quest_or_referral_met:
                                failed_criteria.extend([
                                    value["criteriaName"]
                                    for key, value in elig.items()
                                    if key in {"completedQuestsCounter", "userReferrals"} and not value["meetsCriteria"]
                                ])
                            if failed_criteria:
                                logger.info(self.log_message("The following AirDrop criterias weren't met: " + ", ".join(failed_criteria)))

                        if len(failed_criteria) == 1 and failed_criteria[0] == "activityCheck":
                            if await self.complete_activity_check(http_client_pwa):
                                logger.success(self.log_message('Successfully completed Activity Check (captcha)'))
                        elif not failed_criteria:
                            logger.success(self.log_message('Good Job. Account is eligible for AirDrop'))

                    logger.info(self.log_message(f"All activities for the current session have been completed"))
                    return

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
