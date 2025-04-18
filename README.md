# 🕵️ Honeypot Trap

This project implements both SSH and HTTP (WordPress-style) honeypots for capturing unauthorized access attempts.

## Features

- 🛡 SSH Honeypot:
  - Fake Ubuntu 22.04 shell experience
  - Customizable username and password
  - Logs credentials and shell commands
  - Emulates basic shell commands

- 🌐 Web Honeypot:
  - Fake WordPress login page
  - Logs login attempts with IP addresses
  - Configurable credentials

## Installation


git clone https://github.com/yourusername/honeypot-trap.git
cd honeypot-trap
chmod +x install.sh
./install.sh
