#!/bin/sh

sudo apt update
sudo apt install python3-pip python3-pygame python3-flask python3-watchdog

if ! $(grep -q dtoverlay=vc4-kms-dpi-hyperpixel4sq /boot/config.txt) ; then
    echo "dtoverlay=vc4-kms-dpi-hyperpixel4sq" >> /boot/config.txt
fi

if ! $(grep -q dtoverlay=dwc2 /boot/config.txt) ; then
    echo "dtoverlay=dwc2" >> /boot/config.txt
fi
