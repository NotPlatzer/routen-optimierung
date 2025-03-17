import matplotlib.pyplot as plt
import baustellen_utils as ut

lkw_x = []
zeit_y = []


g = 70  # kmh
m = 200  # t
n = 25  # t
a = 140  # km zum Asphaltwerk

lastValue = 0

l = 1

anzahlFahrten = m / n


charge_time = n / ut.AsphaltierleistungTS


while l < 10:
    restzeit = 0
    if ((anzahlFahrten > l) and (2*a/g > charge_time*l)):
        restzeit = ((2*a/g) * (anzahlFahrten - l) - (l - 1) * charge_time) 
    
    zeit = anzahlFahrten * charge_time + restzeit
    
    if lastValue == zeit:
        print(lastValue, l)
        break
    
    lastValue = zeit
    lkw_x.append(l)
    zeit_y.append(zeit)
    l += 1


print(zeit_y)
plt.plot(lkw_x, zeit_y)
plt.savefig("anzahlLaster.png")
