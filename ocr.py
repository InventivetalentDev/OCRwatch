# Import required packages
import json
from datetime import datetime

import cv2
import pytesseract

from util import rotate

allies_start = (312, 193)
allies_end = (1160, 500)
enemies_start = (312, 613)
enemies_end = (1160, 920)
self_name_start = (170, 950)
self_name_end = (415,1000)
self_hero_start = (1180, 350)
self_hero_end = (1460, 410)
match_info_start = (40, 25)
match_info_end = (800, 110)

name_offset = 95
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

mode_offset = 60
mode_height = 45
time_offset_y = 50
time_offset_x = 65
time_height = 24
time_width = 75

row_height = 62

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


def write_json(file, data):
    with open(file, 'w') as f:
        json.dump(data, f, indent=4)


def crop_top_bottom(img):
    return img[2:-2, 0:-0]


def str_to_number(str):
    str = str.replace(',', '').replace('\n', '')
    if len(str) <= 0:
        return 0
    return int(str)

def process_self_name(im):
    rotated = rotate(im, -4)  # rotate to make the text straight
    cv2.imwrite(f"dbg/name_rotated.jpg", rotated)
    cropped = rotated[16:38, 5:240]
    cv2.imwrite(f"dbg/name_cropped.jpg", cropped)
    name = ocr(cropped, 0, "--psm 7 -c load_system_dawg=0").replace('\n', '')
    print("name", name)

    return {
        "name": name
    }

def process_self_hero(im):
    cv2.imwrite(f"dbg/hero.jpg", im)
    name = ocr(im, 0, "--psm 7 -c load_system_dawg=0").replace('\n', '')
    print("hero", name)

    return {
        "hero": name
    }


def process_match_info(im):
    mode_map_img = im[0:mode_height, mode_offset:]
    cv2.imwrite(f"dbg/mode_map.jpg", mode_map_img)
    mode_map = ocr(mode_map_img, 0, f"--psm 7  -c tessedit_char_whitelist=|:{a_to_z}", crop=False).replace('\n', '')
    print("mode+map", mode_map)

    mode, map, *rest = mode_map.split("|")

    if len(mode) <= 0:
        raise Exception("empty mode")

    if len(map) <= 0:
        raise Exception("empty map")

    time_img = im[time_offset_y:time_offset_y + time_height, time_offset_x:time_offset_y + time_width]
    cv2.imwrite(f"dbg/time.jpg", time_img)
    time = ocr(time_img, 0, f"--psm 7  -c tessedit_char_whitelist={zero_to_nine}:", crop=False).replace('\n', '')
    print("time", time)

    return {
        "mode_map": mode_map,
        "mode": mode,
        "map": map,
        "time": time
    }


def process_player_list(im):
    out = []
    for i in range(0, 5):
        row_y = row_height * i

        name_img = im[row_y:row_y + row_height, name_offset:name_offset + name_width]
        # name_img = crop_top_bottom(name_img)
        cv2.imwrite(f"dbg/name{i}.jpg", name_img)
        name = ocr(name_img, i, "--psm 7 -c load_system_dawg=0").replace('\n', '')
        print("name", name)

        elims_img = im[row_y:row_y + row_height, elims_offset:elims_offset + elims_width]
        cv2.imwrite(f"dbg/elims{i}.jpg", elims_img)
        elims = str_to_number(ocr(elims_img, i, f"--psm 13 -c tessedit_char_whitelist={zero_to_nine}"))
        print("elims", elims)

        assist_img = im[row_y:row_y + row_height, assist_offset:assist_offset + assist_width]
        cv2.imwrite(f"dbg/assist{i}.jpg", assist_img)
        assists = str_to_number(ocr(assist_img, i, f"--psm 13 -c tessedit_char_whitelist={zero_to_nine}"))
        print("assists", assists)

        deaths_img = im[row_y:row_y + row_height, deaths_offset:deaths_offset + deaths_width]
        cv2.imwrite(f"dbg/deaths{i}.jpg", deaths_img)
        deaths = str_to_number(ocr(deaths_img, i, f"--psm 13 -c tessedit_char_whitelist={zero_to_nine}"))
        print("deaths", deaths)

        dmg_img = im[row_y:row_y + row_height, dmg_offset:dmg_offset + dmg_width]
        cv2.imwrite(f"dbg/dmg{i}.jpg", dmg_img)
        dmg = str_to_number(ocr(dmg_img, i, f"--psm 13 -c tessedit_char_whitelist={zero_to_nine},"))
        print("dmg", dmg)

        heal_img = im[row_y:row_y + row_height, heals_offset:heals_offset + heals_width]
        cv2.imwrite(f"dbg/heal{i}.jpg", heal_img)
        heal = str_to_number(ocr(heal_img, i, f"--psm 13 -c tessedit_char_whitelist={zero_to_nine},"))
        print("heal", heal)

        mit_img = im[row_y:row_y + row_height, mit_offset:mit_offset + mit_width]
        cv2.imwrite(f"dbg/mit{i}.jpg", mit_img)
        mit = str_to_number(ocr(mit_img, i, f"--psm 13 -c tessedit_char_whitelist={zero_to_nine},"))
        print("mit", mit)

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


def ocr(img, offs, args, crop=True):
    # Performing OTSU threshold
    ret, thresh1 = cv2.threshold(img, 0, 255, cv2.THRESH_OTSU | cv2.THRESH_BINARY_INV)
    cv2.imwrite(f"dbg/thresh{offs}.jpg", thresh1)

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
    cv2.imwrite(f"dbg/contour{offs}.jpg", im2)

    if crop:
        # Cropping the text block for giving input to OCR
        cropped = img[y + 2:y + h - 2, x + 2:x + w - 2]
    else:
        cropped = img

    cv2.imwrite(f"dbg/cropped{offs}.jpg", cropped)

    text = pytesseract.image_to_string(cropped, config=args)
    return text


def process_screenshot(img):
    # Read image from which text needs to be extracted
    # img = cv2.imread("7b3da7fc15_Overwatch.png")

    # Preprocessing the image starts

    # Convert the image to gray scale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    cv2.imwrite("gray.jpg", gray)

    self_hero = gray[self_hero_start[1]:self_hero_end[1], self_hero_start[0]:self_hero_end[0]]
    cv2.imwrite("dbg/hero.jpg", self_hero)
    self_hero_info = process_self_hero(self_hero)
    print(self_hero_info)
    write_json("hero.json", self_hero_info)

    self_name = gray[self_name_start[1]:self_name_end[1], self_name_start[0]:self_name_end[0]]
    cv2.imwrite("dbg/name.jpg", self_name)
    self_name_info = process_self_name(self_name)
    print(self_name_info)
    write_json("name.json", self_name_info)

    match = gray[match_info_start[1]:match_info_end[1], match_info_start[0]:match_info_end[0]]
    cv2.imwrite("dbg/match.jpg", match)
    match_info = process_match_info(match)
    print(match_info)
    write_json("match.json", match_info)

    allies = gray[allies_start[1]:allies_end[1], allies_start[0]:allies_end[0]]
    cv2.imwrite("dbg/allies.jpg", allies)
    allies_info = process_player_list(allies)
    print(allies_info)
    write_json("allies.json", allies_info)

    enemies = gray[enemies_start[1]:enemies_end[1], enemies_start[0]:enemies_end[0]]
    cv2.imwrite("dbg/enemies.jpg", enemies)
    enemies_info = process_player_list(enemies);
    print(enemies_info)
    write_json("enemies.json", enemies_info)

    return {
        "time": datetime.now().timestamp(),
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
