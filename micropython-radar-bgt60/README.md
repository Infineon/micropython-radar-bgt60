# BGT60TR-Sensor Library
With this Library a BGT60TRxx-Sensor can be configured
and used in Micropython.  

## Things to consider when using this Library
- As Micropython is much slower than standard C-Code, the speed is a lot worse in Micropython
    - measured time for a 128-Bit Chirp (Fetch, FFT, High-Pass-Filter and logaritmic scaling):  
        59.93ms or 16.68Hz  
- The readFIFO-Function can only transmit 8192 words,
which consists of 24 Data-Bits
    - Max Transmission possible: 24.576 Bytes
- The Chip returns an Error when Reading while the Stack is full or empty!
- Data can be checked via a CheckData-Function for Overflow/Underflow

# Default Usage
```python
# import Module
from lib.BGT60TRXX import BGT60TRxxModule

# Create Instance
# An optonal parameter can be used to configure
# the Interrupt-Request to a user-defined function
radar_sensor = BGT60TRxxModule(<optional function>)

# Configures all Registers for Usage
radar_sensor.initSensor(<optional compare value for interrupt (in %)>)

data = radar_sensor.read_reg(<ADDR_REG>)
radar_sensor.write_reg(<ADDR_REG>, <DATA>)

# Reads n-Bytes from the Sensor
data = radar_sensor.readFifo(<noOfBytes>)
```
