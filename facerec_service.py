import os

from facerec import facedb, dlib_api
from PIL import Image, ImageDraw
import numpy as np
from flask_wtf import FlaskForm
from flask_wtf.file import FileField
from flask import Flask, jsonify, request, flash, render_template, redirect, url_for
from wtforms import TextField
from werkzeug.exceptions import BadRequest
import json

import utils

import uuid

# Create flask app
app = Flask(__name__)

app.config.from_object(__name__)
app.config['SECRET_KEY'] = '8da7a0d2-5cec-4cec-99e7-2979768dca67'

# set database path to data dir
facedb.set_db_path(os.path.join(os.path.split(__file__)[0],'data'))

# <Controller>

@app.route('/image/teach', methods=['POST'])
def image_teach():
    file = utils.extract_image(request)
    name, id = utils.extract_name_or_id(request)
    image = Image.open(file.stream, 'r').convert('RGB')
    face = dlib_api.teach_person(image,name=name,id=id,weight=request.args.get('weight',1.0))
    return jsonify(utils.face_to_dict(face))

@app.route('/image/identify', methods=['POST'])
def image_identify():
    file = utils.extract_image(request)
    image = Image.open(file.stream, 'r').convert('RGB')
    faces = dlib_api.detect_and_identify_faces(np.array(image))
    return jsonify(utils.faces_to_list(faces))

@app.route('/facecode/teach', methods=['POST'])
def code_teach():
    code = utils.extract_facecode(request)
    name, id = utils.extract_name_or_id(request)
    p = facedb.teach(code,name=name,id=id,weight=request.args.get('weight',1.0))
    return jsonify(utils.person_to_dict(p))

@app.route('/facecode/identify', methods=['POST'])
def code_identify():
    code = utils.extract_facecode(request)
    p = facedb.identify_person(code)
    return jsonify(utils.person_to_dict(p))

@app.route('/faces', methods=['GET', 'DELETE'])
def faces():
    # GET
    if request.method == 'GET':
        return jsonify(list(map(utils.person_to_dict,facedb.persons())))
    elif request.method == 'DELETE':
        name, id = utils.extract_name_or_id(request)
        session = facedb.Session()
        person = facedb.get_person(name=name, id=id, session=session)
        session.delete(person)
        session.commit()
        return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}

    # Web App
class IdentifyForm(FlaskForm):
    file = FileField('File', validators=[])

class TeachForm(FlaskForm):
    file = FileField('File', validators=[])
    name = TextField('Name', validators=[])
    id = TextField('ID', validators=[])

@app.route('/', methods=['GET', 'POST'])
@app.route('/identify', methods=['GET', 'POST'])
def web_identify():

    form = IdentifyForm(request.form)

    if request.method=='POST':
        if len(request.files)>0:
            file = utils.extract_image(request)

            if utils.is_picture(file.filename):
                try:
                    pilimage = Image.open(file.stream, 'r').convert('RGB')
                except Exception as e:
                    flash("Error: {}".format(e))
                    return render_template('identify.html', form=form)

                try:
                    faces = dlib_api.detect_and_identify_faces(np.array(pilimage))
                except Exception as e:
                    flash("Error: {}".format(e))
                    return render_template('identify.html', form=form)

                font = utils.get_font(1024)

                draw = ImageDraw.Draw(pilimage)
                for p, rect, shape in faces:
                    s = font.getsize(p.name)
                    utils.draw_rectangle(draw, rect, 5, color=128)
                    draw.text(((rect.right()-rect.left())/2+rect.left()-int(s[0]/2), rect.top()-s[1]-20),p.name, fill=128, font=font)
                del draw

                tmpfile = os.path.join('static/tmp','{}.jpg'.format(uuid.uuid4()))

                # resize
                pilimage = utils.resize_image(pilimage, 1024)


                with open(tmpfile, 'wb+') as fp:
                    pilimage.save(fp, 'JPEG')

                flash('found {} faces... '.format(len(faces)) +
                      '\n'.join(("id: {}, name: {}".format(p.id, p.name) for p,_,_ in faces)))

                return render_template('identify.html', form=form, proc_image=tmpfile)

            else:
                flash('Error: Only images allowed!')
        else:
            flash('Error: All the form fields are required. ')

    return render_template('identify.html', form=form)

@app.route("/teach", methods=['GET', 'POST'])
def web_teach():
    form = TeachForm(request.form)

    if request.method=='POST':
        if len(request.files)>0:
            file = request.files['file']

            if utils.is_picture(file.filename):
                pilimage = Image.open(file.stream, 'r')
                try:
                    face = dlib_api.teach_person(np.array(pilimage),name=form.name.data,id=form.id.data)
                    flash("Tought this face!")
                except Exception as e:
                    flash("Error: {}".format(e))

            else:
                flash('Error: Only images allowed!')
        else:
            flash('Error: All the form fields are required. ')

    return render_template('teach.html', form=form)


if __name__ == "__main__":

    # Start app
    print("Starting WebServer...")
    app.run(host='0.0.0.0', port=80, debug=False)
