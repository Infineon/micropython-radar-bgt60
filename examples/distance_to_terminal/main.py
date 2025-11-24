import time
import math
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

try:
 import BGT60TRXX as BGT
except ImportError:
  # Fetch libs to memory
  # Using WiFi of chip.
  nic = network.WLAN()
  nic.connect(ssid="<your-ssid>", key="<your-key>")

  # Installs libs and dependencies
  mip.install("github:infineon/micropython-radar-bgt60")
  nic.disconnect()
  import BGT60TRXX as BGT

# const values
no_of_chirps = const(1)
samples_per_chirp = const(128)
words = const(samples_per_chirp * no_of_chirps)
ADC_DIV = const(60)
start_freq = const(58_000_000) # in kHz
bandwidth = const(4_500_000) # in kHz

threshold = const(8.0)

# set spi interface for communication
spi_interface = SPI(
        baudrate=50_000_000, 
        polarity=0, 
        phase=0, 
        bits=8, 
        firstbit=SPI.MSB, 
        sck='P12_2', 
        mosi='P12_0', 
        miso='P12_1')

# set radar sensor and standard config
radar_sensor = BGT.BGT60TRxxModule(words, spi_interface, Pin("P12_3"), Pin("P11_1"), Pin("P11_0"))
radar_sensor.set_adc_div(ADC_DIV)
radar_sensor.set_chirp_len(samples_per_chirp)

FSU = BGT.calculateFSU(start_freq)
RTU = BGT.calculateRTU(ADC_DIV, samples_per_chirp)
RSU = BGT.calculateRSU(bandwidth, RTU)
radar_sensor.configure_chirp(FSU, RTU, RSU)

radar_sensor.set_vga_gain_ch1(3)  
range_resolution = radar_sensor.get_range_resolution() * 100 # in cm

threshold_func = array.array("f", (threshold for _ in range(int(radar_sensor.fft.length)//2)))
@micropython.native
def find_nearest_peak(radar_sensor: BGT.BGT60TRxxModule):
  """ detec first peak in signal.
  """
  for i in range(len(radar_sensor.fft_data)//2):
    if radar_sensor.fft_data[i] > threshold_func[i]:
      print(">Peak detected at: {:.1f} cm".format(i*range_resolution / no_of_chirps))
      return

#@micropython.native
def readFIFO(radar_sensor: BGT.BGT60TRxxModule):
  """Read FIFO Stack of Sensor and prints the measured data""" 
  radar_sensor.readDistance()
  
  # enable line to also print detected peaks in cm
  find_nearest_peak(radar_sensor)

def main():
  global radar_sensor
  radar_sensor.reset()
  radar_sensor.initSensor()
  radar_sensor.startFrame()

  while(True):
    readFIFO(radar_sensor)
    radar_sensor.resetFIFO()
    radar_sensor.startFrame()

if __name__ == "__main__":
    main()