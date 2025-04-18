#!/bin/bash

echo "Installing virtual environment and dependencies..."
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo "Done. Make sure to generate the SSH key:"
echo "ssh-keygen -t rsa -b 2048 -f server.key"
