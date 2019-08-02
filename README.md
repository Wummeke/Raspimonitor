# Raspimonitor
Used these repositories for inspiration : 
- https://github.com/Sennevds/system_sensors
- https://github.com/LarsBergqvist/RPiClient_MQTT

Follow these instructions to install script on your pi and run it automatically every 10 minutes

copy the following files with winscp to Pi
- raspimonitor.py
- configuration.yaml
- requirements.txt

install dependencies
```
sudo apt-get install -y python3 python3-pip python3-virtualenv virtualenvwrapper python3-gpiozero
```

Create user
```
sudo useradd raspimonitor --home-dir /home/raspimonitor --create-home --shell /bin/bash
```
log in as new user
```
sudo su - raspimonitor
```

create  folder for python files
```
mkdir scripts
```

copy scripts to scripts folder
```
cp -r /home/pi/files/. ~/scripts
```

Create virtual environment
```
virtualenv ~/.virtualenvs/raspimonitor --no-site-packages --python python3
```

add arguments to ~/.bashrc so the next time the user logs in, everything is set for easy user
```
nano ~/.bashrc
```

add these arguments at bottom of the file:
```
source ~/.virtualenvs/raspimonitor/bin/activate
cd ~/scripts
```
Logout as user raspimonitor 
```
exit
```

and log back in
```
sudo su - raspimonitor
```

install requirements
```
pip3 install -r /home/raspimonitor/scripts/requirements.txt
```

add script to crontab to execute it every 10 minutes
```
crontab -e
```

add the following line at the bottom
```
*/10 * * * * /home/raspimonitor/.virtualenvs/raspimonitor/bin/python3 /home/raspimonitor/scripts/raspimonitor.py
```
