#!/bin/bash

sudo uname

echo "\nFetching updates"
echo "------------------"
sudo apt-get update

echo "checking for python3 and pip3"
echo "------------------"
sudo apt-get install -y python3
sudo apt-get install -y python3-pip

if hash pip3>/dev/null; then
	echo "Installing Flask"
	echo "------------------"
	pip3 install flask
	echo "Installing PyBluez"
	echo "------------------"
	pip3 install pybluez
else
	echo "ERROR: Could not install Flask and pybluez - no pip3"
	echo "------------------"
fi

echo "Installing MongoDb"
echo "------------------"
sudo apt-get install mongodb

if hash ufw>/dev/null; then
	echo "Opening port 8080"
	echo "------------------"
	sudo ufw allow 8080/tcp
else
	echo "No firewall found, skipping"
	echo "------------------"
fi

echo "Done."
