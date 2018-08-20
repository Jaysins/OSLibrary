from flask import Flask, render_template, request, url_for, redirect, jsonify
from flask_uploads import UploadSet, configure_uploads, AUDIO, UploadNotAllowed
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

media = UploadSet('media', AUDIO)

file_path = os.path.abspath(os.getcwd()) + "\service.db"

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + file_path
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['UPLOADED_MEDIA_DEST'] = 'static/media'

db = SQLAlchemy(app)

configure_uploads(app, media)


class Library(db.Model):
    """
    Library
    """
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), default='No Title')
    artist = db.Column(db.String(255), default='No Name')
    year = db.Column(db.String(8), default='Unknown')
    source = db.Column(db.String(255), nullable=False)


@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')


@app.route('/library')
def library():
    songs = Library.query.all()
    display = 'no'
    if len(songs) >= 1:
        display = 'yes'
    return render_template('download.html', songs=songs, display=display)


@app.route('/error/<message>')
def error_page(message):
    return render_template('error.html', message=message)


@app.route('/delete')
def delete():
    song_info = Library.query.filter_by(id=request.args['id']).first()
    os.remove(os.path.join(app.config['UPLOADED_MEDIA_DEST'], song_info.source))
    db.session.delete(song_info)
    db.session.commit()
    print('deleted')
    return jsonify({'response': 'deleted'})


@app.route('/edit/<int:info>', methods=['GET', 'POST'])
def edit(info):
    song_info = Library.query.filter_by(id=info).first()
    if request.method == 'POST':
        form = request.form

        print(form)
        song_info.title = 'No Title' if form['title'] == '' else form['title']
        song_info.artist = 'Unknown Artist' if form['artist'] == '' else form['artist']
        song_info.year = 'Unknown' if form['year'] == '' else form['year']
        db.session.commit()
        return redirect(url_for('library'))
    return render_template('edit.html', song=song_info)


@app.route('/add', methods=['GET', 'POST'])
def add():
    print('a')
    if request.method == 'POST':
        try:
            form = request.form
            filename = media.save(request.files['media'])
            new_file = Library(title='No Title' if form['title'] == '' else form['title'],
                               artist='Unknown Artist' if form['artist'] == '' else form['artist'],
                               year='Unknown' if form['year'] == '' else form['year'],
                               source=filename)
            db.session.add(new_file)
            db.session.commit()
            return redirect(url_for('library'))
        except UploadNotAllowed:
            message = 'invalid file'
            return redirect(url_for("error_page", message=message))

    return render_template('add.html')


if __name__ == '__main__':
    app.run(debug=True)
