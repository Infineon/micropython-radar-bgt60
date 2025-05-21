# ================================================
# defines const Values needed for BGT60TRXX Sensor
# Samuel Weissenbacher, 03.2025
#=================================================

# Register Mask and Offset Values
ADDR_MASK                = const(0xFE000000)
ADDR_OFFSET              = const(25)

DATA_MASK                = const(0x00FFFFFF)
DATA_OFFSET              = const(0)

BURST_MODE               = const(0xFF)
BURST_MODE_MASK          = const(0xFF000000)
BURST_MODE_OFFSET        = const(17)

GSR0_STATUS_FLAG_MASK    = const(0x0F)

SFCTL_FIFO_CREF_MASK     = const(0x001FFF)
SFCTL_FIFO_CREF_OFFSET   = const(0 << 0)

ADC0_DIV_OFFSET          = const(14)
ADC0_DIV_MASK            = const(0xFF << ADC0_DIV_OFFSET)

APU0_OFFSET              = const(0)
APU0_MASK                = const(0xFFF << APU0_OFFSET)

PLL1_0_FSU_OFFSET        = const(0)
PLL1_0_FSU_MASK          = const(0xFFFFFF << PLL1_0_FSU_OFFSET)

PLL1_1_RSU_OFFSET        = const(0)
PLL1_1_RSU_MASK          = const(0xFFFFFF << PLL1_1_RSU_OFFSET)

PLL1_2_RTU_OFFSET        = const(0)
PLL1_2_RTU_MASK          = const(0x3FFF << PLL1_2_RTU_OFFSET)

CSU1_2_VGA_GAIN1_OFFSET  = const(2)
CSU1_2_VGA_GAIN1_MASK    = const(0x7 << CSU1_2_VGA_GAIN1_OFFSET)

CSU1_2_VGA_GAIN2_OFFSET  = const(7)
CSU1_2_VGA_GAIN2_MASK    = const(0x7 << CSU1_2_VGA_GAIN2_OFFSET)

CSU1_2_VGA_GAIN3_OFFSET  = const(12)
CSU1_2_VGA_GAIN3_MASK    = const(0x7 << CSU1_2_VGA_GAIN3_OFFSET)

# Flags
SFCTL_MISO_HS_READ       = const(1 << 16)
SFCTL_FIFO_LP_MODE       = const(1 << 13)
WRITE_EN                 = const(0x01000000)
START_FRAME              = const(0x01)
TEST_MODE_EN             = const(0x1 << 17)
FIFO_RESET               = const(1 << 3)
FSM_RESET                = const(1 << 2)
SOFT_RESET               = const(1 << 1)
TEST_IF_ENABLE           = const(7 << 18)
BG_EN                    = const(1 << 7)
MADC_ISOPD               = const(1 << 8)
CS_EN                    = const(1 << 4)
MADC_EN                  = const(1 << 10)

# Register Addresses
MAIN_ADDR                = const(0x00)
ADC0_ADDR                = const(0x01)
CHIP_ID_ADDR             = const(0x02)
STAT1_ADDR               = const(0x03)
PACR1_ADDR               = const(0x04)
PACR2_ADDR               = const(0x05)
SFCTL_ADDR               = const(0x06)
SADC_CTRL_ADDR           = const(0x07)
CSI_0_ADDR               = const(0x08)
CSI_1_ADDR               = const(0x09)
CSI_2_ADDR               = const(0x0A)
CSCI_ADDR                = const(0x0B)
CSDS_0_ADDR              = const(0x0C)
CSDS_1_ADDR              = const(0x0D)
CSDS_2_ADDR              = const(0x0E)
CSCDS_ADDR               = const(0x0F)
CSU1_0_ADDR              = const(0x10)
CSU1_1_ADDR              = const(0x11)
CSU1_2_ADDR              = const(0x12)
CSD1_0_ADDR              = const(0x13)
CSD1_1_ADDR              = const(0x14)
CSD1_2_ADDR              = const(0x15)
CSC1_ADDR                = const(0x16)
CSU2_0_ADDR              = const(0x17)
CSU2_1_ADDR              = const(0x18)
CSU2_2_ADDR              = const(0x19)
CSD2_0_ADDR              = const(0x1A)
CSD2_1_ADDR              = const(0x1B)
CSD2_2_ADDR              = const(0x1C)
CSC2_ADDR                = const(0x1D)
CSU3_0_ADDR              = const(0x1E)
CSU3_1_ADDR              = const(0x1F)
CSU3_2_ADDR              = const(0x20)
CSD3_0_ADDR              = const(0x21)
CSD3_1_ADDR              = const(0x22)
CSD3_2_ADDR              = const(0x23)
CSC3_ADDR                = const(0x24)
CSU4_0_ADDR              = const(0x25)
CSU4_1_ADDR              = const(0x26)
CSU4_2_ADDR              = const(0x27)
CSD4_0_ADDR              = const(0x28)
CSD4_1_ADDR              = const(0x29)
CSD4_2_ADDR              = const(0x2A)
CSC4_ADDR                = const(0x2B)
CCR0_ADDR                = const(0x2C)
CCR1_ADDR                = const(0x2D)
CCR2_ADDR                = const(0x2E)
CCR3_ADDR                = const(0x2F)
PLL1_0_ADDR              = const(0x30)
PLL1_1_ADDR              = const(0x31)
PLL1_2_ADDR              = const(0x32)
PLL1_3_ADDR              = const(0x33)
PLL1_4_ADDR              = const(0x34)
PLL1_5_ADDR              = const(0x35)
PLL1_6_ADDR              = const(0x36)
PLL1_7_ADDR              = const(0x37)
PLL2_0_ADDR              = const(0x38)
PLL2_1_ADDR              = const(0x39)
PLL2_2_ADDR              = const(0x3A)
PLL2_3_ADDR              = const(0x3B)
PLL2_4_ADDR              = const(0x3C)
PLL2_5_ADDR              = const(0x3D)
PLL2_6_ADDR              = const(0x3E)
PLL2_7_ADDR              = const(0x3F)
PLL3_0_ADDR              = const(0x40)
PLL3_1_ADDR              = const(0x41)
PLL3_2_ADDR              = const(0x42)
PLL3_3_ADDR              = const(0x43)
PLL3_4_ADDR              = const(0x44)
PLL3_5_ADDR              = const(0x45)
PLL3_6_ADDR              = const(0x46)
PLL3_7_ADDR              = const(0x47)
PLL4_0_ADDR              = const(0x48)
PLL4_1_ADDR              = const(0x49)
PLL4_2_ADDR              = const(0x4A)
PLL4_3_ADDR              = const(0x4B)
PLL4_4_ADDR              = const(0x4C)
PLL4_5_ADDR              = const(0x4D)
PLL4_6_ADDR              = const(0x4E)
PLL4_7_ADDR              = const(0x4F)
RFT0_ADDR                = const(0x55)
RFT1_ADDR                = const(0x56)
PLL_DFT0_ADDR            = const(0x59)
STAT0_ADDR               = const(0x5D)
NONE_ADDR                = const(0x5B)
SADC_RESULT_ADDR         = const(0x5E)
FIFO_FSTAT_ADDR          = const(0x5F)
FIFO_ADDR                = const(0x60)

