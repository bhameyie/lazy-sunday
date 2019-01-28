# Video content range logic taken from https://github.com/go2starr/py-flask-video-stream

from bson import ObjectId
from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for,
    Response)
from werkzeug.exceptions import abort

import mimetypes
import re

from moviefriday.repositories import Movie
from .auth import login_required
from .db import get_db
import os
import logging

LOG = logging.getLogger(__name__)

bp = Blueprint('watch', __name__)

MB = 1 << 20
BUFF_SIZE = 10 * MB


@login_required
@bp.route('/')
def index():
    db = get_db()
    fakeMovie = Movie(title="Bunny", blob_id='BigBuckBunny.mp4',
                      is_mp4=True, id='ssds')
    return render_template('watch/index.html', movie=fakeMovie)


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
