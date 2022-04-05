from cryptography.fernet import Fernet
from colorama import Fore, Style

inp = str(input("Enter the text to be encrypted: "))

key = Fernet.generate_key()
f = Fernet(key)
token = f.encrypt(bytes(inp, "utf-8"))

print(f"{Fore.GREEN}Token: {token}\n{Fore.RED}Key: {key}" + Style.RESET_ALL)
print(f"{Fore.GREEN}Decrypted: {Fernet(key).decrypt(token).decode()}" + Style.RESET_ALL)
print(f"{Fore.YELLOW}Code: Fernet({key}).decrypt({token}).decode()" + Style.RESET_ALL)