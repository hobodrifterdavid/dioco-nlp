#!/bin/bash

echo XXXXXXXXXX update APT packet cache
apt update -y

echo XXXXXXXXXX Pump up Python enviroment and unzip
apt install python3-pip python3-dev build-essential libssl-dev libffi-dev python3-setuptools python3-venv unzip

echo XXXXXXXXXX Create virtual enviroment
python3.6 -m venv nlp_app_env

echo XXXXXXXXXX Activate virtual enviroment
source nlp_app_env/bin/activate

echo XXXXXXXXXX Install wheel to ensure that our packages will install even if they are missing wheel archives
pip install wheel

echo XXXXXXXXXX Install other requirements
pip install -r requirements.txt

echo XXXXXXXXXX Install libicu-dev
apt install libicu-dev

echo XXXXXXXXXX Install pythainlp icu transliteration option
pip install pythainlp[icu]

# echo XXXXXXXXXX LTP models
# wget http://model.scir.yunfutech.com/model/ltp_data_v3.4.0.zip
# unzip ltp_data_v3.4.0.zip

echo XXXXXXXXXX Copy in Gunicorn service config
cp nlp-gunicorn_2.service /etc/systemd/system/nlp-gunicorn_2.service

systemctl daemon-reload

echo XXXXXXXXXX Start Gunicorn service
systemctl start nlp-gunicorn_2

echo ---------->Start Gunicorn service at boot
systemctl enable nlp-gunicorn_2
