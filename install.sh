#!/bin/bash

if [[ $EUID -ne 0 ]]; then
    echo "This script requires root privileges. Please run as root or use sudo."
    exit 1
fi

apt update
apt install python3-pip python3-pygame python3-flask python3-watchdog python3-jsonschema

if ! $(grep -q dtoverlay=vc4-kms-dpi-hyperpixel4sq /boot/config.txt) ; then
    echo "dtoverlay=vc4-kms-dpi-hyperpixel4sq" >> /boot/config.txt
fi

if ! $(grep -q dtoverlay=dwc2 /boot/config.txt) ; then
    echo "dtoverlay=dwc2" >> /boot/config.txt
fi

if ! id "hotkey" &>/dev/null; then
    useradd -r -m -d /opt/hotkey -s /bin/bash hotkey
    usermod -a -G plugdev hotkey
    usermod -a -G input hotkey
    usermod -a -G video hotkey
    usermod -a -G tty hotkey
fi

mkdir /opt/hotkey
cp -r * /opt/hotkey
chown -R hotkey:hotkey /opt/hotkey
chown -R root:root /opt/hotkey/hid.sh

cp /opt/hotkey/udev/99-hidg0.rules /etc/udev/rules.d
cp /opt/hotkey/udev/99-input.rules /etc/udev/rules.d
cp /opt/hotkey/udev/99-backlight.rules /etc/udev/rules.d
cp /opt/hotkey/udev/99-tty.rules /etc/udev/rules.d
udevadm control --reload-rules
udevadm trigger

cp /opt/hotkey/systemd/hid.service /etc/systemd/system/
cp /opt/hotkey/systemd/hotkey.service /etc/systemd/system/

systemctl daemon-reload
systemctl enable hid.service
systemctl enable hotkey.service