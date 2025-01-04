from os.path import join, dirname
from json import load
from random import choice
import argparse

from PIL import Image, ImageDraw, ImageFont, ImageEnhance
from tqdm import tqdm
import numpy as np
import sympy as sp

cur_dir = dirname(__file__)


def hex_to_rgb(hex_value):
    hex_value = hex_value.strip("#")

    red = int(hex_value[0:2], 16)
    green = int(hex_value[2:4], 16)
    blue = int(hex_value[4:6], 16)

    return red, green, blue


parser = argparse.ArgumentParser(description="这是一个能将图片转成汉字的脚本")
parser.add_argument("image_path", type=str, help="输入图片的路径")
parser.add_argument("output_path", type=str, help="输出图片的路径")
parser.add_argument(
    "-bgc",
    "--background_color",
    type=str,
    default="#FFFFFF",
    help="背景颜色，默认纯白（#FFFFFF)",
)
parser.add_argument(
    "-psp",
    "--path_save_pretreated",
    type=str,
    help="预处理后的图片的保存路径，不填时不保存",
)
parser.add_argument(
    "-nbt",
    "--normalize_brightness_target",
    type=int,
    help="标准化图片亮度目标，在 0~255 之间，值越大图片越亮，不填时不处理",
)
parser.add_argument(
    "-cf",
    "--contrast_factor",
    type=float,
    default=1.0,
    help="对比度因子，在 0 以上，大于 1 时提高对比度，小于 1 时降低对比度，为 1 时无效，默认为 1",
)
parser.add_argument(
    "-s",
    "--size",
    type=int,
    default=300,
    help="横向汉字个数，默认为 300（不建议超过 500）",
)
parser.add_argument(
    "-cs",
    "--char_size",
    type=int,
    default=12,
    help="单个汉字的尺寸，单位为像素，默认为 12（建议在 8~16 之间）",
)

colorful_group = parser.add_mutually_exclusive_group()
colorful_group.add_argument(
    "-crf", "--colorful", action="store_true", help="输出彩色图片"
)
colorful_group.add_argument(
    "-tc",
    "--text_color",
    type=str,
    default="#FFFFFF",
    help="文字颜色，默认纯黑（#000000)",
)

parser.add_argument(
    "-fp",
    "--font_path",
    type=str,
    default=join(cur_dir, "font.ttf"),
    help="扩 A 和基本区字体路径，默认为此脚本所在的文件夹下的 font.ttf 文件，支持 otf，但用 otf 会让速度变慢",
)
parser.add_argument(
    "-fp2",
    "--font_path2",
    type=str,
    default=join(cur_dir, "font2.ttf"),
    help="扩 B~扩 F 字体路径，默认为此脚本所在的文件夹下的 font2.ttf 文件，支持 otf，但用 otf 会让速度变慢",
)
parser.add_argument(
    "-fp3",
    "--font_path3",
    type=str,
    default=join(cur_dir, "font3.ttf"),
    help="扩 G~扩 H 字体路径，默认为此脚本所在的文件夹下的 font3.ttf 文件，支持 otf，但用 otf 会让速度变慢",
)
parser.add_argument(
    "-fp4",
    "--font_path4",
    type=str,
    default=join(cur_dir, "font4.ttf"),
    help="扩 I 字体路径，默认为此脚本所在的文件夹下的 font4.ttf 文件，支持 otf，但用 otf 会让速度变慢",
)

subparsers = parser.add_subparsers(
    help="控制生成的图片中的汉字是否移动", required=True, dest="command"
)
static_parser = subparsers.add_parser(
    "static", help="生成汉字不移动的图片", aliases=["s"]
)
static_parser.add_argument(
    "-c",
    "--count",
    type=int,
    default=5,
    help="分配给同一灰度的汉字数量，默认为 5，最大 100，建议在 1~15 之间",
)
mobile_parser = subparsers.add_parser(
    "mobile", help="生成汉字移动的图片", aliases=["m"]
)
mobile_parser.add_argument(
    "-fps", "--fps", type=int, default=10, help="帧率，默认为 10，建议在 3~30 之间"
)
mobile_parser.add_argument(
    "-t", "--time", type=int, default=3, help="生成 gif 的时长，默认为 3"
)
mobile_parser.add_argument(
    "-t_min", "--t_minimum", type=float, default=0, help="t 的取值下限，默认为 0"
)
mobile_parser.add_argument(
    "-t_max", "--t_maximum", type=float, default=1, help="t 的取值上限，默认为 1"
)
mobile_parser.add_argument(
    "-pex",
    "--parametric_equation_x",
    type=str,
    default="t",
    help="控制汉字偏移量的参数方程的 x 坐标表达式，默认值为 t，参变数为 t",
)
mobile_parser.add_argument(
    "-pey",
    "--parametric_equation_y",
    type=str,
    default="t",
    help="控制汉字偏移量的参数方程的 y 坐标表达式，默认值为 t，参变数为 t",
)
args = parser.parse_args()

image_path = args.image_path
output_path = args.output_path
size = args.size
char_size = args.char_size
font_path = args.font_path
font_path2 = args.font_path2
font_path3 = args.font_path3
font_path4 = args.font_path4
normalize_brightness_target = args.normalize_brightness_target
path_save_pretreated = args.path_save_pretreated
colorful = args.colorful
contrast_factor = args.contrast_factor
background_color = hex_to_rgb(args.background_color)
text_color = hex_to_rgb(args.text_color)

