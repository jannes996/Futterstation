from machine import Pin, PWM
from time import sleep

pwm = PWM(Pin(13), freq=50)


while True:
    pwm.duty(40) # Position 0
    sleep(1)
    pwm.duty(77) # Position 90
    sleep(1)
    pwm.duty(115) # Position 180
    sleep(1)