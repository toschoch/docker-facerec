
from werkzeug.exceptions import BadRequest
from PIL import Image, ImageFont
import base64
import numpy as np

def rect_to_dict(rect):
    return {side: getattr(rect,side) for side in ['left','right','top','bottom']}

def person_to_dict(p, attributes=['id','name','nmeans','code']):
    return dict(zip(attributes,[str(getattr(p, a)) if a!='code' else str(getattr(p, a).tolist()) for a in attributes]))

def face_to_dict(face):
    p, rect, shape = face
    return {'person':person_to_dict(p), 'position': rect_to_dict(rect)}

def faces_to_list(faces):
    return [face_to_dict(face) for face in faces]

def is_picture(filename):
    image_extensions = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in image_extensions

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


def extract_image(request):
    # Check if a valid image file was uploaded
    if 'file' not in request.files:
        raise BadRequest("Missing file parameter!")

    file = request.files['file']
    if file.filename == '':
        raise BadRequest("Given file is invalid")

    return file


def extract_facecode(request):
    if 'code' not in request.args:
        raise BadRequest("Missing code parameter!")
    code = np.frombuffer(base64.b64decode(request.args['code']))
    if len(code.shape) != 1 or code.shape[0] != 128:
        raise BadRequest("Bad code parameter!")
    return code


def extract_name_or_id(request):
    name = request.args.get('name',None)
    id = request.args.get('id',None)
    if name is None and id is None:
        raise BadRequest("either ID or NAME must be specified!")
    return name, id