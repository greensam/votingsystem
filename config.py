import os
basedir = os.path.abspath(os.path.dirname(__file__))

WTF_CSRF_ENABLED = True
SECRET_KEY = 'this_is_CS51'

if os.environ.get('DATABASE_URL') is None:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
else:
    SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']

SQLALCHEMY_TRACK_MODIFICATIONS = True
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')


if os.environ.get('ADMIN_PW') is None:
	ADMIN_PW = 'secretBagMan'
else:
	ADMIN_PW = os.environ['ADMIN_PW']

if os.environ.get('BROTHER_PW') is None:
	BROTHER_PW = 'r0lltide'
else:
	BROTHER_PW = os.environ['BROTHER_PW']
