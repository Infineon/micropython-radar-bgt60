# =============================
# Lib for BGT60TRxx-Sensor
# Samuel Weissenbacher, 03.2025
# =============================
import array
import math

from machine import SPI, Pin

import BGT60TRXX_define as CONST
import dftclass as DFT

class BGT60TRxxModule:
  """Implementation of an BGT60-Radar sensor using one antenna"""

  # Class constants
  _SKIP_FIRST_VALUES = 6  # Workaround for FIFO address misalignment.
                          # 4 words (or 6 bytes) seems to
                          # be the minimum value where
                          # an SPI-Read works.
  _VALID_GSR0_VALUES = (0x00, 0x04)
    
  def __init__(self, word_size: int, spi_interface: SPI, chip_select: Pin, reset: Pin, interrupt_pin: Pin = None, interrupt_handler=None):
    """
      Initialize the BGT60TRxx radar module
      
      Args:
          word_size: Number of samples per chirp
          spi_interface: Configured SPI interface
          chip_select: CS pin for SPI
          reset: Reset pin for sensor
          interrupt_pin: Optional IRQ pin
          interrupt_handler: Optional IRQ callback function
      """
    # SPI Interface
    #=========================================
    self.spi = spi_interface
    self.cs = Pin(chip_select, mode=Pin.OUT, value=1)
    self.reset_radar = Pin(reset, mode=Pin.OUT, value=1)

    # Transfer of SPI Interface
    #============================
    self.word_size = word_size
    self.frame_size = int(word_size*1.5 + 0.5)

    # Validate FIFO size
    if (self.frame_size 
          > (CONST.FIFO_SIZE_BYTE - self._SKIP_FIRST_VALUES)):
      raise Exception("Error! Max Word-Size allowed: {0}".format(CONST.FIFO_SIZE))
    
    self.frame_size  += self._SKIP_FIRST_VALUES

    # Pre-allocate buffers for performance
    self.headerGSR0 = bytearray(CONST.BYTE_SIZE)
    self.data = bytearray(self.frame_size)

    # Load default register configuration
    self.reg_values = CONST.get_init_register_list()

    # Init FFT
    #============
    self.fft = DFT.DFT(self.word_size)
    self.fft_data = array.array('f', (0 for _ in range(self.word_size)))

    # Setup interrupt if provided
    if interrupt_handler is not None:
        self._setup_interrupt(interrupt_pin, interrupt_handler)
    
    # Cache chirp configuration
    self._cache_chirp_config()

  def _setup_interrupt(self, pin: Pin, handler):
    """Configure interrupt pin and handler"""
    self.irq_radar = Pin(pin, mode=Pin.IN, pull=Pin.PULL_UP)
    self.irq_radar.irq(handler=handler, trigger=Pin.IRQ_RISING)
    print(f"Registered IRQ handler: {handler}")
    
  def _cache_chirp_config(self):
      """Cache chirp configuration from registers"""
      self.start_freq = (self.reg_values[CONST.PLL1_0_ADDR] 
                        & CONST.PLL1_0_FSU_MASK)
      self.clk_per_chirp = (self.reg_values[CONST.PLL1_2_ADDR] 
                            & CONST.PLL1_2_RTU_MASK)
      self.step_freq_chirp = (self.reg_values[CONST.PLL1_1_ADDR] 
                              & CONST.PLL1_1_RSU_MASK)
    

  # ===========================
  # Configuration Methods
  # ===========================
    
  def get_range_resolution(self) -> float:
    """ Calculate range resolution in meters per index
    
    Returns:
        Range resolution in meters
    """
    RSU = self.step_freq_chirp
    RTU = self.clk_per_chirp

    delta_f_RF = CONST.STEP_CHIRP_DIVIDER * CONST.F_ADC_CLK * RSU/(2**20)

    bandwidth = (RTU * 8) * delta_f_RF # Multiply with 8! -> See Datasheet BGT60TRXX P.56 RTU
    range_resolution = CONST.SPEED_OF_LIGHT / (2 * bandwidth)

    return range_resolution


  def set_adc_div(self, div: int):
    """ 
    Sets frequency divider of adc. Only enabled with init_sensor-Method 
    """
    self._update_register_field(
        CONST.ADC0_ADDR, div, 
        CONST.ADC0_DIV_MASK, CONST.ADC0_DIV_OFFSET)
    
  def set_chirp_len(self, chirp_len: int):
    """ 
    Sets chirp length of sensor. Only enabled with init_sensor-Method.
    """
    self._update_register_field(
        CONST.PLL1_3_ADDR, chirp_len,
        CONST.APU0_MASK, CONST.APU0_OFFSET)
    
  def configure_chirp(self, N_FSU: int, N_RTU: int, N_RSU: int):
    """ 
    Configures chirp parameters. 
    Only enabled with init_sensor-Method.

    N_FSU = Starting Frequency
    N_RTU = Clock cycles per chirp
    N_RSU = Frequency step per clock cycle

    For calculation of values see Datasheet.
    """
    self._update_register_field(
            CONST.PLL1_0_ADDR, N_FSU,
            CONST.PLL1_0_FSU_MASK, CONST.PLL1_0_FSU_OFFSET)
    self._update_register_field(
        CONST.PLL1_1_ADDR, N_RSU,
        CONST.PLL1_1_RSU_MASK, CONST.PLL1_1_RSU_OFFSET)
    self._update_register_field(
        CONST.PLL1_2_ADDR, N_RTU,
        CONST.PLL1_2_RTU_MASK, CONST.PLL1_2_RTU_OFFSET)
    
    # Update cached values
    self.start_freq = N_FSU
    self.step_freq_chirp = N_RSU
    self.clk_per_chirp = N_RTU

  def set_vga_gain(self, channel: int, gain: int):
      """
      Set VGA gain for specified channel
      
      Args:
          channel: Channel number (1-3)
          gain: Gain value (0-5, see datasheet)
      """
      gain_configs = {
          1: (CONST.CSU1_2_VGA_GAIN1_MASK, CONST.CSU1_2_VGA_GAIN1_OFFSET),
          2: (CONST.CSU1_2_VGA_GAIN2_MASK, CONST.CSU1_2_VGA_GAIN2_OFFSET),
          3: (CONST.CSU1_2_VGA_GAIN3_MASK, CONST.CSU1_2_fVGA_GAIN3_OFFSET),
      }
      
      if channel not in gain_configs:
          raise ValueError(f"Invalid channel: {channel}. Must be 1-3")
      
      mask, offset = gain_configs[channel]
      self._update_register_field(CONST.CSU1_2_ADDR, gain, mask, offset)
    
  def set_compare_value(self, compare_value: int):
    """
    Set compare value using a read-modify-write
    Only enabled with a init_sensor call.
    """
    if compare_value >= 100:
        value = CONST.FIFO_SIZE - 1
    else:
        value = compare_value
    
    self._update_register_field
    (
      CONST.SFCTL_ADDR, 
      value,
      CONST.SFCTL_FIFO_CREF_MASK, 
      CONST.SFCTL_FIFO_CREF_OFFSET
    )

  # ===========================
  # Low-level Register Access
  # ===========================
    
  def read_reg(self, reg_addr: int) -> bytes:  
    """Read register from sensor
    
    Args:
        reg_addr: Register address
        
    Returns:
        Register data (3 bytes)
    """   
    addr = (reg_addr << 1) & 0xFE  # LSB = R/W = 0

    # SPI Read
    self.cs.off()
    data = self.spi.read(CONST.BYTE_SIZE, addr)
    self.cs.on()

    # Check if Error Occured
    status = data[0] & 0x0F
    if status not in self._VALID_GSR0_VALUES:
      raise Exception(
              "Status Register Error! GSR0 = {0}".format(hex(data[0])))
    
    return data[1:]  # Return data bytes only
    
  def write_reg(self, reg_addr: int, data: int):
    """
    Write register to sensor
    
    Args:
        reg_addr: Register address
        data: Data to write (24-bit)
    """
    # Build SPI frame: Addr[7:1] | W | Data[23:0]
    frame = ((reg_addr << CONST.ADDR_OFFSET) & CONST.ADDR_MASK)
    frame |= CONST.WRITE_EN
    frame |= (data & CONST.DATA_MASK)

    data_bytes = frame.to_bytes(CONST.BYTE_SIZE, "big")
        
    # SPI Write
    self.cs.off()
    self.spi.write(data_bytes)
    self.cs.on()

  def _set_bits(self, reg_addr: int, bits: int):
    """ sets data bits inside register to '1' using a read-modify-write """
    data = self.read_reg(reg_addr)
    data = int.from_bytes(data, "big") | bits
    self.write_reg(reg_addr, data)

  def _update_register_field(self, addr: int, 
                             value: int, mask: int, 
                             offset: int):
    """
    Update specific field in register configuration
    
    Args:
        addr: Register address
        value: New value for field
        mask: Bit mask for field
        offset: Bit offset for field
    """
    old_value = self.reg_values[addr]    # read
    new_value = (old_value & ~mask) | (value << offset)    # modify
    self.reg_values[addr] = new_value    # write

  # ===========================
  # Sensor Control Methods
  # ===========================
    
  # inits sensor with all necessary register values.
  # Can set a compare value in percent of the fifo stack 
  # to when an IRQ is send
  def init_sensor(self):
    """ Initializes sensor and writes all registers anew. """
    for reg_addr, reg_data in self.reg_values.items():
      reg_data = (reg_data & CONST.DATA_MASK) # filter out address
      self.write_reg(reg_addr, reg_data)

  def start_frame(self):
    """ Start frame generation and leave Deep-Sleep-Mode. """
    self._set_bits(CONST.MAIN_ADDR, CONST.START_FRAME)
    
  def enable_test_mode(self):
    """ Enables Test-Mode (LFSR Enable) for Sensor. """
    # Enables TestMode
    self._set_bits(CONST.SFCTL_ADDR, CONST.TEST_MODE_EN)

    # Init RFT0 Register
    self._set_bits(CONST.RFT0_ADDR, CONST.TEST_IF_ENABLE)

    self.reset_fsm()

  def reset_fifo(self):
    """ Resets FIFO and FSM"""
    self._set_bits(CONST.MAIN_ADDR, CONST.FIFO_RESET)

  def reset_fsm(self):
    """ Resets FSM"""
    self._set_bits(CONST.MAIN_ADDR, CONST.FSM_RESET)

  def reset(self):
    """ Resets software, FIFO and FSM"""
    self.write_reg(CONST.MAIN_ADDR, CONST.SOFT_RESET)

  # ===========================
  # Data Acquisition Methods
  # ===========================
    
  @micropython.viper
  def read_FIFO(self):    
    """ Read n-words from FIFO-Stack.
    Checks Header-Information for Error (like Overflow/Underflow).
    Data is stored inside self.data object
    """
    # Enable Burst Mode and read GSR0 Register
    self.cs.value(0)
    self.spi.write_readinto(CONST.ENABLE_BURST_MODE, self.headerGSR0)

    if self.headerGSR0[3] not in self._VALID_GSR0_VALUES:
      raise Exception(
        "Error detected in FIFO-Read. GSR0 = {0}".format(hex(self.headerGSR0[3])))

    # Read from SPI
    self.spi.readinto(self.data, 0x00)
    self.cs.value(1)

  @micropython.viper
  def unpack_adc_data(self):
    """Unpacks recorded adc data
    into real-part of fft.    
    
    words (adc) are represented in a byte array:
    a2 a1;  a0 b2;  b1 b0
    """
    byte_index:uint = uint(self._SKIP_FIRST_VALUES)
    fft_index:uint = 0
    frame_len:uint = uint(self.frame_size)

    while byte_index < frame_len - 2:
        # Extract 3 bytes from the byte array
        byte1:uint = uint(self.data[byte_index])
        byte2:uint = uint(self.data[byte_index + 1])
        byte3:uint = uint(self.data[byte_index + 2])
        
        # Reconstruct two 12-bit samples
        a:uint = (((byte1 & 0xFF) << 4) 
                  | ((byte2 & 0xF0) >> 4))
        b:uint = (((byte2 & 0x0F) << 8) 
                  | ((byte3 & 0xFF) >> 0))

        # Store in FFT real part
        self.fft.re[fft_index] = a
        self.fft.re[fft_index + 1] = b

        # self.fft.im is reset by running a FORWARD-FFT

        fft_index += 2
        byte_index += 3

  # ===========================
  # Signal Processing Methods
  # ===========================
    
  @micropython.viper
  def apply_highpass_filter(self):
    """High-Pass Filter Chebyscheff 2nd Order
    over real-part data before fft.
    """
    # High-Pass Filter
    x0: float = 0.0
    x1: float = 0.0
    x2: float = 0.0
    y0: float = 0.0
    y1: float = 0.0
    y2: float = 0.0

    i: int = 0
    limit: int = int(self.word_size)
    while i < limit:
      x2 = x1
      x1 = x0
      x0 = float(self.fft.re[i])

      y2 = y1
      y1 = y0

      # Apply filter coefficients
      y0 = x0*0.943 - x1*1.885 + x2*0.943 + y1*1.881 - y2*0.890 # Chebyshev 2nd Order
      
      self.fft.re[i] = y0
      i += 1

  @micropython.viper
  def apply_anti_coupling_filter(self):
    """Anti Coupling filter for 
    Receiver/Transmitter Antenna
    """
    # Calculation: Typical: sig - mov_avg
    # y[i] = x[i] - 1/N sum_(k = i - (N-1))^(i)(x[k])
    # y[i] = (N-1)/N * x[i] - 1/N sum_(k = i - (N-1))^(i-1)(x[k])
    # Meaning: b0 = (N-1)/N
    # all other bx = -1/N
    # For Decoupling we use a broad moving average to
    # calculate reflections out: N=10
    x0: float = 0.0
    x1: float = 0.0
    x2: float = 0.0
    x3: float = 0.0
    x4: float = 0.0
    x5: float = 0.0
    x6: float = 0.0
    x7: float = 0.0
    x8: float = 0.0
    x9: float = 0.0

    b0 : float = 0.9 # (N-1)/N
    bx : float = -0.1 # -1/N

    i: int = 0
    limit: int = int(self.word_size)
    while i < limit:
      x9 = x8
      x8 = x7
      x7 = x6
      x6 = x5
      x5 = x4
      x4 = x3
      x3 = x2
      x2 = x1
      x1 = x0
      x0 = float(self.fft_data[i])

      # Apply filter coefficients
      y0 = x0*b0 + x1*bx + x2*bx + x3*bx + x4*bx + x5*bx + x6*bx + x7*bx + x8*bx + x9*bx
      
      self.fft.re[i] = y0
      i += 1
      
    # Apply linear attenuation to compensate for near-field effects
    attenuation: float = 80.0
    attenuation_step: float = 1.5
    
    n: int = 0
    while n < limit:
      if attenuation > 0.0:
        if self.fft_data[n] < attenuation:
            self.fft_data[n] = 0.0
        else:
            self.fft_data[n] -= attenuation
        attenuation -= attenuation_step
      n += 1
        
    # Zero out first 3 samples (Tx-Rx coupling region)
    j : int = 0
    while(j < 3):
      self.fft_data[j] = 0.0
      j += 1

  @micropython.native
  def compute_magnitude_spectrum(self):
    for x in range(self.word_size):
      self.fft_data[x] = abs(self.fft.re[x] + self.fft.im[x]*1j)
  
  @micropython.native
  def convert_to_db(self):
    """ Convert magnitude spectrum to dB scale
    Applies floor to values which are too small.
    """
    for i in range(self.word_size):
      self.fft_data[i] = max(0.001, self.fft_data[i])
      # Convert to dB
      self.fft_data[i] = (20.0 * math.log10(self.fft_data[i]))


  # ===========================
  # High-level Processing
  # ===========================
    
  @micropython.viper
  def read_distance(self):
    """
    Complete distance measurement pipeline:
    1. Read FIFO data
    2. Unpack ADC samples
    3. Apply high-pass filter
    4. Compute FFT (range profile)
    5. Convert to magnitude spectrum
    6. Convert to dB scale
    7. Apply anti-coupling filter
    """
    self.read_FIFO()
    self.unpack_adc_data()
    self.apply_highpass_filter()  
    self.fft.run(DFT.FORWARD)  
    self.convert_to_db()
    self.compute_magnitude_spectrum()
    self.apply_anti_coupling_filter()

