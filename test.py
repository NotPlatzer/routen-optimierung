import matplotlib.pyplot as plt
import math
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


def calculateWorkTime(l, fahrt_zeit, load_time):
    restMass = m
    availableTrucks = l
    total_time = 0
    
    trucks = []
    for i in range(l):
        trucks.append(0)
    
    #while work is not done = restMass > 0
    while restMass > 0:
        # every truck has to be loaded. only one truck can be loaded at a time
        for i in enumerate(trucks):
            # first truck is loaded
            
            print("Truck " + i + " loaded: ")
            print("Restmass: " + str(restMass))
            
            disabled = total_time + fahrt_zeit + load_time
            
            print("Truck is available again in: " + disabled)
            

            total_time += load_time
            restMass -= n
            
            # truck drives to the asphalt
            total_time += fahrt_zeit
            

            
            if restMass <= 0:
                break
        availableTrucks = math.ceil(restTime / (fahrt_zeit + load_time))
        
    return total_time



while l < 10:
    zeit = calculateWorkTime(l, asphalt_fahrt_zeit, charge_time)
    
    if lastValue == zeit:
        print(lastValue, l)
        break
    
    lastValue = zeit
    lkw_x.append(l)
    zeit_y.append(zeit)
    l += 1




print(lkw_x)
print(zeit_y)
plt.plot(lkw_x, zeit_y)
plt.savefig("test.png")
