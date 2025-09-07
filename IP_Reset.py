import time, subprocess, keyboard, configparser, importlib
from lang import running_translations

config = configparser.ConfigParser()
config.read("config.ini")
USERNAME = config["CONFIG"]["username"]
PASSWORD = config["CONFIG"]["password"]
MODEM    = config["CONFIG"]["modem"]
URL      = config["CONFIG"]["url"]

def import_from_path(path: str):
    module_path, func_name = path.rsplit(".", 1)
    module = importlib.import_module(module_path)
    return getattr(module, func_name)

restart_modem_connection = import_from_path(f"modems.{MODEM}.restart_modem_connection")

def check_for_IP_timer():
    out = subprocess.check_output("schtasks.exe /query /tn IP_Timer").decode("utf-8", errors="ignore")
    if any(word in out for word in running_translations):
        return True
    return False

def main():

    was_running = check_for_IP_timer()

    if was_running:
        print("SHUTTING DOWN IP_TIMER...")
        subprocess.run("schtasks.exe /end /tn IP_Timer > NUL 2>&1", shell=True)
    else:
        print("NO ISTANCE OF IP_TIMER FOUND!")

    restart_modem_connection(USERNAME, PASSWORD, URL)

    if was_running:
        print("RESTARTING IP_TIMER...")
        subprocess.run("schtasks.exe /run /tn IP_Timer > NUL 2>&1", shell=True)

    print("PROCESS COMPLETED!")

    while True:
        if keyboard.is_pressed("q"):
            time.sleep(0.001)
            break

if __name__ == "__main__":
    main()