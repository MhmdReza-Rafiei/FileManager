from pathlib import Path
from typing import Dict, Any , List , Optional
import shutil
import time
import yaml
import re

_print = print
def print(*args, anim: bool = True, end="\n" , flush = False):
    if anim:
       time.sleep(0.3)
    _print(*args, end=end , flush = flush)

CONFIG_FILE = 'config'
CONFIG = {
    "system": {
        'User_Name': None,
        'Clean_Paths': []
    },
    "path": {
        'SFX': '',
        'Music': '',
        'DataBase': '',
        'Script': '',
        'Document': '',
        'Program': '',
        'File': '',
        'Image': '',
        'Video': '',

        'Defult': '',

        'Clean_Defult': '',
    }
}

EXTENSIONS = {
    "SFX": [
        "wav", "mp3", "ogg", "aiff", "wma", "flac", "m4a", "aac",
    ],
    "Music": [
        "mp3", "wav", "flac", "aac", "ogg", "m4a", "wma", "alac",
        "aiff", "opus", "ac3", "dts", "mid", "midi", "amr", "au", "caf"
    ],
    "Video": [
        "mp4", "mkv", "avi", "mov", "wmv", "flv", "webm", "m4v",
        "mpg", "mpeg", "m2v", "3gp", "3g2", "f4v", "ogv", "ts",
        "m2ts", "mts", "vob", "divx", "xvid", "hevc", "h264", "h265"
    ],
    "Image": [
        "jpg", "jpeg", "jpe", "jif", "jfif", "jfi", "png", "gif",
        "bmp", "webp", "tiff", "tif", "ico", "heic", "heif", "svg",
        "psd", "ai", "raw", "cr2", "nef", "arw", "orf", "dng", "raf"
    ],
    "Document": [
        "txt","pdf", "doc", "docx", "txt", "rtf", "odt", "xls", "xlsx",
        "ods", "ppt", "pptx", "odp", "pages", "numbers", "key", "md"
    ],
    "Archive": [
        "zip", "rar", "7z", "tar", "gz", "bz2", "xz", "iso",
        "cab", "z", "lzh", "ace", "arj", "rpm", "deb", "dmg"
    ],
    "Program": [
        "exe", "msi", "apk", "deb", "rpm", "dmg", "app", "jar",
        "bat", "com", "scr", "gadget", "ipa", "xap", "bin"
    ],
    "Script": [
        "py", "js", "html", "htm", "css", "php", "sh", "bash",
        "bat", "cmd", "ps1", "vbs", "ahk", "rb", "pl", "go",
        "rs", "java","json", "c", "cpp", "h", "cs", "ts", "tsx", "lua"
    ],
    "DataBase": [
        "db", "sqlite", "sqlite3", "mdb", "accdb", "dbf", "sql", "bak"
    ],
    "Font": [
        "ttf", "otf", "woff", "woff2", "eot", "fon", "fnt"
    ]
}
# -- More
def getConfig():
    return CONFIG

def getExtentions():
    return EXTENSIONS

# -- Helper

def clean_filename(name: str) -> str:
    """
    Removes ALL junk: (1) (33) [HD] (!) ★ NEW 2024 etc.
    Works on even the most spammed filenames.
    """
    if not name or "." not in name:
        return name
    name_part, ext = name.rsplit(".", 1)
    ext = "." + ext.lower()
    cleaned = name_part

    cleaned = re.sub(r"\s*[-_.★♦♥!~✨]+", " ", cleaned)                 # ★ ! ~ → space

    cleaned = re.sub(r"\b(NEW|FULL|UNCUT|REPACK|HD|4K|1080p|720p|BluRay|WEB)\b", "", cleaned, flags=re.I)

    cleaned = re.sub(r"\s+\b(19|20)\d{2}\b", "", cleaned)

    cleaned = re.sub(r"[._-]+", " ", cleaned)        # . _ - → space
    cleaned = re.sub(r"\s{2,}", " ", cleaned)        # multiple spaces → one
    cleaned = cleaned.strip(" -_.")                  # trim edges

    if not cleaned.strip():
        cleaned = name_part

    return cleaned + ext

def getCategory(extention) -> str:
    for category, extensions in EXTENSIONS.items():
            if extention in extensions:
                return category

def getPath(path: str) -> Path:
    src = Path(path)
    if src.exists():
        type = "file" if src.is_file() else "dir"
        return src , type
    else:
        return False , False

