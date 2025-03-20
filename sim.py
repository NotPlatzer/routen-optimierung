import math
import copy
import os
import sys
import json

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))
try:
    import myfunctions
except ImportError:
    print("Error importing myfunctions")

# Constants
NUTZLAST = 25  # t
V_LKW = 50  # kmh
ABBRUCH_LEISTUNG = 50  # t / h
OBERFLAECHEN_LEISTUNG = 21  # t / h
ASPHALTIERUNGS_LEISTUNG = 30  # t / h
VOLUMEN_TRICHTER = 13  # t
LOAD_TIME = NUTZLAST / ABBRUCH_LEISTUNG
OBERFLAECHEN_TROCKENDAUER = 20 * 60
OBERFLAECHEN_PUFFER = 10
WALZEN_LEISTUNG = 40  # t / h
WALZEN_PUFFER = 5

MAX_TIME = 100000  # min

TRUCKS_MAX = 10

PHASE_3_START_PUFFER_MIN = 5


TRICHTER_LOAD_TIME = (NUTZLAST - VOLUMEN_TRICHTER) / ASPHALTIERUNGS_LEISTUNG
TRICHTER_WORK_TIME = VOLUMEN_TRICHTER / ASPHALTIERUNGS_LEISTUNG


ABLADEN_WERK_MIN = 5
VOLLADEN_WERK_MIN = 15


VERBOSE = False
VERBOSE_CHANGES = False


def calculate(l, mass, fZeit):
    try:
        print("Calculating...")
        print("Machine 1")
        print(myfunctions.simWorkTime_1(l, mass, NUTZLAST, LOAD_TIME, fZeit*2 / 60, ABLADEN_WERK_MIN / 60, VERBOSE))
        print("Machine 3")
        print(myfunctions.simWorkTime_3(l, mass, NUTZLAST, VOLUMEN_TRICHTER, ASPHALTIERUNGS_LEISTUNG, VOLLADEN_WERK_MIN / 60, fZeit*2 / 60, VERBOSE))
    except ValueError:
        print("Error: Invalid input")
        return


def vprint(*args, **kwargs):
    if VERBOSE:
        print(*args, **kwargs)


class Laster:
    def __init__(self, location):
        self.location = location
        self.load = 0
        self.loadType = None
        self.activity = "Waiting"
        self.startActivity = 0
        self.endActivity = 0
        self.goal = None
    def __str__(self):
        return f"Location: {self.location}, Load: {self.load}, LoadType: {self.loadType}, Activity: {self.activity}, startActivity: {self.startActivity}, endActivity: {self.endActivity}, goal: {self.goal}"


def calculate_Fahrtzeit_eine_Richtung(a, b, distances):
    key = a + b
    if key not in distances.keys():
        return 100
    return distances[key]["duration"]
class Baustelle:
    def __init__(self, name, mass, distances):
        self.startTime = 0
        self.name = name
        self.mass = mass
        self.laster = 0
        self.bestLasterAnzahl = getBestLasterAnzahl(name, mass, distances)
        self.maschinen = {
            "Fraese": None,
            "Oberflaechen": None,
            "Asphaltierer": None,
            "Walze": None
        }
        self.phase = (
            1  # 1: Fraese, 2: asphaltieren und fraesen, 3 : asphalieren, 4 fertgig
        )
        
    
    def addLaster(self, currentTime, distances):
        self.laster += 1
        if self.laster >= 1:
            self.startTime = currentTime
        
        phase_1_finish = calculateWorkTime_1_H(self.laster, mass, calculate_Fahrtzeit_eine_Richtung(self.name, "w", distances) / 60) * 60 # fertig um 1000
        phase_2_finish = min(OBERFLAECHEN_TROCKENDAUER, OBERFLAECHEN_PUFFER + (mass / OBERFLAECHEN_LEISTUNG) * 60) # fertig um 1000 + 20 min + 10 min

        phase_3_work_time_min = simWorkTime_3(self.laster, mass, calculate_Fahrtzeit_eine_Richtung(self.name, "w", distances)  / 60) * 60
        self.phase_3_start = self.startTime + max(self.laster * LOAD_TIME * 60, max(phase_1_finish, phase_2_finish) - phase_3_work_time_min + PHASE_3_START_PUFFER_MIN) # start um 1000 - simWorktime + PUFFER
        #phase_3_start = phase_1_time / 3#timeOfPhase_3(l, mass, fahrt_zeit_eine_richtung) * 60 #
        #print("Phase 1 finish:", phase_1_finish)
        #print("Phase 2 finish:", phase_2_finish)
        #print("Phase 3 work:", phase_3_work_time_min)
        #print("Phase 3 start:", self.phase_3_start)

    def __str__(self):
        return f"Baustelle: {self.name}"


