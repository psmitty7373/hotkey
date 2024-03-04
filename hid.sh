#!/bin/bash

modprobe libcomposite

# Create gadget
mkdir /sys/kernel/config/usb_gadget/g
cd /sys/kernel/config/usb_gadget/g

# Add basic information
echo 0x0100 > bcdDevice # Version 1.0.0
echo 0x0200 > bcdUSB # USB 2.0
echo 0xEF > bDeviceClass
echo 0x01 > bDeviceProtocol
echo 0x02 > bDeviceSubClass
#echo 0x40 > bMaxPacketSize0
echo 0x0104 > idProduct # Multifunction Composite Gadget
echo 0x1d6b > idVendor # Linux Foundation

# Create English locale
mkdir strings/0x409

echo "Pibox" > strings/0x409/manufacturer
echo "Piboxkeyboard" > strings/0x409/product
echo "0123456789" > strings/0x409/serialnumber

# Create HID function
mkdir -p functions/rndis.usb0
mkdir -p functions/hid.usb0

echo 1 > functions/hid.usb0/protocol
echo 8 > functions/hid.usb0/report_length # 8-byte reports
echo 1 > functions/hid.usb0/subclass
echo -ne \\x05\\x01\\x09\\x06\\xa1\\x01\\x05\\x07\\x19\\xe0\\x29\\xe7\\x15\\x00\\x25\\x01\\x75\\x01\\x95\\x08\\x81\\x02\\x95\\x01\\x75\\x08\\x81\\x03\\x95\\x05\\x75\\x01\\x05\\x08\\x19\\x01\\x29\\x05\\x91\\x02\\x95\\x01\\x75\\x03\\x91\\x03\\x95\\x06\\x75\\x08\\x15\\x00\\x25\\x65\\x05\\x07\\x19\\x00\\x29\\x65\\x81\\x00\\xc0 > functions/hid.usb0/report_desc

# Create configuration
mkdir configs/c.1
#echo 0x80 > configs/c.1/bmAttributes
echo 250 > configs/c.1/MaxPower # 200 mA

# Link Ether function to configuration
ln -s functions/rndis.usb0 configs/c.1
# Link HID function to configuration
ln -s functions/hid.usb0 configs/c.1

# os descriptors
echo 1 > os_desc/use
echo 0xcd > os_desc/b_vendor_code
echo MSFT100 > os_desc/qw_sign

echo RNDIS > functions/rndis.usb0/os_desc/interface.rndis/compatible_id
echo 5162001 > functions/rndis.usb0/os_desc/interface.rndis/sub_compatible_id

ln -s configs/c.1 os_desc

udevadm settle -t 5 || :
ls /sys/class/udc/ > UDC
