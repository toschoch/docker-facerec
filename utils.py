
from PIL import Image, ImageFont
import base64
import numpy as np
from io import BytesIO

class BadRequest(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv

def rect_to_dict(rect):
    return {side: getattr(rect,side)() for side in ['left','right','top','bottom']}

def person_to_dict(p, attributes=['id','name','nmeans','code']):
    return dict(zip(attributes,[str(getattr(p, a)) if a!='code' else base64.b64encode(getattr(p, a).tobytes()).decode('ascii') for a in attributes]))

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
    if 'image' not in request.json:
        raise BadRequest("Missing file parameter!")

    image = request.json['image'].encode('ascii')

    image = Image.open(BytesIO(base64.b64decode(image)))

    return image


def extract_facecode(request):
    if 'code' not in request.json:
        raise BadRequest("Missing code parameter!")
    code = np.frombuffer(base64.b64decode(request.json['code']))
    if len(code.shape) != 1 or code.shape[0] != 128:
        raise BadRequest("Bad code parameter!")
    return code

def extract_name_or_id(request):
    name = request.json.get('name',None)
    id = request.json.get('id',None)
    if name is None and id is None:
        raise BadRequest("either ID or NAME must be specified!")
    return name, id