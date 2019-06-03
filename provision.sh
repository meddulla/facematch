#!/usr/bin/env bash

sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt-get update
sudo apt -y upgrade
sudo apt install software-properties-common
sudo apt install git


sudo apt install build-essential libssl-dev libffi-dev python3-dev
sudo apt-get install python3.7
sudo apt-get install python3.7-dev # for uwsgi
sudo apt install -y python3-pip
sudo apt install -y python3.7-venv

su webapper
cd
python3.7 -m venv facematch-venv
source facematch-venv/bin/activate

# install private deploy key in ssh
cd
git clone git@github.com:meddulla/facematch.git

cd facematch
pip install -r requirements.txt


sudo cp /home/webapper/facematch/facematch.service /etc/systemd/system/
sudo systemctl --system enable facematch
sudo systemctl start facematch