# FIFO
FIFO_SIZE                = const(8192)
FIFO_SIZE_BYTE           = const(12288)
BYTE_SIZE                = const(4)

# 0xFF = Adress; 
# FIFO-Address is shifted by (<< 1)
# Address 0x60 << 1 = 0xC0
# But when accessing this address, spi returns error!
# Solution (optimizable!) is to read 3 addresses before
# and skip those values later
ENABLE_BURST_MODE        = const(b'\xFF\xBD\x00\x00')

# See Setup Saw-Tooth p.24
# T_SETUP > T_PAEN + T_SSTART - T_START
T_SETUP                  = 60 # [6us * 8/t_sys]

# Init Register Values for sensor
init_register_list = {
    MAIN_ADDR:      0x011e8270,
    ADC0_ADDR:      0x03088210,
    PACR1_ADDR:     0x09e967fd,
    PACR2_ADDR:     0x0b0805b4,
    SFCTL_ADDR:     0x0d1027ff,
    SADC_CTRL_ADDR: 0x0f010700,
    CSI_0_ADDR:     0x11000000,
    CSI_1_ADDR:     0x13000000,
    CSI_2_ADDR:     0x15000000,
    CSCI_ADDR:      0x17000be0,
    CSDS_0_ADDR:    0x19000000,
    CSDS_1_ADDR:    0x1b000000,
    CSDS_2_ADDR:    0x1d000000,
    CSCDS_ADDR:     0x1f000b60,
    CSU1_0_ADDR:    0x21103c51,
    CSU1_1_ADDR:    0x231ff41f,
    CSU1_2_ADDR:    0x25006f73,
    CSC1_ADDR:      0x2d000490,
    CSC2_ADDR:      0x3b000480,
    CSC3_ADDR:      0x49000480,
    CSC4_ADDR:      0x57000480,
    CCR0_ADDR:      0x5911be0e,
    CCR1_ADDR:      0x5b44c40a, # T_START = (0x0a * 8 + 10) * t_sys = 1.125us
    CCR2_ADDR:      0x5d000000,
    CCR3_ADDR:      0x5f787e1e, # T_PAEN = 0x1e * 8 * t_sys = 3us
                                # T_SSTART = (0x1e * 8 + 1) * t_sys = 3.0125us
    PLL1_0_ADDR:    0x61f5208a,
    PLL1_1_ADDR:    0x630000a4,
    PLL1_2_ADDR:    0x65000252,
    PLL1_3_ADDR:    0x67000080,
    PLL1_4_ADDR:    0x69000000,
    PLL1_5_ADDR:    0x6b000000,
    PLL1_6_ADDR:    0x6d000000,
    PLL1_7_ADDR:    0x6f093910,
    PLL2_7_ADDR:    0x7f000100,
    PLL3_7_ADDR:    0x8f000100,
    PLL4_7_ADDR:    0x9f000100,
    RFT1_ADDR:      0xad000000,
    NONE_ADDR:      0xb7000000,
}