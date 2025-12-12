import serial
import matplotlib.pyplot as plt
import time
import numpy as np

# Open the serial port
ser = serial.Serial('COM4', 115200, timeout=1)

# Data containers for FFT and threshold values
fft_values = []
fft_distance_values = []
threshold_values = []
threshold_distance_values = []

# Send initialization command
ser.write(b"fin\n")

# Mark the start time
start_time = time.time()

# Create a figure with a single subplot
fig, ax = plt.subplots(figsize=(9, 6))
ax.set_xlabel("Distance")
ax.set_ylabel("Amplitude")
ax.set_title("FFT and Threshold Data")
plt.ion()  # Enable interactive mode

while True:
    try:
        # Read a line from the serial port
        data_string = ser.readline().decode('utf-8').strip()
        if ("Virtual File System:" in data_string 
            or "fin" in data_string 
            or "Register IRQ-Event" in data_string 
            or ">>>" in data_string 
            or "MicroPython" in data_string 
            or "Type" in data_string
            or ">" in data_string):
            pass
        elif data_string:
            # Record the time difference for statistics
            end_time = time.time()
            time_diff = end_time - start_time
            print("Time difference:", time_diff, "seconds")
            
            # Split the input into individual data points
            data_points = data_string.split(';')  # Split the incoming data into points
            fft_data_incoming = False
            for data_point in data_points:
                if "fft" in data_point:
                    fft_values = []
                    fft_distance_values = []
                    fft_data_incoming = True
                
                elif "threshold" in data_point:
                    threshold_values = []
                    threshold_distance_values = []
                    fft_data_incoming = False
                elif data_point: # Check if data point is not empty
                    try:
                        distance, amplitude = data_point.split(',')
                    except ValueError:
                        break # Skip malformed data points
                    if fft_data_incoming:
                        fft_distance_values.append(float(distance))
                        fft_values.append(float(amplitude))
                    else:
                        threshold_distance_values.append(float(distance))
                        threshold_values.append(float(amplitude))
                        
            # Plotting the data
            if( len(fft_distance_values) > 0 and len(threshold_distance_values) > 0):            
                # Clear the current plot for updates
                ax.clear()
                ax.set_xlabel("Distance in cm")
                ax.set_ylabel("Amplitude in dB")
                ax.set_title("FFT and Threshold Data")
                
                # Plot the FFT data using filtered distances
                ax.plot(fft_distance_values, fft_values, label="Filtered FFT Data", color="blue")
                
                # Plot the threshold data using raw distance values
                ax.plot(threshold_distance_values, threshold_values, label="Threshold Data", color="red", linestyle="--")
                
                # Add a legend to distinguish between the two streams
                ax.legend()
            
            # Update the plot
            plt.pause(0.1)
            
            # Send an acknowledgment or further instruction to the device
            ser.write(b"fin\n")
            start_time = time.time()
    except KeyboardInterrupt:
        print("Exiting...")
        break
# Close the serial port after exiting
ser.close()