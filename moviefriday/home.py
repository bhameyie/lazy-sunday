import logging

from flask import (
    Blueprint, render_template
)

from moviefriday.auth import login_required, no_auth_only
from moviefriday.db import get_db
from moviefriday.repositories import MovieRepository

LOG = logging.getLogger(__name__)

bp = Blueprint('home', __name__)


@bp.route('/')
@no_auth_only
def landing_page():
    return render_template('home/landing.html')


@bp.route('/home')
@login_required
def index():
    # todo: grab "featured" movies
    movie_repo = MovieRepository(get_db())
    movies = movie_repo.find_all(1, 10)
    return render_template('home/index.html', movies=movies)
