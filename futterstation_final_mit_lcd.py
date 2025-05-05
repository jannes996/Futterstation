# Projekt: Futterstation, automatische Futterstation für Trockenfutter für Katzen.
# Die Futterstation überwacht Füllstand des Napfes, sowie den Nachfüllbehälter. Diese Werte werden live
# über MQTT übertragen und in einem Node-Red UI dargestellt. Außerdem wird das Fressverhalten der Katzen
# in einer Datenbank gespeichert und eine Statistik, die jeweils den Verbrauch + Kosten speichert, ebenfalls
# im UI angezeigt.
# Verbaut sind:
# -Ein Servo zum öffnen einer Drehöffnung damit Futter nachgefüllt wird,
# -eine Wägezelle unter dem Napf zum messen, wie viel Futter noch im Napf ist,
# -ein Entfernungsmesser im Nachfüllbehälter um den Bestand zu messen
# -ein Display zum darstellen von Informationen vor Ort
 
# Ersteller: Jannes
# Datum: 04.03.2025

# Import der Libarys
import time
import network
import ujson
from machine import Pin, SoftI2C, PWM, SPI
from umqtt.simple import MQTTClient

# Bibliotheken der Sensoren
from hcsr04 import HCSR04
from hx711 import HX711
import st7789py as st7789
import vga1_16x32 as font

# Variabeln und PIN's definieren
# Servo MG996-R
servo_trigger = 0
aktor_servo = PWM(Pin(4), freq=50) #gelb

# HC-SR04 Entfernungsmesser
hcsr04_trigger = 2
hcsr04_echo = 3
sensor_hcsr04 = HCSR04(hcsr04_trigger, hcsr04_echo)

# HX0711 + 1kg Wägezelle
hx0711_sck = 9
hx0711_dt = 10
sensor_hx0711 = HX711(hx0711_dt, hx0711_sck)

# ST7789 Display
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

tft.text(font, "Futterstation", 10, 50, st7789.WHITE, st7789.BLACK)

# WLAN-Verbindung
wlan = network.WLAN(network.STA_IF)
wlan.active(True)

#wlan.connect("BZTG-IoT", "WerderBremen24")
wlan.connect("FRITZ!Box 6660 Cable GR", "hupensohn")
print("Verbinde mit dem WLAN...")
tft.text(font, "Wifi verbindet..", 10, 100, st7789.WHITE, st7789.BLACK)

while not wlan.isconnected():
    time.sleep(1)
    
print("WLAN verbunden! IP-Adresse:", wlan.ifconfig()[0])
tft.text(font, "Wifi verbunden", 10, 100, st7789.GREEN, st7789.BLACK)

# Funktionen
def recv_data(topic, msg):
    json_content = ujson.loads(msg)
    print("MQTT Nachricht empfangen:", json_content)
    
    global servo_trigger
    servo_trigger = json_content.get('servo_trigger')

def send_data(topic, content):
    client.publish(topic, str(content))
    print("MQTT Nachricht gesendet:" , content)
    
def entfernung_zu_prozent(entfernung_cm):
    m = -6.2953
    b = 112.5906
    prozent = int(m * entfernung_cm + b)
    if prozent < 0:
        prozent = 0
    if prozent > 100:
        prozent = 99
    return prozent

def rohwert_zu_gewicht(rohwert):
    m = -0.0005912
    b = -30.39
    gewicht = int(m * rohwert + b)
    return gewicht

def schieber_auf():
    aktor_servo.duty(110)
    print("Schieber geöffnet")

def schieber_zu():
    aktor_servo.duty(60)
    print("Schieber geschlossen")
    
def fuettern():
    schieber_auf()
    startzeit = time.time()
    
    while True:
        gewicht = rohwert_zu_gewicht(sensor_hx0711.read())
        print(f"Aktuelles Gewicht: {gewicht}")

        if gewicht >= 90:
            print("Zielgewicht erreicht")
            break

        if time.time() - startzeit > 3:
            print("Schieber wird geschlossen")
            break
        
        time.sleep(0.2)
    schieber_zu()

# MQTT-Client einrichten
tft.text(font, "MQTT verbindet..", 10, 140, st7789.WHITE, st7789.BLACK)
client = MQTTClient("Futterstation", "185.216.176.124", 1883)
client.set_callback(recv_data)

client.connect()
client.subscribe("futterstation/manuell")
print("MQTT verbunden!")
tft.text(font, "MQTT verbunden", 10, 140, st7789.GREEN, st7789.BLACK)

# Daten senden und empfangen
while True:
    client.check_msg()

    gewicht = rohwert_zu_gewicht(sensor_hx0711.read())
    fuellstand = entfernung_zu_prozent(sensor_hcsr04.distance_cm())
    
    daten = {
            "gewicht_napf": gewicht,
            "fuellstand_behaelter": fuellstand,
            }
    
    send_data("futterstation/daten", ujson.dumps(daten))

    if gewicht < 10 or servo_trigger == "1":
        fuettern()
        servo_trigger = 0
    
    gewicht_lcd = f"Napf: {gewicht}g"
    fuellstand_lcd = f"Behaelter: {fuellstand}%"
    tft.text(font, gewicht_lcd, 10, 200, st7789.WHITE, st7789.BLACK)
    tft.text(font, fuellstand_lcd, 10, 240, st7789.WHITE, st7789.BLACK)

    time.sleep(5)