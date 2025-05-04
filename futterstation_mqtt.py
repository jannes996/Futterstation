# Wetterstation über MQTT, Senden und Empfang möglich
 
# Ersteller: Jannes Gonsior
# Datum: 04.03.2025
# Datenaustausch mehrerer Umgebungswerte über MQTT im json Format + Ansteuern einer LED über Node-Red

# Import der Libarys
import time
from machine import Pin, SoftI2C, PWM

import network
from umqtt.simple import MQTTClient
import ujson

# Bibliotheken der Sensoren


# Variabeln und PIN's definieren
servo_trigger = 0
servo = PWM(Pin(12), freq=50)

# WLAN verbinden
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
#wlan.connect("BZTG-IoT", "WerderBremen24")
wlan.connect("FRITZ!Box 6660 Cable GR", "hupensohn")

print("Verbinde mit dem WLAN...")
while not wlan.isconnected():
    time.sleep(1)
print("WLAN verbunden! IP-Adresse:", wlan.ifconfig()[0])

# Sende-/ Empfangfunktion
def recv_data(topic, msg):
    json_content = ujson.loads(msg)
    print("MQTT Nachricht empfangen:", json_content)
    
    global servo_trigger
    servo_trigger = json_content.get('servo_trigger')

def send_data(topic, content):
    client.publish(topic, str(content))
    print("MQTT Nachricht gesendet:" , content)

# MQTT-Client einrichten
client = MQTTClient("Futterstation", "185.216.176.124", 1883)
client.set_callback(recv_data)

client.connect()
client.subscribe("futterstation/manuell")
print("MQTT verbunden!")

# Daten senden
while True:
    time.sleep(0.5)

    futter = 	{
                "gewicht_now": "1212"
                }
    
    #send_data("futterstation/daten", ujson.dumps(futter))
    
    client.check_msg()
    if servo_trigger == "1":
        servo.duty(110)
        servo_trigger = 0
        time.sleep(1)
        servo.duty(60)

