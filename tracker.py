import csv
import queue
import threading
import time
import traceback

from output import append_to_csv, write_to_influx, write_output
from screenshot import take_screenshot
from ocr import process_screenshot_file, write_json

import keyboard

latest = {}


def track(lock):
    global latest

    try:
        screenshot_name = take_screenshot()
        with lock:
            result = process_screenshot_file(screenshot_name)

        latest = result

        write_latest()



    except:
        print("track() broke")
        print(traceback.format_exc())


def write_latest():
    write_output(latest)


def track_loop(lock):
    tab_pressed_time = 0
    while 1:
        try:
            if keyboard.is_pressed('tab'):
                print('Tab pressed!')
                tab_pressed_time += 1
                time.sleep(0.1)
                if (tab_pressed_time == 5):  # only track once at 3 ticks, then wait until tab is released again
                    tab_pressed_time = 0
                    print('track')
                    track(lock)
                    time.sleep(10)  # wait a bit before tracking again
                continue

            tab_pressed_time = 0
            time.sleep(1)

        except:
            print("loop broke")
            break


def cmd_loop(q, lock):
    print("Use Enter to switch to input mode")
    while 1:
        input()
        with lock:
            print("Type 'win' 'loss' or 'draw' to record match result")
            cmd = input('> ')

        q.put(cmd)
        if cmd == 'quit':
            print("break")
            break


def action_win(lock):
    with lock:
        print("win!")
    latest['state'] = 'win'
    write_latest()


def action_loss(lock):
    with lock:
        print("loss")
    latest['state'] = 'loss'
    write_latest()


def action_draw(lock):
    with lock:
        print("draw")
    latest['state'] = 'draw'
    write_latest()


def invalid_input(lock):
    with lock:
        print('---> Unknown command')


def main():
    cmd_actions = {'win': action_win, 'loss': action_loss, 'draw': action_draw}
    cmd_queue = queue.Queue()
    stdout_lock = threading.Lock()

    cmd_thread = threading.Thread(target=cmd_loop, args=(cmd_queue, stdout_lock), daemon=True)
    cmd_thread.start()

    track_thread = threading.Thread(target=track_loop, args=(stdout_lock,), daemon=True)
    track_thread.start()

    while (cmd_thread.is_alive() or track_thread.is_alive()):
        cmd_thread.join(1)
        track_thread.join(1)

        cmd = cmd_queue.get()
        if cmd == 'quit':
            break
        action = cmd_actions.get(cmd, invalid_input)
        action(stdout_lock)


main()
