# Import required packages
import configparser
from datetime import datetime

import cv2
import pytesseract
import numpy as np

from util import rotate, write_json

allies_start = (312, 193)
allies_end = (1160, 500)
enemies_start = (312, 613)
enemies_end = (1160, 920)
self_name_start = (170, 950)
self_name_end = (415, 1000)
self_hero_start = (1180, 350)
self_hero_end = (1460, 410)
match_info_start = (120, 30)
match_info_end = (800, 90)

name_offset = 145
name_offset_enemy = 90
name_width = 210
elims_offset = 384
elims_width = 50
assist_offset = 435
assist_width = 50
deaths_offset = 490
deaths_width = 50
dmg_offset = 555
dmg_width = 100
heals_offset = 655
heals_width = 100
mit_offset = 765
mit_width = 100

mode_offset = 0
mode_height = 35
time_offset_y = 30
time_offset_x = 65
time_height = 35
time_width = 100

row_height = 62
row_padding = 16

zero_to_nine = "0123456789"
a_to_z = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

# Mention the installed location of Tesseract-OCR in your system
pytesseract.pytesseract.tesseract_cmd = 'S:\Program Files\Tesseract-OCR\\tesseract.exe'

# Specify structure shape and kernel size.
# Kernel size increases or decreases the area
# of the rectangle to be detected.
# A smaller value like (10, 10) will detect
# each word instead of a sentence.
rect_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (10, 10))

config = configparser.ConfigParser()
config.read("config.ini")


def crop_top_bottom(img):
    return img[2:-2, 0:-0]


def str_to_number(str):
    str = str.replace(',', '').replace('\n', '')
    if len(str) <= 0:
        return 0
    return int(str)


def debug_json(name, json):
    if config.getboolean("debug", "json"):
        write_json(name, json)


def debug_image(name, im):
    if config.getboolean("debug", "images"):
        cv2.imwrite(name, im)


def debug(*values):
    if config.getboolean("debug", "log"):
        print(*values)


def process_self_name(im):
    rotated = rotate(im, -4)  # rotate to make the text straight
    debug_image(f"dbg/name_rotated.jpg", rotated)
    cropped = rotated[16:38, 5:240]
    debug_image(f"dbg/name_cropped.jpg", cropped)
    name = ocr(cropped, 0, "--psm 7 -c load_system_dawg=0").replace('\n', '')
    debug("name", name)

    if len(name) <= 0:
        raise Exception("empty name")

    return {
        "name": name
    }


def process_self_hero(im):
    debug_image(f"dbg/hero.jpg", im)
    name = ocr(im, 0, f"--psm 7 -c load_system_dawg=0 tessedit_char_whitelist={zero_to_nine}", inv=True).replace('\n', '')
    debug("hero", name)

    if len(name) <= 0:
        raise Exception("empty hero")

    return {
        "hero": name
    }


def process_match_info(im):
    mode_map_img = im[0:mode_height, mode_offset:]
    debug_image(f"dbg/mode.jpg", mode_map_img)
    mode_map = ocr(mode_map_img, 0, f"--psm 7  -c tessedit_char_whitelist=|:-{a_to_z}", crop=False).replace('\n', '')
    debug("mode+map", mode_map)

    mode, map, *rest = mode_map.split("|")

    if len(mode) <= 0:
        raise Exception("empty mode")

    if len(map) <= 0:
        raise Exception("empty map")

    is_comp = "COMPETITIVE" in mode
    if "-COMPETITIVE" in mode:
        mode = mode[:-len("-COMPETITIVE")]
    if "COMPETITIVE" in mode:
        mode = mode[:-len("COMPETITIVE")]

    time_img = im[time_offset_y:time_offset_y + time_height, time_offset_x:time_offset_y + time_width]
    debug_image(f"dbg/time.jpg", time_img)
    time = ocr(time_img, 0, f"--psm 7  -c tessedit_char_whitelist={zero_to_nine}:", crop=False).replace('\n', '')
    debug("time", time)

    return {
        "mode_map": mode_map,
        "mode": mode,
        "map": map,
        "competitive": is_comp,
        "time": time,
        "time_parsed":  datetime.strptime(time, "%M:%S")
    }


# https://stackoverflow.com/questions/33497736/opencv-adjusting-photo-with-skew-angle-tilt
# https://docs.opencv.org/3.4/da/d6e/tutorial_py_geometric_transformations.html
def deskew_player_name(name_img):
    rows, cols = name_img.shape
    pts1 = np.float32(
        [[5, 0],
         [95, 0],
         [0, 25],
         [90, 25]]
    )
    pts2 = np.float32(
        [[-5, 0],
         [95, 0],
         [-3, 25],
         [97, 25]]
    )
    M = cv2.getPerspectiveTransform(pts1, pts2)
    dst = cv2.warpPerspective(name_img, M, (cols, rows))

    return dst


