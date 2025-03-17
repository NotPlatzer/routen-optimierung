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




charge_time = n / ut.AbbruchleistungTS




# calculate the time for the trip
asphalt_fahrt_zeit =  2 * (a / g)



def calculateWorkTime(anzahlFahrten, l, asphalt_fahrt_zeit, charge_time):
    restzeit = 0
    if ((anzahlFahrten > l) and (asphalt_fahrt_zeit > charge_time*l)):
        restzeit = (asphalt_fahrt_zeit * (anzahlFahrten - l) - (l - 1) * charge_time) 
    
    return anzahlFahrten * charge_time + restzeit




while l < 10:
    zeit = calculateWorkTime(anzahlFahrten, l, asphalt_fahrt_zeit, charge_time)
    
    if lastValue == zeit:
        print(lastValue, l)
        break
    
    lastValue = zeit
    lkw_x.append(l)
    zeit_y.append(zeit)
    l += 1


l = 1

arr = []




print(zeit_y)
plt.plot(lkw_x, zeit_y)
plt.savefig("anzahlLaster.png")
