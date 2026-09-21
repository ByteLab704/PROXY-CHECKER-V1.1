import json
import os

STATUS_FILE = r"DATA/WORKING/proxy.json"
TEXT_FILE   = r"DATA/WORKING/working_proxies.txt"


def save_working_proxy(proxy, proxy_type, response_time):
    """
    Save a single working proxy to both JSON and TXT files.
    response_time should be in milliseconds (the function converts it to seconds).
    """

    data = {"proxies": []}

    # Create folder if it doesn't exist
    os.makedirs(os.path.dirname(STATUS_FILE), exist_ok=True)

    # Convert milliseconds → seconds
    try:
        response_time = round(float(response_time) / 1000, 3)
    except (TypeError, ValueError):
        response_time = 0.0

    # ---------- JSON part ----------
    if os.path.exists(STATUS_FILE):
        try:
            with open(STATUS_FILE, "r", encoding="utf-8") as file:
                data = json.load(file)
        except (json.JSONDecodeError, OSError):
            data = {"proxies": []}

    # Update if already exists, otherwise add
    for item in data["proxies"]:
        if item["proxy"] == proxy:
            item["type"] = proxy_type
            item["status"] = "working"
            item["response_time"] = response_time
            break
    else:
        data["proxies"].append({
            "proxy": proxy,
            "type": proxy_type,
            "status": "working",
            "response_time": response_time
        })

    with open(STATUS_FILE, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)

    # ---------- TXT part ----------
    # Read existing proxies from text file (to avoid duplicates)
    existing = set()
    if os.path.exists(TEXT_FILE):
        try:
            with open(TEXT_FILE, "r", encoding="utf-8") as f:
                existing = {line.strip() for line in f if line.strip()}
        except OSError:
            existing = set()

    existing.add(proxy)  # add the new one

    # Write back sorted (or keep original order if you prefer)
    with open(TEXT_FILE, "w", encoding="utf-8") as f:
        for p in sorted(existing):
            f.write(p + "\n")