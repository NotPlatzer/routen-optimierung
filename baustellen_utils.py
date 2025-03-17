import math
# Konstanten
AbbruchleistungTS = 50  # t/h
AbbruchleistungMS = 416.666
OberflächenvorbereitungMS = 175  # m^2/h
AsphaltierleistungTS = 30
AsphaltierleistungMS = 250
AsphaltverfestigungMS = 400  # (m²/h)

Durchschnittlicher_Kraftstoffverbrauch_LKW_leer = 40  # (l/100km)
Durchschnittlicher_Kraftstoffverbrauch_LKW_vollbeladen = 55  # (l/100km)
Schichtdicke_Abbruch_Altasphalt_m = 0.05  # (cm)
Schichtdicke_Neuasphalt_m = 0.05  # (cm)
Dichte_Asphalt = 2.4  # (t/m³) verdichtet
LKV_Nutzlast = 25  # (t)


# Variablen
BaustellenGroesse = 500
BaustellenEntfernung = 150
LKW_Anzahl = 1


# Berechnungen
Asphaltvolumen = Schichtdicke_Abbruch_Altasphalt_m * Dichte_Asphalt
Asphaltmasse = Asphaltvolumen * Dichte_Asphalt
Anzahl_LKW_Fahrten = Asphaltmasse / LKV_Nutzlast
Anzahl_LKW_Fahrten_UP = math.ceil(Anzahl_LKW_Fahrten)
Anzahl_LKW_Fahrten_DOWN = math.floor(Anzahl_LKW_Fahrten)
Dauer_Abbruch = BaustellenGroesse / AbbruchleistungTS
Dauer_Oberflaechenvorbereitung = BaustellenGroesse / OberflächenvorbereitungMS
Dauer_Asphaltierungsarbeiten = BaustellenGroesse / AsphaltierleistungTS
Dauer_Asphaltverfestigung = BaustellenGroesse / AsphaltverfestigungMS

GewichtProLKW = Asphaltmasse / Anzahl_LKW_Fahrten_UP
ProzentBeladen = GewichtProLKW / LKV_Nutzlast

VerbrauchVolleFahrten = Anzahl_LKW_Fahrten_DOWN * Durchschnittlicher_Kraftstoffverbrauch_LKW_vollbeladen

KraftstoffVerbrauch = Anzahl_LKW_Fahrten_UP * ProzentBeladen * Durchschnittlicher_Kraftstoffverbrauch_LKW_vollbeladen
Gesamt_Dauer = Dauer_Abbruch + Dauer_Oberflaechenvorbereitung + Dauer_Asphaltierungsarbeiten + Dauer_Asphaltverfestigung

print("Anzahl LKW Fahrten: ", Anzahl_LKW_Fahrten_UP)
print("Kraftstoffverbrauch (l/100 km): ", KraftstoffVerbrauch)
print("Gesamt Dauer (h): ", Gesamt_Dauer)

