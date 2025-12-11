import time
from typing import Dict, Any
try: 
    import base.main as lib
except:
    print("Could Not Find base\\main as lib")
    print("Pls Install Requirements Using (pip install -r requirements.txt)")
    input("Press Enter To leave...")
    exit()
# ====================== HELPERS ======================
_print = print
def print(*args, end="\n" , flush = False):
    time.sleep(0.15)
    _print(*args, end=end , flush = flush)
_input = input
def input(text:str , type:str = "string" , allow_empty: bool = False):
    while True:
        Input = _input(text).strip()
        if not Input or type != "none" and type != "number" and Input.isdigit():
            continue
        else:
            break
    return Input

def clear_screen():
    print("\n" * 1)

def header(title: str):
    print(f"\n{'='*15} {title} {'='*15}")

def getUser():
    return lib.CONFIG["system"]["User_Name"] if lib.CONFIG["system"]["User_Name"] else False

def delete(self):
    del self

class Panel:
    def __init__(self, selection: dict, help: bool = True, exit: bool = True):
        self.selection = selection.copy()
        self.closed = False

        if help:
            self.selection["help"] = {
                "action": self.show_help,
                "arg": None,
                "desc": "Show help"
            }

        self.selection["exit"] = {
            "action": self.close if exit else goodbye,
            "arg": None,
            "desc": "Exit / Go back"
        }

    def close(self):
        self.closed = True

    def show_help(self):
        header("Help")
        print("You can type the option name or its number.")
        print("Available options:\n")
        for key, item in self.selection.items():
            if key.lower() in ["help", "exit"]:
                continue
            desc = item.get("desc", "")
            print(f"{key.title():<15} → {desc}")
        print("Help              → Show this help")
        print("Exit              → Go back / close panel")
        print()

    def draw(self):
        header("Menu")
        num = 1
        for key, item in self.selection.items():
            item["id"] = num
            print(f"{num}. {key.title():<15} → {item.get('desc', '')}")
            num += 1
        print()

    def handle(self):
        while not self.closed:
            self.draw()
            choice = input("🛠️   What would you like to do? > ", type="none").strip().lower()

            if choice in self.selection:
                item = self.selection[choice]
                arg = item.get("arg")
                if arg is not None:
                    if isinstance(arg, (tuple, list)):
                        item["action"](*arg)
                    else:
                        item["action"](arg)
                else:
                    item["action"]()
                continue

            if choice.isdigit():
                n = int(choice)
                for item in self.selection.values():
                    if item.get("id") == n:
                        arg = item.get("arg")
                        if arg is not None:
                            if isinstance(arg, (tuple, list)):
                                item["action"](*arg)
                            else:
                                item["action"](arg)
                        else:
                            item["action"]()
                        break
                else:
                    print("Invalid choice.")
            elif choice:
                print("Not recognized.")
            time.sleep(0.5)

    def run(self):
        self.handle()

# ====================== Actions ======================

def welcome():
    header(f"{getUser() + " " if getUser() else ""}Welcome to FileManager 📰")
    print("🔔   GitHub: https://github.com/Ariam-AI/Ariam")
    print("🎗️    MadeBy: @MhmdReza Rafiei")

def file_Clean(paths: list = None):
    if paths is None:
        header("File Cleanup")
        Panel({
            "default paths": {
                "desc": "Use Clean_Paths from config",
                "action": file_Clean,
                "arg": (lib.CONFIG["system"].get("Clean_Paths", []),) 
            },
            "custom path": {
                "desc": "Enter your own path(s)",
                "action": lambda: file_Clean(
                    [p.strip() for p in input("Enter path(s) → use comma to separate: ").split(",") if p.strip()]
                )
            },
            "data path": {
                "desc": "data path inside FileManager",
                "action": file_Clean,
                "arg": (["data"],)
            },
        }, help=True, exit=True).run()
        return

    if not paths:
        print("No paths to clean!")

    print(f"Cleaning {len(paths)} path(s):")
    for p in paths:
        print(f"   → {p}")
    print()
    try:
        result = lib.cleanUp(paths) 
        time.sleep(2)
        lib.showStatus(result) 
        time.sleep(6)
    except Exception as e:
        print(f"Error during cleanup: {e}")

    
def setting(mode="start", key=None, value=None):
    if mode == "change" and key and value is not None:
        if key == "Clean_Paths":
            value = [path.strip() for path in value.split(",") if path.strip()]
            print(f"Updating Clean_Paths → {value}")
        else:
            print(f"Updating {key} → {value}")

        lib.changeConfig("system", key, value)
        lib.saveConfig("system")
        print("Saved successfully!")

    if mode == "status":
        header("Current Settings")
        paths = lib.CONFIG['system'].get('Clean_Paths', [])
        paths_str = ", ".join(paths) if paths else "Not set"
        print(f"User Name    : {lib.CONFIG['system'].get('User_Name', 'Not Set')}")
        print(f"Clean Paths  : {paths_str} → {paths}")

    if mode == "start":
        Panel({
            "change": {"desc": "Change Settings",     "action": setting, "arg": ("change",)},
            "status": {"desc": "View Current Status", "action": setting, "arg": ("status",)},
        }).run()

    elif mode == "change":
        Panel({
            "username": {
                "desc": "Change your username",
                "action": lambda: setting("change", "User_Name", input("New username: ").strip())
            },
            "clean paths": {
                "desc": "Set default clean folders (comma separated)",
                "action": lambda: setting("change", "Clean_Paths", input("Enter paths (comma separated): ").strip())
            },
        }).run()

def goodbye():
    header("Goodbye!")
    print(f"{getUser() + "' " if getUser() else ""}Thanks you for using (FileManager) 📰")
    for i in range(5, 0, -1):
        print(f"   Closing in {i}...", end="\r")
        time.sleep(1)
    print("\n   See you next time! 👋\n")
    time.sleep(1)
    exit()
# ====================== Run ======================
def main():
    while True:
        welcome()
        if not getUser():
          header("Need Verification")
          UserName = input("Enter Your UserName: ")
          
          lib.changeConfig("system","User_Name",UserName)
          lib.saveConfig("system")
        header("System - Panel")
        SystemPanel = Panel({
            "file clean":{"desc":"File Cleaner","action":file_Clean},
            "setting":{"desc":"Setting (Change/Status)","action":setting},
        },True)
        SystemPanel.run()
        goodbye()

main()