class Maschine:
    def __init__(self):
        self.startActivity = 0
        self.endActivity = 0
        self.mass = 0
        self.location = "z"
        self.goal = None
        self.activity = "Waiting"

    def __str__(self):
        return (
            f"Maschine(Type: {self.type}, Mass: {self.mass}t, "
            f"EndActivity: {self.endActivity}, Location: {self.location}), Mass: {self.mass}"
        )


class Fraese(Maschine):
    def __init__(self):
        self.type = "Fraese"
        self.startActivity = 0
        self.endActivity = 0
        self.mass = 0
        self.location = "z"
        self.goal = None
        self.activity = "Waiting"

    def __str__(self):
        return f"Maschine(Type: {self.type}, EndActivity: {self.endActivity}, Location: {self.location}), Mass: {self.mass}"


class Oberflaechen(Maschine):

    def __init__(self):
        self.type = "Oberflaechen"
        self.startActivity = 0
        self.endActivity = 0
        self.mass = 0
        self.location = "z"
        self.goal = None
        self.activity = "Waiting"

    def __str__(self):
        return f"Maschine(Type: {self.type}, EndActivity: {self.endActivity}, Location: {self.location}), Mass: {self.mass}"


class Asphaltierer(Maschine):
    def __init__(self):
        self.type = "Asphaltierer"
        self.startActivity = 0
        self.endActivity = 0
        self.mass = 0
        self.location = "z"
        self.goal = None
        self.activity = "Waiting"

    def __str__(self):
        return f"Maschine(Type: {self.type}, EndActivity: {self.endActivity}, Location: {self.location}), Mass: {self.mass}"
        


class Walze(Maschine):
    def __init__(self):
        self.type = "Walze"
        self.startActivity = 0
        self.endActivity = 0
        self.mass = 0
        self.location = "z"
        self.goal = None
        self.activity = "Waiting"

    def __str__(self):
        return f"Maschine(Type: {self.type}, EndActivity: {self.endActivity}, Location: {self.location}), Mass: {self.mass}"


def generateLaster(anzahl, location):
    laster = []
    for i in range(anzahl):
        laster.append(Laster(location))
    return laster


# def calculateWorkTime_1_min(l, mass):
# anzahlFahrten = mass / NUTZLAST
# load_time = NUTZLAST / ABBRUCH_LEISTUNG
# fahrt_zeit = (DISTANZ / V_LKW) * 2

# return (anzahlFahrten * load_time + max(0, fahrt_zeit - (l - 1) * load_time) * (math.ceil(anzahlFahrten / l) - 1)) * 60

def compare_baustellen(b1, b2):
    val = True
    for b in b1:
        if b not in b2:
            val = False
            break
        if b1[b]["Phase"] != b2[b]["Phase"]:
            val = False
        for maschine1, maschine2 in zip(b1[b]["Maschinen"], b2[b]["Maschinen"]):
            if maschine1["type"] in ["Fräse", "Asphaltierer"]:
                if maschine1 != maschine2:
                    val = False
    return val

def compare_dicts(d1, d2):
    val = True
    if d1["Laster"] != d2["Laster"]:
        val = False
    if compare_baustellen(d1["Baustellen"], d2["Baustellen"]) == False:
        val = False
    return val


def get_snapshot(baustellen, maschinenListe, lasterListe, currentTime):
    data = {}
    data["Time"] = currentTime
    data["Laster"] = []
    data["Baustellen"] = {}
    data["Maschinen"] = []
    
    for b in baustellen:
        data["Baustellen"][b] = {}
        data["Baustellen"][b]["Phase"] = baustellen[b].phase
        data["Baustellen"][b]["Maschinen"] = []
        for machine in baustellen[b].maschinen.values():
            if machine != None:
                data["Baustellen"][b]["Maschinen"].append(machine.__dict__)
    
    for machine in maschinenListe:
        data["Maschinen"].append(machine.__dict__)
    
    for laster in lasterListe:
        data["Laster"].append(laster.__dict__)
    return data

