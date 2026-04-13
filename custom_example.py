import time
from ppk2_api.ppk2_api import PPK2_API
# Flush serial garbage before handing over to PPK2_API
try:
    with serial.Serial(ppk2_port, baudrate=115200, timeout=1) as ser:
        ser.reset_input_buffer()
        ser.reset_output_buffer()
except Exception as e:
    print(f"Warning: Failed to flush serial buffers: {e}")
print("Attempting to list PPK2 devices...")
ppk2s_connected = PPK2_API.list_devices()
print(f"Raw output of ppk2s_connected: {ppk2s_connected}")

# --- MODIFIED LOGIC HERE ---
if len(ppk2s_connected) == 1:
    # If ppk2s_connected is ['/dev/ttyACM0'], then ppk2s_connected[0] is '/dev/ttyACM0'
    ppk2_port = ppk2s_connected[0]
    ppk2_serial = "N/A" # We don't get the serial number in this specific list format
    print(f"Found PPK2 at {ppk2_port} (Serial Number: {ppk2_serial})")
elif len(ppk2s_connected) > 1:
    print(f"Too many connected PPK2's found: {ppk2s_connected}")
    # You'll need more sophisticated logic here if you expect multiple PPK2s
    # and need to select a specific one. For now, we'll exit.
    exit()
else:
    print("No PPK2 devices found. Please ensure it's connected and powered on.")
    exit()
# --- END MODIFIED LOGIC ---

try:
    # Initialize the PPK2_API object with the correct serial port
    # ppk2_test = PPK2_API(ppk2_port, timeout=1, write_timeout=1, exclusive=True) # This line is good
    ppk2_test = PPK2_API(ppk2_port, timeout=1, write_timeout=1, exclusive=True)


    # Set up the power profiler (example: source meter mode, 3.3V)
    ppk2_test.get_modifiers()
    ppk2_test.set_source_voltage(3300) # Set source voltage in mV (e.g., 3.3V)
    ppk2_test.use_source_meter() # Set source meter mode

    # Toggle DUT power ON (if using as a source meter)
    ppk2_test.toggle_DUT_power("ON")

    print("Starting measurement...")
    ppk2_test.start_measuring()

    # Read measured values in a loop
    for i in range(10): # Read 10 times for a quick test
        read_data = ppk2_test.get_data()
        if read_data != b'':
            samples = ppk2_test.get_samples(read_data)
            if samples:
                # Samples contain (timestamp, current_mA, voltage_mV)
                # Let's just print the average current for now
                # The get_samples method when called without raw_digital returns a list of (timestamp, current, voltage) tuples
                currents = [s[1] for s in samples if s[1] is not None] # Assuming s[1] is current
                if currents:
                    avg_current = sum(currents) / len(currents)
                    print(f"Average current: {avg_current:.2f} mA")
                else:
                    print("No valid current samples received.")
        time.sleep(0.5) # Wait a bit before next read

    print("Stopping measurement...")
    ppk2_test.stop_measuring()
    ppk2_test.toggle_DUT_power("OFF")
    del ppk2_test
    print("PPK2 API session ended cleanly.")

except Exception as e:
    print(f"An error occurred: {e}")