mode = "static"
if args.command in {"static", "s"}:
    mode = "static"
    count = args.count
    dict_ = tuple(
        map(lambda i: i[::-1][:count], load(open(join(cur_dir, "data.json"))))
    )
elif args.command in {"mobile", "m"}:
    mode = "mobile"
    dict_ = tuple(map(lambda i: i[-1], load(open(join(cur_dir, "data.json")))))
    fps = args.fps
    time = args.time
    t_minimum = args.t_minimum
    t_maximum = args.t_maximum
    parametric_equation_x = sp.sympify(args.parametric_equation_x)
    parametric_equation_y = sp.sympify(args.parametric_equation_y)

font1 = ImageFont.truetype(font_path, char_size)
font2 = ImageFont.truetype(font_path2, char_size)
font3 = ImageFont.truetype(font_path3, char_size)
font4 = ImageFont.truetype(font_path4, char_size)

img = Image.open(image_path)
width, height = img.size
aspect_ratio = height / width
img = img.resize((size, (height := round(size * aspect_ratio))))

if colorful:
    img_rgba = img.convert("RGBA")
    img_data = np.array(img_rgba)

if normalize_brightness_target is not None:
    from normalize_brightness import normalize_brightness

    img = normalize_brightness(img, normalize_brightness_target)

enhancer = ImageEnhance.Contrast(img)
img = enhancer.enhance(contrast_factor)

if path_save_pretreated is not None:
    img.save(path_save_pretreated)

if mode == "mobile":

    def get_weighted_average(arr, center, radius=1):
        arr = arr
        center_row, center_col = center
        rows, cols = arr.shape
        y_indices, x_indices = np.indices((rows, cols))
        distances = np.sqrt(
            (y_indices - center_row) ** 2 + (x_indices - center_col) ** 2
        )

        mask = distances < radius
        weights = radius - distances[mask]
        weighted_elements = arr[mask] * weights

        weighted_average = (
            weighted_elements.sum() / weights.sum() if weights.sum() > 0 else 0
        )
        return weighted_average

    def get_weighted_average_3d(arr, center, radius=1):
        arr = np.array(arr)
        center_row, center_col = center
        rows, cols, _ = arr.shape

        y_indices, x_indices = np.indices((rows, cols))
        distances = np.sqrt(
            (y_indices - center_row) ** 2 + (x_indices - center_col) ** 2
        )

        mask = distances < radius
        weights = radius - distances[mask]

        weighted_sum = np.tensordot(arr[mask], weights, axes=(0, 0))
        weights_sum = weights.sum()
        weighted_average = (
            weighted_sum / weights_sum if weights_sum > 0 else np.zeros(4)
        )

        return weighted_average

    def draw_text(img_array, offset=(0, 0)):
        img = Image.new(
            "RGBA", (size * char_size, height * char_size), background_color
        )
        draw = ImageDraw.Draw(img)
        for yx in tqdm(
            np.ndindex(tuple([i + 2 for i in img_array.shape])),
            total=(height + 2) * (size + 2),
            leave=False,
        ):
            y, x = yx
            y -= 1
            x -= 1
            offset_x = x + offset[0]
            offset_y = y + offset[1]
            gray_value = get_weighted_average(img___, (offset_y, offset_x), 1)
            char = chr(dict_[int(gray_value)])
            if 0x3400 <= ord(char) <= 0x9FFF:
                font = font1
            elif 0x20000 <= ord(char) <= 0x2EBE0:
                font = font2
            elif 0x30000 <= ord(char) <= 0x323AF:
                font = font3
            elif 0x2EBF0 <= ord(char) <= 0x2EE5D:
                font = font4
            else:
                font = font1
            if colorful:
                color = get_weighted_average_3d(img_data, (offset_y, offset_x), 1)
                color = tuple(np.asarray(color, int))
            else:
                color = (0, 0, 0, 0)
            draw.text(
                (offset_x * char_size, (offset_y + 1) * char_size),
                char,
                color,
                font,
                anchor="ls",
            )

        return img

    def calculate_point(t):
        t_val = t_minimum + (t_maximum - t_minimum) * t
        x = float(parametric_equation_x.subs("t", t_val))
        y = float(parametric_equation_y.subs("t", t_val))
        return np.array([x % 1, y % 1])

    points = np.linspace(0, 1, (fps * time) + 1)
    offsets_list = list(map(calculate_point, points))

    img___ = np.array(img.convert("L"))
    imgs = []

    for offset in tqdm(offsets_list[:-1]):
        imgs.append(draw_text(img___, offset))

    imgs[0].save(
        output_path,
        save_all=True,
        append_images=imgs[1:],
        optimize=False,
        duration=int(1000 / fps),
        loop=0,
    )
if mode == "static":
    if colorful:
        img_data = np.array(img.convert("RGBA"))
    img = img.convert("L")
    string_array = np.vectorize(lambda gray: chr(choice(dict_[gray])))(img)
    string_list = string_array.flatten()

    img = Image.new("RGBA", (size * char_size, height * char_size), background_color)
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
            color = (0, 0, 0, 255)
        draw.text((x * char_size, (y + 1) * char_size), char, color, font, anchor="ls")

    img.save(output_path)
