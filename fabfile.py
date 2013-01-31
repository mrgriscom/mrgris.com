from fabric.api import *
from fabric.context_managers import settings
from fabutil.util import _cd
from fabutil.djangoutil import DjangoProject, rule_aggregator
from fabric.contrib.project import rsync_project

DJANGO_APPS = [
    DjangoProject(
        'minesweepr',
        'minesweepr/web_demo',
        'projects/minesweepr/demo',
        'git',
    ),
]

def compile():
    clean()

    with _cd():
        with rule_aggregator() as ragg:
            for app in DJANGO_APPS:
                app.compile(ragg)

        local('cat _Rules >> Rules')
        local('nanoc compile', capture=False)

def clean():
    with _cd():
        with settings(warn_only=True):
            for app in DJANGO_APPS:
                app.clean()
            local('rm -r content/app-static/')

            local('rm Rules')

            # don't remove output/ itself, to keep adsf happy
            local('rm -r output/* tmp/')

def deploy():
    with _cd():
        WWW_ROOT = '/var/www'
        WWW_EXCL = ['a']
        rsync_project(WWW_ROOT, 'output/', delete=True, exclude=WWW_EXCL)

        VGM_ROOT = '/home/drew/vgm'
        VGM_LOCAL_ROOT = '/data/music/vgm/'
        rsync_project(VGM_ROOT, local_dir=VGM_LOCAL_ROOT, delete=True)

        WEBAPP_USER = 'webapp'
        for app in DJANGO_APPS:
            app.deploy(WEBAPP_USER)
        
        # nginx does not need restart

def refresh():
    with _cd():
        for app in DJANGO_APPS:
            app.refresh()

    local('gpg --refresh-keys')

def prod():
    env.user = 'drew'
    env.hosts = ['mrgris.com']
