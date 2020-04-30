# EnvoyS2Emoncms

Purpose of these files is a full integration of the Enphase EnvoyS-Metered multiphase in Emoncms.

This includes:
- configuration file for the EnvoyS and Emoncms settings
- python script to read the EnvoyS data and send them to Emoncms
- Emoncms device templates

It has been tested with:
- Python **3.7.3**
- an **Envoy-S-Metered-EU** multiphase with firmware **5.0.34**.
- emoncms **v10.2.1** installed locally on a Debian **10.3** x64.

***
## Contents
- [EnvoyS2Emoncms](#envoys2emoncms)
  - [Contents](#contents)
  - [Prerequisites](#prerequisites)
    - [Emoncms](#emoncms)
    - [Python3](#python3)
  - [Install on Debian based systems](#install-on-debian-based-systems)
    - [Clone the repository](#clone-the-repository)
    - [Scripts](#scripts)
    - [Configuration file](#configuration-file)
    - [Some system stuff](#some-system-stuff)
  - [Emoncms templates](#emoncms-templates)

***

## Prerequisites

### Emoncms
Please see [Emoncms](https://emoncms.org/) for details.

### Python3
On Debian based system:
```sh
# Install python3
sudo apt-get install python3
sudo apt-get -y install python3-pip

# Update pip
sudo pip3 install --upgrade pip
```

## Install on Debian based systems

### Clone the repository
Navigate to some location like your home directory or */var/tmp*.
```sh
# Clone the repository
git clone -b master https://github.com/FredM67/EnvoyS2Emoncms.git
```
### Scripts
```sh
cd EnvoyS2Emoncms
sudo cp EnvoyS2Emoncms.py /usr/local/bin/EnvoyS2Emoncms.py
sudo chmod +x /usr/local/bin/EnvoyS2Emoncms.py

sudo cp EnvoyS2EmoncmsWatchdog.sh /usr/local/bin/EnvoyS2EmoncmsWatchdog.sh
sudo chmod +x /usr/local/bin/EnvoyS2EmoncmsWatchdog.sh
```

### Configuration file
Install the configuration file, rename it and modify it accordingly to your system by setting the fields marked with **< ... >**.
```sh
sudo mkdir /etc/Enphase
sudo cp EnvoyS2Emoncms_default.cfg /etc/Enphase/EnvoyS2Emoncms.cfg
```

At this point, if you want to check if everything is working properly, you can run the script by hand like this (stop it with `Ctrl-C`):
```sh
sudo /usr/local/bin/EnvoyS2Emoncms.py
```
You should see new inputs in your emoncms.

### Some system stuff
Configure log rotation:
```sh
sudo cp EnvoyS2Emoncms.logrotate /etc/logrotate.d/EnvoyS2Emoncms
```

Add a crontab for the watchdog:
```sh
sudo crontab -e
```
add
```sh
* * * * *       /usr/local/bin/EnvoyS2EmoncmsWatchdog.sh
```

After that, the system will start automatically the python script within 1-2 minutes.

In your emoncms, you should see new inputs under the node id set in the config file.

## Emoncms templates
For those with a local emoncms, you can add 2 templates. They help the user to create feeds, configure them, ... automatically.
For further details about that, please see [Emoncms Documentation](https://github.com/emoncms/emoncms) and [Emoncms Device module](https://github.com/emoncms/device).
```sh
# deploy the template with general data
cp EnvoyS.json /var/www/emoncms/Modules/device/data/EnvoyS.json

# deploy the template with detailed data (general + each phase)
cp EnvoyS-3phase.json /var/www/emoncms/Modules/device/data/EnvoyS-3phase.json
```
After that, you've to update the template list, just call:
```
http://my_emoncms/device/template/reload.json
```
That's it!
Have fun!