def process_player_list(im, name_offs):
    out = []
    for i in range(0, 5):
        row_y = row_height * i

        name_img = im[row_y + row_padding:row_y + row_height - row_padding, name_offs:name_offs + name_width]
        # name_img = crop_top_bottom(name_img)
        debug_image(f"dbg/name{i}.jpg", name_img)
        name_img = deskew_player_name(name_img)
        debug_image(f"dbg/name{i}_deskew.jpg", name_img)
        name = ocr(name_img, i, "--psm 7 -c load_system_dawg=0").replace('\n', '')
        debug("name", name)

        elims_img = im[row_y + row_padding:row_y + row_height - row_padding, elims_offset:elims_offset + elims_width]
        debug_image(f"dbg/elims{i}.jpg", elims_img)
        elims = str_to_number(ocr(elims_img, i, f"--psm 8 -c tessedit_char_whitelist={zero_to_nine}"))
        debug("elims", elims)

        assist_img = im[row_y + row_padding:row_y + row_height - row_padding, assist_offset:assist_offset + assist_width]
        debug_image(f"dbg/assist{i}.jpg", assist_img)
        assists = str_to_number(ocr(assist_img, i, f"--psm 8 -c tessedit_char_whitelist={zero_to_nine}"))
        debug("assists", assists)

        deaths_img = im[row_y + row_padding:row_y + row_height - row_padding, deaths_offset:deaths_offset + deaths_width]
        debug_image(f"dbg/deaths{i}.jpg", deaths_img)
        deaths = str_to_number(ocr(deaths_img, i, f"--psm 8 -c tessedit_char_whitelist={zero_to_nine}"))
        debug("deaths", deaths)

        dmg_img = im[row_y + row_padding:row_y + row_height - row_padding, dmg_offset:dmg_offset + dmg_width]
        debug_image(f"dbg/dmg{i}.jpg", dmg_img)
        dmg = str_to_number(ocr(dmg_img, i, f"--psm 8 -c tessedit_char_whitelist={zero_to_nine},"))
        debug("dmg", dmg)

        heal_img = im[row_y + row_padding:row_y + row_height - row_padding, heals_offset:heals_offset + heals_width]
        debug_image(f"dbg/heal{i}.jpg", heal_img)
        heal = str_to_number(ocr(heal_img, i, f"--psm 8 -c tessedit_char_whitelist={zero_to_nine},"))
        debug("heal", heal)

        mit_img = im[row_y + row_padding:row_y + row_height - row_padding, mit_offset:mit_offset + mit_width]
        debug_image(f"dbg/mit{i}.jpg", mit_img)
        mit = str_to_number(ocr(mit_img, i, f"--psm 8 -c tessedit_char_whitelist={zero_to_nine},"))
        debug("mit", mit)

        out.append({
            "name": name,

            "elims": elims,
            "assists": assists,
            "deaths": deaths,

            "dmg": dmg,
            "heal": heal,
            "mit": mit
        })
    return out


def ocr(img, offs, args, crop=True, inv=False):
    # Performing OTSU threshold
    thr = cv2.THRESH_OTSU | cv2.THRESH_BINARY_INV if inv else cv2.THRESH_OTSU
    ret, thresh1 = cv2.threshold(img, 0, 255, thr)
    debug_image(f"dbg/thresh{offs}.jpg", thresh1)

    # Applying dilation on the threshold image
    dilation = cv2.dilate(thresh1, rect_kernel, iterations=1)

    # Finding contours
    contours, hierarchy = cv2.findContours(dilation, cv2.RETR_EXTERNAL,
                                           cv2.CHAIN_APPROX_NONE)

    cnt = contours[0]
    x, y, w, h = cv2.boundingRect(cnt)

    # # Drawing a rectangle on copied image
    im2 = img.copy()
    rect = cv2.rectangle(im2, (x, y), (x + w, y + h), (0, 255, 0), 2)
    debug_image(f"dbg/contour{offs}.jpg", im2)

    if crop:
        # Cropping the text block for giving input to OCR
        cropped = img[y + 2:y + h - 2, x + 2:x + w - 2]
    else:
        cropped = img

    debug_image(f"dbg/cropped{offs}.jpg", cropped)

    text = pytesseract.image_to_string(cropped, config=args)
    return text


def process_screenshot(img):
    # Read image from which text needs to be extracted
    # img = cv2.imread("7b3da7fc15_Overwatch.png")

    # Preprocessing the image starts

    # Convert the image to gray scale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    debug_image("gray.jpg", gray)

    self_hero = gray[self_hero_start[1]:self_hero_end[1], self_hero_start[0]:self_hero_end[0]]
    debug_image("dbg/hero.jpg", self_hero)
    self_hero_info = process_self_hero(self_hero)
    debug(self_hero_info)
    debug_json("hero.json", self_hero_info)

    self_name = gray[self_name_start[1]:self_name_end[1], self_name_start[0]:self_name_end[0]]
    debug_image("dbg/name.jpg", self_name)
    self_name_info = process_self_name(self_name)
    debug(self_name_info)
    debug_json("name.json", self_name_info)

    match = gray[match_info_start[1]:match_info_end[1], match_info_start[0]:match_info_end[0]]
    debug_image("dbg/match.jpg", match)
    match_info = process_match_info(match)
    debug(match_info)
    debug_json("match.json", match_info)

    allies = gray[allies_start[1]:allies_end[1], allies_start[0]:allies_end[0]]
    debug_image("dbg/allies.jpg", allies)
    allies_info = process_player_list(allies, name_offset)
    debug(allies_info)
    debug_json("allies.json", allies_info)

    enemies = gray[enemies_start[1]:enemies_end[1], enemies_start[0]:enemies_end[0]]
    debug_image("dbg/enemies.jpg", enemies)
    enemies_info = process_player_list(enemies, name_offset_enemy)
    debug(enemies_info)
    debug_json("enemies.json", enemies_info)

    return {
        "time": datetime.now().timestamp(),
        "state": "in_progress",
        "match": match_info,
        "self": self_hero_info | self_name_info,
        "players": {
            "allies": allies_info,
            "enemies": enemies_info
        }
    }


def process_screenshot_file(filename):
    img = cv2.imread(filename)
    return process_screenshot(img)