def printSnapshot(snapshot):
    print("Time:", snapshot["Time"])
    for b in snapshot["Baustellen"].keys():
        print("Baustelle:", b)
        print("Phase:", snapshot["Baustellen"][b]["Phase"])
        for machine in snapshot["Baustellen"][b]["Maschinen"]:
            print(machine)
    print("Laster:")
    for laster in snapshot["Laster"]:
        print(laster)
    print("Maschinen:")
    for machine in snapshot["Maschinen"]:
        print(machine)



def simWorkTime_3(l, mass, fahrt_zeit_eine_richtung, verbose = False):
    restMass = mass
    total_time = 0
    
    trucks_time_avalable = []
    for i in range(l):
        trucks_time_avalable.append(0)
    
    #while work is not done = restMass > 0
    while restMass > 0:
        for i in range(l):
            # truck is loaded
            total_time = max(total_time, trucks_time_avalable[i])
            
            dump_volume = min(NUTZLAST, restMass)
            restMass -= dump_volume
            
            dump_anzahl = dump_volume / VOLUMEN_TRICHTER
            full_dumps = math.floor(dump_anzahl)  # integer
            rest_dump = (dump_anzahl - full_dumps) # 0 - 0.99
            
            rest_dump_time = (rest_dump * VOLUMEN_TRICHTER) / ASPHALTIERUNGS_LEISTUNG
            
            waltz_time = rest_dump_time
            
            if full_dumps == 0:
                full_dump_time = 0
            else:
                full_dump_time = (full_dumps - 1) * VOLUMEN_TRICHTER / ASPHALTIERUNGS_LEISTUNG
                waltz_time += VOLUMEN_TRICHTER / ASPHALTIERUNGS_LEISTUNG
            
            truck_work_time = full_dump_time + rest_dump_time
            available_time = total_time + truck_work_time + fahrt_zeit_eine_richtung * 2
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



def calculateWorkTime_1_H(l, mass, fahrt_zeit_eine_richtung):
    anzahlFahrten = mass / NUTZLAST
    return anzahlFahrten * LOAD_TIME + max(0, fahrt_zeit_eine_richtung * 2 - (l - 1) * LOAD_TIME) * (math.ceil(anzahlFahrten / l) - 1)

def timeOfPhase_3_H(l, mass, fahrt_zeit_eine_richtung):
    return (2 *(mass / (mass / NUTZLAST + (NUTZLAST / ABBRUCH_LEISTUNG + fahrt_zeit_eine_richtung * 2 + ABLADEN_WERK_MIN / 60 + VOLLADEN_WERK_MIN / 60 - (l - 1) * (NUTZLAST - VOLUMEN_TRICHTER) / ASPHALTIERUNGS_LEISTUNG - (VOLUMEN_TRICHTER * l) / ASPHALTIERUNGS_LEISTUNG) * math.floor(mass / (NUTZLAST * l)))) ) / 3


def getBestLasterAnzahl(name, mass, distances):
    fahrt_zeit_eine_richtung = calculate_Fahrtzeit_eine_Richtung("z", name, distances)
    bestL1 = TRUCKS_MAX
    l = 1
    lastValue = -1
    while l <= TRUCKS_MAX:
        zeit = simWorkTime_3(l, mass, fahrt_zeit_eine_richtung)
        
        if lastValue == zeit:
            bestL1 = l
            break
        
        lastValue = zeit
        l += 1

    l = 1
    lastValue = -1
    bestL2 = TRUCKS_MAX
    while l <= TRUCKS_MAX:
        zeit = calculateWorkTime_1_H(l, mass, fahrt_zeit_eine_richtung)
        
        if lastValue == zeit:
            bestL2 = l
            break
        
        lastValue = zeit
        l += 1
    
    return max(bestL1, bestL2)

