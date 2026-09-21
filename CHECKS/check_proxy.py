import requests
import time


def check_user_proxy(types, proxy, is_it):

    
    if not proxy:
        return False, None

    start_time = time.time()

    try:
        types = types.lower().strip()
        proxy = proxy.strip()

        # Proxy type অনুযায়ী scheme
        if types == "http":
            scheme = "http"
        elif types == "https":
            scheme = "https"
        elif types == "socks4":
            scheme = "socks4"
        elif types == "socks5":
            scheme = "socks5"
        else:
            return False, None

        if is_it is False:
            return False, None

        proxy_url = f"{scheme}://{proxy}"

        proxys = {
            "http": proxy_url,
            "https": proxy_url
        }

        response = requests.get(
            "https://httpbin.org/ip",
            proxies=proxys,
            timeout=5
        )

        response_time = round((time.time() - start_time) * 1000)

        if response.ok:
            return True, response_time

        return False, None

    except requests.RequestException:
        return False, None