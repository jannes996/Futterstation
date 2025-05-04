from hx711 import HX711
from utime import sleep

DOUT_PIN = 4
SCK_PIN = 5

hx = HX711(d_out=DOUT_PIN, pd_sck=SCK_PIN)

def mittelwert(hx, messungen=10):
    return sum(hx.read() for _ in range(messungen)) / messungen

print("⚖️  Kalibrierung startet...")
sleep(1)

# Schritt 1: Leere Plattform
input("➡️  Plattform leer lassen und ENTER drücken...")
rohwert_0g = mittelwert(hx)
print(f"Rohwert bei 0 g: {rohwert_0g:.0f}")
sleep(1)

# Schritt 2: Gewicht auflegen
gewicht1 = float(input("➡️  Lege bekanntes Gewicht auf und gib den Wert in g ein (z. B. 300): "))
input("➡️  ENTER drücken, wenn Gewicht liegt...")
rohwert_1 = mittelwert(hx)
print(f"Rohwert bei {gewicht1:.1f} g: {rohwert_1:.0f}")

# Berechnung
delta_raw = rohwert_1 - rohwert_0g
m = gewicht1 / delta_raw
b = -m * rohwert_0g

# Ergebnis anzeigen
print("\n✅ Kalibrierung abgeschlossen!")
print(f"Berechnete Werte:")
print(f"  m = {m:.7f}")
print(f"  b = {b:.2f}\n")
