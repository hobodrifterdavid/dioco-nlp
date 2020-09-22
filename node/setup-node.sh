#!/bin/bash

echo update APT packet cache
apt update -y

# apt install nodejs
# Note: Ubuntu repo executable is called node, note nodejs
# apt install npm

# https://www.digitalocean.com/community/tutorials/how-to-install-node-js-on-ubuntu-18-04
curl -sL https://deb.nodesource.com/setup_14.x -o nodesource_setup.sh
chmod +x nodesource_setup.sh
./nodesource_setup.sh

rm nodesource_setup.sh

apt install nodejs

npm -v

apt install build-essential

npm install -g typescript

npm install

npm install pm2@latest -g
pm2 update

pm2 install pm2-logrotate

tsc

pm2 start build/express-app.js --watch --max-memory-restart 2000M

pm2 startup

pm2 save
