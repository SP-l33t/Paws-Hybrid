import re


headers = {
    'accept': 'application/json',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'en-US,en;q=0.9',
    'origin': 'https://app.paws.community',
    'referer': 'https://app.paws.community/',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-site',
    'sec-ch-ua-mobile': '?1',
    'sec-ch-ua-platform': '"Android"',
    'x-requested-with': "org.telegram.messenger"
}


def get_sec_ch_ua(user_agent):
    pattern = r'(Chrome|Chromium)\/(\d+)\.(\d+)\.(\d+)\.(\d+)'

    match = re.search(pattern, user_agent)

    if match:
        version = match.group(2)

        return {'Sec-Ch-Ua': f'"Android WebView";v="{version}", "Chromium";v="{version}", "Not?A_Brand";v="24"'}
    else:
        return {}
