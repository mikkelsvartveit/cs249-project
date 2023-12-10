import serial
import time

# Open the serial port
ser = serial.Serial('/dev/ttyAMA0', 9600, timeout=1)
time.sleep(3)
try:
    # Send a test message
    test_message = "Hello, Serial!"
    ser.write(test_message.encode())

    # Wait for a short period to ensure transmission
    time.sleep(1)

    # Read the incoming data
    incoming_data = ser.read(ser.inWaiting())

    # Decode the incoming data and print it
    print("Received:", incoming_data.decode())
finally:
    # Close the serial port
    ser.close()