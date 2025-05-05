# Ersteller: Jannes Gonsior
# Datum: 26.11.2024
# Version 1.0
# Programm zur Darstellung auf einem Display 

# Import der Libarys
from machine import Pin, SPI
import st7789py as st7789
import vga1_16x32 as font
import time

#scl=sck
#sda=mosi

# Variabeln und PIN's definieren
spi = SPI(1,
    baudrate=20000000,
    polarity=0,
    phase=0,
    sck=Pin(6),
    mosi=Pin(7),
    miso=Pin(0))

tft = st7789.ST7789(
    spi,
    240,
    320,
    reset=Pin(21, Pin.OUT),
    cs=Pin(5, Pin.OUT),
    dc=Pin(8, Pin.OUT),
    backlight=Pin(0, Pin.OUT),
    rotation=2)

# Ausgabe
tft.text(font, "Hallo Welt", 30, 30, st7789.WHITE, st7789.BLACK)

