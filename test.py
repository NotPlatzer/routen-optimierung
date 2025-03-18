import matplotlib.pyplot as plt
import math
#import baustellen_utils as ut

lkw_x = []
zeit_y = []


M = 501  # t
N = 25  # t
G = 20  # kmh
A = 140  # km zum Asphaltwerk
AG = 10

lastValue = 0

l = 1

anzahlFahrten = M / N
load_time = N / AG

# calculate the time for the trip
fahrt_zeit =  2 * (A / G)


def calculateWorkTime2(l):
    return anzahlFahrten * load_time + max(0, fahrt_zeit - (l - 1) * load_time) * (math.ceil(anzahlFahrten / l) - 1)



def calulateWorkTime1(l):
    if N >= M:
        l = 1
    if math.ceil(anzahlFahrten) < l:
        return -1
    if fahrt_zeit < load_time * (l - 1):
        l = 2
    print("l: " + str(l))
    ges = anzahlFahrten * load_time + (math.ceil(anzahlFahrten / l) - 1) * (fahrt_zeit - ((l - 1) * load_time))
    
    return ges


def calculateWorkTimeSim(l, verbose = False):
    restMass = M
    total_time = 0
    
    trucks_time_avalable = []
    for i in range(l):
        trucks_time_avalable.append(0)
    
    #while work is not done = restMass > 0
    while restMass > 0:
        for i in range(l):
            # truck is loaded
            total_time = max(total_time, trucks_time_avalable[i])
            load_volume = min(N, restMass)
            restMass -= load_volume
            
            if (verbose):
                print("Truck " + str(i) + " loads at " + str(round(total_time, 2)) + " - " + str(round(total_time + load_time * (load_volume / N), 2)))
                print("Restmass: " + str(restMass))
                
            total_time += load_time * (load_volume / N)
            available_time = total_time + fahrt_zeit
            
            if (verbose):
                print("Truck is available again in: " + str(round(available_time, 2)))
            
            trucks_time_avalable[i] = available_time
            
            if restMass <= 0:
                break
        
    return round(total_time, 2)



while l < 10:
    zeit = calculateWorkTimeSim(l)
    zeit1 = calculateWorkTime2(l)
    
    print("LKW: " + str(l) + " Zeit: " + str(zeit) + " Zeit1: " + str(round(zeit1, 2)))
    
    if lastValue == zeit:
        print(lastValue, l)
        break
    
    lastValue = zeit
    lkw_x.append(l)
    zeit_y.append(zeit)
    l += 1


print("-------------------")
print("With 3 trucks: ")
calculateWorkTimeSim(3, True)



print(lkw_x)
print(zeit_y)
plt.plot(lkw_x, zeit_y)
