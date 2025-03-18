import math
import time

# Constants
NUTZLAST = 25  # t
V_LKW = 100  # kmh
DISTANZ = 350  # km zum Asphaltwerk
ABBRUCH_LEISTUNG = 50  # t / h
OBERFLAECHEN_LEISTUNG = 21  # t / h
ASPHALTIERUNGS_LEISTUNG = 30  # t / h
VOLUMEN_TRICHTER = 13  # t
LOAD_TIME = NUTZLAST / ABBRUCH_LEISTUNG
OBERFLAECHEN_TROCKENDAUER = 20 * 60
OBERFLAECHEN_PUFFER = 1
WALZEN_LEISTUNG = 40  # t / h
WALZEN_PUFFER = 1

NEU_ASPHALT_LADE_ZEIT_MIN = 30

TRICHTER_LOAD_TIME = (NUTZLAST - VOLUMEN_TRICHTER) / ASPHALTIERUNGS_LEISTUNG
TRICHTER_WORK_TIME = VOLUMEN_TRICHTER / ASPHALTIERUNGS_LEISTUNG

FAHRT_ZEIT_EINE_RICHTUNG = (DISTANZ / V_LKW) * 60


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
        return f"Location: {self.location}, Load: {self.load}, LoadType: {self.loadType}, Activity: {self.activity}, startActivity: {self.startActivity}, endActivity: {self.endActivity}"


class Baustelle:
    def __init__(self, name, mass):
        self.name = name
        self.mass = mass
        self.maschinen = {}
        self.anzahlFahrten = mass / NUTZLAST
        self.phase = (
            1  # 1: Fräse, 2: asphaltieren und fräsen, 3 : asphalieren, 4 fertgig
        )

    def addMaschine(self, maschine):
        self.maschinen[maschine.type] = maschine
        print(f"Maschine {maschine.type} wurde hinzugefügt.")

    def __str__(self):
        maschinen_str = "\n".join(str(m) for m in self.maschinen)
        return f"Baustelle: {self.name}\nMaschinen:\n{maschinen_str if maschinen_str else 'Keine Maschinen vorhanden'}"


class Maschine:
    def __init__(self, mass):
        self.active = 0
        self.location = 0
        self.fertig = False
        self.mass = mass

    def __str__(self):
        return (
            f"Maschine(Type: {self.type}, Mass: {self.mass}t, "
            f"Active: {'Ja' if self.active else 'Nein'}, Location: {self.location}), Fertig: {self.fertig}, Mass: {self.mass}"
        )


class Fräse(Maschine):
    def __init__(self, mass):
        self.type = "Fräse"
        self.active = False
        self.fertig = False
        self.mass = mass
        self.location = 0

    def __str__(self):
        return f"Maschine(Type: {self.type}, Active: {'Ja' if self.active else 'Nein'}, Location: {self.location}), Mass: {self.mass}"


class Oberflächen(Maschine):

    def __init__(self, mass):
        self.type = "Oberflächen"
        self.active = False
        self.fertig = False
        self.mass = mass
        self.location = 0

    def __str__(self):
        return (
            f"Maschine(Type: {self.type}, "
            f"Active: {'Ja' if self.active else 'Nein'}, Location: {self.location}), Mass: {self.mass}"
        )


class Asphaltierer(Maschine):
    def __init__(self, mass):
        self.type = "Asphaltierer"
        self.active = False
        self.volume = 0
        self.fertig = False
        self.mass = mass
        self.location = 0
        

    def __str__(self):
        return (
            f"Maschine(Type: {self.type}, Volume: {self.volume}t, "
            f"Active: {'Ja' if self.active else 'Nein'}, Location: {self.location}), Mass: {self.mass}"
        )


class Walze(Maschine):
    def __init__(self, mass):
        self.type = "Walze"
        self.active = False
        self.fertig = False
        self.mass = mass
        self.location = 0

    def __str__(self):
        return f"Maschine(Type: {self.type}, Active: {'Ja' if self.active else 'Nein'}, Location: {self.location}), Mass: {self.mass}"


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


