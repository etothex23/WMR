import serial
import pynmea2
import time

# --- Configuration ---
# On Mac, your device is likely /dev/tty.usbmodemXXXX
# On Linux, it's often /dev/ttyACM0 or /dev/ttyUSB0
#SERIAL_PORT = "/dev/tty.usbserial-0001"
SERIAL_PORT = "/dev/tty.usbmodem2101"
BAUD_RATE = 9600
# ---------------------

def read_gps_data():
    """Connects to the GPS dongle and prints parsed data."""
    print(f"Attempting to connect to {SERIAL_PORT} at {BAUD_RATE} baud...")
    
    try:
        # Connect to the serial port
        with serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1) as ser:
            print("Connection successful. Reading GPS data...")
            while True:
                try:
                    # Read one line of data from the dongle
                    line = ser.readline().decode('ascii', errors='replace').strip()

                    # If the line contains NMEA data, parse it
                    if line.startswith('$'):
                        msg = pynmea2.parse(line)
                        
                        # We are interested in GGA sentences, which have the fix info
                        if isinstance(msg, pynmea2.GGA):
                            if msg.is_valid:
                                print(f"Fix Acquired: YES | Satellites: {msg.num_sats} | "
                                      f"Lat: {msg.latitude:.6f} | Lon: {msg.longitude:.6f} | "
                                      f"Alt: {msg.altitude} {msg.altitude_units}")
                            else:
                                print(f"Fix Acquired: NO  | Satellites: {msg.num_sats} | Searching...")
                    
                    time.sleep(0.5) # Don't spam the console

                except pynmea2.ParseError:
                    # This happens if the line is incomplete or corrupted; just ignore it
                    continue
                except KeyboardInterrupt:
                    print("\nExiting program.")
                    break

    except serial.SerialException as e:
        print(f"Error: Could not open serial port {SERIAL_PORT}. Details: {e}")

if __name__ == "__main__":
    read_gps_data()