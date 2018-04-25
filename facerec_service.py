import os
from os import listdir
from os.path import isfile, join, splitext

import tempfile
from facerec import facedb, dlib_api
from PIL import Image
import numpy as np
from flask import Flask, jsonify, request, flash, render_template, url_for
#from flask_cors import CORS
from werkzeug.exceptions import BadRequest
from wtforms import Form, FileField, validators, TextField

# Create flask app
app = Flask(__name__)


app.config.from_object(__name__)
app.config['SECRET_KEY'] = '8da7a0d2-5cec-4cec-99e7-2979768dca67'
#CORS(app)

# <Picture functions> #

def load_image(fname):
    return np.array(Image.open(fname))


facedb.set_db_path(os.path.join(os.path.split(__file__)[0],'data'))
# dlib_api.teach_person(load_image(r"D:\Users\TOS\Pictures\Camera Roll\WIN_20180412_14_00_21_Pro.jpg"),name='Tobias Schoch')
# dlib_api.teach_person(load_image(r"D:\Users\TOS\Pictures\Camera Roll\WIN_20180412_14_00_22_Pro.jpg"),name='Tobias Schoch')

def is_picture(filename):
    image_extensions = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in image_extensions


def get_all_picture_files(path):
    files_in_dir = [join(path, f) for f in listdir(path) if isfile(join(path, f))]
    return [f for f in files_in_dir if is_picture(f)]


def remove_file_ext(filename):
    return splitext(filename.rsplit('/', 1)[-1])[0]


def person_to_dict(p, attributes=['id','name','nmeans','code']):
    return dict(zip(attributes,[str(getattr(p, a)) if a!='code' else str(getattr(p, a).tolist()) for a in attributes]))

# <Picture functions> #

# <Controller>
class IdentifyForm(Form):
    file = TextField('File:', validators=[validators.required()])

@app.route("/identify", methods=['GET', 'POST'])
def web_identify():
    form = IdentifyForm(request.form)

    if request.method == 'POST':
        file = request.form['file']

        print(form.file.data)

        if form.validate():
            # Save the comment here.
            flash('Upload ' + file)
        else:
            flash('Error: All the form fields are required. ')

    return render_template('identify.html', form=form)


# @app.route('/identify', methods=['POST'])
# def web_recognize():
#     file = extract_image(request)
#
#     if file and is_picture(file.filename):
#         # The image file seems valid! Detect faces and return the result.
#         return jsonify(detect_faces_in_image(file))
#     else:
#         raise BadRequest("Given file is invalid!")


@app.route('/faces', methods=['GET', 'POST', 'DELETE'])
def web_faces():
    # GET
    if request.method == 'GET':
        return jsonify(list(map(person_to_dict,facedb.persons())))
    # else:
    #     # POST/DELETE
    #     if 'id' not in request.args:
    #         raise BadRequest("Identifier for the face was not given!")
    #
    #     if request.method == 'POST':
    #         file = extract_image(request)
    #         try:
    #             new_encoding = calc_face_encoding(file)
    #             faces_dict.update({request.args.get('id'): new_encoding})
    #         except Exception as exception:
    #             raise BadRequest(exception)
    #
    #     elif request.method == 'DELETE':
    #         faces_dict.pop(request.args.get('id'))



def extract_image(request):
    # Check if a valid image file was uploaded
    if 'file' not in request.files:
        raise BadRequest("Missing file parameter!")

    file = request.files['file']
    if file.filename == '':
        raise BadRequest("Given file is invalid")

    return file
# </Controller>


if __name__ == "__main__":
    # print("Starting by generating encodings for found images...")
    # Calculate known faces
    # faces_dict = get_faces_dict("/root/faces")

    # Start app
    print("Starting WebServer...")
    app.run(host='0.0.0.0', port=8081, debug=False)
