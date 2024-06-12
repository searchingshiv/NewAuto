#!/bin/bash

if [ -z "$UPSTREAM_REPO" ]; then
  echo "Cloning main Repository"
  git clone https://github.com/searchingshiv/NewAuto.git /searchingshiv/NewAuto
else
  echo "Cloning Custom Repo from $UPSTREAM_REPO"
  git clone "$UPSTREAM_REPO" /searchingshiv/NewAuto
fi

cd /searchingshiv/NewAuto || exit
pip3 install -U -r requirements.txt
echo "Starting Bot...."
python3 bot.py
