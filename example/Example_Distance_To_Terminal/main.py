import time
import math
import array
import network
import mip

from machine import Pin

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
start_freq = const(62_500_000) # in kHz
bandwidth = const(2_000_000) # in kHz

threshold_for_lower_freq = const(45.0)
threshold_for_upper_freq = const(24.5)

# set radar sensor and standard config
radar_sensor = BGT.BGT60TRxxModule(words)
radar_sensor.set_adc_div(ADC_DIV)
radar_sensor.set_chirp_len(samples_per_chirp)

FSU = BGT.calculateFSU(start_freq)
RTU = BGT.calculateRTU(ADC_DIV, samples_per_chirp)
RSU = BGT.calculateRSU(bandwidth, RTU)
radar_sensor.configure_chirp(FSU, RTU, RSU)

radar_sensor.set_vga_gain_ch1(4)  
range_resolution = radar_sensor.get_range_resolution() * 100 # in cm

threshold_func = array.array("f", (0.0 for _ in range(int(radar_sensor.fft.length//2))))
@micropython.native
def find_nearest_peak(signal: array.array, threshold_index_start: int, threshold_index_end: int):
  """ detec first peak in signal.
  Uses a Threshold Function:
    if x < start -> threshold_for_lower_freq
    if x > end   -> threshold_for_upper_freq
    else         -> build linear function between first two
  """
  global threshold_func
  for i in range(len(signal)):
    if (i < threshold_index_start):
      threshold_func[i] = threshold_for_lower_freq
    elif(i > threshold_index_end):
      threshold_func[i] = threshold_for_upper_freq
    else:
      # kx + d
      threshold_func[i] = (-((threshold_for_lower_freq-threshold_for_upper_freq)
                             /(threshold_index_end-threshold_index_start))
                           *(i-threshold_index_start) 
                           + threshold_for_lower_freq)
  for i in range(1, len(signal) - 1):
    if signal[i] > threshold_func[i]:
      print(">Peak detected at: {:.1f} cm".format(i*range_resolution / no_of_chirps))
      return

fft_data = array.array("f", (0.0 for _ in range(int(radar_sensor.fft.length//2))))

@micropython.native
def fft_to_dB(fft_data: array.array, length: int):
  """ Recalculate a given string to a logaritmic scale.
  Clips signal when to low.
  """
  i:int = 1
  while i < length:
    # clip signal
    fft_data[i] = max(0.001, fft_data[i])
    # calculate to dB-Scale
    fft_data[i] = (20.0 * math.log10(fft_data[i]))
    i += 1
  fft_data[0] = 0 # Remove DC-Value

@micropython.native
def readFIFO(radar_sensor: BGT.BGT60TRxxModule):
  """Read FIFO Stack of Sensor and prints the measured data""" 
  global fft_data
  radar_sensor.readDistance()
  
  len = radar_sensor.fft.length//2
   
  for x in range(len):
    fft_data[x] = abs(radar_sensor.fft.re[x] + radar_sensor.fft.im[x]*1j)
  BGT.checkData(fft_data, len)

  fft_to_dB(fft_data, len)

  # enable line to also print detected peaks in cm
  find_nearest_peak(fft_data, 50/(range_resolution/ no_of_chirps), 
                    190/(range_resolution/ no_of_chirps))

was_button_pressed = False
def button_pressed(event):
  """ Event when button is pressed.
  Used, so no endless loop is generated for MicroPython
  """
  global was_button_pressed
  was_button_pressed = True

@micropython.native
def printString(radar_sensor: BGT.BGT60TRxxModule):
  """ prints calculated data in fft_data.
  Format: <distance>,<data>;
  """
  global fft_data
  data_string = ""
  for x in range(radar_sensor.fft.length//2):
      distance = x*range_resolution / no_of_chirps
      data_string += "{:.1f},{:.2f};".format(distance, fft_data[x])
  print(data_string)

def main():
  UserButton = Pin("P5_2", mode=Pin.IN, pull=Pin.PULL_UP)
  UserButton.irq(handler=button_pressed,trigger=Pin.IRQ_FALLING)
  UserLED = Pin("P5_3", mode=Pin.OUT, value=0)

  
  radar_sensor.reset()
  radar_sensor.initSensor()
  radar_sensor.startFrame()

  while(not was_button_pressed):
    readFIFO(radar_sensor)
    #movingAverageFilter(radar_sensor)
    #printString(radar_sensor)
    radar_sensor.resetFIFO()
    radar_sensor.startFrame()
    
  UserLED.value(1)

if __name__ == "__main__":
    main()