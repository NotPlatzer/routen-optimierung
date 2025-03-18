import math


# Constants
NUTZLAST = 25  # t
V_LKW = 100  # kmh
DISTANZ = 350  # km zum Asphaltwerk
ABBRUCH_LEISTUNG = 50  # t / h
ASPHALTIERUNGS_LEISTUNG = 30  # t / h
VOLUMEN_TRICHTER = 13  # t
LOAD_TIME = NUTZLAST / ABBRUCH_LEISTUNG

TRICHTER_LOAD_TIME = (NUTZLAST - VOLUMEN_TRICHTER) / ASPHALTIERUNGS_LEISTUNG
TRICHTER_WORK_TIME = VOLUMEN_TRICHTER / ASPHALTIERUNGS_LEISTUNG

FAHRT_ZEIT_EINE_RICHTUNG = (DISTANZ / V_LKW) * 60


class Laster:
    def __init__(self, location, load, loadType, activity, StartActivity, EndActivity):
        self.location = location
        self.load = load
        self.loadType = loadType
        self.activity = activity
        self.startActivity = StartActivity
        self.endActivity = EndActivity
        self.goal = None

    def __str__(self):
        return f"Location: {self.location}, Load: {self.load}, LoadType: {self.loadType}, Activity: {self.activity}, StartActivity: {self.StartActivity}, EndActivity: {self.EndActivity}"


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
            f"Maschine(Type: {self.type}, Volume: {self.volume}t, "
            f"Active: {'Ja' if self.active else 'Nein'}, Location: {self.location})"
        )


class Fräse(Maschine):
    def __init__(self, mass):
        self.type = "Fräse"
        self.active = False
        self.fertig = False
        self.mass = mass

    def __str__(self):
        return f"Maschine(Type: {self.type}, Active: {'Ja' if self.active else 'Nein'}, Location: {self.location})"


class Oberflächen(Maschine):

    def __init__(self, mass):
        self.type = "Oberflächen"
        self.active = False
        self.fertig = False
        self.mass = mass

    def __str__(self):
        return (
            f"Maschine(Type: {self.type}, "
            f"Active: {'Ja' if self.active else 'Nein'}, Location: {self.location})"
        )


class Asphaltierer(Maschine):
    def __init__(self, mass):
        self.type = "Asphaltier"
        self.active = False
        self.volume = 0
        self.fertig = False
        self.mass = mass
        

    def __str__(self):
        return (
            f"Maschine(Type: {self.type}, Volume: {self.volume}t, "
            f"Active: {'Ja' if self.active else 'Nein'}, Location: {self.location})"
        )


class Walze(Maschine):
    def __init__(self, mass):
        self.type = "Walze"
        self.active = False
        self.fertig = False
        self.mass = mass

    def __str__(self):
        return f"Maschine(Type: {self.type}, Active: {'Ja' if self.active else 'Nein'}, Location: {self.location})"


def generateLaster(anzahl, location):
    laster = []
    for i in range(anzahl):
        laster.append(Laster(location, 0, None, None, None, None))
    return laster


def simulate():
    timeStep = 1  # minuten
    time = 0

    lasterListe = generateLaster(3, "A")
    baustelle = Baustelle("A", 500)
    baustelle.addMaschine(Fräse(baustelle.mass))
    baustelle.addMaschine(Oberflächen())
    baustelle.addMaschine(Asphaltierer())
    baustelle.addMaschine(Walze())

    while not baustelle.maschinen["Asphaltier"].fertig:
        print(f"Time: {time}")
        for laster in lasterListe:
            if laster.location == baustelle.name:
                if time == laster.endActivity:
                    laster.activity = "None"
                    laster.endActivity = None
                    
                if laster.activity == "None":
                    if laster.loadType == "Schutt" and laster.load > 0:
                        laster.activity = "Drive"
                        laster.location = baustelle.name + "w"
                        laster.startActivity = time
                        laster.endActivity = time + FAHRT_ZEIT_EINE_RICHTUNG
                    if (
                        baustelle.phase < 3
                        and not baustelle.maschinen["Fräse"].fertig
                        and not baustelle.maschinen["Fräse"].active
                        and laster.load < NUTZLAST
                    ):
                        laster.activity = "Fräse"
                        zuLadeneMasse = None
                        if baustelle.maschinen["Fräse"].mass >= NUTZLAST:
                            zuLadeneMasse = NUTZLAST
                        else:
                            zuLadeneMasse = baustelle.maschinen["Fräse"].mass
                        baustelle.maschinen["Fräse"].mass -= zuLadeneMasse
                        laster.load = zuLadeneMasse
                        laster.loadType = "Schutt"
                        laster.startActivity = time
                        laster.endActivity = time + zuLadeneMasse / ABBRUCH_LEISTUNG * 60
                    elif (
                        baustelle.phase > 1
                        and not baustelle.maschinen["Apasphaltier"].ferig
                        and not baustelle.maschinen["Asphaltier"].active
                        and laster.load > 0
                        and laster.loadType == "Teer"
                    ):
                        laster.activity = "Asphaltier"
                        zuBeladeneMasse = None
                        if baustelle.maschinen["Asphaltier"].mass >= NUTZLAST:
                            zuBeladeneMasse = NUTZLAST
                        else:
                            zuBeladeneMasse = baustelle.maschinen["Asphaltier"].mass
                        baustelle.maschinen["Asphaltier"].mass -= zuBeladeneMasse
                        laster.load = 0
                        laster.loadType = None
                        laster.startActivity = time

                        dump_anzahl = zuBeladeneMasse / TRICHTER_WORK_TIME
                        full_dumps = math.floor(dump_anzahl)  # integer
                        rest_dump = (dump_anzahl - full_dumps) # 0 - 0.99
                        rest_dump_time = (rest_dump * VOLUMEN_TRICHTER) / ASPHALTIERUNGS_LEISTUNG
                        full_dump_time = max(0, (full_dumps - 1) * VOLUMEN_TRICHTER / ASPHALTIERUNGS_LEISTUNG)

                        laster.endActivity = time + full_dump_time + rest_dump_time
                    else:
                        laster.activity = None

            if laster.location == baustelle.name + "w":
                if time == laster.endActivity:
                    if laster.loadType == "Schutt":
                        laster.goal = baustelle.name
                        laster.activity = "Abladen"
                        laster.load = 0
                        laster.loadType = None
                        laster.startActivity = time
                        laster.endActivity = (
                            time + 10 * 60
                        )
                        laster.location = "w"
                    else:
                        laster.goal = baustelle.name
                        laster.activity = "Aufladen"
                        laster.startActivity = time
                        laster.load = NUTZLAST
                        laster.loadType = "Teer"
                        laster.endActivity = time + 10 * 60
                        laster.location = "w"

            if laster.location == "w":
                if time == laster.endActivity:
                    laster.activity = "Drive"
                    laster.location = "w" + laster.goal
                    laster.startActivity = time
                    laster.endActivity = time + FAHRT_ZEIT_EINE_RICHTUNG

            if laster.location == "w" + baustelle.name:
                if time == laster.endActivity:
                    if laster.loadType == "Schutt":
                        laster.activity = None
                        laster.startActivity = time
                        laster.endActivity = None
                        laster.location = laster.goal
                    elif laster.load == 0:
                        laster.activity = None
                        laster.startActivity = time
                        laster.endActivity = None
                        laster.location = laster.goal
        
            time += timeStep


simulate()
# sommmer: 15 bis 25 min
# 40 -50
# maybe fixe zohl lkws und wiaviele baustellen konn i mochen
# 5m/min
# dicke schicht
# 25 euro/m2
