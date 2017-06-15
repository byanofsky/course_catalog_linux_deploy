apt-get -qqy update
apt-get -qqy install apache2
apt-get -qqy install libapache2-mod-wsgi
apt-get -y install python-pip
apt-get -y install postgresql
#

adduser --disabled-password --quiet --gecos course_catalog course_catalog

sudo -u postgres createuser --no-createdb --encrypted course_catalog
sudo -u postgres createdb course_catalog

pip install virtualenv
cd /var/www/html/course_catalog
virtualenv venv
source venv/bin/activate

cp /var/www/html/course_catalog/files-for-server/course_catalog.conf /etc/apache2/sites-available/course_catalog.conf

a2dissite 000-default.conf
a2ensite course_catalog.conf
service apache2 reload
