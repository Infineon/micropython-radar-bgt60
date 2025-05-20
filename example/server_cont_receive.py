import serial
import matplotlib.pyplot as plt
import time

# Open the serial port
ser = serial.Serial('COM15', 115200, timeout=1)

fft_values = []
distance_values = []

ser.write(b"fin\n")

start_time = time.time()

# Create a figure with multiple subplots
fig, axs = plt.subplots(1, figsize=(9, 20))
axs.set_xlabel("Distance")
axs.set_ylabel("Amplitude")
axs.set_title("FFT Data")

plt.ion()  # Enable interactive mode

while True:
    # Read a line from the serial port
    data_string = ser.readline().decode('utf-8').strip()

    # Check if the data string is a system message
    if ("Virtual File System:" in data_string 
        or "fin" in data_string 
        or "Register IRQ-Event" in data_string 
        or ">>>" in data_string 
        or "MicroPython" in data_string 
        or "Type" in data_string
        or ">" in data_string):
        pass
    elif(data_string):
        end_time = time.time()
        time_diff = end_time - start_time
        print("Time difference:", time_diff, "seconds")
        # Split the data string into individual data points
        data_points = data_string.split(';')
        
        for data_point in data_points:
            if data_point:  # Check if the data point is not empty
                # Split the data point into distance and amplitude
                distance, amplitude = data_point.split(',')
                distance = float(distance)
                amplitude = float(amplitude)
                
                # Append the values to the lists
                distance_values.append(distance)
                fft_values.append(amplitude)

        # Clear the current plot
        axs.clear()
        axs.set_xlabel("Distance")
        axs.set_ylabel("Amplitude")
        axs.set_title("FFT Data")

        # Plot the FFT data
        axs.plot(distance_values, fft_values)

        # Update the plot
        plt.pause(0.1)

        ser.write(b"fin\n")
        start_time = time.time()

        ## Reset the list of ADC values
        fft_values = []
        distance_values = []
