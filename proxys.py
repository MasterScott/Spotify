import collections
import json
import logging
import socks
import threading
import time

import requests

from colorama import Fore
from colorama import init

import configparser

cfg = configparser.ConfigParser()
cfg.read("config.ini")
retry = cfg.getboolean("proxies", "new_proxies")


class Proxies:
    def __init__(self, ip, proxy_type):
        self.ip = ip
        self.being_used = False
        self.banned = False
        self.proxy_type = proxy_type
        if self.proxy_type == "socks4":
            self.proxy = {'http': f'socks4://{self.ip}',
                          'https': f'socks4://{self.ip}'}
        elif self.proxy_type == "socks5":
            self.proxy = {'http': f'socks5h://{self.ip}',
                          'https': f'socks5h://{self.ip}'}
        else:
            self.proxy = {'http': f'{self.ip}',
                          'https': f'{self.ip}'}


class Handler:
    def __init__(self, timeout=10, display_messages=False, url="https://www.google.com", success_key="</html>"):
        init()
        self.url = url
        self.success_key = success_key
        self.proxy_list = collections.deque()
        self.display_good = False
        self.working_proxies = list()
        self.r = threading.RLock()
        self.display_messages = display_messages
        self.banned_proxies = collections.deque()
        self.time_out = timeout

    def __len__(self):
        return len(self.proxy_list)

    def start(self, proxy_l, proxy_type):
        self.proxy_type = proxy_type
        self.proxy_list = collections.deque()
        for ip in proxy_l:
            self.proxy_list.append(Proxies(ip, proxy_type))

    def give_proxy(self):
        while self.proxy_list:
            for x in self.proxy_list:
                if x.being_used is False and x.banned is False:
                    x.being_used = True
                    return x
            if self.display_messages:
                print(Fore.YELLOW + "All proxies are being used, waiting 10 seconds")
            time.sleep(10)
        if retry:
            cc = self.grab(self.proxy_type)
            if cc:
                return self.give_proxy()
        time.sleep(1800)
        self.proxy_list = self.banned_proxies
        return self.give_proxy()

    def grab(self, proxy_type):
        self.proxy_type = proxy_type
        try:
            response = requests.get(
                f"https://api.proxyscrape.com/?request=displayproxies&proxytype={proxy_type.lower()}&timeout=10000&country=all&ssl=all&anonymity=all&uptime=0&status=alive&age=unlimited&port=all").text.split(
                "\r\n")
            response = [x for x in response if x != "" and ":" in x]
            response = list(dict.fromkeys(response))
            if len(response) > 50:
                self.start(response, proxy_type)
                return True
            else:
                return False
        except:
            return False

    def ban(self, proxy_object):
        proxy_object.banned = True
        if proxy_object not in self.banned_proxies:
            self.banned_proxies.appendleft(proxy_object)
        try:
            self.proxy_list.remove(proxy_object)
        except ValueError:
            return 1

    def save(self):
        with open("working proxies.txt", "w") as f:
            if self.proxy_list:
                for x in self.proxy_list:
                    if x != self.proxy_list[-1]:
                        f.write(f"{x.ip}\n")
                    else:
                        f.write(x.ip)
                if self.display_messages:
                    print(Fore.GREEN + "Proxies were saved in working proxies.txt")
            else:
                if self.display_messages:
                    print(Fore.RED + "There're not proxies to be saved")

    def check(self, thread_number, display_good_only=False):
        th = []
        self.display_good = display_good_only
        for _ in range(thread_number):
            t = threading.Thread(target=self.__checker)
            th.append(t)
            t.start()
        for j in th:
            j.join()
        self.proxy_list = self.working_proxies
        for x in self.proxy_list:
            x.being_used = False
        self.save()

    def __checker(self):
        while self.proxy_list:
            self.r.acquire()
            x = self.give_proxy()
            self.r.release()
            with requests.session() as s:
                s.proxies.update(x.proxy)
                try:
                    response = s.get(self.url)
                except:
                    if self.display_messages:
                        self.r.acquire()
                        print(Fore.RED + f"{x.ip} not working")
                        self.r.release()
                    continue
                if self.success_key in response.text:
                    self.r.acquire()
                    self.working_proxies.append(x)
                    print(Fore.GREEN + f"{x.ip} is working")
                    self.r.release()

