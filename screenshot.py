import configparser

from mss import mss

config = configparser.ConfigParser()
config.read("config.ini")

monitor = config.getint("input", "monitor")


def take_screenshot():
    with mss() as sct:
        sct.shot(mon=monitor)
    print("*snap*")
    return f"monitor-{monitor}.png"
