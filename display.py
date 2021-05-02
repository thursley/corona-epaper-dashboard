import os
import time
import numpy as np

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from PIL import ImageOps

from vac_quote import get_vac_quote

def to_bytes(image):
    data = [0 for i  in range(width * height // 8)]
    for i, byte in enumerate(ImageOps.mirror(image).getdata()):
        if 0xff != byte:
            data[i // 8]  |= (1 << (i % 8))
    data.reverse()
    return data

height = 250
width = 128

im_black = Image.new('1', (width, height), 255)
im_red = Image.new('1', (width, height), 255)

padding = 15

draw_red = ImageDraw.Draw(im_red)
draw_black = ImageDraw.Draw(im_black)
original_fontsize = 10
font_factor = 2

font = ImageFont.truetype('./fonts/Minecraftia-Regular.ttf', original_fontsize * font_factor)
font_caption = ImageFont.truetype('./fonts/Minecraftia-Regular.ttf', original_fontsize)


message1 = f"{(get_vac_quote('th') * 100).round(2)}"
message2 = f"{(get_vac_quote('brd') * 100).round(2)}"

w1, h1 = draw_red.textsize(message1, font=font)
w2, h2 = draw_red.textsize(message2, font=font)

w = max(w1, w2)

inner_padd_v = 5
inner_padd_h = 10
upper_border = padding - inner_padd_v
# now inner padding for lower border looks better.
lower_border = padding + h1 * 2 

left_border = (width - w) / 2 - inner_padd_h
right_border = (width + w) / 2 + inner_padd_h

upper_left = (left_border, upper_border)
upper_right = (right_border, upper_border)
lower_left = (left_border, lower_border)
lower_right = (right_border, lower_border)

upper_caption = 'th'

w_c1, h_c1 = draw_red.textsize(upper_caption,font=font_caption)
upper_caption_line = (((width - w_c1) / 2 - inner_padd_h, upper_border), ((width + w_c1) / 2 + inner_padd_h, upper_border))

lower_caption = 'brd'

w_c2, h_c2 = draw_red.textsize(lower_caption,font=font_caption)
lower_caption_line = (((width - w_c2) / 2 - inner_padd_h, lower_border - 1), ((width + w_c2) / 2 + inner_padd_h, lower_border - 1))


draw_red.text(((width - w1) / 2, padding), message1, font = font, fill = 0x0)
w,h = draw_red.textsize(message2, font=font)

draw_red.text(((width - w2) / 2, padding + h), message2, font = font, fill = 0x0)

draw_red.line([upper_left, upper_right, lower_right, lower_left, upper_left],width=2, fill=0x0)

draw_red.line(upper_caption_line, width = 2, fill =0xff)
draw_red.line(lower_caption_line, width = 2, fill =0xff)

draw_red.text(((width - w_c1) / 2, upper_border - h_c1 / 4), upper_caption, font=font_caption)
draw_red.text(( 0 / 2, lower_border - h_c2 / 3), lower_caption, font=font_caption)

if 'raspberrypi' == os.uname().nodename: 
    from Epaper import Epaper

    print('flashing ...', end='')
    e = Epaper(height,width)
    e.flash_red(buf=to_bytes(im_red))
    e.flash_black(on=False)
    e.update()

    time.sleep(1)
    print(' done.')
else:
    for i, byte in enumerate(im_red.getdata()):
        if byte != 0xff: 
            print(i)
            break
    # we are not running on pi, just show image.
    im_red.show()
