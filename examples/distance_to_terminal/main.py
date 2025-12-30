"""
BGT60TRxx Radar Sensor Example
Demonstrates distance measurement using the BGT60 radar module

Author: Samuel Weissenbacher
Date: 03.2025
"""

import array
import network
import mip

from machine import Pin, SPI

# Libraries can be installed
# using the MIP via 2 Methods.
# 1.) Install using mpremote, this has to
#     be done in a terminal
# 2.) The code sample below
#     installs the libs using
#     a given wlan connection

# ===========================
# Library Import with Auto-Install
# ===========================
try:
 import BGT60TRXX as BGT
except ImportError:
  print("BGT60TRXX library not found. Installing from GitHub...")

  # Connect to WiFi
  nic = network.WLAN()
  nic.connect(ssid="<your-ssid>", key="<your-key>")

  # Installs libs and dependencies
  mip.install("github:infineon/micropython-radar-bgt60")
  nic.disconnect()
  import BGT60TRXX as BGT


# ===========================
# Configuration Constants
# ===========================

# Chirp Configuration
no_of_chirps = const(1)
samples_per_chirp = const(128)
total_samples = const(samples_per_chirp * no_of_chirps)

# RF Configuration
start_freq = const(58_000_000) # in kHz
bandwidth = const(4_500_000) # in kHz
vga_gain = const(3)  # VGA Gain Setting (0-5)

# Detection Parameters
detection_threshold_dB = const(8.0)

# ADC Configuration
adc_div = const(60)

# SPI Configuration
SPI_BAUDRATE = 50_000_000
SPI_POLARITY = 0
SPI_PHASE = 0

# Pin Configuration (PSoC 6 specific)
PIN_SCK = 'P12_2'
PIN_MOSI = 'P12_0'
PIN_MISO = 'P12_1'
PIN_CS = 'P12_3'
PIN_RESET = 'P11_1'
PIN_IRQ = 'P11_0'

# set spi interface for communication
spi_interface = SPI(
        baudrate=SPI_BAUDRATE, 
        polarity=SPI_POLARITY, 
        phase=SPI_PHASE, 
        bits=8, 
        firstbit=SPI.MSB, 
        sck=PIN_SCK, 
        mosi=PIN_MOSI, 
        miso=PIN_MISO)

# set radar sensor and standard config
radar_sensor = BGT.BGT60TRxxModule(total_samples, spi_interface, Pin(PIN_CS), Pin(PIN_RESET), Pin(PIN_IRQ))
radar_sensor.set_adc_div(adc_div)
radar_sensor.set_chirp_len(samples_per_chirp)

FSU = BGT.calculate_FSU(start_freq)
RTU = BGT.calculate_RTU(adc_div, samples_per_chirp)
RSU = BGT.calculate_RSU(bandwidth, RTU)
radar_sensor.configure_chirp(FSU, RTU, RSU)

radar_sensor.set_vga_gain(1,3)  
range_resolution = radar_sensor.get_range_resolution() * 100 # in cm

@micropython.native
def detect_nearest_target(radar_sensor: BGT.BGT60TRxxModule):
  """ Detect first peak in signal.
  """
  for i in range(len(radar_sensor.fft_data)//2):
    if radar_sensor.fft_data[i] > detection_threshold_dB:
      print(">Peak detected at: {:.1f} cm".format(
        BGT.calculate_range_from_index(i, range_resolution)
        / no_of_chirps)
      )
      return

def read_FIFO(radar_sensor: BGT.BGT60TRxxModule):
  """Read FIFO Stack of Sensor and prints the measured data""" 
  radar_sensor.read_distance()
  
  # enable line to also print detected peaks in cm
  detect_nearest_target(radar_sensor)

def reset_and_restart(radar_sensor: BGT.BGT60TRxxModule):
    """Reset FIFO and restart frame acquisition"""
    radar_sensor.reset_fifo()
    radar_sensor.start_frame()

def main():
  global radar_sensor
  radar_sensor.reset()
  radar_sensor.init_sensor()
  radar_sensor.start_frame()

  while(True):
    read_FIFO(radar_sensor)
    reset_and_restart(radar_sensor)

if __name__ == "__main__":
    main()