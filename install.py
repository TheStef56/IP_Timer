import tkinter as tk, os, configparser, shutil, sys, ctypes, pathlib
from tkinter import ttk, messagebox, filedialog

def is_int(char):
    return char.isdigit()

class Install():
    def __init__(self):
        if not self.is_admin():
            ctypes.windll.shell32.ShellExecuteW(
                None, "runas", sys.executable, " ".join(sys.argv), None, 0
            )
            sys.exit()
        self.root = tk.Tk()
        self.root.title("Configuration Form")
        self.root.geometry("400x660")
        self.root.resizable(False, False)

        vis_int = (self.root.register(is_int), "%S")

        tk.Label(self.root, text="*Username:").pack(anchor="w", padx=10, pady=(10, 0))
        self.username_entry = tk.Entry(self.root, width=40)
        self.username_entry.pack(padx=10, pady=5)

        tk.Label(self.root, text="*Password:").pack(anchor="w", padx=10, pady=(10, 0))
        self.password_entry = tk.Entry(self.root, show="*", width=40)
        self.password_entry.pack(padx=10, pady=5)

        tk.Label(self.root, text="URL (default depends on modem):").pack(anchor="w", padx=10, pady=(10, 0))
        self.url = tk.Entry(self.root, width=40)
        self.url.pack(padx=10, pady=5)

        tk.Label(self.root, text="IP reset timer (seconds) default=14400 (4h):").pack(anchor="w", padx=10, pady=(10, 0))
        self.reset_timeout_entry = tk.Entry(self.root, validate="key", validatecommand=vis_int, width=40)
        self.reset_timeout_entry.pack(padx=10, pady=5)

        tk.Label(self.root, text="Update interval (seconds) default=5:").pack(anchor="w", padx=10, pady=(10, 0))
        self.interval_entry = tk.Entry(self.root, validate="key", validatecommand=vis_int, width=40)
        self.interval_entry.pack(padx=10, pady=5)

        tk.Label(self.root, text="Overlay placement (xy) default=+0+0").pack(anchor="w", padx=10, pady=(10, 0))
        self.overlay_placement = tk.Entry(self.root, width=40)
        self.overlay_placement.pack(padx=10, pady=5)

        tk.Label(self.root, text="Modem:").pack(anchor="w", padx=10, pady=(10, 0))
        self.modem_choices = [file.split(".")[0] for file in os.listdir("modems") if file.endswith(".py")]
        self.modem_var = tk.StringVar(value=self.modem_choices[0])
        self.modem_dropdown = ttk.OptionMenu(self.root, self.modem_var, self.modem_choices[0], *self.modem_choices)
        self.modem_dropdown.pack(padx=10, pady=5, fill="x")

        self.check_ipauto_val = tk.IntVar(value=0)
        self.check_ipauto = tk.Checkbutton(self.root, text="Auto IP reset timer discovery", variable=self.check_ipauto_val)
        self.check_ipauto.pack(pady=10)

        self.check_symlinks_val = tk.IntVar(value=0)
        self.check_symlinks = tk.Checkbutton(self.root, text="Add symlinks to desktop", variable=self.check_symlinks_val)
        self.check_symlinks.pack(pady=10)

        self.folder_button = tk.Button(self.root, text="Select Folder", command=self.select_folder)
        self.folder_button.pack(pady=20, ipadx=70)

        self.install_button = tk.Button(self.root, text="Install", command=self.install)
        self.install_button.pack(pady=20, ipadx=90)

    def is_admin(self):
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False

    def select_folder(self):
        self.folder = filedialog.askdirectory()
        if self.folder:
            cut = len("Select Folder")
            self.folder_button.configure(text=self.folder if len(self.folder) <= cut else "..."+self.folder[len(self.folder) - cut + 3:])

    def add_symlinks(self, start_py, reset_py):
        desktop = pathlib.Path.home() / "Desktop"
        start_py_lnk = desktop / "IP_Timer_start_stop"
        reset_py_lnk = desktop / "IP_Reset"
        try: os.remove(start_py_lnk)
        except: pass
        try: os.remove(reset_py_lnk)
        except: pass
        try: os.symlink(start_py, start_py_lnk)
        except: pass
        try: os.symlink(reset_py, reset_py_lnk)
        except: pass

    def install(self):
        username  = self.username_entry.get()
        password  = self.password_entry.get()
        reset     = self.reset_timeout_entry.get()
        interval  = self.interval_entry.get()
        modem     = self.modem_var.get()
        auto      = self.check_ipauto_val.get()
        sym       = self.check_symlinks_val.get()
        url       = self.url.get()
        placement = self.overlay_placement.get()

        if not username:
            messagebox.showerror("Error", "No username was provided!")
            return
        if not password:
            messagebox.showerror("Error", "No password was provided!") 
            return
        if not self.folder:
            messagebox.showerror("Error", "No installation folder was selected!") 
            return
        if not reset:
            reset = 14400
        if not interval:
            interval = 5
    
        config = configparser.ConfigParser()
        config["CONFIG"] = {
            "username"     : username,
            "password"     : password,
            "reset_timeout": reset,
            "interval"     : interval,
            "modem"        : modem,
            "auto"         : auto,
            "url"          : url,
            "placement"    : placement
        }
        with open("config.ini", "w") as f:
            config.write(f)

        inst_path = os.path.join(self.folder, "IP_Timer")
        IP_timer_path = os.path.join(inst_path, "IP_Timer.py")
        IP_start_path = os.path.join(inst_path, "start.bat")
        run_bat_path = os.path.join(inst_path, "run.bat")
        reset_bat_path = os.path.join(inst_path, "reset.bat")

        self.create_task(IP_timer_path, run_bat_path, inst_path)
        os.makedirs(inst_path, exist_ok=True)
        shutil.copytree(os.path.dirname(os.path.abspath(__file__)), inst_path, dirs_exist_ok=True, ignore=shutil.ignore_patterns("__pycache__", ".*"))

        if sym:
            self.add_symlinks(IP_start_path, reset_bat_path)

        messagebox.showinfo("Info", "Installation successfull!")
        exit(0)

    def run(self):
        self.root.mainloop()

    def create_task(self, py_file_path, bat_file_path, workdir):
        with open("run.bat", "w") as r:
            r.write(
    f"""@echo off
cd /d {workdir}
{sys.executable} {py_file_path}
                """)
        
        with open("reset.bat", "w") as r:
            r.write(
    f"""@echo off
cd /d {workdir}
{sys.executable} {os.path.join(workdir, "IP_Reset.py")}
                """)
        
        with open("start.bat", "w") as r:
            r.write(
    f"""@echo off
cd /d {workdir}
{sys.executable} {os.path.join(workdir, "start.py")}
                """)
                    
        os.system(f'schtasks /Create /TN "IP_Timer" /TR "powershell.exe -WindowStyle Hidden -Command {bat_file_path} -WindowStyle Hidden" /SC ONLOGON /F > NUL 2>&1')


if __name__ == "__main__":
    app = Install()
    app.run()
