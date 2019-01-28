import os
from contextlib import contextmanager


@contextmanager
def chdir(directory):
    cwd = os.getcwd()
    try:
        os.chdir(os.path.expanduser(directory))
        yield
    finally:
        os.chdir(cwd)
