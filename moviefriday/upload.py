import os

import flask
from flask import (
    Blueprint, flash, redirect, render_template, request, url_for, current_app,
    Flask)
from werkzeug.utils import secure_filename

from moviefriday import vidconvert
from moviefriday.auth import login_required
from moviefriday.db import get_db
from moviefriday.repositories import Movie, MovieRepository
import logging

ALLOWED_MOVIE_EXTENSIONS = ['mp4']

bp = Blueprint('upload', __name__)


@bp.route('/movies/uploaded/<movie_id>')
def uploaded_movie(movie_id):
    movie_repo = MovieRepository(get_db())
    movie = movie_repo.find_by_id(movie_id)
    return render_template('upload/movie_uploaded.html', movie=movie)


@bp.route('/movies/upload', methods=['GET', 'POST'])
@login_required
def upload_file():
    if request.method == 'POST':
        print(request.form)
        movie_title = request.form['title']
        force_replace = 'forceReplace' in request.form

        print('Dealing wth POST')

        if not movie_title:
            flash('Movie title required')
            return redirect(request.url)

        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)

        file = request.files['file']

        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)

        if file and _allowed_file(file.filename):
            return _upload_movie(file, force_replace, movie_title)
        else:
            flash('File not allowed. Please ensure it is an MP4 file')
            return redirect(request.url)

    return render_template('upload/movie_upload.html')


def _allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_MOVIE_EXTENSIONS


def _upload_movie(file, force_replace, movie_title):
    movie_repo = MovieRepository(get_db())
    filename = secure_filename(file.filename)
    filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    movie_id = ''

    if 'convert' in request.form:
        model = vidconvert.make_default_req(filename, filepath)
        conversion = vidconvert.convert_mp4(model, force_replace)

        if conversion["succeeded"]:
            new_movie = Movie(title=movie_title, blob_id=filename, is_mp4=False)
            movie_id = movie_repo.insert(new_movie)
        else:
            os.remove(filepath)
            flash(conversion['reason'])
            return redirect(request.url)
    else:
        new_movie = Movie(title=movie_title, blob_id=filename, is_mp4=True)
        movie_id = movie_repo.insert(new_movie)

    return redirect(url_for('uploaded_movie', movie_id=movie_id))