# ===========================
# Utility Functions
# ===========================

def calculate_RTU(adc_div: int, samples_per_chirp: int) -> int:
  """Calculate clock cycles per chirp (RTU register value)
  Args:
      adc_div: ADC clock divider
      samples_per_chirp: Number of samples per chirp
      
  Returns:
      RTU register value
  """
  return (adc_div * samples_per_chirp)//8 + CONST.T_SETUP
  
def calculate_FSU(start_freq_khz: int) -> int:
  """Calculate starting frequency register value (FSU)
  Args:
      start_freq_khz: Starting frequency in kHz
      
  Returns:
      FSU register value (24-bit two's complement)
  """
  fsu = int(2**20 * ((start_freq_khz / 640_000) - 96))
  return fsu & 0xFFFFFF  # 24-bit mask

def calculate_RSU(bandwidth_hz: int, RTU: int) -> int:
  """Calculate frequency step per clock cycle (RSU register value)
  Args:
      bandwidth_hz: Desired bandwidth in Hz
      RTU: Clock cycles per chirp (from calculate_RTU)
      
  Returns:
      RSU register value
  """
  delta_rf = bandwidth_hz / (8 * RTU)
  return int(2**20 * delta_rf / 640_000)


def calculate_range_from_index(index: int, range_resolution: float) -> float:
  """ Convert FFT bin index to physical range
  Args:
      index: FFT bin index
      range_resolution: Range resolution in meters (from get_range_resolution)
      
  Returns:
      Range in meters
  """
  return index * range_resolution