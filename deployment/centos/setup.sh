#!/bin/bash
source vars/setup_config.sh

CWD=`pwd`
NOW=$(date +"%Y-%m-%d")
SETUP_LOGFILE=$CWD/setup.log

if [ ! -f $CWD/vars/$TARGET.py ]; then
    echo "Configuration file '$CWD/vars/$TARGET.py' does not exist. Copy 'vars/settings_example.py' to vars/$TARGET.py and modify it to your needs."
fi

echo "[$NOW] Start..." > $SETUP_LOGFILE
echo "Installing system packages..."

yum install -y net-tools git gcc libxslt-devel >> $SETUP_LOGFILE

# The commands below are done for convenience and should not be done on a true
# production server. The Permissive setting will also only last until the next
# reboot.
# setenforce Permissive
# chcon -Rt httpd_sys_content_t $PROJECT_PATH

# Enable EPEL-repository
yum install -y epel-release >> $SETUP_LOGFILE

# Security settings
echo "Configuring security policies..."
yum install -y policycoreutils-{python,devel} >> $SETUP_LOGFILE
touch /etc/selinux/targeted/contexts/files/file_contexts.local
setsebool -P httpd_can_network_connect 1 >> $SETUP_LOGFILE
semodule -i vars/nginx.pp >> $SETUP_LOGFILE
firewall-cmd --permanent --zone=public --add-service=http >> $SETUP_LOGFILE
firewall-cmd --permanent --zone=public --add-service=https >> $SETUP_LOGFILE
firewall-cmd --reload >> $SETUP_LOGFILE

# Nginx webserver
echo "Installing Nginx..."
yum install -y nginx >> $SETUP_LOGFILE
systemctl start nginx >> $SETUP_LOGFILE
systemctl enable nginx >> $SETUP_LOGFILE

if [ ! -f /etc/nginx/nginx.conf.bak ]; then
    echo "Creating backup of nginx.conf" >> $SETUP_LOGFILE
    cp /etc/nginx/nginx.conf /etc/nginx/nginx.conf.bak >> $SETUP_LOGFILE
fi

# Add within http-block: disable_symlinks off;
sed -i 's/^\(http {\)$/\1\n    disable_symlinks  off;/g' /etc/nginx/nginx.conf
# Remove default server manually, since it can overrule our config.
sed -i '/server {/,/#    }/d' /etc/nginx/nginx.conf

# Redis cache server
echo "Installing Redis..."
yum install -y redis >> $SETUP_LOGFILE
systemctl start redis >> $SETUP_LOGFILE
systemctl enable redis >> $SETUP_LOGFILE

# Supervisor
echo "Installing Supervisor..."
yum install -y supervisor >> $SETUP_LOGFILE
systemctl start supervisord >> $SETUP_LOGFILE
systemctl enable supervisord >> $SETUP_LOGFILE

# PostgreSQL database (optional)
if [ "$DB_NAME" != "" ]; then
    PG_CONFIG=/var/lib/pgsql/data/pg_hba.conf

    echo "Installing PostgreSQL..."
    yum install -y postgresql-server postgresql-devel postgresql-contrib >> $SETUP_LOGFILE
    postgresql-setup initdb

    if [ ! -f $PG_CONFIG.bak ]; then
        echo "Creating backup of pg_hba.conf" >> $SETUP_LOGFILE
        cp $PG_CONFIG $PG_CONFIG.bak
    fi

    # Change local peer auth with md5
    sed -i 's/^\(local.*all.*all.*\)peer$/local   all             postgres                                peer\n\1md5/g' $PG_CONFIG
    systemctl restart postgresql >> $SETUP_LOGFILE
    systemctl enable postgresql >> $SETUP_LOGFILE

    # Create database user
    echo "Creating database user \"$DB_USERNAME\""
    su postgres --command="createuser --login --pwprompt $DB_USERNAME"
    su postgres --command="createdb --owner=$DB_USERNAME --encoding=UTF-8 $DB_NAME"
fi

# Python 3.4, pip and virtualenv
echo "Installing Python..."
yum install -y python34 python34-devel >> $SETUP_LOGFILE
curl -k -s -O https://bootstrap.pypa.io/get-pip.py >> $SETUP_LOGFILE
/usr/bin/python3.4 get-pip.py --trusted-host pypi.python.org >> $SETUP_LOGFILE
rm get-pip.py
pip3 install virtualenv >> $SETUP_LOGFILE

#
# Project
#
echo "Installing Zaakmagazijn..."
mkdir -p $PROJECT_PATH
cd $PROJECT_PATH
git clone -b $BRANCH $REPO . >> $SETUP_LOGFILE
virtualenv env >> $SETUP_LOGFILE

# Install project libs
env/bin/pip install -r requirements/$TARGET.txt --trusted-host pypi.python.org >> $SETUP_LOGFILE

# Copy local settings
cp $CWD/vars/$TARGET.py $PROJECT_PATH/src/zaakmagazijn/conf/

# Update database and copy assets
env/bin/python src/manage.py collectstatic --link --noinput --settings=$SETTINGS >> $SETUP_LOGFILE
env/bin/python src/manage.py migrate --noinput --settings=$SETTINGS >> $SETUP_LOGFILE

# Create superuser
echo "Creating Zaakmagazijn superuser"
env/bin/python src/manage.py createsuperuser --settings=$SETTINGS

# Give the web-user permission to write to log and media paths.
chown nginx:nginx -R . > /dev/null
chmod g+rw -R . > /dev/null

cd $CWD

# Link appropriate config files and reload services
echo "Reloading services..."
PROJECT_CONF_PATH=$PROJECT_PATH/deployment/conf
mkdir -p $PROJECT_CONF_PATH

cp -f $CWD/vars/uwsgi.ini $PROJECT_CONF_PATH/

cp -f $CWD/vars/supervisor.ini $PROJECT_CONF_PATH/
rm -f /etc/supervisord.d/$PROJECT_NAME.ini > /dev/null
ln -s $PROJECT_CONF_PATH/supervisor.ini /etc/supervisord.d/$PROJECT_NAME.ini > /dev/null
supervisorctl reread >> $SETUP_LOGFILE
supervisorctl reload >> $SETUP_LOGFILE

cp -f $CWD/vars/nginx.conf $PROJECT_CONF_PATH/
rm -f /etc/nginx/conf.d/$PROJECT_NAME.conf > /dev/null
ln -s $PROJECT_CONF_PATH/nginx.conf /etc/nginx/conf.d/$PROJECT_NAME.conf > /dev/null
systemctl reload nginx >> $SETUP_LOGFILE

echo "[$NOW] Done." >> $SETUP_LOGFILE
echo "Done."
