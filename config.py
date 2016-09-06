import os
basedir = os.path.abspath(os.path.dirname(__file__))

if not os.environ.get('SECRET') is None:
	SECRET_KEY = os.environ['SECRET']
else:
	print "Environment Variable Not Found: SECRET"
	exit(1)

if os.environ.get('DATABASE_URL') is None:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
else:
    SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']

SQLALCHEMY_TRACK_MODIFICATIONS = True
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')


if not os.environ.get('ADMIN_PW') is None:
	ADMIN_PW = os.environ['ADMIN_PW']
else:
	print "Environment Variable Not Found: ADMIN_PW"
	exit(1)

if not os.environ.get('BROTHER_PW') is None:
	BROTHER_PW = os.environ['BROTHER_PW']
else:
	print "Environment Variable Not Found: BROTHER_PW"
	exit(1)