def simulate(l,inGoingBaustellen, distances):
    maschinen = [
        Fraese(),
        Oberflaechen(),
        Asphaltierer(),
        Walze(),
    ]
    baustellen = {}
    for k in inGoingBaustellen.keys():
        baustellen[k] = Baustelle(k, inGoingBaustellen[k]["größe"], distances)
    
    lasterListe = generateLaster(l, "z")
    
    timeStep = 1  # minuten
    currentTime = 0
    
    saveDatei = {"schritte": []}

    lasterPositions = [[] for _ in range(len(lasterListe))]
    

    prev_snapshot = ""
    while currentTime <= MAX_TIME and not [baustellen[b].phase for b in baustellen] == [5] * len(baustellen):
        vprint(f"Time: {currentTime}")
        for machine in maschinen:        
            if machine.goal != None and machine.location == machine.goal + "z" and currentTime >= machine.endActivity:  
                machine.location = "z"
                machine.activity = "Waiting"
                machine.startActivity = currentTime
                machine.endActivity = 0  
                
            elif machine.mass == 0 and currentTime >= machine.endActivity:
                for b in baustellen:
                    if baustellen[b].phase >= 5:
                        continue

                    type = machine.type
                    
                    if type == "Fraese" and baustellen[b].phase >= 2:
                        continue
                    if type == "Oberflaechen" and baustellen[b].phase >= 3:
                        continue
                    if type == "Asphaltierer" and baustellen[b].phase >= 4:
                        continue
                    
                    for konkurrenten in maschinen:
                        if konkurrenten.type == type and konkurrenten.goal == baustellen[b].name:
                            break
                    else:
                        machine.goal = baustellen[b].name
                        baustellen[machine.goal].maschinen[machine.type] = machine
                        
                        if machine.location in baustellen.keys():
                            baustellen[machine.location].maschinen[machine.type] = None
                        machine.mass = baustellen[machine.goal].mass
                        machine.location = machine.location + baustellen[b].name
                        machine.activity = "Drive"
                        machine.startActivity = currentTime
                        machine.endActivity = currentTime + calculate_Fahrtzeit_eine_Richtung("z", baustellen[b].name, distances)
                        break
                else:
                    if machine.location != "z":
                        machine.activity = "Drive"
                        machine.startActivity = currentTime
                        machine.endActivity = currentTime + calculate_Fahrtzeit_eine_Richtung(machine.location, "z", distances)
                        machine.location = machine.location + "z"
            
            if machine.location == "z" + machine.goal and currentTime >= machine.endActivity:
                machine.location = machine.goal
                machine.activity = "Waiting"
                machine.startActivity = currentTime
                machine.endActivity = 0
            
            # DRIVE FROM A TO B
            elif len(machine.location) >= 2 and "z" not in machine.location:
                if currentTime >= machine.endActivity:
                    machine.activity = "Waiting"
                    machine.startActivity = currentTime
                    machine.endActivity = 0
                    machine.location = machine.location[-1]



        for lasterIndex, laster in enumerate(lasterListe):
            if laster.goal != None and laster.location == laster.goal + "z" and currentTime >= laster.endActivity:  
                laster.location = "z"
                laster.activity = "Waiting"
                laster.endActivity = 0  
                lasterPositions[lasterIndex].append([laster.location, laster.startActivity, None])
            elif laster.goal == None and currentTime >= laster.endActivity:
                for b in baustellen:
                    #count laster working for the same goal
                    count = 0
                    for konkurrenten in lasterListe:
                        if konkurrenten.goal == baustellen[b].name:
                            count += 1
                    
                    if count < baustellen[b].bestLasterAnzahl and baustellen[b].maschinen["Fraese"] != None and baustellen[b].maschinen["Fraese"].mass - count * NUTZLAST > 0:
                        laster.goal = baustellen[b].name
                        laster.location = laster.location + baustellen[b].name
                        laster.activity = "Drive"
                        laster.startActivity = currentTime
                        laster.endActivity = currentTime + calculate_Fahrtzeit_eine_Richtung("z", baustellen[b].name, distances)
                        baustellen[b].addLaster(laster.endActivity, distances)
                        lasterPositions[lasterIndex].append([laster.location, laster.startActivity, laster.endActivity])
                        break
                else:
                    if laster.location != "z":
                        laster.activity = "Drive"
                        laster.startActivity = currentTime
                        laster.endActivity = currentTime + calculate_Fahrtzeit_eine_Richtung(laster.location, "z", distances)
                        laster.location = laster.location + "z"
                        lasterPositions[lasterIndex].append([laster.location, laster.startActivity, laster.endActivity])
                    

            elif laster.goal != None and laster.location == "z" + laster.goal:
                if currentTime >= laster.endActivity:
                    laster.activity = "Waiting"
                    laster.startActivity = currentTime
                    laster.endActivity = 0
                    laster.location = laster.goal
                    lasterPositions[lasterIndex].append([laster.location, currentTime, None])
            elif laster.goal != None and laster.location == "w" + laster.goal:
                if currentTime >= laster.endActivity:
                    if laster.loadType == "Teer":
                        laster.activity = "Waiting"
                        laster.startActivity = currentTime
                        laster.endActivity = 0
                        laster.location = laster.goal
                        lasterPositions[lasterIndex].append([laster.location, currentTime, None])
                    elif laster.load == 0:
                        laster.activity = "Waiting"
                        laster.startActivity = currentTime
                        laster.endActivity = 0
                        laster.location = laster.goal
                        lasterPositions[lasterIndex].append([laster.location, currentTime, None])
                        
            elif laster.location == "wz" and currentTime >= laster.endActivity:
                laster.activity = "Waiting"
                laster.startActivity = currentTime
                laster.endActivity = 0
                laster.location = "z"
                lasterPositions[lasterIndex].append([laster.location, currentTime, None])
            elif len(laster.location) >= 2 and "w" not in laster.location and "z" not in laster.location:
                if currentTime >= laster.endActivity:
                    laster.activity = "Waiting"
                    laster.startActivity = currentTime
                    laster.endActivity = 0
                    laster.location = laster.location[-1]
                    lasterPositions[lasterIndex].append([laster.location, currentTime, None])

            if laster.location == laster.goal:
                if currentTime >= laster.endActivity:
                    laster.activity = "Waiting"
                    laster.endActivity = 0
                
                if baustellen[laster.goal].phase >= 5:
                    laster.goal = None
                    laster.endActivity = 0
                    laster.activity = "Waiting"
                    continue

                if laster.activity == "Waiting":
                    # Wenn Laster leer ist und Fraese noch zu bedienen ist -> Faesenarbeit
                    if (
                        baustellen[laster.goal].maschinen["Fraese"] != None
                        and currentTime >= baustellen[laster.goal].maschinen["Fraese"].endActivity
                        and baustellen[laster.goal].maschinen["Fraese"].mass > 0
                        and laster.load < NUTZLAST
                        and laster.loadType != "Teer"
                        and laster.activity == "Waiting"
                    ):
                        laster.activity = "Fraese"
                        zuLadeneMasse = None
                        if baustellen[laster.goal].maschinen["Fraese"].mass >= NUTZLAST:
                            zuLadeneMasse = NUTZLAST
                        else:
                            zuLadeneMasse = baustellen[laster.goal].maschinen["Fraese"].mass

                        baustellen[laster.goal].maschinen["Fraese"].mass -= zuLadeneMasse
                        
                        laster.load = zuLadeneMasse
                        laster.loadType = "Schutt"
                        laster.startActivity = currentTime
                        laster.endActivity = (
                            currentTime + zuLadeneMasse / ABBRUCH_LEISTUNG * 60
                        )
                        baustellen[laster.goal].maschinen["Fraese"].startActivity = currentTime
                        baustellen[laster.goal].maschinen["Fraese"].endActivity = currentTime + zuLadeneMasse / ABBRUCH_LEISTUNG * 60
                    
                    # Wenn Phase 3 und Asphaltierer hat noch Masse und Laster haben noch zu wenig Teer
                    # -> fahre zur Asphaltierer und hole Teer
                    elif (
                        baustellen[laster.goal].maschinen["Asphaltierer"] != None 
                        and baustellen[laster.goal].phase >= 3
                        and laster.load == 0
                        and baustellen[laster.goal].maschinen["Asphaltierer"].mass > 0
                        and sum(
                            [
                                (
                                    l.load
                                    if l.loadType == "Teer" and l.goal == laster.goal
                                    else 0
                                )
                                for l in lasterListe
                            ]
                        )
                        + sum(
                            [
                                (
                                    NUTZLAST
                                    if l.goal == laster.goal
                                    and l.activity == "Drive"
                                    and l.location == laster.goal + "w"
                                    else 0
                                )
                                for l in lasterListe
                            ]
                        )
                        < baustellen[laster.goal].maschinen["Asphaltierer"].mass
                    ):

                        laster.activity = "Drive"
                        lasterPositions[lasterIndex].append([laster.goal + "w", currentTime, currentTime + calculate_Fahrtzeit_eine_Richtung(laster.goal, "w", distances)])
                        laster.location = laster.goal + "w"
                        laster.startActivity = currentTime
                        laster.endActivity = currentTime + calculate_Fahrtzeit_eine_Richtung(laster.goal, "w", distances)

                    # Wenn Laster noch Schutt geladen hat -> fahre zum Werk und lade ab
                    elif laster.loadType == "Schutt" and laster.load > 0:
                        laster.activity = "Drive"
                        lasterPositions[lasterIndex].append([laster.goal + "w", currentTime, currentTime + calculate_Fahrtzeit_eine_Richtung(laster.goal, "w", distances)])
                        laster.location = laster.goal + "w"
                        laster.startActivity = currentTime
                        laster.endActivity = currentTime + calculate_Fahrtzeit_eine_Richtung(laster.goal, "w", distances)

                    # Wenn Laster noch Teer laden muss und Asphaltierer zu bedienen ist
                    # -> Lade Teer in Asphaltierer
                    if (
                        baustellen[laster.goal].maschinen["Asphaltierer"] != None
                        and baustellen[laster.goal].phase > 1
                        and baustellen[laster.goal].maschinen["Asphaltierer"].mass > 0
                        and (
                                baustellen[laster.goal].maschinen["Oberflaechen"] == None 
                                or baustellen[laster.goal].maschinen["Oberflaechen"].mass - NUTZLAST < baustellen[laster.goal].maschinen["Asphaltierer"].mass
                            )
                        and baustellen[laster.goal].maschinen["Asphaltierer"].endActivity
                        <= currentTime
                        and laster.load > 0
                        and laster.loadType == "Teer"
                        and laster.activity == "Waiting"
                    ):
                        laster.activity = "Asphaltierer"
                        zuBeladeneMasse = None

                        if baustellen[laster.goal].maschinen["Asphaltierer"].mass >= NUTZLAST:
                            zuBeladeneMasse = NUTZLAST
                        else:
                            zuBeladeneMasse = baustellen[laster.goal].maschinen["Asphaltierer"].mass

                        baustellen[laster.goal].maschinen["Asphaltierer"].mass -= zuBeladeneMasse

                        laster.load = 0
                        laster.loadType = None
                        

                        dump_anzahl = zuBeladeneMasse / VOLUMEN_TRICHTER
                        full_dumps = math.floor(dump_anzahl)  # integer
                        rest_dump = dump_anzahl - full_dumps  # 0 - 0.99

                        rest_dump_time = (
                            rest_dump * VOLUMEN_TRICHTER
                        ) / ASPHALTIERUNGS_LEISTUNG * 60

                        full_dump_time = max(
                            0,
                            (full_dumps - 1)
                            * VOLUMEN_TRICHTER
                            / ASPHALTIERUNGS_LEISTUNG * 60,
                        )

                        trichter_dump_time = max(
                            0,
                            full_dumps * VOLUMEN_TRICHTER / ASPHALTIERUNGS_LEISTUNG * 60,
                        )

                        baustellen[laster.goal].maschinen["Asphaltierer"].startActivity = currentTime
                        baustellen[laster.goal].maschinen["Asphaltierer"].endActivity = (
                            currentTime + trichter_dump_time + rest_dump_time
                        )
                        laster.startActivity = currentTime
                        laster.endActivity = (
                            currentTime + full_dump_time + rest_dump_time
                        )
            
            if laster.goal == None:
                continue
            # Wenn Laster an Werk angekommen ist
            # Setze auf Warten und Location auf Werk
            if laster.location == laster.goal + "w":
                if currentTime >= laster.endActivity:
                    laster.activity = "Waiting"
                    laster.location = "w"

            if laster.location == "w":
                if currentTime >= laster.endActivity:
                    # Wenn Laster voll Schutt ist, lade ab
                    if laster.loadType == "Schutt":
                        laster.activity = "Abladen"
                        laster.load = 0
                        laster.loadType = None
                        laster.startActivity = currentTime
                        laster.endActivity = currentTime + ABLADEN_WERK_MIN
                        lasterPositions[lasterIndex].append([laster.location, currentTime, laster.endActivity])

                    # Wenn Laster leer ist und Asphalterierer Masse braucht
                    # -> Lade Teer auf
                    elif (
                        baustellen[laster.goal].maschinen["Asphaltierer"] != None
                        and baustellen[laster.goal].phase >= 3
                        and laster.load == 0
                        and baustellen[laster.goal].maschinen["Asphaltierer"].mass > 0
                        and sum(
                            [l.load if l.loadType == "Teer" else 0 for l in lasterListe]
                        )
                        < baustellen[laster.goal].maschinen["Asphaltierer"].mass
                    ):
                        need_teer = baustellen[laster.goal].maschinen["Asphaltierer"].mass
                        for l in lasterListe:
                            if l.loadType == "Teer" and l.goal == laster.goal:
                                need_teer -= l.load

                        laster.loadType = "Teer"
                        laster.load = min(need_teer, NUTZLAST)
                        laster.activity = "Laden"
                        laster.startActivity = currentTime
                        laster.endActivity = currentTime + (VOLLADEN_WERK_MIN * (laster.load / NUTZLAST))
                        lasterPositions[lasterIndex].append(
                            [laster.location, currentTime, laster.endActivity]
                        )

                    # wenn laster leer und baustelle brauch kuan teer und is isch nichtes mehr obzutrogen und wenn i eaz mit teer start kimm i zur baustelle vor phase dings un
                    # Wenn Laster beim Werk ist, Fraese noch arbeitet und noch nicht genug Laster zur verfügung dafür stehen
                    # -> Fahre zur Baustelle und nimm Schutt mit
                    elif (
                        baustellen[laster.goal].maschinen["Fraese"] != None
                        and baustellen[laster.goal].phase < 3 
                        and laster.load == 0 
                        and baustellen[laster.goal].maschinen["Fraese"].mass > 0 # wos do platzer denkt, wos lim x-> pi von phase 5pi/x isch
                        and sum (
                            [
                                NUTZLAST if l.goal == laster.goal and l.load == 0
                                and (l.location == laster.goal or l.location == "w" + laster.goal) 
                                else 0 for l in lasterListe
                            ]
                        ) < baustellen[laster.goal].maschinen["Fraese"].mass
                    ): 
                        laster.activity = "Drive"
                        laster.location = "w" + laster.goal
                        laster.startActivity = currentTime
                        laster.endActivity = currentTime + calculate_Fahrtzeit_eine_Richtung(laster.goal, "w", distances)
                        lasterPositions[lasterIndex].append(
                            [laster.location, currentTime, laster.endActivity]
                        )

                    # Wenn Laster Teer geladen hat -> fahre zur Baustelle
                    elif laster.loadType == "Teer" and laster.load > 0:
                        laster.activity = "Drive"
                        lasterPositions[lasterIndex].append(["w"+laster.goal, currentTime, currentTime + calculate_Fahrtzeit_eine_Richtung(laster.goal, "w", distances)])
                        laster.location = "w" + laster.goal
                        laster.startActivity = currentTime
                        laster.endActivity = currentTime + calculate_Fahrtzeit_eine_Richtung(laster.goal, "w", distances)
                    else:
                        laster.activity = "Waiting"
                        laster.location = "w"
                        laster.endActivity = 0
                        laster.goal = None

        for baustelle in baustellen:
            if ((baustellen[baustelle].maschinen["Oberflaechen"] != None and baustellen[baustelle].maschinen["Oberflaechen"].mass > 0)
                and (baustellen[baustelle].maschinen["Fraese"] != None 
                    and (
                    baustellen[baustelle].maschinen["Oberflaechen"].mass > 0 and (
                    baustellen[baustelle].maschinen["Fraese"].mass
                    < baustellen[baustelle].maschinen["Oberflaechen"].mass
                    - OBERFLAECHEN_LEISTUNG / 60
                    - OBERFLAECHEN_PUFFER
                    or baustellen[baustelle].maschinen["Fraese"].mass == 0)
                ) or (baustellen[baustelle].maschinen["Fraese"] == None))
            ):
                baustellen[baustelle].maschinen["Oberflaechen"].mass -= OBERFLAECHEN_LEISTUNG / 60
                if baustellen[baustelle].maschinen["Oberflaechen"].mass < 0:
                    baustellen[baustelle].maschinen["Oberflaechen"].mass = 0

            if (
                (
                    baustellen[baustelle].maschinen["Walze"] != None 
                    and baustellen[baustelle].maschinen["Walze"].mass > 0 
                    and baustellen[baustelle].phase >= 4
                )
                and 
                (
                    baustellen[baustelle].maschinen["Asphaltierer"] != None
                    and (
                        baustellen[baustelle].maschinen["Walze"].mass > 0
                        and (
                            baustellen[baustelle].maschinen["Asphaltierer"].mass
                            < baustellen[baustelle].maschinen["Walze"].mass
                            - WALZEN_LEISTUNG / 60
                            - WALZEN_PUFFER
                            or baustellen[baustelle].maschinen["Asphaltierer"].mass == 0
                        ) 
                        and (
                            (baustellen[baustelle].maschinen["Asphaltierer"].mass == 0
                            and baustellen[baustelle].maschinen["Asphaltierer"].endActivity <= currentTime)
                            
                            or baustellen[baustelle].maschinen["Walze"].mass > WALZEN_PUFFER
                        )
                    ) or (baustellen[baustelle].maschinen["Asphaltierer"] == None)
                )
                ):
                baustellen[baustelle].maschinen["Walze"].mass -= WALZEN_LEISTUNG / 60
                if baustellen[baustelle].maschinen["Walze"].mass < 0:
                    baustellen[baustelle].maschinen["Walze"].mass = 0


            if baustellen[baustelle].phase == 1 and (baustellen[baustelle].maschinen["Fraese"] != None and baustellen[baustelle].maschinen["Oberflaechen"] != None):
                if (
                    baustellen[baustelle].mass - OBERFLAECHEN_PUFFER >= baustellen[baustelle].maschinen["Fraese"].mass
                    and baustellen[baustelle].phase < 2
                ):
                    baustellen[baustelle].phase = 2
                    vprint("Start Phase 2")
            if baustellen[baustelle].phase == 2 and (baustellen[baustelle].maschinen["Oberflaechen"] != None and baustellen[baustelle].maschinen["Asphaltierer"] != None):
                if currentTime >= baustellen[baustelle].phase_3_start:
                    baustellen[baustelle].phase = 3
                    vprint("Start Phase 3")
            if baustellen[baustelle].phase == 3 and (baustellen[baustelle].maschinen["Asphaltierer"] != None and baustellen[baustelle].maschinen["Walze"] != None):
                if (
                    baustellen[baustelle].mass - WALZEN_PUFFER >= baustellen[baustelle].maschinen["Asphaltierer"].mass
                    and baustellen[baustelle].phase < 4
                ):
                    baustellen[baustelle].phase = 4
                    vprint("Start Phase 4")
            if baustellen[baustelle].phase == 4 and baustellen[baustelle].maschinen["Walze"] != None:
                if baustellen[baustelle].maschinen["Walze"].mass == 0:
                    baustellen[baustelle].phase = 5
                    vprint("Walzen fertig")
                    break
            vprint("Phase:", baustellen[baustelle].phase)

            vprint("Maschinen:")
            for maschine in maschinen:
                vprint(maschine)
            vprint("Laster:")
            for laster in lasterListe:
                vprint(laster)
            snapshot = get_snapshot(baustellen, maschinen, lasterListe, currentTime)
            if prev_snapshot == ""  or not compare_dicts(snapshot, prev_snapshot):  # only print if something changed
                saveDatei["schritte"].append(snapshot)

            if VERBOSE_CHANGES:
                snapshot = get_snapshot(baustellen, maschinen, lasterListe, currentTime)
                if prev_snapshot == ""  or not compare_dicts(snapshot, prev_snapshot):  # only print if something changed
                    printSnapshot(snapshot)
                    print()
                    print("-" * 40)  # separator for clarity
            prev_snapshot = copy.deepcopy(snapshot)

            vprint("Phase:", baustellen[baustelle].phase)
            for maschine in baustellen[baustelle].maschinen:
                vprint(baustellen[baustelle].maschinen[maschine])
            vprint("Laster:")
            for i, laster in enumerate(lasterListe):
                vprint(laster)
        
        currentTime += timeStep
    
    snapshot = get_snapshot(baustellen, maschinen, lasterListe, currentTime)
    printSnapshot(snapshot)
    newPositions = []
    for laster in lasterPositions:
        l = []
        for i,pos in enumerate(laster):
            if pos[2] == None and i < len(laster) - 1:
                pos[2] = laster[i+1][1]
            if pos[2] == None:
                pos[2] = 1000000000000
            l.append([pos[0], pos[2]-pos[1]])
        newPositions.append(l)
    return newPositions


# print everything in output.txt
# sys.stdout = open("output.txt", "w")

fZeit = 175 / V_LKW * 60
mass = 200
# ergebnis = simulate(3, mass, fZeit)

# print(ergebnis)


# open("ergebnisSim.json", "w").write(json.dumps(ergebnis, indent=4))
# sommmer: 15 bis 25 min
# 40 -50
# maybe fixe zohl lkws und wiaviele baustellen konn i mochen
# 5m/min
# dicke schicht
# 25 euro/m2


# calculate(3, mass, fZeit)
print(calculateWorkTime_1_H(3, 200, fZeit / 60))