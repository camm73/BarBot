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

/usr/bin/python3 -m pip install flask Flask-API boto3 AWSIoTPythonSDK RPi.GPIO awscli

export PATH=/home/pi/.local/bin:$PATH
echo "Done installing python packages."
echo "================================================"

echo "You will now setup you AWS credentials. Please type them when prompted..."
sleep 2
aws configure
echo "Your AWS credentials have been set up successfully!"

echo "================================================"

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
echo "================================================"

echo "Setting up BarBot systemd service"
sudo cp /home/pi/BarBot/controller/barbot.service /etc/systemd/system/barbot.service
sleep 1
sudo systemctl enable barbot.service
echo "BarBot startup service successfully setup"
echo "================================================"

echo "Changing default hostname to 'barbot'"
sudo hostnamectl set-hostname 'barbot'
echo "Hostname successfully changed"
echo "================================================"

echo "BarBot setup is complete! BarBot will now reboot itself..."
sleep 6
sudo reboot
exit 0
