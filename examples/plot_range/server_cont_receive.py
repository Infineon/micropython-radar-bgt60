"""
BGT60TRxx Radar Sensor - Server Side Data Receiver
Reads FFT and threshold data from a serial port and visualizes it using Matplotlib.

Author: Samuel Weissenbacher
Date: 03.2025
"""
import serial
import matplotlib.pyplot as plt
import time
from typing import Tuple, List, Optional

# Configuration
CONFIG = {
    'port': 'COM4',
    'baudrate': 115200,
    'timeout': 1,
    'figure_size': (9, 6),
    'pause_duration': 0.1
}

# Patterns to skip in serial data
SKIP_PATTERNS = [
    "Virtual File System:",
    "fin",
    "Register IRQ-Event",
    ">>>",
    "MicroPython",
    "Type",
    ">"
]

def should_skip_line(line: str) -> bool:
    """Check if the line should be skipped based on skip patterns."""
    return not line or any(pattern in line for pattern in SKIP_PATTERNS)

def parse_data_point(data_point: str) -> Optional[Tuple[float, float]]:
    """
    Parse a single data point into distance and amplitude.
    
    Returns:
        Tuple of (distance, amplitude) or None if parsing fails
    """
    try:
        distance, amplitude = data_point.split(',')
        return float(distance), float(amplitude)
    except (ValueError, IndexError):
        return None

def is_valid_data(distances: List[float], amplitudes: List[float]) -> bool:
    """Check if the data lists are valid for plotting."""
    return len(distances) > 0 and len(distances) == len(amplitudes)

def setup_plot() -> Tuple[plt.Figure, plt.Axes]:
    """Initialize and configure the matplotlib plot."""
    fig, ax = plt.subplots(figsize=CONFIG['figure_size'])
    ax.set_xlabel("Distance in cm")
    ax.set_ylabel("Amplitude in dB")
    ax.set_title("FFT and Threshold Data")
    plt.ion()  # Enable interactive mode
    return fig, ax

def update_plot(ax, fft_distances: List[float], 
                fft_amplitudes: List[float],
                threshold_distances: List[float], 
                threshold_amplitudes: List[float]):
    """Update the plot with new FFT and threshold data."""
    if not (is_valid_data(fft_distances, fft_amplitudes) and 
            is_valid_data(threshold_distances, threshold_amplitudes)):
        return
    
    # Clear and setup the plot
    ax.clear()
    ax.set_xlabel("Distance in cm")
    ax.set_ylabel("Amplitude in dB")
    ax.set_title("FFT and Threshold Data")
    
    # Plot FFT data
    ax.plot(fft_distances, fft_amplitudes, 
            label="Filtered FFT Data", color="blue")
    
    # Plot threshold data
    ax.plot(threshold_distances, threshold_amplitudes,
            label="Threshold Data", color="red", linestyle="--")
    
    ax.legend()
    plt.pause(CONFIG['pause_duration'])

def parse_serial_data(data_string: str, 
                     current_fft_distances: List[float],
                     current_fft_amplitudes: List[float],
                     current_threshold_distances: List[float],
                     current_threshold_amplitudes: List[float]) \
                -> Tuple[List[float], List[float], List[float], List[float]]:
    """
    Parse the incoming serial data string and update FFT or threshold data.
    Only clears the data that is being updated in this message.
    
    Args:
        data_string: The raw serial data string
        current_fft_distances: Current FFT distance values
        current_fft_amplitudes: Current FFT amplitude values
        current_threshold_distances: Current threshold distance values
        current_threshold_amplitudes: Current threshold amplitude values
    
    Returns:
        Tuple of:
        (fft_distances, fft_amplitudes, threshold_distances, threshold_amplitudes)
    """
    # Start with current values
    fft_distances = current_fft_distances.copy()
    fft_amplitudes = current_fft_amplitudes.copy()
    threshold_distances = current_threshold_distances.copy()
    threshold_amplitudes = current_threshold_amplitudes.copy()
    
    data_points = data_string.split(';')
    is_fft_data = None  # None means no data type detected yet
    
    for data_point in data_points:
        data_point = data_point.strip()
        
        if "fft" in data_point:
            # Clear FFT data only when new FFT data arrives
            fft_distances = []
            fft_amplitudes = []
            is_fft_data = True
            
        elif "threshold" in data_point:
            # Clear threshold data only when new threshold data arrives
            threshold_distances = []
            threshold_amplitudes = []
            is_fft_data = False
            
        elif data_point and is_fft_data is not None:
            # Parse the data point
            parsed = parse_data_point(data_point)
            if parsed:
                distance, amplitude = parsed
                if is_fft_data:
                    fft_distances.append(distance)
                    fft_amplitudes.append(amplitude)
                else:
                    threshold_distances.append(distance)
                    threshold_amplitudes.append(amplitude)
    return fft_distances, fft_amplitudes, threshold_distances, threshold_amplitudes

def main():
    """
    Main function to read serial data and visualize radar measurements.
    Continuously reads FFT and threshold data from the serial port and plots it.
    """
    try:
        # Open the serial port
        ser = serial.Serial(CONFIG['port'], 
                            CONFIG['baudrate'], 
                            timeout=CONFIG['timeout'])

        # Data containers for FFT and threshold values
        fft_amplitudes = []
        fft_distance = []
        threshold_amplitudes = []
        threshold_distance = []

        # Setup plot
        _, ax = setup_plot()
        
        # Mark the start time
        start_time = time.time()

        # Main loop
        while True:
            # Read line from serial port
            try:
                data_string = ser.readline().decode('utf-8').strip()
            except UnicodeDecodeError:
                continue

            # Skip unwanted lines
            if should_skip_line(data_string):
                continue

            # Record the time difference for statistics
            end_time = time.time()
            time_diff = end_time - start_time
            print(f"Time difference: {time_diff:.3f} seconds")

            # Parse the data - only updates the data type that's in the message
            fft_distance, fft_amplitudes, threshold_distance, threshold_amplitudes \
                = \
                parse_serial_data(data_string, 
                                fft_distance, 
                                fft_amplitudes,
                                threshold_distance, 
                                threshold_amplitudes)
            
            # Update the plot with current data
            update_plot(ax, fft_distance, fft_amplitudes, 
                       threshold_distance, threshold_amplitudes)
             
            # Reset start time for next iteration
            start_time = time.time()
    except KeyboardInterrupt:
        print("\nExiting...")
    except serial.SerialException as e:
        print(f"Serial port error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
    finally:
        # Clean up
        if ser and ser.is_open:
            ser.close()
            print("Serial port closed")
        plt.close('all')


if __name__ == "__main__":
    main()
