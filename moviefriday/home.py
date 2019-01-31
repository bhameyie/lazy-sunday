import logging

from flask import (
    Blueprint, render_template
)

from moviefriday.auth import login_required, no_auth_only

LOG = logging.getLogger(__name__)

bp = Blueprint('home', __name__)


@bp.route('/')
@no_auth_only
def landing_page():
    return render_template('home/landing.html')


@bp.route('/home')
@login_required
def index():
    return render_template('home/index.html')
