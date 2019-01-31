# Video content range logic taken from https://github.com/go2starr/py-flask-video-stream

import logging
import mimetypes
import os
import re

from flask import (
    Blueprint, render_template, request, Response, flash, redirect
)

from moviefriday.repositories import Movie, MovieRepository
from moviefriday.auth import login_required
from moviefriday.db import get_db

LOG = logging.getLogger(__name__)

bp = Blueprint('watch', __name__)

MB = 1 << 20
BUFF_SIZE = 10 * MB


@login_required
@bp.route('/watch/vids/<movie_id>')
def screen_it(movie_id):
    movie_repo = MovieRepository(get_db())
    movie = movie_repo.find_by_id(movie_id)
    if movie is None:
        flash('Requested movie not found')
        return redirect(request.url)

    return render_template('watch/index.html', movie=movie)


def partial_response(path, start, end=None):
    LOG.info('Requested: %s, %s', start, end)
    file_size = os.path.getsize(path)

    # Determine (end, length)
    if end is None:
        end = start + BUFF_SIZE - 1
    end = min(end, file_size - 1)
    end = min(end, start + BUFF_SIZE - 1)
    length = end - start + 1

    # Read file
    with open(path, 'rb') as fd:
        fd.seek(start)
        bytes = fd.read(length)
    assert len(bytes) == length

    response = Response(
        bytes,
        206,
        mimetype=mimetypes.guess_type(path)[0],
        direct_passthrough=True,
    )
    response.headers.add(
        'Content-Range', 'bytes {0}-{1}/{2}'.format(
            start, end, file_size,
        ),
    )
    response.headers.add(
        'Accept-Ranges', 'bytes'
    )
    LOG.info('Response: %s', response)
    LOG.info('Response: %s', response.headers)
    return response


def get_range(request):
    content_range = request.headers.get('Range')
    LOG.info('Requested: %s', content_range)
    m = re.match('bytes=(?P<start>\d+)-(?P<end>\d+)?', content_range)
    if m:
        start = m.group('start')
        end = m.group('end')
        start = int(start)
        if end is not None:
            end = int(end)
        return start, end
    else:
        return 0, None


@bp.route('/vids/<movie_id>/mp4')
@login_required
def mp4_video(movie_id):
    # validate movie exists and movie is_mp4

    movie = Movie(title="Bunny", blob_id='BigBuckBunny.mp4',
                  is_mp4=True, id='dssd')
    file_path = os.path.join(os.getcwd(), 'mp4_stash', movie.blob_id)
    start, end = get_range(request)
    return partial_response(file_path, start, end)
