from lcd_api import LcdApi
from machine import I2C
import time

# LCD Commands
LCD_CLR             = 0x01
LCD_HOME            = 0x02
LCD_ENTRY_MODE      = 0x04
LCD_ENTRY_INC       = 0x02
LCD_ENTRY_SHIFT     = 0x01
LCD_ON_CTRL         = 0x08
LCD_ON_DISPLAY      = 0x04
LCD_ON_CURSOR       = 0x02
LCD_ON_BLINK        = 0x01
LCD_MOVE            = 0x10
LCD_MOVE_DISP       = 0x08
LCD_MOVE_RIGHT      = 0x04
LCD_FUNCTION        = 0x20
LCD_FUNCTION_8BIT   = 0x10
LCD_FUNCTION_2LINES = 0x08
LCD_FUNCTION_10DOTS = 0x04
LCD_CGRAM           = 0x40
LCD_DDRAM           = 0x80

MASK_RS = 0x01
MASK_RW = 0x02
MASK_E  = 0x04
SHIFT_BACKLIGHT = 3
SHIFT_DATA = 4


class I2cLcd(LcdApi):
    def __init__(self, i2c, i2c_addr, num_lines, num_columns):
        self.i2c = i2c
        self.i2c_addr = i2c_addr
        self.num_lines = num_lines
        self.num_columns = num_columns
        self.backlight = 1
        time.sleep_ms(20)
        self.hal_write_init_nibble(0x03)
        time.sleep_ms(5)
        self.hal_write_init_nibble(0x03)
        time.sleep_ms(1)
        self.hal_write_init_nibble(0x03)
        self.hal_write_init_nibble(0x02)

        cmd = LCD_FUNCTION | LCD_FUNCTION_2LINES
        self.hal_write_command(cmd)
        cmd = LCD_ON_CTRL | LCD_ON_DISPLAY
        self.hal_write_command(cmd)
        self.hal_write_command(LCD_CLR)
        cmd = LCD_ENTRY_MODE | LCD_ENTRY_INC
        self.hal_write_command(cmd)
        self.hal_backlight_on()

    def hal_backlight_on(self):
        self.backlight = 1
        self.i2c.writeto(self.i2c_addr, bytearray([self.backlight << SHIFT_BACKLIGHT]))

    def hal_backlight_off(self):
        self.backlight = 0
        self.i2c.writeto(self.i2c_addr, bytearray([self.backlight << SHIFT_BACKLIGHT]))

    def hal_write_command(self, cmd):
        self.hal_write_byte(cmd, 0)

    def hal_write_data(self, data):
        self.hal_write_byte(data, MASK_RS)

    def hal_write_init_nibble(self, nibble):
        self.hal_write_byte(nibble, 0)

    def hal_write_byte(self, data, mode):
        byte = (data & 0xF0) | mode
        self.i2c.writeto(self.i2c_addr, bytearray([byte | (self.backlight << SHIFT_BACKLIGHT) | MASK_E]))
        self.i2c.writeto(self.i2c_addr, bytearray([byte | (self.backlight << SHIFT_BACKLIGHT)]))
        byte = ((data << 4) & 0xF0) | mode
        self.i2c.writeto(self.i2c_addr, bytearray([byte | (self.backlight << SHIFT_BACKLIGHT) | MASK_E]))
        self.i2c.writeto(self.i2c_addr, bytearray([byte | (self.backlight << SHIFT_BACKLIGHT)]))
