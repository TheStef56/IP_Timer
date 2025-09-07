import subprocess
from lang import running_translations

out = subprocess.check_output("schtasks.exe /query /tn IP_Timer").decode("utf-8", errors="ignore")

if any(word in out for word in running_translations):
    subprocess.run("schtasks.exe /end /tn IP_Timer", shell=True)
else:
    subprocess.run("schtasks.exe /run /tn IP_Timer", shell=True)