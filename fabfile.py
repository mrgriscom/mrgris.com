from fabric.api import *
from fabric.context_managers import settings
from fabutil.util import _cd
from fabutil.djangoutil import DjangoProject, rule_aggregator


DJANGO_APPS = [
    DjangoProject(
        'minesweepr',
        'minesweepr/web_demo',
        'projects/minesweepr/demo',
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
    #rsync static
    #deploy django?
    pass

def refresh():
    pass
