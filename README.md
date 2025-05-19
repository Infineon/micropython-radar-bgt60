# MicroPython Driver for 60 GHz Radar BGT60TRxx
With this library a XENSIV™ BGT60TRxx 60 GHz radar sensor can be configured
and used with MicroPython.

> [!NOTE]  
> This project is work in progress and not covering all functions
of the sensor yet.   
> If you are missing any functionality feel free to [contribute](https://github.com/Infineon/micropython-radar-bgt60/fork) or [open an issue](https://github.com/Infineon/micropython-radar-bgt60/issues).

## Overview
The [XENSIV™ BGT60TRxx](https://www.infineon.com/cms/en/product/sensor/radar-sensors/radar-sensors-for-iot/60ghz-radar/)
is a 60 GHz radar sensor developed by Infineon, designed for advanced sensing applications.

It supports detection ranges of up to 15 meters and features low power consumption,
making it well-suited for a wide range of IoT use cases.

Typical use cases:
 - Presence Detection/Segmentation
 - Touchless Interaction
 - Vital Sensing

## Dependencies
This module depends on the [micropython-fourier module](https://github.com/peterhinch/micropython-fourier),
written by Peter Hinch.

TODO: Refer to modified version of module.

Dependencies can be installed using [mip](https://docs.micropython.org/en/latest/reference/packages.html#installing-packages-with-mip),
a package manager built-in to MicroPython:
```
import mip
mip.install('github:infineon/TODO')
```

TODO: Dependency installation might not be needed, if handled in package.json.

## Installation of this Module
Once the dependencies are installed, this module can be installed using the same method:
```
import mip
mip.install('github:infineon/micropython-radar-bgt60')
```

TODO: Add package.json to install library & dependencies automatically.

## Usage

### MicroPython Firmware Installation
Before using this library, ensure that the MicroPython firmware is installed on your device.
If you are using a PSOC™ 6 board, you can find the installation instructions [here](https://ifx-micropython.readthedocs.io/en/latest/psoc6/intro.html#install-micropython-on-the-board).

### Things to consider when using this Library
- MicroPython executes code significantly slower than standard C, resulting in reduced performance when using this library:
    - measured time for a 128-bit chirp (fetch, FFT, high-pass filter, and logarithmic scaling):
        59.93 ms or 16.68 Hz  
- The `readFifo` function can only transmit 8192 words,
which consist of 24 data bits
    - Maximum transmission possible: 24.576 bytes
- The chip returns an error when reading while the stack is full or empty
- Data can be checked for overflow or underflow errors using the `checkData` function

### Example Code
```python
# import Module
import BGT60TRXX as BGT

# Create Instance
# An optonal parameter can be used to configure
# the Interrupt-Request to a user-defined function
radar_sensor = BGT.BGT60TRxxModule(<wordsize>, <optional function>)

# Configure Register Values with pre-defined functions
radar_sensor.setCompareValue(50) # in '%'
#...

# Configures all Registers for Usage
# They need to be configured before hand
radar_sensor.initSensor()

data = radar_sensor.read_reg(<ADDR_REG>)
radar_sensor.write_reg(<ADDR_REG>, <DATA>)

# reset fifo state
radar_sensor.resetFIFO()

# start frame generation before a fifo read
radar_sensor.startFrame()

# Reads from the Sensor.
# data is stored inside radar_sensor.data
radar_sensor.readFifo()

# Read and calculate Distance-Profile
radar_sensor.readDistance()
```