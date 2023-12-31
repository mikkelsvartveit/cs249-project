import serial
import keyboard


serial_port = "/dev/tty.HC-05" # name of the bluetooth device 
baud_rate = 9600               # baud rate for communication 

try:
    bluetooth_serial = serial.Serial(serial_port, baud_rate, timeout=1)
    print("Connected to HC-05\n")

    # Sending a test message
    message = "0\n"

    while True:

        message = keyboard.read_key()
        if (message == 'w' or message == 'd' or message == 's' or message == 'a' or message == 'f'):
            #print("Sending message:", message)
            bluetooth_serial.write(message.encode())
        elif (message == 'q'):
            break
    

        # Wait for response
        #while bluetooth_serial.inWaiting() <= 0:
        #    continue

        # # Receiving response
        #incoming = bluetooth_serial.readline().decode()
        #print(f"\nReceived message:", incoming)

except serial.SerialException as e:
    print(f"Error connecting to {serial_port}: {e}")

finally:
    if "bluetooth_serial" in locals() and bluetooth_serial.is_open:
        bluetooth_serial.close()
