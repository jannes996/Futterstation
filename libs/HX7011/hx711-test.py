from hx711 import HX711
from time import sleep

DOUT_PIN = 10 #gelb
SCK_PIN = 9 #weiß
hx = HX711(DOUT_PIN, SCK_PIN)

def rohwert_zu_gewicht(rohwert):
    m = -0.0005259
    b = -46.70
    gewicht = int(m * rohwert + b)
    return gewicht

def mittelwert(hx, messungen=10):
    return sum(hx.read() for _ in range(messungen)) / messungen

while True:
    gewicht = rohwert_zu_gewicht(mittelwert(hx))
    print(f"Gemessenes Gewicht: {gewicht}g")
    print(hx.read())
    sleep(1)