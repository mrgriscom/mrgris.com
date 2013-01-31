
class HgRepo(object):
    
    @staticmethod
    def update_to_latest(exec_):
        exec_('hg pull')
        exec_('hg update')

class GitRepo(object):
    
    @staticmethod
    def update_to_latest(exec_):
        exec_('git checkout master')
        exec_('git pull')
