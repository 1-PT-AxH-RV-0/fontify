# fontify

## 简介
`fontify.py` 是一个 Python 脚本，用于将图片转换为汉字图像。该脚本通过分析输入图片的灰度值，将其转换为相应的汉字，生成一幅新的图像。它支持多种字体和亮度、对比度的调整，适合用于艺术创作和图像处理。

## 特性
- 将图片转换为汉字图像；
- 支持自定义字体；
- 可调整图像的亮度和对比度（即预处理）以得到更好的效果；
- 支持预处理后的图像保存；
- 可自定义汉字的数量和大小。

## 准备

1. 确保您的系统已安装 `Python 3.x`；

2. 确保您的系统已安装以下Python第三方库：
   - `pillow`；
   - `tqdm`；
   - `numpy`.

   使用命令：

   ```bash
   pip install pillow tqdm numpy
   ```

   若您在安装numpy时遇到错误，请尝试：

   ```bash
   apt install python-numpy
   ```

3. 克隆此仓库：
   ```bash
   git clone https://github.com/tile-WWDCCS-name/fontify
   cd fontify
   ```

## 使用方法
运行脚本时，需要指定输入图片路径和输出图片路径。可以使用以下命令行参数：

```bash
python fontify.py <image_path> <output_path> [options]
```

### 参数说明
- `image_path`: 输入图片的路径；
- `output_path`: 输出图片的路径；
- `-psp`, `--path_save_pretreated`: 预处理后的图片的保存路径（可选）
- `-nbt`, `--normalize_brightness_target`: 标准化图片亮度目标，范围在 0~255 之间（可选）
- `-cf`, `--contrast_factor`: 对比度因子，默认为 1.0（可选）
- `-c`, `--count`: 分配给同一灰度的汉字数量，默认为 5（可选）
- `-s`, `--size`: 横向汉字个数，默认为 300（可选）
- `-cs`, `--char_size`: 单个汉字的尺寸，默认为 12（可选）
- `-fp`, `--font_path`: 字体路径，默认为脚本所在文件夹下的 `font.ttf`（可选）
- `-fp2`, `--font_path2`: 扩B~扩F的字体路径，默认为脚本所在文件夹下的 `font2.ttf`（可选）
- `-fp3`, `--font_path3`: 扩G~扩H的字体路径，默认为脚本所在文件夹下的 `font3.ttf`（可选）
- `-fp4`, `--font_path4`: 扩I的字体路径，默认为脚本所在文件夹下的 `font4.ttf`（可选）

### 示例
```bash
python fontify.py input.jpg output.png -nbt 200 -cf 1.5 -c 10 -s 400 -cs 14
```

## chinese_character_blackness_sort.py

`chinese_character_blackness_sort.py` 是一个用于更新字体黑度排序的脚本。它会根据字体文件中的汉字黑度生成一个 JSON 文件，以便在需要更换字体时使用。

### 使用方法
运行脚本时，需要指定字体文件路径。可以使用以下命令行参数：

```bash
python chinese_character_blackness_sort.py [options]
```

### 参数说明
- `-fp`, `--font_path`: 基本和扩A的字体路径，默认为脚本所在文件夹下的 `font.ttf`（可选）
- `-fp2`, `--font_path2`: 扩B~扩F的字体路径，默认为脚本所在文件夹下的 `font2.ttf`（可选）
- `-fp3`, `--font_path3`: 扩G~扩H的字体路径，默认为脚本所在文件夹下的 `font3.ttf`（可选）
- `-fp4`, `--font_path4`: 扩I的字体路径，默认为脚本所在文件夹下的 `font4.ttf`（可选）

### 示例
```bash
python chinese_character_blackness_sort.py -fp path/to/font.ttf -fp2 path/to/font2.ttf
```

## 注意事项
- 确保输入的图片路径正确且图片格式受支持；
- 字体文件（如 `font.ttf`, `font2.ttf`, `font3.ttf`, `font4.ttf`）需放在与脚本相同的目录下，或者提供正确的路径；
- 对于较大的 `--size` 或 `--char_size` 参数值，处理时间可能会较长；
- 若您需使用其他的自定义字体，请确保您的字体能够显示对应区段的所有汉字，并在运行 `fontify.py` 前运行 `chinese_character_blackness_sort.py`（注意传入您需要的字体路径）；
