# /bin/bash
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
set -a
source $SCRIPT_DIR/.env
set +a
sudo mkdir /etc/$APP_NAME
sudo mkdir /var/log/$APP_NAME
sudo mkdir -p /srv/www/$APP_NAME
sudo mkdir -p /srv/www/$APP_NAME/static

sudo cp $SCRIPT_DIR/configs/configs_examples/* /etc/$APP_NAME/
sudo cp $SCRIPT_DIR/configs/nginx/$APP_NAME.conf /etc/nginx/sites-availabe/
sudo ls -s /etc/nginx/sites-availabe/$APP_NAME.conf /etc/nginx/sites-enabled/$APP_NAME.conf

sudo $SCRIPT_DIR/configs/nginx/$APP_NAME-gunicorn.service /etc/systemd/system/
sudo $SCRIPT_DIR/configs/nginx/$APP_NAME-celery.service /etc/systemd/system/
sudo $SCRIPT_DIR/configs/nginx/$APP_NAME-celerybeat.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable $APP_NAME-gunicorn.service
sudo systemctl enable $APP_NAME-celery.service
sudo systemctl enable $APP_NAME-celerybeat.service

sudo chown -R $APP_NAME:$APP_NAME /etc/$APP_NAME
sudo chown -R $APP_NAME:$APP_NAME /var/log/$APP_NAME
sudo chown -R $APP_NAME:$APP_NAME /srv/www/$APP_NAME

sudo mysql -uroot -e "CREATE DATABASE ${DB_NAME} /*\!40100 DEFAULT CHARACTER SET utf8 */;"
sudo mysql -uroot -e "CREATE USER ${DB_USER}@localhost IDENTIFIED BY '${DB_PASSWORD}';"
sudo mysql -uroot -e "GRANT ALL PRIVILEGES ON ${DB_NAME}.* TO '${DB_USER}'@'localhost';"
sudo mysql -uroot -e "FLUSH PRIVILEGES;"

sudo certbot --nginx -d "sta.bluishred.net" -d "www.sta.bluishred.net"
sudo crontab -l > mycron
sudo echo "0 12 * * * /usr/bin/certbot renew --quiet" >> mycron
sudo crontab mycron
sudo rm mycron


