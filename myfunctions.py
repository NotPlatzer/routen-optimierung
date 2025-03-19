import math

def calculateWorkTime_1_2(l, anzahlFahrten, fahrt_zeit, load_time):
    return anzahlFahrten * load_time + max(0, fahrt_zeit - (l - 1) * load_time) * (
        math.ceil(anzahlFahrten / l) - 1
    )

def simWorkTime_1(l, M, N, load_time, fahrt_zeit, abladen_werk_h, verbose = False):
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
            available_time = total_time + fahrt_zeit + abladen_werk_h

            if (verbose):
                print(f"Truck is available again in: {str(round(available_time, 2))}")

            trucks_time_avalable[i] = available_time

            if restMass <= 0:
                break
    #print(trucks)
    return round(total_time, 2)

def simWorkTime_3(l, M, N, TL, AS, fahrt_zeit, asphalt_lade_zeit_h, verbose = False):
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
            available_time = total_time + truck_work_time + fahrt_zeit + asphalt_lade_zeit_h
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

