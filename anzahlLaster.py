import matplotlib.pyplot as plt
import math
lkw_x = []
zeit_y = []

distance_c_km = 0 #km zum LKW Startpunkt
velocity_kmh = 70 #kmh
masse_asphalt_t = 80 #t
nutzlast_t = 25 #t
distance_a_km = 70 #km zum Asphaltwerk

lastValue = 0

l = 1
while l < 10:
    anzahl_fahrten = (masse_asphalt_t / (nutzlast_t * l))
    if (anzahl_fahrten < 1):
        break
    time1 = 2 * distance_c_km / velocity_kmh + math.ceil(anzahl_fahrten) * 2 + 0.5
    time2 = 2 * distance_a_km / velocity_kmh - ((l - 1) / (2 * distance_a_km / velocity_kmh))
    ges = time1 + max(0, time2)
    if lastValue == ges:
        print(lastValue, l)
        break
    lastValue = ges
    lkw_x.append(l)
    zeit_y.append(ges)
    l+=1

print(zeit_y[0], zeit_y[-1])
plt.plot(lkw_x, zeit_y)
plt.savefig("anzahlLaster.png")
