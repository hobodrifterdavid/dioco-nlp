#!/bin/bash

echo XXXXXXXXXX Update APT packet cache
apt update -y

echo XXXXXXXXXX Installing Nginx
apt install nginx -y

# echo XXXXXXXXXX Installing GeoIP support not GeoIP2
# apt-get install geoip-database-extra libgeoip1 libnginx-mod-http-geoip -y

echo XXXXXXXXXX Disabling the default virtual host
unlink /etc/nginx/sites-enabled/default

echo XXXXXXXXXX Creating NLP Cache directory
mkdir /nlp_cache

echo XXXXXXXXXX Moving config file reverse-proxy.conf to /etc/nginx/sites-available/
cp nlp.conf /etc/nginx/sites-available/nlp.conf

echo XXXXXXXXXX Creating soft link from /etc/nginx/sites-enabled/
ln -s /etc/nginx/sites-available/nlp.conf /etc/nginx/sites-enabled/nlp.conf

echo XXXXXXXXXX Testing config file
nginx -t

echo XXXXXXXXXX Restarting Ngninx
systemctl restart nginx

echo XXXXXXXXXX Make some nice shortcuts
alias ne='tail -f /var/log/nginx/error.log'
alias na='tail -f /var/log/nginx/access.log'

echo XXXXXXXXXX Show IP address
curl -4 icanhazip.com
