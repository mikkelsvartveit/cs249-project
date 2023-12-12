import serial 
import time
import sys
import tty
import termios
import threading  # Import threading module


class Steer:
    
    def __init__(self, baud_rate = 9600) -> None:
        self.baud_rate = baud_rate
        self.ser = serial.Serial('/dev/serial0',self.baud_rate)
        self.defined_keys = ['w', 'd', 's', 'a', 'f', 'p', 'l']

    def _send_command(self, cmd, delay = 0):
        if delay == 0:
            self.ser.write(cmd.encode())
        else:
            time.sleep(delay)
            self.ser.write(cmd.encode())
    
    def _get_char(self):
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
            if ord(ch) == 3: # ASCII Code for Ctrl-C
                raise KeyboardInterrupt
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch
    
    def turn_left(self):
        self._send_command('a')
        # threading.Thread(target=self._send_command, args=('f',  0.2)).start()
    
    def turn_right(self):
        self._send_command('d')
        # threading.Thread(target=self._send_command, args=('f',  0.2)).start()

    def forward(self):
        self._send_command('w')

    def stop(self):
        self._send_command('f')    

    
    def keyboard(self):
        try:
            while True:
                message = self._get_char()
                if message in self.defined_keys:
                    print("Sending message:", message)
                    self._send_command(message)
                elif message == 'q':
                    break
        except KeyboardInterrupt:
            print('\nInterrupted by user')

if __name__ == '__main__':
    s = Steer()
    s.forward()
    time.sleep(1)
    s.stop()
    time.sleep(1)
    s.turn_right()
    s.keyboard()
    s.stop()
    #s.keyboard()