# -- Config Handler
def load_config() -> Dict[str, Any]:
    Config , _ = getPath(Path(CONFIG_FILE))
    if Config and (Config.is_dir if Config else False):
        try:
            with open(f"{CONFIG_FILE}\\path.yaml", "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
                CONFIG["path"] = data
            with open(f"{CONFIG_FILE}\\system.yaml", "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
                CONFIG["system"] = data
        except Exception as e:
            print(f"⚠️  Failed to load config: {e} Using defaults")
    else: 
        print("ℹ️  No config found Using default settings")
load_config()

def saveConfig(file) -> CONFIG:
    try:
        with open(f"{CONFIG_FILE}\\{file}.yaml", "w", encoding="utf-8") as f:
            yaml.safe_dump(CONFIG[file], f, sort_keys=False, allow_unicode=True)
            print(f"💽 Settings saved to config/{file}.yaml")
    except Exception as e:
        print(f"❌ Failed to save settings: {e}")

def changeConfig(config:str,key:str,value:Any):
    CONFIG[config][key] = value

# -- File Mover
def move(path) -> Optional[dict]:
    file, type_ = getPath(path)
    if not file or type_ != "file":
        return False, "Not a file or doesn't exist"

    extention = file.suffix
    category = getCategory(extention.lstrip("."))

    url = CONFIG["path"].get(category)
    if not url or url == "":
        url = CONFIG["path"].get("Defult") or CONFIG["path"]["Clean_Defult"]

    if not url:
        return False, "No destination folder configured"

    dest_folder = Path(url)
    dest_folder.mkdir(parents=True, exist_ok=True)

    dest_path = dest_folder / clean_filename(file.name)

    if dest_path.exists():
        counter = 1
        while dest_path.exists():
            new_name = f"{file.stem} ({counter}){file.suffix}"
            dest_path = dest_folder / new_name
            counter += 1

    try:
        shutil.move(str(file), str(dest_path))
        print(f"Moved: {path} → {dest_path}  [{category}]",anim=False)
        return True, category
    except Exception as error:
        print(f"Failed to move {path}: {error}",anim=False)
        return False, str(error)

# -- Clean Up 
def cleanUp(dirs: List) -> Optional[dict]:
    Stats = {
        "success": {'total': 0, 'list': []},
        'fails': {'total': 0, 'list': []},
        "done": [],
        "total": 0
    }

    for dir in dirs:
        path, type_ = getPath(dir)
        
        if not path:
            Stats['fails']['total'] += 1
            Stats['fails']['list'].append(str(dir))
            Stats['done'].append({"path": str(dir), "status": "failed", "error": "Path not found"})
            continue

        if type_ == "file":
            Stats["total"] += 1
            success, info = move(path)
            if success:
                Stats['success']['total'] += 1
                Stats['success']['list'].append(str(path))
                Stats['done'].append({"path": str(path), "status": "success", "category": info})
            else:
                Stats['fails']['total'] += 1
                Stats['fails']['list'].append(str(path))
                Stats['done'].append({"path": str(path), "status": "failed", "error": info})

        elif type_ == "dir":
            print(f"Scanning folder: {path}")
            for file in path.rglob("*"):
                if file.is_file():
                    Stats["total"] += 1
                    success, info = move(file)
                    if success:
                        Stats['success']['total'] += 1
                        Stats['done'].append({"path": str(file), "status": "success", "category": info})
                    else:
                        Stats['fails']['total'] += 1
                        Stats['done'].append({"path": str(file), "status": "failed", "error": info})
            Stats['success']['list'].append(str(path))

    return Stats

# -- Better Stats Ui - str
def showStatus(status) -> str:
    print("\n" + "═" * 62)
    print("                     CLEANUP RESULT                     ".center(62))
    print("═" * 62)

    total_processed = status["total"]
    success_count = status["success"]["total"]
    fail_count = status["fails"]["total"]

    print(f"\n{'🔍 SUCCESS' if success_count > 0 else '○ SUCCESS'} ({success_count} files)")
    if success_count > 0:
        for file_path in status["success"]["list"][:15]:
            print(f"   • {Path(file_path).name}")
        if len(status["success"]["list"]) > 15:
            print(f"   ⋯ and {len(status['success']['list']) - 15} more")
    else:
        print("   → No files were moved successfully 🪧")

    print(f"\n{'❗ FAILED' if fail_count > 0 else '○ FAILED'} ({fail_count} items)")
    if fail_count > 0:
        for item in status["fails"]["list"][:12]:
            print(f"   • {Path(item).name if Path(item).exists() else item}")
        if len(status["fails"]["list"]) > 12:
            print(f"   ⋯ and {len(status['fails']['list']) - 12} more")
    else:
        print("   → No errors or missing paths 💡")

    print(f"\n{'≡' * 22} DETAILED LOG {'≡' * 22}")
    done = status["done"]

    if not done:
        print("   No operations were performed. 🔒")
        if total_processed == 0:
            print("   → All given paths were invalid, empty, or inaccessible 🔐")
    else:
        success_log = sum(1 for x in done if x["status"] == "success")
        fail_log = len(done) - success_log

        print(f"   Total actions: {len(done)}  →  Success: {success_log}  |  Failed: {fail_log}")

        shown = 0
        for item in done:
            if shown >= 20:
                break
            name = Path(item["path"]).name
            if item["status"] == "success":
                cat = item.get("category", "Unknown")
                print(f"   ♻️  {name}  →  [{cat}]")
            else:
                err = str(item.get("error", "Unknown error"))
                short_err = err[:50] + ("..." if len(err) > 50 else "")
                print(f"   ❗ {name}  →  {short_err}")
            shown += 1

        if len(done) > 20:
            print(f"   ⋯ and {len(done) - 20} more actions")

    print(f"\n" + "━" * 62)
    if total_processed == 0:
        print("   NO FILES PROCESSED")
        print("   → All paths were empty, invalid, or had no files")
    else:
        print(f"   TOTAL SCANNED: {total_processed} items 💻")
        print(f"   SUCCESS: {success_count} ♻️   |  FAILED: {fail_count} ❗")

    print("━" * 62 + "\n")

