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

trichter_load_time = (N - TL) / AS
trichter_work_time = TL / AS


# calculate the time for the trip
fahrt_zeit = 2 * (A / G)


# teeren simulieren
def teeren(l, verbose=False):
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

            dump_volume = min(N, restMass)
            restMass -= dump_volume

            dump_anzahl = dump_volume / TL
            full_dumps = math.floor(dump_anzahl)  # integer
            rest_dump = dump_anzahl - full_dumps  # 0 - 0.99

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

            if verbose:
                print(
                    f"Truck {str(i)} dumps at {str(round(total_time, 2))} - {str(round(total_time + truck_work_time, 2))}"
                )
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

# fräsen simulieren
def fraesen(l, verbose=False):
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
            trucks[i].append(
                {"type": "loadSchutt", "volume": load_volume, "time": total_time}
            )
            if verbose:
                print(
                    "Truck "
                    + str(i)
                    + " loads at "
                    + str(round(total_time, 2))
                    + " - "
                    + str(round(total_time + load_time * (load_volume / N), 2))
                )
                print("Restmass: " + str(restMass))
            trucks[i].append(
                {
                    "type": "drive",
                    "fromTo": "Aw",
                    "volume": load_volume,
                    "time": total_time+load_time * (load_volume / N),
                    "drive_time": fahrt_zeit / 2,
                }
            )
            trucks[i].append(
                {
                    "type": "unloadSchutt",
                    "volume": load_volume,
                    "time": total_time + load_time * (load_volume / N) + fahrt_zeit / 2,
                }
            )
            unloadSchuttTime = 1/12
            trucks[i].append(
                {
                    "type": "drive",
                    "fromTo": "wA",
                    "time": total_time+load_time*(load_volume/N)+fahrt_zeit/2 + unloadSchuttTime,
                    "drive_time": fahrt_zeit / 2,
                }
            )
            total_time += load_time * (load_volume / N) 
            available_time = total_time + fahrt_zeit + unloadSchuttTime

            if verbose:
                print("Truck is available again in: " + str(round(available_time, 2)))

            trucks_time_avalable[i] = available_time

            if restMass <= 0:
                break
    print(trucks[0])
    print(trucks[9])

    return round(total_time, 2)


print(fraesen(10))
