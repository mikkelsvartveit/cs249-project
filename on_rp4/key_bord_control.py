import serial
import time
import sys
import tty
import termios

# pi4 TX GPIO 14
# pi4 RX GPIO 15

ser = serial.Serial('/dev/serial0', 9600)

def send_command(cmd):
    ser.write(cmd.encode())


def get_char():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
        if ord(ch) == 3:  # ASCII Code for Ctrl-C
            raise KeyboardInterrupt
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch

try:
    while True:
        message = get_char()
        if message in ['w', 'd', 's', 'a', 'f', 'p', 'l']:
            print("Sending message:", message)
            ser.write(message.encode())
        elif message == 'q':
            break
except KeyboardInterrupt:
    print("\nInterrupted by user")
