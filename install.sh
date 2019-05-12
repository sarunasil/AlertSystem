#!/bin/bash

sudo uname

echo ""
echo "Fetching updates"
echo "------------------"
sudo apt-get update

echo "checking for python3 and pip3"
echo "------------------"
sudo apt-get install -y python3
sudo apt-get install -y python3-pip

if hash pip3 2>/dev/null; then
	echo "Installing Flask"
	echo "------------------"
	pip3 install flask flask_cors flasks_jwt_extended

	echo "Installing PyBluez"
	echo "------------------"
	pip3 install pybluez

	echo "Installing pymongo"
	echo "------------------"
	pip3 install pymongo==3.4
elif hash pip-3.2 2>/dev/null; then
	echo "Installing Flask"
	echo "------------------"
	pip-3.2 install flask flask_cors flasks_jwt_extended

	echo "Installing PyBluez"
	echo "------------------"
	pip-3.2 install pybluez

	echo "Installing pymongo"
	echo "------------------"
	pip-3.2 install pymongo==3.4
else
	echo "ERROR: Could not install Flask and pybluez - no pip3 or pip-3.2"
	echo "------------------"
fi

echo "Installing MongoDb"
echo "------------------"
sudo apt-get install mongodb

if hash ufw 2>/dev/null; then
	echo "Opening port 8080"
	echo "------------------"
	sudo ufw allow 8080/tcp
else
	echo "No firewall found, skipping"
	echo "------------------"
fi

echo "Installing Nginx"
sudo apt-get install nginx -y

echo "Done."
