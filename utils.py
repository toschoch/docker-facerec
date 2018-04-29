
from PIL import Image, ImageFont

def resize_image(image, width=1024):
    basewidth = width
    wpercent = (basewidth / float(image.size[0]))
    hsize = int((float(image.size[1]) * float(wpercent)))
    return image.resize((basewidth, hsize), Image.ANTIALIAS)

def get_font(width):

    fontsize = 1  # starting font size

    # portion of image width you want text width to be
    img_fraction = 0.05

    font = ImageFont.truetype("static/Ubuntu-Regular.ttf", fontsize)
    while font.getsize("Test")[0] < img_fraction * width:
        # iterate until the text size is just larger than the criteria
        fontsize += 1
        font = ImageFont.truetype("static/Ubuntu-Regular.ttf", fontsize)

    # optionally de-increment to be sure it is less than criteria
    fontsize -= 1
    return ImageFont.truetype("static/Ubuntu-Regular.ttf", fontsize)

def draw_rectangle(draw, rect, width, color):
    for i in range(width):
        draw.rectangle([(rect.left()+i, rect.top()+i), (rect.right()-i, rect.bottom()-i)], outline=color)