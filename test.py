import time
import numpy as np

from Epaper import *
from PIL import Image
from PIL import ImageDraw 
from PIL import ImageFont 
from PIL import ImageOps


# Demo Configuration
X_PIXEL = 128
Y_PIXEL = 250
RED_CH = True # If the module has only two colors(B&W), please set it to False.

height = 128
width = 250

im_black = Image.new('1', (height, width), 255)
im_red = Image.new('1', (height, width), 255)

draw_red = ImageDraw.Draw(im_red)
draw_black = ImageDraw.Draw(im_black) 
font = ImageFont.truetype('/usr/share/fonts/truetype/freefont/FreeMonoBold.ttf', 14)

draw_red.text((10,10), 'Hello world!', font = font, fill = 0x0)
# draw_red.text((10,30), 'Hello next!', font = font, fill = 0x0)
# draw_red.text((10,50), 'Hello Henry!', font = font, fill = 0x0)
# draw_red.text((10,70), "Hello Q'thulu!", font = font, fill = 0x0)



def to_bytes(image):
    data = [0 for i  in range(width * height // 8)]
    for i, byte in enumerate(ImageOps.mirror(image).getdata()):
        if 0xff != byte:
            data[i // 8]  |= (1 << (i % 8))
    data.reverse()
    return ImageOps.mirror(image).getdata()

print('flashing ...', end='')
e = Epaper(height,width)
e.flash_red(buf=to_bytes(im_red))
e.flash_black(on=False)
e.update()

time.sleep(1)
print(' done.')