from os.path import join, dirname
from json import load
from random import choice
import argparse

from PIL import Image, ImageDraw, ImageFont, ImageEnhance
from tqdm import tqdm
import numpy as np

parser = argparse.ArgumentParser(description="这是一个能将图片转成汉字的脚本")
parser.add_argument('image_path', type=str,
                    help='输入图片的路径')
parser.add_argument('output_path', type=str,
                    help='输出图片的路径')
parser.add_argument('-psp', '--path_save_pretreated', type=str,
                    help='预处理后的图片的保存路径，不填时不保存')
parser.add_argument('-nbt', '--normalize_brightness_target', type=int,
                    help='标准化图片亮度目标，在0~255之间，值越大图片越亮，不填时不处理')
parser.add_argument('-cf', '--contrast_factor', type=float, default=1.0,
                    help='对比度因子，在0以上，大于1时提高对比度，小于1时降低对比度，为1时无效，默认为1')
parser.add_argument('-c', '--count', type=int, default=5,
                    help='分配给同一灰度的汉字数量，默认为5，最大100，建议在1~15之间')
parser.add_argument('-s', '--size', type=int, default=300,
                    help='横向汉字个数，默认为300（不建议超过500）')
parser.add_argument('-cs', '--char_size', type=int, default=12,
                    help='单个汉字的尺寸，单位为像素，默认为12（建议在8~16之间）')
parser.add_argument('-crf', '--colorful', action='store_true',
                    help='输出彩色图片')
parser.add_argument('-fp', '--font_path', type=str, default=join((cur_dir := dirname(__file__)), 'font.ttf'),
                    help='字体路径，默认为此脚本所在的文件夹下的font.ttf文件，支持otf，但用otf会让速度变慢')
parser.add_argument('-fp2', '--font_path2', type=str, default=join((cur_dir := dirname(__file__)), 'font2.ttf'),
                    help='扩B~扩F的字体路径，默认为此脚本所在的文件夹下的font2.ttf文件，支持otf，但用otf会让速度变慢')
parser.add_argument('-fp3', '--font_path3', type=str, default=join((cur_dir := dirname(__file__)), 'font3.ttf'),
                    help='扩G~扩H的字体路径，默认为此脚本所在的文件夹下的font3.ttf文件，支持otf，但用otf会让速度变慢')
parser.add_argument('-fp4', '--font_path4', type=str, default=join((cur_dir := dirname(__file__)), 'font4.ttf'),
                    help='扩I的字体路径，默认为此脚本所在的文件夹下的font4.ttf文件，支持otf，但用otf会让速度变慢')
args = parser.parse_args()

image_path = args.image_path
output_path = args.output_path
count = args.count
size = args.size
char_size = args.char_size
font_path = args.font_path
font_path2 = args.font_path2
font_path3 = args.font_path3
font_path4 = args.font_path4
normalize_brightness_target = args.normalize_brightness_target
path_save_pretreated = args.path_save_pretreated

dict_ = tuple(map(lambda i: i[:count], load(open(join(cur_dir, 'data.json')))))
img = Image.open(image_path)

width, height = img.size
aspect_ratio = height / width
img = img.resize((size, (height := round(size * aspect_ratio))))

if args.colorful:
    img_rgba = img.convert('RGBA')
    img_data = np.array(img_rgba)
    bgc_r = round(255 - np.mean(img_data[:, :, 0]))
    bgc_g = round(255 - np.mean(img_data[:, :, 1]))
    bgc_b = round(255 - np.mean(img_data[:, :, 2]))
    bgc = (round(bgc_r * 299/1000 + bgc_g * 587/1000 + bgc_b * 114/1000), ) * 3 + (255, )
else:
    bgc = (255, 255, 255, 255)

enhancer = ImageEnhance.Contrast(img)
img = enhancer.enhance(args.contrast_factor)
if normalize_brightness_target is not None:
    from normalize_brightness import normalize_brightness
    img = normalize_brightness(img, normalize_brightness_target)

if path_save_pretreated is not None:
    img.save(path_save_pretreated)

img = img.convert('L')
string_array = np.vectorize(lambda gray: chr(choice(dict_[gray])))(img)
string_list = string_array.flatten()

font1 = ImageFont.truetype(font_path, char_size)
font2 = ImageFont.truetype(font_path2, char_size)
font3 = ImageFont.truetype(font_path3, char_size)
font4 = ImageFont.truetype(font_path4, char_size)

img = Image.new('RGBA', (size * char_size, height * char_size), bgc)
draw = ImageDraw.Draw(img)
for index, char in tqdm(enumerate(string_list), total=height * size):
    x = index % size
    y = index // size
    font = font1
    if 0x3400 <= ord(char) <= 0x9FFF:
        font = font1
    elif 0x20000 <= ord(char) <= 0x2EBE0:
        font = font2
    elif 0x30000 <= ord(char) <= 0x323AF:
        font = font3
    elif 0x2EBF0 <= ord(char) <= 0x2EE5D:
        font = font4
    if args.colorful:
        color = tuple(img_data[y, x])
    else:
        color = (0, 0, 0, 0)
    draw.text((x * char_size, (y + 1) * char_size), char, color, font, anchor='lb')

img.save(output_path)
