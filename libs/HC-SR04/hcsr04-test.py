from hcsr04 import HCSR04
from time import sleep

trigger_pin = 2 #weiß
echo_pin = 3 #gelb
sensor = HCSR04(trigger_pin, echo_pin)
    
    
def entfernung_zu_prozent(entfernung_cm):
    m = -6.2953
    b = 112.5906
    prozent = int(m * entfernung_cm + b)
    return prozent


while True:
    fuellstand = int(entfernung_zu_prozent(sensor.distance_cm()))
    print(f"Füllstand: {fuellstand}%")
    sleep(1)
    