def simulate(l):
    timeStep = 1  # minuten
    currentTime = 0

    lasterListe = generateLaster(l, "A")
    baustelle = Baustelle("A", 500)
    baustelle.addMaschine(Fräse(baustelle.mass))
    baustelle.addMaschine(Oberflächen(baustelle.mass))
    baustelle.addMaschine(Asphaltierer(baustelle.mass))
    baustelle.addMaschine(Walze(baustelle.mass))

    while baustelle.phase < 5:
        print(f"Time: {currentTime}")
        for laster in lasterListe:
            if laster.location == baustelle.name:
                if currentTime >= laster.endActivity:
                    if laster.activity == "Fräse":
                        baustelle.maschinen["Fräse"].active = False
                    if laster.activity == "Asphaltierer":
                        baustelle.maschinen["Asphaltierer"].active = False
                    laster.activity = "Waiting"
                    laster.endActivity = 0

            if laster.activity == "Waiting":
                if currentTime >= laster.endActivity:
                    if baustelle.phase >= 3 and laster.load == 0:
                        laster.activity = "Drive"
                        laster.location = baustelle.name + "w"
                        laster.startActivity = currentTime
                        laster.endActivity = currentTime + FAHRT_ZEIT_EINE_RICHTUNG
                    if laster.loadType == "Schutt" and laster.load > 0:
                        laster.activity = "Drive"
                        laster.location = baustelle.name + "w"
                        laster.startActivity = currentTime
                        laster.endActivity = currentTime + FAHRT_ZEIT_EINE_RICHTUNG

                    if (
                        baustelle.phase < 3
                        and not baustelle.maschinen["Fräse"].fertig
                        and not baustelle.maschinen["Fräse"].active
                        and laster.load < NUTZLAST and laster.activity == "Waiting"
                    ):
                        laster.activity = "Fräse"
                        zuLadeneMasse = None
                        if baustelle.maschinen["Fräse"].mass >= NUTZLAST:
                            zuLadeneMasse = NUTZLAST
                        else:
                            zuLadeneMasse = baustelle.maschinen["Fräse"].mass

                        baustelle.maschinen["Fräse"].mass -= zuLadeneMasse
                        baustelle.maschinen["Fräse"].active = True
                        laster.load = zuLadeneMasse
                        laster.loadType = "Schutt"
                        laster.startActivity = currentTime
                        laster.endActivity = currentTime + zuLadeneMasse / ABBRUCH_LEISTUNG * 60
                    elif (
                        baustelle.phase > 1
                        and not baustelle.maschinen["Asphaltierer"].fertig
                        and not baustelle.maschinen["Asphaltierer"].active
                        and laster.load > 0
                        and laster.loadType == "Teer"
                        and laster.activity == "Waiting"
                    ):
                        laster.activity = "Asphaltierer"
                        zuBeladeneMasse = None
                        if baustelle.maschinen["Asphaltierer"].mass >= NUTZLAST:
                            zuBeladeneMasse = NUTZLAST
                        else:
                            zuBeladeneMasse = baustelle.maschinen["Asphaltierer"].mass
                        print(zuBeladeneMasse)
                        if zuBeladeneMasse == 0:
                            continue
                        baustelle.maschinen["Asphaltierer"].mass -= zuBeladeneMasse
                        baustelle.maschinen["Asphaltierer"].active = True
                        laster.load = 0
                        laster.loadType = None
                        laster.startActivity = currentTime

                        dump_anzahl = zuBeladeneMasse / TRICHTER_WORK_TIME
                        full_dumps = math.floor(dump_anzahl)  # integer
                        rest_dump = (dump_anzahl - full_dumps) # 0 - 0.99
                        rest_dump_time = (rest_dump * VOLUMEN_TRICHTER) / ASPHALTIERUNGS_LEISTUNG
                        full_dump_time = max(0, (full_dumps - 1) * VOLUMEN_TRICHTER / ASPHALTIERUNGS_LEISTUNG)

                        laster.endActivity = currentTime + full_dump_time + rest_dump_time

            if laster.location == baustelle.name + "w":
                if currentTime >= laster.endActivity:
                    if laster.loadType == "Schutt":
                        laster.goal = baustelle.name
                        laster.activity = "Abladen"
                        laster.load = 0
                        laster.loadType = None
                        laster.startActivity = currentTime
                        laster.endActivity = (
                            currentTime + 10 / 60
                        )
                        laster.location = "w"
                    else:
                        laster.goal = baustelle.name
                        laster.activity = "Aufladen"
                        laster.startActivity = currentTime
                        laster.load = NUTZLAST
                        laster.loadType = "Teer"
                        laster.endActivity = currentTime + 10 / 60
                        laster.location = "w"

            if laster.location == "w":
                if currentTime >= laster.endActivity:
                    if baustelle.phase >= 3 and laster.load == 0:
                        laster.loadType = "Teer"
                        laster.load = NUTZLAST
                        laster.activity = "Laden"
                        laster.startActivity = currentTime
                        laster.endActivity = currentTime + NEU_ASPHALT_LADE_ZEIT_MIN
                    else:
                        laster.activity = "Drive"
                        laster.location = "w" + laster.goal
                        laster.startActivity = currentTime
                        laster.endActivity = currentTime + FAHRT_ZEIT_EINE_RICHTUNG

            if laster.location == "w" + baustelle.name:
                if currentTime >= laster.endActivity:
                    if laster.loadType == "Teer":
                        laster.activity = "Waiting"
                        laster.startActivity = currentTime
                        laster.endActivity = 0
                        laster.location = laster.goal
                    elif laster.load == 0:
                        laster.activity = "Waiting"
                        laster.startActivity = currentTime
                        laster.endActivity = 0
                        laster.location = laster.goal

        if baustelle.maschinen["Oberflächen"].mass > 0 and (baustelle.maschinen["Fräse"].mass < baustelle.maschinen["Oberflächen"].mass - OBERFLAECHEN_LEISTUNG / 60 - OBERFLAECHEN_PUFFER or baustelle.maschinen["Fräse"].mass == 0):
            baustelle.maschinen["Oberflächen"].mass -= OBERFLAECHEN_LEISTUNG / 60
            if baustelle.maschinen["Oberflächen"].mass < 0:
                baustelle.maschinen["Oberflächen"].mass = 0

        if baustelle.phase >= 4 and baustelle.maschinen["Walze"].mass > 0 and (baustelle.maschinen["Asphaltierer"].mass < baustelle.maschinen["Walze"].mass - WALZEN_LEISTUNG / 60 - WALZEN_PUFFER or baustelle.maschinen["Asphaltierer"].mass == 0):
            baustelle.maschinen["Walze"].mass -= WALZEN_LEISTUNG / 60
            if baustelle.maschinen["Walze"].mass < 0:
                baustelle.maschinen["Walze"].mass = 0

        if baustelle.phase == 1:
            if (
                baustelle.mass - 8 >= baustelle.maschinen["Fräse"].mass
                and baustelle.phase < 2
            ):
                baustelle.phase = 2
                print("Start Phase 2")
        if baustelle.phase == 2:
            if baustelle.maschinen["Oberflächen"].mass == 0:
                baustelle.maschinen["Oberflächen"].fertig = True
                baustelle.phase = 3
                print("Oberflächen fertig")
        if baustelle.phase == 3:
            if (
                baustelle.mass - 8 >= baustelle.maschinen["Asphaltierer"].mass
                and baustelle.phase < 4
            ):
                baustelle.phase = 4
                print("Start Phase 4")
        if baustelle.phase == 4:
            if baustelle.maschinen["Walze"].mass == 0:
                baustelle.maschinen["Walze"].fertig = True
                baustelle.phase = 5
                print("Walzen fertig")
                break
        print("Phase: ", baustelle.phase)
        for maschine in baustelle.maschinen:
            print(baustelle.maschinen[maschine])
        print("Laster:")
        for laster in lasterListe:
            print(laster)

        currentTime += timeStep
        # time.sleep(0.005)

    print("Phase: ", baustelle.phase)
    for maschine in baustelle.maschinen:
        print(baustelle.maschinen[maschine])
    print("Laster:")
    for laster in lasterListe:
        print(laster)

simulate(5)
# sommmer: 15 bis 25 min
# 40 -50
# maybe fixe zohl lkws und wiaviele baustellen konn i mochen
# 5m/min
# dicke schicht
# 25 euro/m2
