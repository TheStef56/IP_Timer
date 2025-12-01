import requests, hashlib, asyncio, subprocess, time, traceback

class modemLogin():
    def __init__(self, username: str, password: str, url: str = None):
        self.username = username
        self.password = password
        self.url = url if url else "http://192.168.0.1"
        self.host = self.url.split("//")[1]
        self.sep = ":" if ":" in self.host else "/"
        self.host = self.host.split(self.sep)[0]
        self.headers = {
            "referer": "strict-origin-when-cross-origin",
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "it-IT,it;q=0.9,en-US;q=0.8,en;q=0.7,es;q=0.6",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Host": self.host,
            "Origin": f"{self.url}",
            "Pragma": "no-cache",
            "Referer": f"{self.url}/login.html",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            "X-Requested-With": "XMLHttpRequest"
        }

    def getCookieHeaders(self):
        for _ in range(10):
            r = requests.post(f"{self.url}/login/Auth", data = {
                "username": self.username,
                "password": hashlib.md5(self.password.encode("utf-8")).hexdigest()
                },
                headers=self.headers,
                allow_redirects=True)

            cookie = r.request.headers.get("Cookie")

            if not cookie:
                time.sleep(1)
                continue
            self.headers.update({"Cookie": cookie})
            print("GOT COOKIE!")
            return self.headers
        return None
    
    async def asyncGetCookieHeaders(self):
        for _ in range(10):
            try:
                r = await asyncio.to_thread(requests.post, f"{self.url}/login/Auth", data = {
                    "username": self.username,
                    "password": hashlib.md5(self.password.encode("utf-8")).hexdigest()
                    },
                    headers=self.headers,
                    allow_redirects=True)

                cookie = r.request.headers.get("Cookie")

                if not cookie:
                    continue
                self.headers.update({"Cookie": cookie})
                return self.headers
            except Exception as e:
                traceback.print_exception(e)
                pass
        return None

async def get_connection_time(username, password, url):
    try:
        login = modemLogin(username, password, url)
        headers = await login.asyncGetCookieHeaders()
        if not headers:
            return None
        r = await asyncio.to_thread(requests.get, f"{login.url}/goform/GetSystemStatus", headers=headers)
        return int(r.json()["wanInfo"][0]["adv_connect_time"])
    except Exception as e:
            traceback.print_exception(e)
            pass
    return None

async def get_messages(username, password, url):
    login = modemLogin(username, password, url)
    headers = await login.asyncGetCookieHeaders()
    if not headers:
        return None
    try:
        r = await asyncio.to_thread(requests.get, f"{login.url}/goform/getSimList", headers=headers)
        return [x for x in r.json() if x.get("index")]
    except Exception as e:
        traceback.print_exception(e)
    return None

def restart_modem_connection(username, password, url):
    login = modemLogin(username, password, url)
    headers = login.getCookieHeaders()
    if not headers:
        print("ERROR: DIDN'T GET COOKIE!")
        subprocess.run("pause", shell=True)
        return

    print("SENDING DISCONNECT PAYLOAD...")
    r = requests.get(f"{login.url}/goform/setSimWanInfo?mobileData=1&dataRoaming=1&dataOptions=1&profileIndex=0&action=0", headers=headers, allow_redirects=True)
    print(f"SENT! CODE:{r.status_code}")
    
    
    print("SENDING CONNECT PAYLOAD...")
    r = requests.get(f"{login.url}/goform/setSimWanInfo?mobileData=1&dataRoaming=1&dataOptions=1&profileIndex=0&action=1", headers=headers, allow_redirects=True)
    print(f"SENT! CODE:{r.status_code}")