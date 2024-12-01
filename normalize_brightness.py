from PIL import Image
import numpy as np

def normalize_brightness(img, target_brightness):
    gray_img = img.convert('L')

    pixels = np.array(gray_img)
    mean_brightness = np.mean(pixels)

    adjustment_factor = target_brightness / mean_brightness if mean_brightness != 0 else 1

    normalized_img_array = np.clip(pixels * adjustment_factor, 0, 255).astype(np.uint8)
    normalized_img = Image.fromarray(normalized_img_array, 'L')

    return normalized_img
