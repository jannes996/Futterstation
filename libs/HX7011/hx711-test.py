from hx711 import HX711
from time import sleep

DOUT_PIN = 10 #gelb
SCK_PIN = 9 #weiß
hx = HX711(DOUT_PIN, SCK_PIN)

def rohwert_zu_gewicht(rohwert):
    m = -0.0005924
    b = -29.84
    gewicht = int(m * rohwert + b)
    return gewicht

while True:
    gewicht = rohwert_zu_gewicht(hx.read())
    print(f"Gemessenes Gewicht: {gewicht}g")
    sleep(1)
    print(hx.read())