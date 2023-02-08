from PIL import Image, ImageDraw
from pathlib import Path
import argparse
import json
import matplotlib.pyplot as plt

parser = argparse.ArgumentParser(description = 'Rico Intro Task')
parser.add_argument('task_number', type=int, choices=[1, 2, 3, 4])
parser.add_argument('im_number', type=int, nargs='?')
args = parser.parse_args()

DS_LEN = 72218

def get_unique_sizes_and_ratios():
    # time: 20 sec
    # [(1080, 1920), (540, 960), (1920, 1080), (960, 540)]
    # [0.5625, 1.7778]

    sizes,ratios = [], []
    for i in range(DS_LEN + 1):
        path = Path(f'dataset/{i}.jpg')
        if not path.is_file():
            continue
        im = Image.open(path)
        size = im.size
        ratio = round(size[0] / size[1], 4)
        if size not in sizes:
            sizes.append(size)
        if ratio not in ratios:
            ratios.append(ratio)
    return sizes, ratios

def get_count_of_greyscale_images():
    # time: 30 min
    # 53572
    count = 0
    for i in range(DS_LEN + 1):
        path = Path(f'dataset/{i}.jpg')
        if not path.is_file():
            continue
        im = Image.open(path)
        w, h = im.size
        resized_im = im.resize((w // 2, h // 2), resample=0)
        colors = resized_im.getcolors(w * h // 4)
        sorted_colors = sorted(colors, key=lambda c: c[0])
        mfc = sorted_colors[-1][1]
        if (mfc[0] == mfc[1] == mfc[2]):
            count += 1
    return count

def get_bounds(i):
    im_path = Path(f'dataset/{i}.jpg')
    json_path = Path(f'dataset/{i}.json')
    if not (im_path.is_file() and json_path.is_file()):
        return []
    info_size = (1440, 2560)
    im = Image.open(im_path)
    w, h = im.size
    im_size = (w, h) if w < h else (h, w)
    with open(json_path, 'r') as f:
        data = json.load(f)
    data_str = json.dumps(data)
    clickable_elements = data_str.split('"clickable": true')[1:]
    bounds = []
    for elem in clickable_elements:
        bound = elem.split('"bounds": [')[1].split(']')[0]
        bound = list(map(int, bound.split(',')))
        bound[0] = round(bound[0] / info_size[0] * im_size[0])
        bound[1] = round(bound[1] / info_size[1] * im_size[1])
        bound[2] = round(bound[2] / info_size[0] * im_size[0])
        bound[3] = round(bound[3] / info_size[1] * im_size[1])
        bounds.append(bound)
    return bounds

def draw_bounds(i):
    im_path = Path(f'dataset/{i}.jpg')
    if not im_path.is_file():
        return
    im = Image.open(im_path)
    im_dr = ImageDraw.Draw(im)
    bounds = get_bounds(i)
    for bound in bounds:
        im_dr.rectangle(bound, outline='red', width=8)
    im.show()

def draw_histogram():
    # time: 2 min
    areas = []
    for i in range(DS_LEN + 1):
        bounds = get_bounds(i)
        for bound in bounds:
            areas.append(abs((bound[2] - bound[0]) * (bound[3] - bound[1])))
    _, ax = plt.subplots(1, 1)
    s = 1080 * 1920
    ax.hist(areas, bins=[0, s // 128, s // 64, s // 32, s // 16, s // 8, s // 4, s // 2,  s])
    ax.set_title("Areas of clickable elements")
    ax.set_xlabel('Area size')
    ax.set_ylabel('Count')
    plt.savefig('hist.png')
    

if args.task_number == 1:
    sizes, ratios = get_unique_sizes_and_ratios()
    print(sizes)
    print(ratios)
elif args.task_number == 2:
    n = get_count_of_greyscale_images()
    print(n)
elif args.task_number == 3:
    draw_bounds(args.im_number)
else:
    draw_histogram()