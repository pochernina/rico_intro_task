from PIL import Image, ImageDraw
from pathlib import Path
import argparse
import json
import matplotlib.pyplot as plt
import imagesize
import itertools

parser = argparse.ArgumentParser(description='Rico Intro Task')
parser.add_argument('task_num', type=int, choices=[1, 2, 3, 4, 5], help='Task number')
parser.add_argument('input_dir', type=str, help='Input directory')
parser.add_argument('-l', '--limit', type=int, help='Limit for task 3')
parser.add_argument('-o', '--output_dir', type=str, help='Output directory for task 3')
args = parser.parse_args()

dir_path = args.input_dir
info_size = (1440, 2560)

def get_unique_sizes_and_ratios():
    # time: 16 sec (without lib imagesize: 21 sec)
    # [(1080, 1920), (540, 960), (1920, 1080), (960, 540)]
    # [0.5625, 1.7778]
    sizes, ratios = [], []
    img_paths = Path(dir_path).glob('*.jpg')
    for path in img_paths:
        size = imagesize.get(path)
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
    img_paths = Path(dir_path).glob('*.jpg')
    for path in img_paths:
        im = Image.open(path)
        w, h = im.size
        resized_im = im.resize((w // 2, h // 2), resample=0)
        # Image.getcolors(maxcolors) returns an unsorted list of (count, pixel) values
        colors = resized_im.getcolors(w * h // 4)
        sorted_colors = sorted(colors, key=lambda c: c[0])
        mfc = sorted_colors[-1][1]
        if (mfc[0] == mfc[1] == mfc[2]):
            count += 1
    return count

def get_bounds(json_path):
    with open(json_path, 'r') as f:
        elements = json.load(f)['activity']['root']['children']
    bounds = []
    for elem in elements:
        if elem is None:
            continue
        if 'children' in elem:
            elements.extend(elem['children'])
        if elem['clickable'] == True:
            bound = elem['bounds']
            if (bound[2] > info_size[0] or bound[3] > info_size[1] or bound[0] >= bound[2] or bound[1] >= bound[3]):
                continue
            bounds.append(bound)
    return bounds

def draw_bounds(limit):
    img_paths = itertools.islice(Path(dir_path).glob('*.jpg'), limit)
    for im_path in img_paths:
        json_path = str(im_path).split('.jpg')[0] + '.json'
        bounds = get_bounds(json_path)
        im = Image.open(im_path)
        w, h = im.size
        im_size = (w, h) if w < h else (h, w)
        im_dr = ImageDraw.Draw(im)
        for bound in bounds:
            bound[0] = round(bound[0] / info_size[0] * im_size[0])
            bound[1] = round(bound[1] / info_size[1] * im_size[1])
            bound[2] = round(bound[2] / info_size[0] * im_size[0])
            bound[3] = round(bound[3] / info_size[1] * im_size[1])
            im_dr.rectangle(bound, outline='red', width=8)
        i = str(im_path).split('/')[-1].split('.jpg')[0]
        im.save(f'{args.output_dir}/{i}_with_bounds.jpg')

def draw_histogram():
    # time: 80 sec
    area_ratios = []
    json_paths = Path(dir_path).glob('*.json')
    for path in json_paths:
        bounds = get_bounds(path)
        for bound in bounds:
            area_ratios.append((bound[2] - bound[0]) * (bound[3] - bound[1]) / (info_size[0] * info_size[1]))

    _, ax1 = plt.subplots(1, 1)
    ax1.hist(area_ratios, bins=50, rwidth=0.8)
    ax1.set_title("Clickable elements size distribution")
    ax1.set_xlabel('Propotion of the clickable element area to the screen area')
    plt.savefig('hist1.png')

    _, ax2 = plt.subplots(1, 1)
    ax2.hist(area_ratios, range=[0, 0.1], bins=50, rwidth=0.8)
    ax2.set_title("Clickable elements size distribution (0-10%)")
    ax2.set_xlabel('Propotion of the clickable element area to the screen area')
    plt.savefig('hist2.png')

def draw_bounds_with_large_propotion():
    img_paths = itertools.islice(Path(dir_path).glob('*.jpg'), 10)
    for im_path in img_paths:
        json_path = str(im_path).split('.jpg')[0] + '.json'
        bounds = get_bounds(json_path)
        im = Image.open(im_path)
        w, h = im.size
        im_size = (w, h) if w < h else (h, w)
        im_dr = ImageDraw.Draw(im)
        for bound in bounds:
            if (bound[2] - bound[0]) * (bound[3] - bound[1]) / (info_size[0] * info_size[1]) >= 0.8:
                bound[0] = round(bound[0] / info_size[0] * im_size[0])
                bound[1] = round(bound[1] / info_size[1] * im_size[1])
                bound[2] = round(bound[2] / info_size[0] * im_size[0])
                bound[3] = round(bound[3] / info_size[1] * im_size[1])
                im_dr.rectangle(bound, outline='red', width=8)
        i = str(im_path).split('/')[-1].split('.jpg')[0]
        im.save(f'{args.output_dir}/{i}_large_propotion.jpg')


if args.task_num == 1:
    sizes, ratios = get_unique_sizes_and_ratios()
    print(sizes)
    print(ratios)
elif args.task_num == 2:
    n = get_count_of_greyscale_images()
    print(n)
elif args.task_num == 3:
    draw_bounds(args.limit)
elif args.task_num == 4:
    draw_histogram()
else:
    draw_bounds_with_large_propotion()
