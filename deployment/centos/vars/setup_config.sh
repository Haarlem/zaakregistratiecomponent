# The project path is also in the configuration files. If this path is changed,
# changes should also be made in those files.
#
# See: nginx.conf
# See: supervisor.ini

# Basics
#
# To name config files appropriatly.
PROJECT_NAME=zaakmagazijn
# The path where the project is installed.
PROJECT_PATH=/var/sites/$PROJECT_NAME
# This will be passed to "git clone -b $BRANCH $REPO".
REPO=https://github.com/Haarlem/zaakregistratiecomponent.git
BRANCH=master
# Available options are: dev, staging, production
TARGET=staging
# Django project settings.
SETTINGS=zaakmagazijn.conf.$TARGET

# Database
#
# Leave empty to skip database installation.
DB_NAME=$PROJECT_NAME
DB_USERNAME=$DB_NAME


