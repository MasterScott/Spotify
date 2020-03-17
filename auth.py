import hashlib
import subprocess
import requests
import time

class Auth:
    def __init__(self, n_to, program_id, secret_id):
        self.hwid = str(subprocess.check_output('wmic cpu get processorid')).split('\\r\\n')[1].strip('\\r').strip()
        self.nulled_auth = n_to
        self.id = program_id
        self.secret = secret_id

    def check(self):
        try:
            hash_r = requests.get(f"https://nulledauth.net/API/Auth/Login?Auth={self.nulled_auth}&Hwid={self.hwid}&Distinct={self.id}").text
        except:
            return "Error"
        hs = hashlib.sha256(f"{self.secret} {self.nulled_auth} {self.hwid} {round(time.time()/200)*200}".encode('utf-8')).hexdigest()
        if hs.upper() == hash_r:
            return True
        else:
            return False


