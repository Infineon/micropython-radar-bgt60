# Micropython-Radar BGT60TR13C Example Program
This example program reads data from the BGT60TR13C radar sensor on the CY8CKIT-062S2-AI Kit from Infineon and prints the distance of the nearest object to the terminal.

## Threshold Function
To detect a distance a threshold is used.
This needs to be calibrated using the Plot-Range-Example Program.

## Usage
1) Upload the ```main.py``` to the microcontroller
2) Open a Terminal
3) The terminal output will be in the format: 
    >Peak detected at: \<x> cm