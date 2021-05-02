import os
import time
import numpy as np

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from PIL import ImageOps

from vac_quote import get_vac_quote
from incidences import get_7days_incidence

def to_bytes(image):
    data = [0 for i  in range(width * height // 8)]
    for i, byte in enumerate(ImageOps.mirror(image).getdata()):
        if 0xff != byte:
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
        draw_red.line([upper_end, self._offset, right_end], width=2, fill=0)
        # draw_red.point(self._points)
        draw_red.line(self._points)

        if self._title is not None:
            draw_red.text(self._offset, self._title, font=font_caption)

    

height = 250
width = 128

im_black = Image.new('1', (width, height), 255)
im_red = Image.new('1', (width, height), 255)

padding = 15

draw_red = ImageDraw.Draw(im_red)
draw_black = ImageDraw.Draw(im_black)
original_fontsize = 10
font_factor = 2

font = ImageFont.truetype('./fonts/DejaVuSans.ttf', original_fontsize * font_factor)
font_caption = ImageFont.truetype('./fonts/DejaVuSans.ttf', original_fontsize)


message1 = f"{(get_vac_quote('th') * 100).round(2)}"
message2 = f"{(get_vac_quote('brd') * 100).round(2)}"

w1, h1 = draw_red.textsize(message1, font=font)
w2, h2 = draw_red.textsize(message2, font=font)

w = max(w1, w2)

inner_padd_v = 5
inner_padd_h = 10
upper_border = padding - inner_padd_v
# now inner padding for lower border looks better.
lower_border = padding + h1 * 2 + inner_padd_v

left_border = (width - w) / 2 - inner_padd_h
right_border = (width + w) / 2 + inner_padd_h

upper_left = (left_border, upper_border)
upper_right = (right_border, upper_border)
lower_left = (left_border, lower_border)
lower_right = (right_border, lower_border)

upper_caption = 'th'

w_c1, h_c1 = draw_red.textsize(upper_caption,font=font_caption)
upper_caption_line = (((width - w_c1) / 2 - inner_padd_v, upper_border), ((width + w_c1) / 2 + inner_padd_v, upper_border))

lower_caption = 'brd'

w_c2, h_c2 = draw_red.textsize(lower_caption,font=font_caption)
lower_caption_line = (((width - w_c2) / 2 - inner_padd_v, lower_border - 1), ((width + w_c2) / 2 + inner_padd_v, lower_border - 1))


draw_red.text(((width - w1) / 2, padding), message1, font = font, fill = 0x0)
w,h = draw_red.textsize(message2, font=font)

draw_red.text(((width - w2) / 2, padding + h), message2, font = font, fill = 0x0)

draw_red.line([upper_left, upper_right, lower_right, lower_left, upper_left],width=2, fill=0x0)

draw_red.line(upper_caption_line, width = 2, fill =0xff)
draw_red.line(lower_caption_line, width = 2, fill =0xff)

draw_red.text(((width - w_c1) / 2, upper_border - h_c1 / 2), upper_caption, font=font_caption)
draw_red.text(((width - w_c2) / 2, lower_border - h_c2 / 2), lower_caption, font=font_caption)

diag_width = width - 20
diag_height = 60

incidences = get_7days_incidence()

diag = Diagram(diag_width, diag_height, (10, 80))
diag.plot(incidences)
diag.set_title(f'akt. Inzidenz: {round(incidences[-1], 1)}')
diag.draw()

if 'raspberrypi' == os.uname().nodename: 
    from Epaper import Epaper

    print('flashing ...', end='')
    e = Epaper(height,width)
    e.flash_red(buf=to_bytes(im_red))
    e.flash_black(buf=to_bytes(im_black))
    e.update()

    time.sleep(1)
    print(' done.')
else:
    # we are not running on pi, just show image.
    im_red.show()
