build-light-indicator
=====================

A small script that interface to `DelCom USB` led products based on `TeamCity`'s build status.

### Installation

First install pyusb to interface usb devices:

    pip install pyusb

Also you might wanna change the TeamCity uri from the Controller class.

```python
class Controller():
    TEAMCITY_URI = 'my awesome host'
```

### Usage

Pass as many as build types to the script to check. You might wanna put this script into the cron to do periodic checking..

    sudo python delcom.py bt1 bt2 bt7

or

    sudo python delcom.py all

In second case though, you gotta edit the api url to enter ur project id. I don't have time to make it generic atm.
