import math
import matplotlib.pyplot as plt

M = 400  # t
N = 25  # t
V = 100  # kmh
A = 350  # km zum Asphaltwerk
AG = 50  # t / h
AS = 30  # t / h
TL = 13
dicht_asphalt = 2.4  # t / m^3
OberflächenvorbereitungMS = 175
AsphaltverfestigungMS = 400
AsphaltverfestigungTS = (AsphaltverfestigungMS / 20) * dicht_asphalt
OberflächenvorbereitungTS = (OberflächenvorbereitungMS / 20) * dicht_asphalt



lastValue = 0

l = 1
anzahlFahrten = M / N
load_time = N / AG

trichter_load_time = ((N - TL) / AS)
trichter_work_time = TL / AS


# calculate the time for the trip
fahrt_zeit = 2 * (A / V)

ABLADEN = 0.05
VOLLADEN = 0.1


def calculateFullTime(l):
    ges = M/AG + math.ceil(M/(N*l)) * ((2 * A / V + ABLADEN + VOLLADEN + (N - TL) / AS) - (l-1) * N/AG) + TL/AS
    return ges


def calculateWorkTime_3_2(l):
    if (math.ceil(M/N) < l) or (2 * A / V < (N / AS) * (l - 1)):
        return -1
    return (anzahlFahrten) * trichter_load_time + (anzahlFahrten - 1) * trichter_work_time + (math.ceil(anzahlFahrten/l) - 1) * (fahrt_zeit - ((l - 1) * trichter_load_time + l * trichter_work_time))

def calculateWorkTime_1_2(l):
    if (math.ceil(M/N) < l) or (2 * A / V < (N / AG) * (l - 1)):
        return -1
    return anzahlFahrten * load_time + max(0, fahrt_zeit - (l - 1) * load_time) * (
        math.ceil(anzahlFahrten / l) - 1
    )

def simWorkTime_1(l, verbose = False):
    restMass = M
    total_time = 0

    trucks_time_avalable = []
    for i in range(l):
        trucks_time_avalable.append(0)
    # while work is not done = restMass > 0
    while restMass > 0:
        for i in range(l):
            # truck is loaded
            total_time = max(total_time, trucks_time_avalable[i])
            load_volume = min(N, restMass)
            restMass -= load_volume
            if (verbose):
                print(f"Truck {str(i+1)} loads at {str(round(total_time, 2))} - {str(round(total_time + load_time * (load_volume / N), 2))}")
                print(f"Restmass: {str(restMass)}")
            total_time += load_time * (load_volume / N)
            available_time = total_time + fahrt_zeit

            if (verbose):
                print(f"Truck is available again in: {str(round(available_time, 2))}")

            trucks_time_avalable[i] = available_time

            if restMass <= 0:
                break
    #print(trucks)
    return round(total_time, 2)

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
                print(f"Truck {str(i+1)} dumps at {str(round(total_time, 2))} - {str(round(total_time + truck_work_time, 2))}")
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

xs = []
values_1= []
values_2 = []
values_3 = []
values_4 = []

print("OberflächenvorbereitungTS: ", OberflächenvorbereitungTS)
print("AsphaltverfestigungTS: ", AsphaltverfestigungTS)

oberflaechen_zeit = M / OberflächenvorbereitungTS
asphaltierungs_zeit = M / AsphaltverfestigungTS

x = 1
lastValue1 = 0
lastValue2 = 0
while x < 16:
    values_1.append(round(simWorkTime_1(x), 2))
    values_2.append(oberflaechen_zeit)
    values_3.append(round(simWorkTime_3(x), 2))
    values_4.append(asphaltierungs_zeit)
    
    if lastValue1 == values_1[-1] and lastValue2 == values_3[-1]:
        break
    
    xs.append(x)
    x+=1

# plot the graph
print("xs: ", xs)
print("values_1: ", values_1)
print("values_3: ", values_3)
plt.plot(xs, values_1, label="fraesen_zeit")
plt.plot(xs, values_2, label="oberflaechen_zeit")
plt.plot(xs, values_3, label="asphaltierungs_zeit")
plt.plot(xs, values_4, label="walzen_zeit")
plt.xlabel("Anzahl der LKW")
plt.ylabel("Zeit")
plt.legend()
plt.show()


print("1: ", values_1)
print("2: ", values_2)
print("3: ", values_3)
print("4: ", values_4)


simWorkTime_3(9, True)