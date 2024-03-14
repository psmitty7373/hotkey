import os
import time

class HIDKeyboard:
    def __init__(self, device_path="/dev/hidg0"):
        self.dev = os.open(device_path, os.O_RDWR)

    def send_keypresses(self, keypresses):
        for key in keypresses:
            report = bytes([0, 0, key, 0, 0, 0, 0, 0])
            os.write(self.dev, report)
            time.sleep(0.02)
            report = bytes([0, 0, 0, 0, 0, 0, 0, 0])
            os.write(self.dev, report)
            time.sleep(0.02)

    def send_string(self, string):
        keypresses = self.string_to_keypresses(string)
        self.send_keypresses(keypresses)

    def string_to_keypresses(self, s):
        keypresses = []
        i = 0
        while i < len(s):
            char = s[i]
            if char == '\\':
                if i + 1 < len(s):
                    next_char = s[i + 1]
                    if next_char == '\\':
                        keypresses.append(0x31)
                    elif next_char == 'U':
                        keypresses.append(0x52)  # Up arrow key
                    elif next_char == 'D':
                        keypresses.append(0x51)  # Down arrow key
                    elif next_char == 'R':
                        keypresses.append(0x4f)  # Right arrow key
                    elif next_char == 'L':
                        keypresses.append(0x50)  # Left arrow key
                    elif next_char == 'r' or next_char == 'n':
                        keypresses.append(0x28)
                    i += 1  # Skip the next character
                else:
                    keypresses.append(self.key_map[char])
            elif char.isalpha():
                keypresses.append(self.key_map[char.lower()])
            elif char in self.key_map:
                keypresses.append(self.key_map[char])
            i += 1

        return keypresses

    def close(self):
        os.close(self.dev)

    # Define the mapping of characters to key codes
    key_map = {
        'a': 0x04, 'b': 0x05, 'c': 0x06, 'd': 0x07, 'e': 0x08, 'f': 0x09, 'g': 0x0a, 'h': 0x0b,
        'i': 0x0c, 'j': 0x0d, 'k': 0x0e, 'l': 0x0f, 'm': 0x10, 'n': 0x11, 'o': 0x12, 'p': 0x13,
        'q': 0x14, 'r': 0x15, 's': 0x16, 't': 0x17, 'u': 0x18, 'v': 0x19, 'w': 0x1a, 'x': 0x1b,
        'y': 0x1c, 'z': 0x1d, 'A': 0x04 + 0x80, 'B': 0x05 + 0x80, 'C': 0x06 + 0x80, 'D': 0x07 + 0x80,
        'E': 0x08 + 0x80, 'F': 0x09 + 0x80, 'G': 0x0a + 0x80, 'H': 0x0b + 0x80, 'I': 0x0c + 0x80,
        'J': 0x0d + 0x80, 'K': 0x0e + 0x80, 'L': 0x0f + 0x80, 'M': 0x10 + 0x80, 'N': 0x11 + 0x80,
        'O': 0x12 + 0x80, 'P': 0x13 + 0x80, 'Q': 0x14 + 0x80, 'R': 0x15 + 0x80, 'S': 0x16 + 0x80,
        'T': 0x17 + 0x80, 'U': 0x18 + 0x80, 'V': 0x19 + 0x80, 'W': 0x1a + 0x80, 'X': 0x1b + 0x80,
        'Y': 0x1c + 0x80, 'Z': 0x1d + 0x80, '1': 0x1e, '2': 0x1f, '3': 0x20, '4': 0x21, '5': 0x22,
        '6': 0x23, '7': 0x24, '8': 0x25, '9': 0x26, '0': 0x27, '!': 0x1e + 0x80, '@': 0x1f + 0x80,
        '#': 0x20 + 0x80, '$': 0x21 + 0x80, '%': 0x22 + 0x80, '^': 0x23 + 0x80, '&': 0x24 + 0x80,
        '*': 0x25 + 0x80, '(': 0x26 + 0x80, ')': 0x27 + 0x80, ' ': 0x2c  # Space key
    }
