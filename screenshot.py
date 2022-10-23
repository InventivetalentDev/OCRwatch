from mss import mss

monitor = 2


def take_screenshot():
    with mss() as sct:
        sct.shot(mon=monitor)
    return f"monitor-{monitor}.png"
