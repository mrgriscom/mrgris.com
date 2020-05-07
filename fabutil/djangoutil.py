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
from repo import *
from fabric.context_managers import cd

def no_leading_slash(url):
    return url[1:] if url.startswith('/') else url


class DjangoProject(object):
    def __init__(self, name, reporoot, contentroot, dvcs=None):
        self.name = name

        # path of the django project repo, relative to nanoc root
        self.reporoot = reporoot

        # path of static pages, relative to nanoc content root
        self.contentroot = contentroot

        self.template_override_dir = tempfile.mkdtemp()

        for dirname, handler in (('hg', HgRepo), ('git', GitRepo)):
            if dirname == dvcs or os.path.exists(os.path.join(self.repopath(), '.%s' % dirname)):
                self.dvcs = handler()
                break

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

    def deploydir(self):
        """path where repo is deployed on server"""
        return os.path.join('/var/webapp', self.reporoot)

    def static_pages(self):
        """search for all pages for which a static version of the django page will be rendered"""
        return [f[:-len('.html')] for f in os.listdir(self.contentpath()) if f.endswith('.html')]

    def project_context(self):
        return _cd(self.repopath())

    def localsettings(self, deploy):
        settings = [
            ('BASE_URL', no_leading_slash(self.appurl())),
            ('BASE_STATIC_URL', no_leading_slash(self.contenturl())),
            ('STATIC_ROOT', self.staticpath()),
        ]
        if deploy:
            settings.extend([
                ('LOGGING', self.deployment_logging_config()),
            ])
        else:
            settings.extend([
                ('STATIC_URL', self.staticurl()),
                ('TEMPLATE_DIRS', (self.template_override_dir,)),
            ])
        return settings

    def deployment_logging_config(self):
        return {
            'version': 1,
            'formatters': {
                'default': {
                    'format': '%(asctime)s:%(levelname)s:%(message)s'
                    },
                },
            'handlers': {
                'file': {
                    'class': 'logging.handlers.RotatingFileHandler',
                    'formatter': 'default',
                    'filename': os.path.join('/var/log/webapp', '%s.log' % self.name),
                    'maxBytes': 2**24,
                    'backupCount': 3,
                    },
                },
            'root': {
                'level': 'INFO',
                'handlers': ['file'],
                },
            }

    def write_localsettings(self, f, deploy=False):
        for name, val in self.localsettings(deploy):
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
        base = get_base_template(pagename)
        with open(os.path.join(self.template_override_dir, '%s.html' % pagename), 'w') as f:
            f.write('{%% extends "%s.html" %%}\n' % base)

            for blockname in get_blocks(base):
                if blockname == 'main':
                    inner = 'yield'
                else:
                    if blockname.startswith('content_'):
                        inner = 'content_for(@item, :%s)' % blockname[len('content_'):]
                    else:
                        inner = '@item[:%s]' % blockname

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

    def pull_latest(self, user):
        with cd(self.deploydir()):
            self.dvcs.update_to_latest(lambda cmd: sudo(cmd, user=user))

    def deploy_localsettings(self, user=None):
        fd, tmppath = tempfile.mkstemp()
        with os.fdopen(fd, 'w') as f:
            self.write_localsettings(f, True)
        remotepath = os.path.join(self.deploydir(), 'localsettings.py')
        put(tmppath, remotepath, use_sudo=True)
        if user:
            sudo('chown %s %s' % (user, remotepath))

    def restart_wsgi(self):
        sudo('service %s restart' % self.name)

    def compile(self, rule_buffer):
        with self.project_context():
            with open('localsettings.py', 'w') as f:
                self.write_localsettings(f)

            local('python manage.py collectstatic --noinput')
            self.render_static(rule_buffer)

    def clean(self):
        local('rm %s' % os.path.join(self.repopath(), 'localsettings.py*'))
        local('rm -r %s' % self.renderdir())
        
    def deploy(self, user):
        self.pull_latest(user)
        self.deploy_localsettings(user)
        self.restart_wsgi()

    def refresh(self):
        with self.project_context():
            self.dvcs.update_to_latest(lambda cmd: local(cmd))

def django_dump(url, path):
    with django_env():
        from django.test.client import Client
        c = Client()
        response = c.get(url)

        mkdirs(path)
        with open(path, 'w') as f:
            f.write(response.content)

def get_base_template(pagename):
    template_path = glob.glob('*/templates/%s.html' % pagename)[0]
    with open(template_path) as f:
        template = f.read()
    EXT_TAG = '\{% *extends +"(?P<id>[a-zA-Z0-9_]+).html" *%\}'
    return re.search(EXT_TAG, template).group('id')
            
def get_blocks(pagename):
    template_path = glob.glob('*/templates/%s.html' % pagename)[0]
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


