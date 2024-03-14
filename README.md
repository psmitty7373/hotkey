# hotkey

## About

This project is a desktop-style macro board configured via a web interface. It uses a Raspberry Pi Zero operating as a HID gadget to transmit keypresses to the host system and incorporates an LCD touchscreen for user interaction. This device is ideal for games like Helldivers 2!

## Requirements
- 3d printed case
- Raspberry Pi Zero 2 W
- Pimorono HyperPixel 4.0 Square Touchscreen
- Some nylon screws and standoffs
- 8gb SD card
- Micro USB cable

## Case Printing
An [STL file](./printable_case/printable_case.stl) is included for printing the case. The case can be printed without supports and snaps together.

![Case Design](./printable_case/case_screenshot.png)

Files for the case can be found in the "printable_case" directory.
## Assembly

After printing the case, assembly is straightforward:

1. **Screen Placement**: The screen is pressure-fitted into the lid and will only fit in one direction.

   ![screen placement](./help_images/screen.png)

2. **Securing the Screen**: The screen is secured using 2 metal screws and 2 short nylon standoffs commonly found in makerspaces or Microcenter.

   ![screws](./help_images/screws.png)

3. **Connecting the Pi Zero**: The Pi Zero is socketed into the 40-pin connector and secured using 2 nylon screws.

4. **Cable Routing**: A micro-USB cable is routed through the hole in the back of the case and connected to the OTG port on the Pi Zero.

   ![cable placement](./help_images/cable.png)

5. **Final Assembly**: Snap the front of the case, screen, Pi, and cable onto the rear of the case. The fit should be snug depending on your print settings.

6. **SD Card Insertion**: Insert the SD card into the cutout in the side of the case, ensuring it is inserted correctly.

   ![sdcard](./help_images/sdcard.png)

7. **Stabilization**: Optionally, add small rubber feet to the bottom of the case to prevent it from sliding around.

## Setup

The recommended starting distro is a Debian image. Once logged in via SSH, clone this repository using git.

## User Interface

Layouts and macros are created via a web server listening on the Raspberry Pi. The design uses a simplistic drag-and-drop interface for most features.

![example web layout](./help_images/web_layout.png)

### Layouts

Layouts are the largest macro building block, comprised of a series of buttons of 3 different sizes arranged to the user's preference. The layouts accommodate up to 25 of the smallest button sizes. Layouts can be created by editing the "New Layout" at the top left of the page. Layouts can be swapped by clicking their names and removed by dragging them to the trashcan at the bottom center of the page.

### Buttons

Buttons are visible in the center grid area of the page, representing what is visible on the device's LCD. They can be dragged around to relocate or remove by dragging them to the trashcan. New buttons can be added to the grid by dragging them from the "New Button" area in the bottom left of the web interface.

### Macros

Macros are on the right side of the web interface. They can be created via the "New Macro" at the top of the display. Macros can be edited directly in the textarea found below the macro name. New images can be added to the macro by dragging and dropping a .PNG file onto the old image. Macros can be added to buttons by dragging them over the target button and deleted by dragging them to the trashcan.

## Credits

- Included icons from: [Helldivers 2 Stratagems Icons for Streamdeck](https://www.reddit.com/r/Helldivers/comments/1ayhofq/hell_divers_2_stratagems_icons_for_streamdeck/)
- Touchscreen driver from: [Pimoroni Python Multitouch](https://github.com/pimoroni/python-multitouch/blob/master/library/ft5406.py)