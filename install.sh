#!/bin/bash

sudo uname

echo "Fetching updates"
sudo apt-get update

echo "checking for python3 and pip3"
sudo apt-get install -y python3
sudo apt-get install -y python3-pip

if hash pip3>/dev/null; then
	echo "Installing Flask"
	sudo pip3 install flask
	echo "Installing PyBluez"
	sudo pip3 install pybluez
else
	echo "ERROR: Could not install Flask and pybluez - no pip3"
fi

echo "Installing MongoDb"
sudo apt-get install mongodb

if hash ufw>/dev/null; then
	echo "Opening port 8080"
	sudo ufw allow 8080/tcp
else
	echo "No firewall found, skipping"
fi

echo "Done"
