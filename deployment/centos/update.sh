#!/bin/bash
source vars/setup_config.sh

CWD=`pwd`
NOW=$(date +"%Y-%m-%d")
SETUP_LOGFILE=$CWD/update.log

echo "Start..."
echo "[$NOW] Start..." > $SETUP_LOGFILE

supervisorctl stop all >> $SETUP_LOGFILE

cd $PROJECT_PATH
git pull >> $SETUP_LOGFILE

# Install project libs
env/bin/pip install -r requirements/$TARGET.txt --trusted-host pypi.python.org >> $SETUP_LOGFILE

# Update database and copy assets
env/bin/python src/manage.py collectstatic --link --noinput --settings=$SETTINGS >> $SETUP_LOGFILE
env/bin/python src/manage.py migrate --noinput --settings=$SETTINGS >> $SETUP_LOGFILE

# Copy local settings
cp $CWD/vars/$TARGET.py $PROJECT_PATH/src/zaakmagazijn/conf/

# Give the web-user permission to write to log and media paths.
chown nginx:nginx -R . > /dev/null
chmod g+rw -R . > /dev/null

cd $CWD

supervisorctl start all >> $SETUP_LOGFILE

echo "[$NOW] Done." >> $SETUP_LOGFILE
echo "Done."

