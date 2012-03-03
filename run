#!/bin/bash

SETUPTOOLS_URL='http://pypi.python.org/packages/2.7/s/setupvenv/setuptools-0.6c11-py2.7.egg#md5=fe1f997bc722265116870bc7919059ea'
SETUPTOOLS_EGG="/tmp/setuptools-0.6c11-py2.7.egg"

if [ ! -x venv/bin/fab ]; then
  if [ -z `which virtualenv` ]; then
    if [ -z `which easy_install` ]; then
      if [ ! -f $SETUPTOOLS_EGG ]; then
        echo "Downloading to $SETUPTOOLS_EGG"
        curl $SETUPTOOLS_URL -o $SETUPTOOLS_EGG
      fi
      echo "Installing $SETUPTOOLS_EGG - you may be asked for your SUDO password"
      sudo sh $SETUPTOOLS_EGG
    fi
    echo "Installing virtualenv - you may be asked for your SUDO password"
    sudo easy_install virtualenv
  fi
  if [ ! -x venv/bin/pip ]; then
    virtualenv venv
  fi
  venv/bin/python venv/bin/pip install -r libs.pip
fi

if [ $# == 0 ]; then
  venv/bin/python venv/bin/fab --list
  echo ""
  echo "OR ./run <any local python script>"
  echo ""
elif [ -e $1 ]; then
  venv/bin/python $@
else
  venv/bin/python venv/bin/fab $@
fi
