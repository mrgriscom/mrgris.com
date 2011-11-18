from fabric.api import *
from fabric.context_managers import lcd, settings
import os.path

# args: staging?

DJANGO_APPS = [
    ('minesweepr/web_demo', 'projects/minesweepr/demo')
]

def compile():
    clean()

    with _cd():
        # django
        for django_root, static_root in DJANGO_APPS:
            with _cd(os.path.join('lib/app', django_root)):
                with open('localsettings.py', 'w') as f:
                    f.write('STATIC_ROOT = "%s"\n' % abspath('content', static_root))
                local('python manage.py collectstatic --noinput')

        local('nanoc compile', capture=False)

def clean():
    with _cd():
        with settings(warn_only=True):
            # django
            for django_root, static_root in DJANGO_APPS:
                local('rm -r %s' % os.path.join('content', static_root, '*'))

            # don't remove output/ itself, to keep adsf happy
            local('rm -r output/* tmp/')

def deploy():
    #rsync static
    #deploy django?
    pass






from contextlib import contextmanager, nested

def rootdir():
    return os.path.dirname(__file__)

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

