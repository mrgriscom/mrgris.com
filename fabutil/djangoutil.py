import sys
from django.core.management import setup_environ
from contextlib import contextmanager
import tempfile
import glob
import re
import os
import os.path
from fabric.api import *
from util import *
from util import _cd


def no_leading_slash(url):
    return url[1:] if url.startswith('/') else url


class DjangoProject(object):
    def __init__(self, name, reporoot, contentroot):
        self.name = name

        # path of the django project repo, relative to nanoc root
        self.reporoot = reporoot

        # path of static pages, relative to nanoc content root
        self.contentroot = contentroot

        self.template_override_dir = tempfile.mkdtemp()

    def repopath(self):
        """path of repository, relative to nanoc root"""
        return os.path.join('lib/app', self.reporoot)

    def contentpath(self):
        """absolute path of static pages"""
        return abspath('content', self.contentroot)

    def contenturl(self):
        """url of static pages"""
        return '/%s/' % self.contentroot

    def staticpath(self):
        """absolute path of static media"""
        return abspath('content/app-static', self.name)

    # TODO: attempt to change this?
    def staticurl(self):
        """url of static media"""
        return '/app-static/%s/' % self.name

    def appurl(self):
        """url of dynamic requests (ajax/django)"""
        return '/app/%s/' % self.name

    def renderdir(self):
        """dest path of rendered pages"""
        return abspath('layouts/app', self.name)

    def static_pages(self):
        """search for all pages for which a static version of the django page will be rendered"""
        return [f[:-len('.html')] for f in os.listdir(self.contentpath()) if f.endswith('.html')]

    def project_context(self):
        return _cd(self.repopath())

    def localsettings(self):
        return [
            ('BASE_URL', no_leading_slash(self.appurl())),
            ('BASE_STATIC_URL', no_leading_slash(self.contenturl())),
            ('STATIC_ROOT', self.staticpath()),
            ('STATIC_URL', self.staticurl()),
            ('TEMPLATE_DIRS', (self.template_override_dir,)),
        ]

    def write_localsettings(self, f):
        for name, val in self.localsettings():
            f.write('%s = %s\n' % (name, repr(val)))

    def render_static(self, rule_buffer):
        for page in self.static_pages():
            self._render_static(page, rule_buffer)

    # requires project_context
    def _render_static(self, pagename, rule_buffer):
        self.override_template(pagename)

        page_url = '%s%s/' % (self.contenturl(), pagename)
        page_dst_path = os.path.join(self.renderdir(), '%s.html' % pagename)
        django_dump(page_url, page_dst_path)

        rule_buffer.add((self, pagename))

    def override_template(self, pagename):
        with open(os.path.join(self.template_override_dir, '%s.html' % pagename), 'w') as f:
            f.write('{%% extends "_%s.html" %%}\n' % pagename)

            for blockname in get_blocks(pagename):
                if blockname == 'main':
                    inner = 'yield'
                else:
                    content = blockname.startswith('content_')
                    inner = '@item[:%s%s]' % (
                        'content_for_' if content else '',
                        blockname[len('content_') if content else 0:]
                    )

                f.write('{%% block %s %%}\n' % blockname)
                f.write('<%%= %s %%>\n' % inner)
                f.write('{% endblock %}\n')

    def mk_rule(self, pagename):
        return """
compile '%s%s/' do
  filter :erb
  layout '%s'
end
        """ % (self.contenturl(), pagename, os.path.join(os.path.relpath(self.renderdir(), abspath('layouts')), pagename))

    def compile(self, rule_buffer):
        with self.project_context():
            with open('localsettings.py', 'w') as f:
                self.write_localsettings(f)

            local('python manage.py collectstatic --noinput')
            self.render_static(rule_buffer)

    def clean(self):
        local('rm %s' % os.path.join(self.repopath(), 'localsettings.py*'))
        local('rm -r %s' % self.renderdir())
        


def django_dump(url, path):
    with django_env():
        from django.test.client import Client
        c = Client()
        response = c.get(url)

        os.makedirs(os.path.dirname(path))
        with open(path, 'w') as f:
            f.write(response.content)

def get_blocks(pagename):
    template_path = glob.glob('*/templates/_%s.html' % pagename)[0]
    with open(template_path) as f:
        template = f.read()
    BLOCK_TAG = '\{% *block +(?P<id>[a-zA-Z0-9_]+) *%\}'
    return [m.group('id') for m in re.finditer(BLOCK_TAG, template)]

@contextmanager
def rule_aggregator():
    rules = set()
    try:
        yield rules
    finally:
        with open('Rules', 'w') as f:
            for app, page in rules:
                f.write(app.mk_rule(page))
            f.write('\n\n')

@contextmanager
def django_env():
    sys.path.insert(0, os.getcwd())
    import settings as djsettings
    setup_environ(djsettings)
    try:
        yield
    finally:
        sys.path.pop(0)

