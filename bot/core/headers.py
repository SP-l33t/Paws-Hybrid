import re


headers_app = {
    'Accept': 'application/json',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'en-US,en;q=0.9',
    'Origin': 'https://app.paws.community',
    'Referer': 'https://app.paws.community/',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-site',
    'Sec-Ch-Ua-Mobile': '?1',
    'Sec-Ch-Ua-Platform': '"Android"',
    'X-Requested-With': "org.telegram.messenger"
}

headers_pwa = {
    'Accept': 'application/json',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'en-US,en;q=0.9',
    'Origin': 'https://paws.community',
    'Referer': 'https://paws.community/',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-site',
    'Sec-Ch-Ua-Mobile': '?1',
    'Sec-Ch-Ua-Platform': '"Android"',
}


def get_sec_ch_ua(user_agent, is_webview=True):
    pattern = r'(Chrome|Chromium)\/(\d+)\.(\d+)\.(\d+)\.(\d+)'

    match = re.search(pattern, user_agent)

    if match:
        version = match.group(2)
        browser = "Android WebView" if is_webview else "Google Chrome"
        return {'Sec-Ch-Ua': f'"{browser}";v="{version}", "Chromium";v="{version}", "Not?A_Brand";v="24"'}
    else:
        return {}
