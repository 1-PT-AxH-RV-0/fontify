from os.path import join, dirname
from decimal import Decimal
from json import dump
import argparse

from PIL import Image, ImageFont, ImageDraw
from tqdm.rich import tqdm

parser = argparse.ArgumentParser(description="这是一个能将字体内的汉字按黑度排序的脚本")
parser.add_argument('-fp', '--font_path', type=str, default=join((cur_dir := dirname(__file__)), 'font.ttf'),
                    help='基本和扩A的字体路径，默认为此脚本所在的文件夹下的font.ttf文件，支持otf，但用otf会让速度变慢')
parser.add_argument('-fp2', '--font_path2', type=str, default=join((cur_dir := dirname(__file__)), 'font2.ttf'),
                    help='扩B~扩F的字体路径，默认为此脚本所在的文件夹下的font2.ttf文件，支持otf，但用otf会让速度变慢')
parser.add_argument('-fp3', '--font_path3', type=str, default=join((cur_dir := dirname(__file__)), 'font3.ttf'),
                    help='扩G~扩H的字体路径，默认为此脚本所在的文件夹下的font3.ttf文件，支持otf，但用otf会让速度变慢')
parser.add_argument('-fp4', '--font_path4', type=str, default=join((cur_dir := dirname(__file__)), 'font4.ttf'),
                    help='扩I的字体路径，默认为此脚本所在的文件夹下的font4.ttf文件，支持otf，但用otf会让速度变慢')
args = parser.parse_args()

font_path = args.font_path
font_path2 = args.font_path2
font_path3 = args.font_path3
font_path4 = args.font_path4
chars = [*range(0x4E00, 0x9FFF + 1),   #Basic
         *range(0x3400, 0x4DBF + 1),   #Ext.A
         *range(0x20000, 0x2A6DF + 1), #Ext.B
         *range(0x2A700, 0x2B739 + 1), #Ext.C
         *range(0x2B740, 0x2B81D + 1), #Ext.D
         *range(0x2B820, 0x2CEA1 + 1), #Ext.E
         *range(0x2CEB0, 0x2EBE0 + 1), #Ext.F
         *range(0x30000, 0x3134A + 1), #Ext.G
         *range(0x31350, 0x323AF + 1), #Ext.H
         *range(0x2EBF0, 0x2EE5D + 1)] #Ext.I
size = 256

font1 = ImageFont.truetype(font_path, size)
font2 = ImageFont.truetype(font_path2, size)
font3 = ImageFont.truetype(font_path3, size)
font4 = ImageFont.truetype(font_path4, size)
dict_ = {}
total_pixel_count = Decimal(size * round(size * 1.2))

def calculate_black_pixel_ratio(image):
    return Decimal(list(img.getdata()).count(0)) / total_pixel_count


def find_closest_decimals(decimal_list, targets, k=1):
    closest_dict = {}

    for target in targets:
        differences = [(abs(value - target), value) for value in decimal_list]
        sorted_differences = sorted(differences, key=lambda x: x[0])[:100]

        closest_dict[str(target)] = [i[1] for i in sorted_differences][::-1]

    return closest_dict


for char in tqdm(chars):
    img = Image.new('1', (size, round(size * 1.2)), 1)
    draw = ImageDraw.Draw(img)
    if 0x3400 <= char <= 0x9FFF:
        font = font1
    elif 0x20000 <= char <= 0x2EBE0:
        font = font2
    elif 0x30000 <= char <= 0x323AF:
        font = font3
    elif 0x2EBF0 <= char <= 0x2EE5D:
        font = font4
    draw.text((0, 0), chr(char), 0, font)
    dict_[calculate_black_pixel_ratio(img)] = char

scale = Decimal(1) / max(dict_.keys()) * 255
dict_ = {k * scale: i for k, i in dict_.items()}
closest_dict = find_closest_decimals(list(dict_.keys()), map(Decimal, range(0, 256)))
dict_ = {str(k): [dict_[j] for j in i] for k, i in closest_dict.items()}

dump(list(dict_.values())[::-1], open(join(cur_dir, 'data.json'), "w"), ensure_ascii=False)