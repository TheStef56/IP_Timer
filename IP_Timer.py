import datetime, asyncio, configparser, importlib
from tkinter import Tk, Label

CONFIG = configparser.ConfigParser()
CONFIG.read("config.ini")
USERNAME      = CONFIG["CONFIG"]["username"]
PASSWORD      = CONFIG["CONFIG"]["password"]
RESET_TIMEOUT = int(CONFIG["CONFIG"]["reset_timeout"])
INTERVAL      = int(CONFIG["CONFIG"]["interval"])
MODEM         = CONFIG["CONFIG"]["modem"]
AUTO          = CONFIG["CONFIG"]["auto"]
URL           = CONFIG["CONFIG"]["url"]
PLACEMENT     = CONFIG["CONFIG"]["placement"]

LAST_TIME = 0

def validate_placement(pl):
    try:
        if pl[0] not in "+-":
            return False
        off = pl[1:]
        delim = "+" if "+" in off else "-"
        int(off.split(delim)[0])
        int(off.split(delim)[1])
        return True
    except:
        return False

def import_from_path(path: str):
    module_path, func_name = path.rsplit(".", 1)
    module = importlib.import_module(module_path)
    return getattr(module, func_name)

get_connection_time = import_from_path(f"modems.{MODEM}.get_connection_time")

async def update_rendering(root):
    while True:
        root.update()
        await asyncio.sleep(0.01)

def ip_timeout_auto_discovery(conn_time):
    global LAST_TIME, CONFIG
    if conn_time < LAST_TIME:
        CONFIG["CONFIG"]["reset_timeout"] = LAST_TIME
        with open("config.ini", "w") as f:
            CONFIG.write(f) 
    LAST_TIME = conn_time

async def update_label(label):
    while True:
        try:
            conn_time = await get_connection_time(USERNAME, PASSWORD, URL)
            if AUTO:
                ip_timeout_auto_discovery(conn_time)                
            await asyncio.sleep(0.01)
            if conn_time == None:
                label.config(text="NET_ER")
                continue
            elif conn_time == 0:
                label.config(text="NO_NET")
            else:
                time_left = RESET_TIMEOUT - conn_time
                date_obj = datetime.datetime.utcfromtimestamp(time_left)
                sec_left_formatted = date_obj.strftime("%H:%M:%S")
                label.config(text=sec_left_formatted)
            await asyncio.sleep(INTERVAL)
        except:
            label.config(text="NO_NET")

async def main():
    global PLACEMENT
    root = Tk()
    root.title("overlay")
    if not validate_placement(PLACEMENT):
        PLACEMENT = "+0+0"
    root.geometry(f'85x30+{PLACEMENT}') 
    root.overrideredirect(True) 
    root.attributes("-transparentcolor","black") 
    root.config(bg="black")               

    l=Label(root, text="TRYING...",fg="white",font=("Arial", 14),bg="black")
    l.pack() 
    root.wm_attributes("-topmost", 1)          
    
    await asyncio.gather(update_label(l), update_rendering(root))


if __name__ == "__main__":
    asyncio.run(main())

    