from machine import Pin, PWM
from time import sleep

servo = PWM(Pin(4), freq=50)

# Kalibrierte duty-Werte für "zu" und "auf"
ZU = 67     # z. B. 0°
AUF = 110   # z. B. 90°

def schieber_auf():
    servo.duty(110)
    print("Schieber geöffnet")
    
def schieber_zu():
    servo.duty(60)
    print("Schieber geschlossen")

# Testweise öffnen und schließen
schieber_zu()
sleep(5)
schieber_auf()