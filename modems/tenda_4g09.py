import requests, hashlib, asyncio, subprocess, time

async def get_connection_time(username, password, url):
    if not url:
        url = "http://192.168.0.1"
    host = url.split("//")[1]
    sep = ":" if ":" in host else "/"
    host = host.split(sep)[0]
    headers = {
        "referer": "strict-origin-when-cross-origin",
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "it-IT,it;q=0.9,en-US;q=0.8,en;q=0.7,es;q=0.6",
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "Content-Length": "56",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Host": host,
        "Origin": f"{url}",
        "Pragma": "no-cache",
        "Referer": f"{url}/login.html",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest"
    }

    for _ in range(10):
        try:
            r = await asyncio.to_thread(requests.post, f"{url}/login/Auth", data = {
                "username": username,
                "password": hashlib.md5(password.encode("utf-8")).hexdigest()
                },
                headers=headers,
                allow_redirects=True)

            cookie = r.request.headers.get("Cookie")

            if not cookie:
                continue
            headers.update({"Cookie": cookie})
            r = await asyncio.to_thread(requests.get, f"{url}/goform/GetSystemStatus", headers=headers)
            return int(r.json()["wanInfo"][0]["adv_connect_time"])
        except:
            print("exception")
            pass
    return None

def restart_modem_connection(username, password, url):
    if not url:
        url = "http://192.168.0.1"
    host = url.split("//")[1]
    sep = ":" if ":" in host else "/"
    host = host.split(sep)[0]
    headers = {
        "referer": "strict-origin-when-cross-origin",
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "it-IT,it;q=0.9,en-US;q=0.8,en;q=0.7,es;q=0.6",
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "Content-Length": "56",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Host": host,
        "Origin": f"{url}",
        "Pragma": "no-cache",
        "Referer": f"{url}/login.html",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest"
    }

    for _ in range(10):
        r = requests.post(f"{url}/login/Auth", data = {
            "username": username,
            "password": hashlib.md5(password.encode("utf-8")).hexdigest()
            },
            headers=headers,
            allow_redirects=True)

        cookie = r.request.headers.get("Cookie")

        if not cookie:
            time.sleep(1)
            continue
        headers.update({"Cookie": cookie})
        print("GOT COOKIE!")
        break
    if not cookie:
        print("ERROR: DIDN'T GET COOKIE!")
        subprocess.run("pause", shell=True)

    print("SENDING DISCONNECT PAYLOAD...")
    r = requests.get(f"{url}/goform/setSimWanInfo?mobileData=1&dataRoaming=1&dataOptions=1&profileIndex=0&action=0", headers=headers, allow_redirects=True)
    print(f"SENT! CODE:{r.status_code}")
    
    
    print("SENDING CONNECT PAYLOAD...")
    r = requests.get(f"{url}/goform/setSimWanInfo?mobileData=1&dataRoaming=1&dataOptions=1&profileIndex=0&action=1", headers=headers, allow_redirects=True)
    print(f"SENT! CODE:{r.status_code}")