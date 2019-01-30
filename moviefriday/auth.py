import functools

from bson import ObjectId
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from moviefriday.db import get_db
from moviefriday.repositories import UserRepository, User

bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        user_repository = UserRepository(get_db())
        username = request.form['username']
        password = request.form['password']
        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'
        elif user_repository.find_by_username(username) is not None:
            error = 'User {} is already registered.'.format(username)

        if error is None:
            user_repository.insert(User(username=username, password=generate_password_hash(password)))
            return redirect(url_for('auth.login'))

        flash(error)

    return render_template('auth/register.html')


@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        user_repository = UserRepository(get_db())
        username = request.form['username']
        password = request.form['password']
        error = None
        user = user_repository.find_by_username(username)

        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user.password, password):
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['user_id'] = str(user.id)
            return redirect(url_for('watch.index'))

        flash(error)

    return render_template('auth/login.html')


@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('watch.index'))


@bp.before_app_request
def load_logged_in_user():
    user_repository = UserRepository(get_db())
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = user_repository.find_by_id(user_id)


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view
