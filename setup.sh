#!/bin/bash

echo "Welcome to the BarBot setup script. We'll start configuring your device..."
echo "================================================"

echo "Checking installation of apt packages:"
pkgs='python3-pip python3-tk'

if ! dpkg -s $pkgs >/dev/null 2>&1; then
	echo "Installing apt packages..."
	sudo apt install -y $pkgs
	echo "Done installing apt packages"
else
	echo "Necessary apt packages already installed"
fi

echo "================================================"
echo "Installing necessary python packages for BarBot..."

/usr/bin/python3 -m pip install flask Flask-API boto3 AWSIoTPythonSDK RPi.GPIO

echo "Done installing python packages."

FILE=/usr/local/bin/rmate
if [ -f FILE ];
then
	echo "Now installing rmate for remote code editting..."

	sudo wget -O /usr/local/bin/rmate https://raw.githubusercontent.com/aurora/rmate/master/rmate
	sudo chmod a+x /usr/local/bin/rmate

	echo "Done installing rmate"
else
	echo "rmate is already installed. Skipping..."
fi

echo "BarBot setup is complete"
exit 0
