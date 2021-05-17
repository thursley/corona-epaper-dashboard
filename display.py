import os
import time
import numpy as np

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from PIL import ImageOps

from datetime import datetime

from vac_quote import get_vac_quote
from incidences import get_7days_incidence
from weather import get_temperature
from weather import get_icon_name

def to_bytes(image):
    data = [0 for i in range(width * height // 8)]
    for i, byte in enumerate(ImageOps.mirror(image).getdata()):
        if 0 != byte:
            data[i // 8]  |= (1 << (i % 8))
    data.reverse()
    return data

class Diagram:
    _points = []

    def __init__(self, width, height, position):
        self._width = width
        self._height = height
        self._offset = (position[0], position[1] + height)

    def add_point(self, point):
        new_point = (point[0] + self._offset[0], self._offset[1] - point[1])
        self._points.append(new_point)

    def set_title(self, title):
        self._title = title

    def plot(self, values):
        bucket_size = len(values) // self._width  +1
        buckets = [values[i-bucket_size:i] for i in range(bucket_size, len(values)+1, bucket_size)]
        mean_values = [np.mean(bucket) for bucket in buckets]
        height_factor = self._height / max(mean_values)

        for i, value in enumerate(mean_values):
            self.add_point((i, int(value * height_factor)))


    def draw(self):
        upper_end = (self._offset[0], self._offset[1] - self._height)
        right_end = (self._offset[0] + self._width, self._offset[1])
        draw_black.line([upper_end, self._offset, right_end], width=2, fill=0xff)
        # draw_red.point(self._points)
        draw_red.line(self._points, fill=0xff)

        if self._title is not None:
            draw_black.text(self._offset, self._title, font=caption_font, fill=0xff)

class DoubleValue:

    _padding = 5
    _padding_small = 2

    def __init__(self, width, position):
        self._width = width
        self._position = position
        self._height = draw_red.textsize(" ", font)[1] * 2 + self._padding * 2

    def set_upper_value(self, text, title=None):
        self._upper_value = text
        self._upper_title = title

    def set_lower_value(self, text, title=None):
        self._lower_value = text
        self._lower_title = title

    def draw(self):
        self._draw_frame()
        self._draw_values()
        self._draw_titles()

    def _draw_frame(self):
        upper_left = (self._position[0], self._position[1])
        upper_right = (self._position[0] + self._width, self._position[1])
        lower_left = (self._position[0], self._position[1] + self._height)
        lower_right = (self._position[0] + self._width, self._position[1] + self._height)

        draw_black.line((upper_left, upper_right, lower_right, lower_left, upper_left), width=2, fill=0xff)

    def _draw_values(self):
        w, h = draw_red.textsize(self._upper_value, font=font)
        pos = (self._position[0] + (self._width - w) / 2, self._position[1] + self._padding)
        draw_red.text(pos, self._upper_value, font=font, fill=0xff)
       
        w, _ = draw_red.textsize(self._lower_value, font=font)
        pos = (self._position[0] + (self._width - w) / 2, self._position[1] + h + self._padding)
        draw_red.text(pos, self._lower_value, font=font, fill=0xff)

    def _draw_titles(self):
        if self._upper_title is not None:
            w, h = draw_black.textsize(self._upper_title, font=caption_font)
            left = self._position[0] + (self._width - w) / 2 - self._padding
            right = self._position[0] +  (self._width + w) / 2 + self._padding
            line = (left, self._position[1]), (right, self._position[1])
            draw_black.line(line, width=2, fill=0)
            
            pos = (self._position[0] + (self._width - w) / 2, self._position[1] - h / 2)
            draw_red.text(pos, self._upper_title, font=caption_font, fill=0xff)

        if self._lower_title is not None:
            w, h = draw_black.textsize(self._lower_title, font=caption_font)
            height = self._position[1] + self._height - 1
            left  = self._position[0] + (self._width - w) / 2 - self._padding
            right = self._position[0] + (self._width + w) / 2 + self._padding
            line = (left, height), (right, height)
            draw_black.line(line, width=2, fill=0)
            pos = (self._position[0] + (self._width - w) / 2, height - h / 2)
            draw_red.text(pos, self._lower_title, font=caption_font, fill=0xff)

height = 250
width = 128

print('preparing image... ', end='')
im_black = Image.new('1', (width, height), 0)
im_red = Image.new('1', (width, height), 0)

draw_red = ImageDraw.Draw(im_red)
draw_black = ImageDraw.Draw(im_black)

padding = 15
original_fontsize = 10
font_factor = 2
big_font_factor = 2.5

font = ImageFont.truetype('./fonts/DejaVuSans.ttf', original_fontsize * font_factor)
big_font = ImageFont.truetype('./fonts/DejaVuSans.ttf', int(original_fontsize * big_font_factor))
caption_font = ImageFont.truetype('./fonts/DejaVuSans.ttf', original_fontsize)
print('done.')

print('getting vaccination quotes... ', end='')
inc_th = f"{(get_vac_quote('th') * 100).round(2)}"
inc_de = f"{(get_vac_quote('brd') * 100).round(2)}"
print('done.')

diag_width = width - 2 * padding
diag_height = 60

print('getting incidences... ', end='')
incidences = get_7days_incidence()
print('done.')

diag = Diagram(diag_width, diag_height, (padding, 80))
diag.plot(incidences)
diag.set_title(f'akt. Inzidenz: {round(incidences[-1], 1)}')
diag.draw()

dv = DoubleValue(width - 2 * padding, (padding, 12))
dv.set_upper_value(inc_th, "th")
dv.set_lower_value(inc_de, "de")
dv.draw()

now = datetime.now()
timestamp_date = now.strftime("%d.%m.%Y")
timestamp_time = now.strftime("%H:%M")

_, h = draw_black.textsize(timestamp_date, font=caption_font)
w, _ = draw_black.textsize(timestamp_time, font=caption_font)
draw_black.text((padding, height - h), timestamp_date, font=caption_font, fill=0xff)
draw_black.text((width - padding - w, height- h), timestamp_time, font=caption_font, fill=0xff)

print('getting weather data... ', end='')
temperature = f'{get_temperature()}°C'
weather_icon = f'weather-icons/{get_icon_name()}.png'
print('done.')


icon_height = 80 + diag_height + 10
temp_height = icon_height + 67

icon = ImageOps.invert(Image.open(weather_icon))
w, _ = icon.size
im_black.paste(icon, (int((width -w ) / 2), icon_height))

w, _ = draw_black.textsize(temperature, font=font)
draw_black.text(((width - w) / 2, temp_height), temperature, font=font, fill=0xff)

if 'raspberrypi' == os.uname().nodename: 
    from Epaper import Epaper

    print('flashing ...', end='')
    e = Epaper(height, width)
    e.flash_red(buf=to_bytes(im_red))
    e.flash_black(buf=to_bytes(im_black))
    e.update()

    time.sleep(1)
    print(' done.')
else:
    # we are not running on pi, just show image.
    imb = im_black.load()
    imr = im_red.load()
    arr = np.zeros(shape=(250,128,3), dtype=np.uint8)
    for x in range(width):
        for y in range(height):
            if imb[x,y] == 0xff:
                arr[y, x] = (0,0,0)
            elif imr[x,y] == 0xff:
                arr[y, x] = (0xff,0,0)
            else:
                arr[y, x] = (0xff,0xff,0xff)

    im = Image.fromarray(arr)
    im.show()
