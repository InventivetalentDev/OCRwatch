import csv
import queue
import threading
import time
import traceback

from output import append_to_csv, write_to_influx, write_output, write_rank
from screenshot import take_screenshot
from ocr import process_screenshot_file, write_json

import keyboard

ranks = [
    "b5", "b4", "b3", "b2", "b1",
    "s5", "s4", "s3", "s2", "s1",
    "g5", "g4", "g3", "g2", "g1",
    "p5", "p4", "p3", "p2", "p1",
    "d5", "d4", "d3", "d2", "d1",
    "m5", "m4", "m3", "m2", "m1",
    "gm5", "gm4", "gm3", "gm2", "gm1"
]

latest = {}


def track(lock):
    global latest

    start = time.time()

    try:
        screenshot_name = take_screenshot()
        if keyboard.is_pressed('tab'):
            with lock:
                print("Processing...")
                result = process_screenshot_file(screenshot_name)

            end = time.time()
            print(f"Took {end - start}s")

            latest = result

            write_latest()

    except:
        print('track() broke')
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
                if (tab_pressed_time == 3):  # only track once at 3 ticks, then wait until tab is released again
                    tab_pressed_time = 0
                    print('track')
                    track(lock)
                    time.sleep(10)  # wait a bit before tracking again
                continue

            tab_pressed_time = 0
            time.sleep(0.5)

        except:
            print("loop broke")
            break


def cmd_loop(q, lock):
    print("Use Enter to switch to input mode")
    while 1:
        input()
        with lock:
            print("Type '[w]in' '[l]oss' or '[d]raw' to record result of latest match - or 'quit' to exit")
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
    cmd_actions = {
        'win': action_win,
        'w': action_win,
        'loss': action_loss,
        'l': action_loss,
        'draw': action_draw,
        'd': action_draw
    }
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
        if cmd in ranks:
            print("Tracking comp rank", cmd)
            write_rank(cmd, ranks)
        else:
            action = cmd_actions.get(cmd, invalid_input)
            action(stdout_lock)

if __name__ == '__main__':
    main()
