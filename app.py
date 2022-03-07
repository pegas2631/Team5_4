import os
import traceback

from flask import Flask, render_template, url_for, request, redirect, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from os.path import join, dirname, realpath

from werkzeug.utils import secure_filename

PASSWORD = 'qwe'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'TIF', 'tiff', 'txt'])
ABS_FOLDER = dirname(realpath(__file__))
UPLOAD_FOLDER_REL = 'data/screens'  # сохраненные снимки

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///team5_test_1.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = join(ABS_FOLDER, UPLOAD_FOLDER_REL)
db = SQLAlchemy(app)


class Screen(db.Model):
    ID = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String(80), nullable=False)
    PhotoSrc = db.Column(db.String(200), nullable=False)
    NDVISrc = db.Column(db.String(200))
    NDTISrc = db.Column(db.String(200))
    IRSrc = db.Column(db.String(200))
    Date = db.Column(db.DateTime, default=datetime.utcnow)
    Latitude = db.Column(db.String(50))
    Longitude = db.Column(db.String(50))

    def __repr__(self):
        return '<Screen %r>' % self.id


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@app.route('/')
@app.route('/home')
def index():
    return render_template("index.html")


@app.route('/about')
def about():
    return render_template("about.html")


@app.route('/photo', methods=['POST', 'GET'])
def photo():
    if request.method == "POST":
        form_photo = request.files['file']
        if form_photo and allowed_file(form_photo.filename):
            filename = secure_filename(form_photo.filename)
            path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            form_photo.save(path)  # 'data/screens' сохраненные снимки

        form_name = request.form['name']
        form_lat = request.form['lat']
        form_long = request.form['long']

        if request.form['date']:
            form_date = datetime.strptime(request.form['date'], '%Y-%m-%d')
            screen = Screen(Name=form_name, Date=form_date, PhotoSrc=filename, Latitude=form_lat, Longitude=form_long)
        else:  # для пустых дат
            screen = Screen(Name=form_name, PhotoSrc=filename, Latitude=form_lat, Longitude=form_long)

        try:
            db.session.add(screen)
            db.session.commit()
            return render_template("screen_page.html", screen=screen)
            # переброс на страницу снимка
            # различные обработки на ней
        except Exception as e:
            return 'Ошибка:\n', traceback.format_exc()
    else:
        return render_template("photo.html ")


@app.route('/gallery')
def gallery():
    # screens = Screen.query.first()
    screens = Screen.query.order_by(Screen.Date.desc()).all()
    return render_template("gallery.html", screens=screens)


@app.route('/gallery/procScreen')  # страница ожидания для обработки снимка
def screen_processing():
    return "Пока не реализовано"


@app.route('/gallery/procScreen/<int:id>')  # страница снимка
def processed_screen(id):
    screen = Screen.query.get(id)
    return render_template("screen_page.html", screen=screen)


@app.route('/photo/update/<int:id>/<string:password>', methods=['POST', 'GET'])
def update_screen(id, password):
    if password == PASSWORD:
        if request.method == "POST":
            screen = Screen.query.get(id)

            form_photo = request.files['file']
            if form_photo and allowed_file(form_photo.filename):
                filename = secure_filename(form_photo.filename)
                path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                form_photo.save(path)  # 'data/screens' сохраненные снимки
                screen.PhotoSrc = filename
            screen.Name = request.form['name']
            screen.Latitude = request.form['lat']
            screen.Longitude = request.form['long']
            if request.form['date']:
                screen.Date = datetime.strptime(request.form['date'], '%Y-%m-%d')

            try:
                db.session.commit()
                return render_template("screen_page.html", screen=screen)
            except Exception as e:
                return 'Ошибка:\n', traceback.format_exc()

        else:
            screen = Screen.query.get(id)
            return render_template("update_photo.html", screen=screen)
    else:
        return 'Нет доступа'


@app.route('/gallery/procScreen/<int:id>/delete/<string:password>')
def delete_screen(id, password):
    if password == PASSWORD:
        try:
            screen = Screen.query.get_or_404(id)
            db.session.delete(screen)
            db.session.commit()
            return redirect('/gallery')
        except:
            return 'При удалении произошла ошибка'
    else:
        return 'Нет доступа'


@app.route('/user/<string:name>/<int:id>')  # example
def user(name, id):
    return "user page: " + name + " - " + str(id)


@app.route('/data/<path:filename>')  # раздача файлов из директории data
def serve_static(filename):
    return send_from_directory("data/", filename)


if __name__ == '__main__':
    app.run(debug=True)
