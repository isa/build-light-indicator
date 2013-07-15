build-light-indicator
=====================

A small script that interface to `DelCom USB` led products based on `TeamCity`'s build status.

### Installation

First install pyusb to interface usb devices:

    pip install pyusb

### Usage

Pass as many as build types to the script to check. You might wanna put this script into the cron to do periodic checking..

    python delcom.py bt1 bt2 bt7


