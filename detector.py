import subprocess
import cv2
import requests
import pytesseract
from PIL import Image
import fake_useragent
import numpy as np
import win32ui
import win32gui
from time import sleep, time
from ctypes import windll
import re
import os
from fuzzywuzzy import fuzz
from config import needed, location, catch_iv
from math import radians, cos, sin, asin, sqrt


prev = None
count = 1
iv_counter = 0
device_id = '7pwozpzpaqqkjr9d'
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
user_agent = fake_useragent.UserAgent()['google chrome']
headers = {'user-agent': user_agent, 'if-none-match': "2979-3kcziSj429jfGMhljZ/o5eCq/7E", 'referer': 'https://sgpokemap.com/', 'authority': 'sgpokemap.com', 'x-requested-with': 'XMLHttpRequest'}
url = 'https://nycpokemap.com/pokestop.php?time='
already = []
end = False
current_time, reopen_time, next_time = time(), time(), time()


class MainAction():
    def __init__(self):
        self.cur_inv_list = []
        img = self.make_adb_screencap()
        x, y = img.shape[:2][::-1]
        self.battle_loc = (x // 2, y * 0.85)
        self.open_pokestop_loc = (x//2, int(y/1.7))
        print(self.open_pokestop_loc)
        self.throw = ((x // 2, int(y * 0.1)), (x // 2, int(y * 0.9)))
        print(self.throw)
        self.trashnews = (5, int(y * 0.1))
        self.close_exit = (x // 2, int(y * 0.57))

    def run(self, args):
        subprocess.Popen([str(arg) for arg in args], stdout=subprocess.PIPE).communicate()

    def click(self, location):
        self.run(["adb", "-s", device_id, "shell", "input", "tap", str(location[0]), str(location[1])])

    def get_poke_iv(self, img_1):     
        sizes = [int(img_1.shape[:2][::-1][x] * 2) for x in range(0, 2)]
        img_resized = cv2.resize(img_1, tuple(sizes), interpolation=cv2.INTER_AREA)
        img_resized = cv2.cvtColor(img_resized, cv2.COLOR_BGR2GRAY)

        _, img_binary = cv2.threshold(img_resized, 130, 255, cv2.THRESH_TOZERO)
        img_binary = abs(255-img_binary)
        cv2.imwrite('image.png', img_binary)

        words = pytesseract.image_to_string(Image.open('image.png'), lang='eng').split(' ')
        for i in words:
            iv = re.search(r'\d{,2}/\d{,2}/\d{,2}', i)
            if iv:
                try:
                    iv = list(map(int, iv.group(0).split('/')))
                    print(sum(iv))
                    if sum(iv) >= catch_iv:
                        return 'try_again'
                    return iv
                except:
                    return 'try_again'

        return 'try_again'

    def perform_image(self, img_1, threshold_percent=130):
        _, img_binary = cv2.threshold(img_1, threshold_percent, 255, cv2.THRESH_TOZERO)
        # img_binary = abs(255-img_binary)
        img_binary = cv2.cvtColor(img_binary, cv2.COLOR_BGR2GRAY)
        
        return img_binary
        
    def click_back(self):
        self.run('adb shell input keyevent 4'.split())

    def gotcha(self):
        subprocess.run(f'adb -s {device_id} shell am start -a android.intent.action.VIEW -d "https://pk.md/{location}"', stdout=subprocess.PIPE)
        sleep(5)
        self.swipe(self.throw[1], self.throw[0], 300)

    def reopen(self):
        self.run(f'adb -s {device_id} shell am force-stop com.nianticlabs.pokemongo'.split(' '))
        sleep(2)
        self.run(f'adb -s {device_id} shell am start -n com.pokemod.hal.public/com.pokemod.hal.ui.activities.AuthActivity'.split(' '))
        sleep(2)
        self.run(f'adb -s {device_id} shell input keyevent 23'.split())
        sleep(1)
        self.run(f'adb -s {device_id} shell input keyevent 23'.split())
        sleep(1)
        self.run(f'adb -s {device_id} shell input keyevent 23'.split())
        sleep(50)
        self.click(self.trashnews)
        sleep(0.5)
        self.click(self.trashnews)
        self.get_invasion()

    def battle(self):
        self.click(self.battle_loc)

    def open_stop(self):
        self.click(self.open_pokestop_loc)

    def click_close_exit(self):
        self.click(self.close_exit)

    def swipe(self, start_point, target_point, duration=None):
        args = [
            "adb",
            "-s",
            device_id,
            "shell",
            "input",
            "swipe",
            start_point[0],
            start_point[1],
            target_point[0],
            target_point[1],
            duration
        ]
        self.run(args)

    def get_invasion(self):
        global already, end
        cords = []
        data = requests.get(url=url, headers=headers).json()
        invasions, server_time = data['invasions'], data['meta']['time']

        if len(self.cur_inv_list) > 0:
            cur_cords = ','.join(self.cur_inv_list[0]),
            self.run(
                f'adb -s {device_id} shell am start -a android.intent.action.VIEW -d "https://pk.md/{cur_cords}"'.split()
            )

            self.cur_inv_list.remove(self.cur_inv_list[0])
        else:
            for i in invasions:
                if int(i['invasion_end']) - server_time > 300 and int(i['character']) in needed and (i['lat'], i['lng']) not in already:
                    cords.append((str(i['lat']), str(i['lng'])))
                    if len(cords) == 10:
                        self.cur_inv_list = cords
                        already += self.cur_inv_list

                        cur_cords = ','.join(self.cur_inv_list[0]),
                        self.run(
                            f'adb -s {device_id} shell am start -a android.intent.action.VIEW -d "https://pk.md/{cur_cords}"'.split()
                        )
                        self.cur_inv_list.remove(self.cur_inv_list[0])

                        break
        
        end = False

    def make_screencap(self):
        hand = win32gui.FindWindow(None, 'ForezsFarm')

        left, top, right, bottom = win32gui.GetWindowRect(hand)
        w = right - left
        h = bottom - top

        handDC = win32gui.GetWindowDC(hand)
        mfcDC = win32ui.CreateDCFromHandle(handDC)
        saveDC = mfcDC.CreateCompatibleDC()

        saveBitmMap = win32ui.CreateBitmap()
        saveBitmMap.CreateCompatibleBitmap(mfcDC, w, h)

        saveDC.SelectObject(saveBitmMap)

        result = windll.user32.PrintWindow(hand, saveDC.GetSafeHdc(), 2)

        bmpinfo = saveBitmMap.GetInfo()
        bmpstr = saveBitmMap.GetBitmapBits(True)

        im = Image.frombuffer(
            "RGB",
            (bmpinfo['bmWidth'], bmpinfo['bmHeight']),
            bmpstr, 'raw', 'BGRX', 0, 1
        )

        win32gui.DeleteObject(saveBitmMap.GetHandle())
        saveDC.DeleteDC()
        mfcDC.DeleteDC()
        win32gui.ReleaseDC(hand, handDC)

        if result == 1:
            im.save('test.png')
            return cv2.imread('test.png')
        else:
            return None

    def make_adb_screencap(self):
        os.system('adb exec-out screencap -p > screencap.png')
        return cv2.imread('screencap.png')

    def crop_img(self, img, cords):
        x, y, w, h = cords
        return img[y:y+h, x:x+w]

action = MainAction()

class MainDetector:
    def __init__(self):
        self.device_id = 'r_photo/'
        self.team_r = cv2.imread(self.device_id + 'r_detect.png', cv2.IMREAD_GRAYSCALE)
        self.team_r_2 = cv2.imread(self.device_id + 'r_detect_2.png', cv2.IMREAD_GRAYSCALE)
        self.stop = cv2.imread(self.device_id + 'stop.png', cv2.IMREAD_GRAYSCALE)
        x, y = self.stop.shape[:2][::-1]
        self.stop_2 = cv2.resize(self.stop, (x//2, y//2))

    def timers_check(self):
        global current_time, reopen_time, next_time
        current_time = time()

        if current_time - reopen_time > 180:
            print('[INFO] Reopening..')
            action.reopen()
            reopen_time = time()
            next_time = time()
        
        elif current_time - next_time > 45 and not end:
            print('[INFO] Getting next invasion..')
            action.get_invasion()
            next_time = time()

    def open_pokestop(self):
        if not end:
            stop_img = action.make_screencap()
            x, y = stop_img.shape[:2][::-1]
            stop_img = stop_img[int(y/2.4):int(y/1.6),int(x/2.5):int(x/1.5)]
            cv2.imwrite('r.png', stop_img)
            capture = cv2.cvtColor(stop_img, cv2.COLOR_BGR2GRAY)
            res = cv2.matchTemplate(capture, self.team_r, cv2.TM_CCOEFF_NORMED)
            loc = np.where(res >= 0.35)

            if loc[::-1][1].size > 0:
                action.open_stop()
                print('[INFO] Pokestop opened..')
                sleep(1)

            capture = cv2.cvtColor(stop_img, cv2.COLOR_BGR2GRAY)
            res = cv2.matchTemplate(capture, self.team_r_2, cv2.TM_CCOEFF_NORMED)
            loc = np.where(res >= 0.35)

            if loc[::-1][1].size > 0:
                action.open_stop()
                print('[INFO] Pokestop opened..')
                sleep(1)

    def close_pokestop(self):
        if not end:
            close_img = action.make_screencap()
            x, y = close_img.shape[:2][::-1]
            close_img = close_img[y//8:y//4,int(x/1.3):x]
            cv2.imwrite('close.png', close_img)
            capture = cv2.cvtColor(close_img, cv2.COLOR_BGR2GRAY)
            res = cv2.matchTemplate(capture, self.stop, cv2.TM_CCOEFF_NORMED)
            loc = np.where(res >= 0.6)

            res = cv2.matchTemplate(capture, self.stop_2, cv2.TM_CCOEFF_NORMED)
            loc_2 = np.where(res >= 0.6)

            if loc[::-1][1].size > 0 or loc_2[::-1][1].size > 0:
                action.click_back()
                print('[INFO] Pokestop closed..')

    def battle(self):
        global next_time, reopen_time, count, end
        img = action.make_screencap()

        x, y = img.shape[:2][::-1]
        img = img[y//4:int(y/1.5),x//4:int(x/1.3)]

        words = pytesseract.image_to_string(action.perform_image(img, threshold_percent=120)).split('\n')
        for i in words:
            if fuzz.WRatio(i, 'choose your party') > 90:
                action.battle()
                print('[INFO] Battled, all timers cleared..')
                next_time, reopen_time = time(), time()
                end = True

    def detect_poke(self):
        global next_time, reopen_time, count, iv_counter
        n = action.get_poke_iv(action.make_screencap())
        if n == 'try_again':
            pass
        else:
            while True:
                n = action.get_poke_iv(action.make_screencap())
                iv_counter += 1
                if iv_counter == 30:
                    action.click_back()
                    action.get_invasion()
                    next_time, reopen_time = time(), time()
                    end = False
                    iv_counter = 0
                    return
                if n == 'try_again':
                    continue
                else:
                    n = '/'.join(list(map(str, n)))
                    print(n)
                    if re.search(r'[0-1]{1}[0-5]{1}/[0-1]{1}[0-5]{1}/[0-1]{1}[0-5]{1}', n):
                        n = sum(list(map(int, n.split('/'))))
                        if 41 <= n <= 45:
                            action.gotcha()
                    break
            action.click_back()
            next_time, reopen_time = time(), time()
            print('[INFO] Getting next invasion..')
            while True:
                try:
                    action.get_invasion()
                    break
                except:
                    pass
            end = False
            sleep(2)
            iv_counter = 0

    def check_exit(self):
        img = action.make_screencap()
        x, y = img.shape[:2][::-1]

        img = img[y//4:y//2, x//4:int(x/1.3)]
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        _, img = cv2.threshold(img, 120, 255, cv2.THRESH_TOZERO)
        img = abs(255-img)

        words = pytesseract.image_to_string(img).split('\n')
        for i in words:
            if fuzz.WRatio(i, 'Exit the Trainer Battle?') > 90:
                print('[INFO] Exit closed..')
                action.click_close_exit()

    def check_speed(self):
        img = action.make_screencap()
        x, y = img.shape[:2][::-1]

        img = img[y//5:y//2, x//5:int(x/1.2)]
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        _, img = cv2.threshold(img, 120, 255, cv2.THRESH_TOZERO)
        img = abs(255-img)

        words = pytesseract.image_to_string(img).split('\n')
        for i in words:
            if fuzz.WRatio(i, "You're going too fast!") > 90:
                print('[INFO] Speed closed..')
                action.click((540, 1550))

