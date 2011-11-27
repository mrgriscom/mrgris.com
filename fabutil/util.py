from fabric.api import env
from fabric.context_managers import lcd
import os.path
import os
from contextlib import contextmanager, nested

def rootdir():
    return os.path.dirname(env.real_fabfile)

def abspath(*paths):
    return os.path.join(rootdir(), *paths)

@contextmanager
def chdir(dir):
    cwd = os.getcwd()
    os.chdir(dir)
    try:
        yield
    finally:
        os.chdir(cwd)

def _cd(dir=None):
    dir = dir or rootdir()
    return nested(chdir(dir), lcd(dir))

def mkdirs(path):
    dir = os.path.dirname(path)
    if not os.path.isdir(dir):
        os.makedirs(dir)
