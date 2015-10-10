from fabric.api import *
import os
from os.path import join, dirname, abspath
import time
from datetime import datetime

env.use_ssh_config = True

def setup_development_environment():
    with lcd(dirname(abspath(__file__))):
        local('sudo pip install virtualenvwrapper')
        with prefix('source `which virtualenvwrapper.sh`'):
            local('mkvirtualenv -p `which python2.7` teamlunch.info')
            with prefix('workon teamlunch.info'):
                local('pip install -r development_requirements.txt')
                local('python manage.py migrate')
                print("\n\n**************")
                print("\nCreating an administrative user")
                local('python manage.py createsuperuser')
    print("\n\n**************")
    print("To work on this project, perform the following command line:")
    print("$> source /usr/local/virtualenvwrapper.sh")
    print("$> workon teamlunch.info")

def cleanup_development_environment():
    with prefix('source `which virtualenvwrapper.sh`'):
        local('rmvirtualenv teamlunch.info')

def deploy():
    run_tests()
    update_requirements()
    with cd('/var/www/teamlunch.info'):
        run('git pull -Xours')
        run('mkdir -p logs')
        run('chmod -R g+w logs')
        with prefix('source /usr/share/virtualenvwrapper/virtualenvwrapper.sh'):
            with prefix('workon teamlunch.info'):
                run('pip install -r production_requirements.txt')
                run('python manage.py migrate')
                run('chmod g+w .')
                run('chmod g+w db.sqlite3')
                run('cp ~/teamlunch.info/production_settings.py teamlunch/settings.py')

def run_tests():
    with prefix('source `which virtualenvwrapper.sh`'):
        with prefix('workon teamlunch.info'):
            local('python manage.py test')

def update_requirements():
    with prefix('source `which virtualenvwrapper.sh`'):
        with prefix('workon teamlunch.info'):
            local('pip freeze > development_requirements.txt')
            local('pip freeze > production_requirements.txt')
