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
 
# Ersteller: Jannes Gonsior
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
zielgewicht = 40 # Defaultwert für den Napf
daten_alt = 0 # Vergleich zwischen den Daten zum Senden

# Servo MG996-R
servo_trigger = 0
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

wlan.connect("BZTG-IoT", "WerderBremen24")

print("Verbinde mit dem WLAN...")
tft.text(font, "Wifi verbindet..", 10, 100, st7789.WHITE, st7789.BLACK)

while not wlan.isconnected():
    time.sleep(1)
    
print("WLAN verbunden! IP-Adresse:", wlan.ifconfig()[0])
tft.text(font, "Wifi verbunden", 10, 100, st7789.GREEN, st7789.BLACK)

# Funktionen
def recv_data(topic, msg): # Funktion zum Empfangen von MQTT Nachrichten
    json_content = ujson.loads(msg)
    print("MQTT Nachricht empfangen:", json_content)
    
    global servo_trigger # globae Variabel zum nutzen außerhalb der Funktion
    servo_trigger = json_content.get('servo_trigger')
    
    global zielgewicht # globale Variabel zum nutzen außerhalb der Funktion
    zielgewicht = json_content.get('zielgewicht')
    
def send_data(topic, content): # Funktion zum Senden von MQTT Nachrichten
    client.publish(topic, str(content))
    print("MQTT Nachricht gesendet:" , content)
    
def entfernung_zu_prozent(entfernung_cm): # lineare Formel zum Umrechnen von cm zu Prozent - es wird nur ein Wert zwischen 0 und 99% ausgegeben
    m = -6.2953
    b = 112.5906
    prozent = int(m * entfernung_cm + b)
    if prozent < 0:
        prozent = 0
    if prozent > 100:
        prozent = 99
    return prozent

def rohwert_zu_gewicht(rohwert_waage): # lineare Formel zum Umrechnen vom Rohwert der Wägezelle zur metrischen Einheit Gramm
    m = -0.0005259
    b = -46.70
    gewicht = int(m * rohwert_waage + b)
    return gewicht

def schieber_auf(): # Funktion die den Schieber öffnet
    aktor_servo.duty(110)
    print("Schieber geöffnet")

def schieber_zu(): # Funktion die den Schieber schließt
    aktor_servo.duty(60)
    print("Schieber geschlossen")
    
def fuettern(): # Funktion zum auffüllen des Napfes. Es wird der Schieber geöffnet, die akutelle Zeit genommen. Es wird alle 0.2s geprüft ob das Gewicht erreicht wird. Sollte nach 3s das Gewicht nicht erreicht werden, schließt der Drehverschluss (z.B. wenn der Behälter leer ist). Ansonsten wird der Drehverschluss nach erreichen des eingestellten Zielgewichts geschlossen.
    schieber_auf()
    startzeit = time.time()
    
    while True:
        gewicht = rohwert_zu_gewicht(sensor_hx0711.read())
        print(f"Aktuelles Gewicht: {gewicht}")

        if gewicht >= zielgewicht:
            print(f"Zielgewicht ({zielgewicht}g) erreicht")
            break

        if time.time() - startzeit > 3:
            print("Schieber wird geschlossen")
            break
        
        time.sleep(0.2)
    schieber_zu()

# MQTT-Client einrichten
tft.text(font, "MQTT verbindet..", 10, 140, st7789.WHITE, st7789.BLACK)

client = MQTTClient("Futterstation", "185.216.176.124", 1883) # MQTT Broker Verbindung
client.set_callback(recv_data) # Weißt die Funktion zu, wenn eine MQTT-Nachricht empfangen wird

client.connect() # Verbindet mit dem oben eingegeben Broker
client.subscribe("futterstation/manuell") # Subscribed unsere genutzten Topics
client.subscribe("futterstation/fuellmenge")

print("MQTT verbunden!")
tft.text(font, "MQTT verbunden", 10, 140, st7789.GREEN, st7789.BLACK)

# Daten senden und empfangen
while True:
    client.check_msg() # prüft ob eine neue MQTT-Nachricht vom Broker empfangen wurde und ruft die bei set_callback() eingegebene Funktion auf
    time.sleep(5)

    gewicht = rohwert_zu_gewicht(sensor_hx0711.read()) # lineare Funktion
    fuellstand = entfernung_zu_prozent(sensor_hcsr04.distance_cm()) # lineare Funktion

    # Messwerte in JSON zum senden
    daten = {
            "gewicht_napf": gewicht,
            "fuellstand_behaelter": fuellstand,
            }
    if daten != daten_alt: # Vergleicht ob die Messwerte sich geändert haben, sendet erst bei Unterschied
        send_data("futterstation/daten", ujson.dumps(daten))
        
    daten_alt = daten
            
    if gewicht < 10 or servo_trigger == "1": # löst das Auffüllen aus wenn das gemessene Gewicht unter 10g oder wenn im UI aktiviert wird
        fuettern()
        servo_trigger = 0
    
    gewicht_lcd = f"Napf: {gewicht}g"
    fuellstand_lcd = f"Behaelter: {fuellstand}%"
    tft.text(font, gewicht_lcd, 10, 200, st7789.WHITE, st7789.BLACK)
    tft.text(font, fuellstand_lcd, 10, 240, st7789.WHITE, st7789.BLACK)