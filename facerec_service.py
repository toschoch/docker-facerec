import os

from facerec import facedb, dlib_api
from PIL import Image, ImageDraw
import numpy as np
from flask_wtf import FlaskForm
from flask_wtf.file import FileField

from flask import Flask, jsonify, request, flash, render_template, redirect, url_for
from flask_restful import reqparse, abort, Api, Resource
from wtforms import TextField


import utils

import uuid

# RESTful API
parser = reqparse.RequestParser(bundle_errors=True)
parser.add_argument('name', type=str, help="name must be a string", required=True)


# shows a list of all todos, and lets you POST to add new tasks
class Faces(Resource):
    def get(self):
        session = facedb.Session()
        faces = list(map(lambda p: {'person': utils.person_to_dict(p)}, facedb.persons(session)))
        session.close()
        return faces

class FaceIds(Resource):

    def _get_person_for_id(self, face_id):
        session = facedb.Session()
        return session.query(facedb.Person).filter(facedb.Person.id == face_id).first(), session

    def _get(self, p, session, msg):
        try:
            person = utils.person_to_dict(p)
        except AttributeError:
            abort(404, message=msg)
        finally:
            session.close()
        return person

    def _delete(self, p, session, msg):
        try:
            person = utils.person_to_dict(p)
            session.delete(p)
            session.commit()
        except AttributeError:
            abort(404, message=msg)
        finally:
            session.close()
        return

    def _patch(self, p, session, msg):
        args = parser.parse_args()
        try:
            p.name = args['name']
            session.commit()
            person = utils.person_to_dict(p)
        except AttributeError:
            abort(404, message=msg)
        finally:
            session.close()
        return person

    def get(self, face_id):
        p, session = self._get_person_for_id(face_id)
        msg = "Face with id '{}' doesn't exist".format(face_id)
        return self._get(p, session, msg)

    def delete(self, face_id):
        p, session = self._get_person_for_id(face_id)
        msg = "Face with id '{}' doesn't exist".format(face_id)
        return self._delete(p, session, msg)

    def patch(self, face_id):
        p, session = self._get_person_for_id(face_id)
        msg = "Face with id '{}' doesn't exist".format(face_id)
        return self._patch(p, session, msg)

class FaceNames(FaceIds):

    def _get_person_for_name(self, name):
        session = facedb.Session()
        return session.query(facedb.Person).filter(facedb.Person.name == name).first(), session

    def get(self, name):
        p, session = self._get_person_for_name(name)
        msg = "Face with name '{}' doesn't exist".format(name)
        return self._get(p, session, msg)

    def get(self, name):
        p, session = self._get_person_for_name(name)
        msg = "Face with name '{}' doesn't exist".format(name)
        return self._delete(p, session, msg)

    def patch(self, name):
        p, session = self._get_person_for_name(name)
        msg = "Face with name '{}' doesn't exist".format(name)
        return self._patch(p, session, msg)


parser_float= reqparse.RequestParser(bundle_errors=True)
parser_float.add_argument('value', type=float, help="threshold must be a float value", required=True)

class Config(Resource):
    def get(self):
        return {'threshold': facedb.get_distance_threshold()}

class Configs(Resource):

    def get(self, parameter):
        if parameter == 'threshold':
            return facedb.get_distance_threshold()
        # elif
        abort(404, message="No configuration parameter '{}' found".format(parameter))

    def patch(self, parameter):
        if parameter == 'threshold':
            args = parser_float.parse_args()
            facedb.set_distance_threshold(args['value'], persistent=True)
            return facedb.get_distance_threshold()
        # elif
        abort(404, message="No configuration parameter '{}' found".format(parameter))


def create_app():

    app = Flask(__name__)
    api = Api(app)

    api.add_resource(Config, '/config')
    api.add_resource(Configs, '/config/<string:parameter>')

    api.add_resource(Faces, '/faces')
    api.add_resource(FaceIds, '/faces/<int:face_id>')
    api.add_resource(FaceNames, '/faces/<string:name>')

    app.config.from_object(__name__)
    app.config['SECRET_KEY'] = '8da7a0d2-5cec-4cec-99e7-2979768dca67'

    # <Controller>
    @app.route('/image/teach', methods=['POST'])
    def image_teach():
        image = utils.extract_image(request)
        name, id = utils.extract_name_or_id(request)
        face = dlib_api.teach_person(np.array(image),name=name,id=id,weight=request.json.get('weight',1.0))
        return jsonify(utils.face_to_dict(face))

    @app.route('/image/identify', methods=['POST'])
    def image_identify():
        image = utils.extract_image(request)
        faces = dlib_api.detect_and_identify_faces(np.array(image))
        return jsonify(utils.faces_to_list(faces))

    @app.route('/facecode/teach', methods=['POST'])
    def code_teach():
        code = utils.extract_facecode(request)
        name, id = utils.extract_name_or_id(request)
        try:
            p = facedb.teach(code,name=name,id=id,weight=request.json.get('weight',1.0))
        except Exception as e:
            raise utils.BadRequest(str(e))
        return jsonify(utils.person_to_dict(p))

    @app.route('/facecode/identify', methods=['POST'])
    def code_identify():
        code = utils.extract_facecode(request)
        p = facedb.identify_person(code)
        return jsonify(utils.person_to_dict(p))

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
                file = request.files['file']
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

    @app.errorhandler(utils.BadRequest)
    def handle_invalid_usage(error):
        response = jsonify(error.to_dict())
        response.status_code = error.status_code
        return response

    return app

if __name__ == "__main__":

    import logging
    logging.basicConfig(level=logging.INFO)

    # set database path to data dir
    datapath = os.path.join(os.path.split(__file__)[0], 'data')
    os.makedirs(datapath, exist_ok=True)
    facedb.set_db_path(datapath, persistent=True)
    logging.info("facedb database: {} containes {} persons...".format(facedb.get_db_file().absolute(),
                                                                      len(facedb.persons())))

    # Start app
    print("Starting WebServer...")
    app = create_app()
    app.run(host='0.0.0.0', port=80, debug=False)
