import matplotlib.pyplot as plt
import math
# import baustellen_utils as ut

lkw_x = []
zeit_y = []


M = 400  # t
N = 25  # t
G = 100  # kmh
A = 350  # km zum Asphaltwerk
AG = 50  # t / h
AS = 30  # t / h
TL = 13


l = 1

anzahlFahrten = M / N
load_time = N / AG

trichter_load_time = ((N - TL) / AS)
trichter_work_time = TL / AS


# calculate the time for the trip
fahrt_zeit =  2 * (A / G)


def calculateWorkTime_3_2(l):
    if (math.ceil(M/N) < l) or (2 * A / G < (N / AS) * (l - 1)):
        return -1
    return (anzahlFahrten) * trichter_load_time + (anzahlFahrten - 1) * trichter_work_time + (math.ceil(anzahlFahrten/l) - 1) * (fahrt_zeit - ((l - 1) * trichter_load_time + l * trichter_work_time))


def calculateWorkTime_3_1(l):
    if (math.ceil(M/N) < l) or (2 * A / G < (N / AS) * (l - 1)):
        return -1
    ges = (M / N) * (N - TL) / AS + (M/N - 1) * TL / AS + (math.ceil(M/(N*l)) - 1) * (fahrt_zeit - ((l - 1) * (N - TL) / AS + l * TL / AS))
    return ges

# teeren simulieren
def simWorkTime_3(l, verbose = False):
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
            
            dump_volume = min(N, restMass)
            restMass -= dump_volume
            
            dump_anzahl = dump_volume / TL
            full_dumps = math.floor(dump_anzahl)  # integer
            rest_dump = (dump_anzahl - full_dumps) # 0 - 0.99
            
            rest_dump_time = (rest_dump * TL) / AS
            
            waltz_time = rest_dump_time
            
            if full_dumps == 0:
                full_dump_time = 0
            else:
                full_dump_time = (full_dumps - 1) * TL / AS
                waltz_time += TL / AS
            
            truck_work_time = full_dump_time + rest_dump_time
            available_time = total_time + truck_work_time + fahrt_zeit
            trucks_time_avalable[i] = available_time
            
            if (verbose):
                print(f"Truck {str(i)} dumps at {str(round(total_time, 2))} - {str(round(total_time + truck_work_time, 2))}")
                print(f"\tFull dumps: {str(full_dumps)}")
                print(f"\tRest dump: {str(rest_dump)}")
                print(f"\tRest dump time: {str(round(rest_dump_time, 2))}")
                print(f"\tFull dump time: {str(round(full_dump_time, 2))}")
                print(f"\tWaltz time: {str(round(waltz_time, 2))}")
                print(f"\tTruck is available again in: {str(round(available_time, 2))}")
                print(f"\tRestmass: {str(restMass)} ")
                print("\n")
                
            
            if restMass <= 0:
                total_time += rest_dump_time + full_dump_time
                break
            
            total_time += waltz_time
        
    return round(total_time, 2)


def calculateWorkTime_1_2(l):
    return anzahlFahrten * load_time + max(0, fahrt_zeit - (l - 1) * load_time) * (math.ceil(anzahlFahrten / l) - 1)


def calculateWorkTime_1_1(l):
    if (math.ceil(M/N) < l) or (2 * A / G < (N / AG) * (l - 1)):
        return -1
    ges = anzahlFahrten * load_time + (math.ceil(anzahlFahrten / l) - 1) * (fahrt_zeit - ((l - 1) * load_time))
    return ges


# fräsen simulieren
def simWorkTime_1(l, verbose = False):
    trucks = []

    restMass = M
    total_time = 0

    trucks_time_avalable = []
    for i in range(l):
        trucks_time_avalable.append(0)
        trucks.append([])
    # while work is not done = restMass > 0
    while restMass > 0:
        for i in range(l):
            # truck is loaded
            total_time = max(total_time, trucks_time_avalable[i])
            load_volume = min(N, restMass)
            restMass -= load_volume
            trucks[i].append({"type": "load", "volume": load_volume, "time": total_time})
            if (verbose):
                print("Truck " + str(i) + " loads at " + str(round(total_time, 2)) + " - " + str(round(total_time + load_time * (load_volume / N), 2)))
                print("Restmass: " + str(restMass))
            trucks[i].append(
                {"type": "drive","fromTo": "Aw" , "volume": load_volume, "time": total_time, "drive_time": fahrt_zeit/2}
            )
            trucks[i].append(
                {
                    "type": "drive",
                    "fromTo": "wA",
                    "volume": load_volume,
                    "time": total_time,
                    "drive_time": fahrt_zeit/2,
                }
            )
            total_time += load_time * (load_volume / N)
            available_time = total_time + fahrt_zeit

            if (verbose):
                print("Truck is available again in: " + str(round(available_time, 2)))

            trucks_time_avalable[i] = available_time

            if restMass <= 0:
                break
    #print(trucks)
    return round(total_time, 2)


def machine_3(trucks_max):
    l = 1
    lastValue = 0
    print("-------------------")
    print("Asphaltieren (3): ")
    while l < trucks_max:
        zeit = simWorkTime_3(l, False)
        zeit1 = calculateWorkTime_3_1(l)
        zeit2 = calculateWorkTime_3_2(l)
        
        print(f"LKW: {l} David: {zeit} Goliath: {round(zeit1, 2)} Jakob: {round(zeit2, 2)}")
        
        if lastValue == zeit:
            print(lastValue, l)
            #break
        
        lastValue = zeit
        lkw_x.append(l)
        zeit_y.append(zeit)
        l += 1
    
    print(lkw_x)
    print(zeit_y)
    plt.plot(lkw_x, zeit_y, label="Zeit Asphaltierer")
    plt.xlabel("Anzahl LKW")
    plt.ylabel("Zeit in min")
    plt.title("Asphaltieren")

def machine_1(trucks_max):
    l = 1
    lastValue = 0
    print("-------------------")
    print("Fräsen (1): ")
    while l < trucks_max:
        zeit = simWorkTime_1(l, False)
        zeit1 = calculateWorkTime_1_1(l)
        zeit2 = calculateWorkTime_1_2(l)
        
        print(f"LKW: {l+1} David: {zeit} Goliath: {round(zeit1, 2)} Jakob: {round(zeit2, 2)}")
        
        if lastValue == zeit:
            print(lastValue, l)
            break
        
        lastValue = zeit
        lkw_x.append(l)
        zeit_y.append(zeit)
        l += 1
    
    print(lkw_x)
    print(zeit_y)
    plt.plot(lkw_x, zeit_y, label="Zeit Fräse")
    plt.xlabel("Anzahl LKW")
    plt.ylabel("Zeit in min")
    plt.title("Fräsen")


simWorkTime_1(1)

#machine_1(10)
machine_3(10)
plt.legend()
plt.show()
