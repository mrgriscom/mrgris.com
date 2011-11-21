from fabric.api import *
from fabric.context_managers import lcd, settings
import os.path

class AjaxDjangoProject(object):
    def __init__(self, reporoot, staticroot, dynroot, static_pages):
        # path of the django project repo, relative to nanoc root
        self.reporoot = reporoot
        # path of static content, relative to nanoc content root
        # (and therefore, relative base url of content)
        self.staticroot = staticroot
        # base url for dynamic (ajax/django) requests
        self.dynroot = dynroot
        # list of static pages to generate
        self.static_pages = static_pages

    def repopath(self):
        return os.path.join('lib/app', self.reporoot)

    def staticpath(self):
        return abspath('content', self.staticroot)

    def staticurl(self):
        return '/%s/' % self.staticroot

    def dynurl(self):
        return '/%s/' % self.dynroot

    def project_context(self):
        return _cd(self.repopath())

    def write_localsettings(self, f):
        def no_leading_slash(url):
            return url[1:] if url.startswith('/') else url

        settings = [
            ('BASE_URL', no_leading_slash(self.dynurl())),
            ('BASE_STATIC_URL', no_leading_slash(self.staticurl())),
            ('STATIC_ROOT', self.staticpath()),
            ('STATIC_URL', self.staticurl()),
        ]

        for name, val in settings:
            f.write('%s = %s\n' % (name, repr(val)))

    def render_static(self):
        for page in self.static_pages:
            self._render_static(page)

    def _render_static(self, pagename):
        page_url = '%s%s/' % (self.staticurl(), pagename)
        page_dst_path = os.path.join(self.staticpath(), '%s.html' % pagename)

        # requires project_context
        django_dump(page_url, page_dst_path)

    def compile(self):
        with self.project_context():
            with open('localsettings.py', 'w') as f:
                self.write_localsettings(f)
            local('python manage.py collectstatic --noinput')
            self.render_static()

    def clean(self):
        local('rm -r %s' % os.path.join(self.staticpath(), '*'))
        local('rm %s' % os.path.join(self.repopath(), 'localsettings.py*'))

        

DJANGO_APPS = [
    AjaxDjangoProject(
        'minesweepr/web_demo',
        'projects/minesweepr/demo',
        'app/minesweepr',
        ['player', 'query']
    ),
]

def compile():
    clean()

    with _cd():
        for app in DJANGO_APPS:
            app.compile()

        local('nanoc compile', capture=False)

def clean():
    with _cd():
        with settings(warn_only=True):
            for app in DJANGO_APPS:
                app.clean()

            # don't remove output/ itself, to keep adsf happy
            local('rm -r output/* tmp/')

def deploy():
    #rsync static
    #deploy django?
    pass

def refresh():
    pass








def django_dump(url, path):
    with django_env():
        from django.test.client import Client
        c = Client()
        response = c.get(url)
        with open(path, 'w') as f:
            f.write(response.content)

from contextlib import contextmanager, nested
import sys
from django.core.management import setup_environ

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

@contextmanager
def django_env():
    sys.path.insert(0, os.getcwd())
    import settings as djsettings
    setup_environ(djsettings)
    try:
        yield
    finally:
        sys.path.pop(0)
