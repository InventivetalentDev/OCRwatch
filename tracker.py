import time

from screenshot import take_screenshot
from ocr import process_screenshot_file

import keyboard  # using module keyboard


def track():
    try:
        screenshot_name = take_screenshot()
        process_screenshot_file(screenshot_name)
    except:
        print("track() broke")


tab_pressed_time = 0
while True:
    try:
        if keyboard.is_pressed('tab'):
            print('Tab pressed!')
            tab_pressed_time += 1
            time.sleep(0.1)
            if (tab_pressed_time == 2):  # only track once at 2 ticks, then wait until tab is released again
                tab_pressed_time = 0
                print('track')
                track()
                time.sleep(10)  # wait a bit before tracking again
            continue

        tab_pressed_time = 0
        time.sleep(1)
    except:
        print("loop broke")
        break
