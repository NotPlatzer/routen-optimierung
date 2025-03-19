import math
import json

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
OBERFLAECHEN_PUFFER = 10
WALZEN_LEISTUNG = 40  # t / h
WALZEN_PUFFER = 5


TRICHTER_LOAD_TIME = (NUTZLAST - VOLUMEN_TRICHTER) / ASPHALTIERUNGS_LEISTUNG
TRICHTER_WORK_TIME = VOLUMEN_TRICHTER / ASPHALTIERUNGS_LEISTUNG

FAHRT_ZEIT_EINE_RICHTUNG = (DISTANZ / V_LKW) * 60


NEU_ASPHALT_LADE_ZEIT_MIN = 30
ABLADEN_WERK_H = 0.05
VOLLADEN_WERK_H = NEU_ASPHALT_LADE_ZEIT_MIN / 60


VERBOSE = False
VERBOSE_CHANGES = False


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
        return f"Location: {self.location}, Load: {self.load}, LoadType: {self.loadType}, Activity: {self.activity}, startActivity: {self.startActivity}, endActivity: {self.endActivity}"


class Baustelle:
    def __init__(self, name, mass):
        self.name = name
        self.mass = mass
        self.maschinen = {}
        self.anzahlFahrten = mass / NUTZLAST
        self.phase = (
            1  # 1: Fraese, 2: asphaltieren und fraesen, 3 : asphalieren, 4 fertgig
        )

    def addMaschine(self, maschine):
        self.maschinen[maschine.type] = maschine
        vprint(f"Maschine {maschine.type} wurde hinzugefügt.")

    def __str__(self):
        maschinen_str = "\n".join(str(m) for m in self.maschinen)
        return f"Baustelle: {self.name}\nMaschinen:\n{maschinen_str if maschinen_str else 'Keine Maschinen vorhanden'}"


class Maschine:
    def __init__(self, mass):
        self.endActivity = 0
        self.location = 0
        self.fertig = False
        self.mass = mass

    def __str__(self):
        return (
            f"Maschine(Type: {self.type}, Mass: {self.mass}t, "
            f"EndActivity: {self.endActivity}, Location: {self.location}), Fertig: {self.fertig}, Mass: {self.mass}"
        )


class Fraese(Maschine):
    def __init__(self, mass):
        self.type = "Fraese"
        self.endActivity = 0
        self.fertig = False
        self.mass = mass
        self.location = 0

    def __str__(self):
        return f"Maschine(Type: {self.type}, EndActivity: {self.endActivity}, Location: {self.location}), Mass: {self.mass}"


class Oberflaechen(Maschine):

    def __init__(self, mass):
        self.type = "Oberflaechen"
        self.endActivity = 0
        self.fertig = False
        self.mass = mass
        self.location = 0

    def __str__(self):
        return (
            f"Maschine(Type: {self.type}, "
            f"EndActivity: {self.endActivity}, Location: {self.location}), Mass: {self.mass}"
        )


class Asphaltierer(Maschine):
    def __init__(self, mass):
        self.type = "Asphaltierer"
        self.endActivity = 0
        self.volume = 0
        self.fertig = False
        self.mass = mass
        self.location = 0

    def __str__(self):
        return (
            f"Maschine(Type: {self.type}, Volume: {self.volume}t, "
            f"EndActivity: {self.endActivity}, Location: {self.location}), Mass: {self.mass}"
        )


class Walze(Maschine):
    def __init__(self, mass):
        self.type = "Walze"
        self.endActivity = 0
        self.fertig = False
        self.mass = mass
        self.location = 0

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

def calculateFullTime(l, mass):
    ges = mass/ABBRUCH_LEISTUNG + math.ceil(mass/(NUTZLAST*l)) * ((2 * DISTANZ / V_LKW + ABLADEN_WERK_H + VOLLADEN_WERK_H + (NUTZLAST - VOLUMEN_TRICHTER) / ASPHALTIERUNGS_LEISTUNG) - (l-1) * NUTZLAST/ABBRUCH_LEISTUNG) + VOLUMEN_TRICHTER/ASPHALTIERUNGS_LEISTUNG
    return ges

def get_snapshot(baustelle, lasterListe):
    lines = []
    lines.append(f"Phase: {baustelle.phase}")
    for machine in baustelle.maschinen.values():
        lines.append(str(machine))
    lines.append("Laster:")
    for laster in lasterListe:
        lines.append(str(laster))
    return "\n".join(lines)


def simulate(l):
    timeStep = 1  # minuten
    currentTime = 0
    saveDatei = {"schritte": []}

    lasterListe = generateLaster(l, "A")
    baustelle = Baustelle("A", 500)
    baustelle.addMaschine(Fraese(baustelle.mass))
    baustelle.addMaschine(Oberflaechen(baustelle.mass))
    baustelle.addMaschine(Asphaltierer(baustelle.mass))
    baustelle.addMaschine(Walze(baustelle.mass))

    prev_snapshot = ""
    while baustelle.phase < 5:
        vprint(f"Time: {currentTime}")
        for laster in lasterListe:
            if laster.location == baustelle.name:
                if currentTime >= laster.endActivity:

                    # random code
                    if laster.activity == "Fraese":
                        if baustelle.maschinen["Fraese"].endActivity > currentTime:
                            print("ADFNJIADNAISDHD")
                        baustelle.maschinen["Fraese"].endActivity = 0

                    laster.activity = "Waiting"
                    laster.endActivity = 0

                if laster.activity == "Waiting":
                    # Wenn Phase 3 und Asphaltierer hat noch Masse und Laster haben noch zu wenig Teer
                    # -> fahre zur Asphaltierer und hole Teer
                    if (
                        baustelle.phase >= 3
                        and laster.load == 0
                        and baustelle.maschinen["Asphaltierer"].mass > 0
                        and sum(
                            [
                                (
                                    l.load
                                    if l.loadType == "Teer" and l.goal == baustelle.name
                                    else 0
                                )
                                for l in lasterListe
                            ]
                        )
                        + sum(
                            [
                                (
                                    NUTZLAST
                                    if l.goal == baustelle.name
                                    and l.activity == "Drive"
                                    and l.location == baustelle.name + "w"
                                    else 0
                                )
                                for l in lasterListe
                            ]
                        )
                        < baustelle.maschinen["Asphaltierer"].mass
                    ):

                        laster.activity = "Drive"
                        laster.location = baustelle.name + "w"
                        laster.startActivity = currentTime
                        laster.endActivity = currentTime + FAHRT_ZEIT_EINE_RICHTUNG

                    # Wenn Laster noch Schutt geladen hat -> fahre zur Asphaltierer
                    if laster.loadType == "Schutt" and laster.load > 0:
                        laster.activity = "Drive"
                        laster.location = baustelle.name + "w"
                        laster.startActivity = currentTime
                        laster.endActivity = currentTime + FAHRT_ZEIT_EINE_RICHTUNG

                    # Wenn Laster leer ist und Fraese noch zu bedienen ist -> Faesenarbeit
                    if (
                        baustelle.phase < 3
                        and not baustelle.maschinen["Fraese"].fertig
                        and not baustelle.maschinen["Fraese"].endActivity
                        and laster.load < NUTZLAST
                        and laster.activity == "Waiting"
                    ):
                        laster.activity = "Fraese"
                        zuLadeneMasse = None
                        if baustelle.maschinen["Fraese"].mass >= NUTZLAST:
                            zuLadeneMasse = NUTZLAST
                        else:
                            zuLadeneMasse = baustelle.maschinen["Fraese"].mass

                        baustelle.maschinen["Fraese"].mass -= zuLadeneMasse
                        baustelle.maschinen["Fraese"].endActivity = True
                        laster.load = zuLadeneMasse
                        laster.loadType = "Schutt"
                        laster.startActivity = currentTime
                        laster.endActivity = (
                            currentTime + zuLadeneMasse / ABBRUCH_LEISTUNG * 60
                        )

                    # Wenn Laster noch Teer laden muss und Asphaltierer zu bedienen ist
                    # -> Lade Teer in Asphaltierer
                    elif (
                        baustelle.phase > 1
                        and not baustelle.maschinen["Asphaltierer"].fertig
                        and baustelle.maschinen["Asphaltierer"].endActivity
                        <= currentTime
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

                        vprint(zuBeladeneMasse)

                        if zuBeladeneMasse == 0:
                            continue
                        baustelle.maschinen["Asphaltierer"].mass -= zuBeladeneMasse

                        laster.load = 0
                        laster.loadType = None
                        laster.startActivity = currentTime

                        dump_anzahl = zuBeladeneMasse / TRICHTER_WORK_TIME
                        full_dumps = math.floor(dump_anzahl)  # integer
                        rest_dump = dump_anzahl - full_dumps  # 0 - 0.99
                        rest_dump_time = (
                            rest_dump * VOLUMEN_TRICHTER
                        ) / ASPHALTIERUNGS_LEISTUNG
                        full_dump_time = max(
                            0,
                            (full_dumps - 1)
                            * VOLUMEN_TRICHTER
                            / ASPHALTIERUNGS_LEISTUNG,
                        )
                        trichter_dump_time = max(
                            0,
                            full_dumps * VOLUMEN_TRICHTER / ASPHALTIERUNGS_LEISTUNG,
                        )

                        baustelle.maschinen["Asphaltierer"].endActivity = (
                            currentTime + trichter_dump_time + rest_dump_time
                        )
                        laster.endActivity = (
                            currentTime + full_dump_time + rest_dump_time
                        )

            # Wenn Laster an Werk angekommen ist
            # Setze auf Warten und Location auf Werk
            if laster.location == baustelle.name + "w":
                if currentTime >= laster.endActivity:
                    laster.activity = "Waiting"
                    laster.location = "w"

            if laster.location == "w":
                if currentTime >= laster.endActivity:
                    # Wenn Laster voll Schutt ist, lade ab
                    if laster.loadType == "Schutt":
                        laster.goal = baustelle.name
                        laster.activity = "Abladen"
                        laster.load = 0
                        laster.loadType = None
                        laster.startActivity = currentTime
                        laster.endActivity = currentTime + ABLADEN_WERK_H * 60
                    
                    
                    # Wenn Laster leer ist und Asphalterierer Masse braucht
                    # -> Lade Teer auf
                    if (
                        baustelle.phase >= 3
                        and laster.load == 0
                        and baustelle.maschinen["Asphaltierer"].mass > 0
                        and sum(
                            [l.load if l.loadType == "Teer" else 0 for l in lasterListe]
                        )
                        < baustelle.maschinen["Asphaltierer"].mass
                    ):
                        need_teer = baustelle.maschinen["Asphaltierer"].mass
                        for l in lasterListe:
                            if l.loadType == "Teer" and l.goal == baustelle.name:
                                need_teer -= l.load

                        laster.loadType = "Teer"
                        laster.goal = baustelle.name
                        laster.load = min(need_teer, NUTZLAST)
                        laster.activity = "Laden"
                        laster.startActivity = currentTime
                        laster.endActivity = currentTime + (NEU_ASPHALT_LADE_ZEIT_MIN * need_teer / NUTZLAST)
                    
                    #wenn laster leer und baustelle brauch kuan teer und is isch nichtes mehr obzutrogen und wenn i eaz mit teer start kimm i zur baustelle vor phase dings un
                    # Wenn Laster beim Werk ist, Fraese noch arbeitet und noch nicht genug Laster zur verfügung dafür stehen
                    # -> Fahre zur Baustelle und nimm Schutt mit
                    elif (
                            baustelle.phase < 3 
                            and laster.load == 0 
                            and baustelle.maschinen["Fraese"].mass > 0 # wos do platzer denkt, wos lim x-> pi von phase 5pi/x isch
                            and sum (
                                [
                                    NUTZLAST if l.goal == baustelle.name and l.load == 0
                                    and (l.location == baustelle.name or l.location == "w" + baustelle.name) 
                                    else 0 for l in lasterListe
                                ]
                            ) < baustelle.maschinen["Fraese"].mass
                        ): 
                        laster.activity = "Drive"
                        laster.location = "w" + laster.goal
                        laster.startActivity = currentTime
                        laster.endActivity = currentTime + FAHRT_ZEIT_EINE_RICHTUNG
                    
                    # Wenn Laster Teer geladen hat -> fahre zur Baustelle
                    elif laster.loadType == "Teer" and laster.load > 0:
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

        if baustelle.maschinen["Oberflaechen"].mass > 0 and (
            baustelle.maschinen["Fraese"].mass
            < baustelle.maschinen["Oberflaechen"].mass
            - OBERFLAECHEN_LEISTUNG / 60
            - OBERFLAECHEN_PUFFER
            or baustelle.maschinen["Fraese"].mass == 0
        ):
            baustelle.maschinen["Oberflaechen"].mass -= OBERFLAECHEN_LEISTUNG / 60
            if baustelle.maschinen["Oberflaechen"].mass < 0:
                baustelle.maschinen["Oberflaechen"].mass = 0

        if (
            baustelle.phase >= 4
            and baustelle.maschinen["Walze"].mass > 0
            and (
                baustelle.maschinen["Asphaltierer"].mass
                < baustelle.maschinen["Walze"].mass
                - WALZEN_LEISTUNG / 60
                - WALZEN_PUFFER
                or baustelle.maschinen["Asphaltierer"].mass == 0
            )
        ):
            baustelle.maschinen["Walze"].mass -= WALZEN_LEISTUNG / 60
            if baustelle.maschinen["Walze"].mass < 0:
                baustelle.maschinen["Walze"].mass = 0

        if baustelle.phase == 1:
            if (
                baustelle.mass - 8 >= baustelle.maschinen["Fraese"].mass
                and baustelle.phase < 2
            ):
                baustelle.phase = 2
                vprint("Start Phase 2")
        if baustelle.phase == 2:
            if baustelle.maschinen["Oberflaechen"].mass == 0:
                baustelle.maschinen["Oberflaechen"].fertig = True
                baustelle.phase = 3
                vprint("Oberflaechen fertig")
        if baustelle.phase == 3:
            if (
                baustelle.mass - 8 >= baustelle.maschinen["Asphaltierer"].mass
                and baustelle.phase < 4
            ):
                baustelle.phase = 4
                vprint("Start Phase 4")
        if baustelle.phase == 4:
            if baustelle.maschinen["Walze"].mass == 0:
                baustelle.maschinen["Walze"].fertig = True
                baustelle.phase = 5
                vprint("Walzen fertig")
                break
        vprint("Phase: ", baustelle.phase)
        zeitAbschnitt = {"Zeit": currentTime, "laster": []}
        
        for maschine in baustelle.maschinen:
            vprint(baustelle.maschinen[maschine])
            zeitAbschnitt[maschine] = baustelle.maschinen[maschine].__dict__
        vprint("Laster:")
        for laster in lasterListe:
            zeitAbschnitt["laster"].append(laster.__dict__)
            vprint(laster)
        if VERBOSE_CHANGES:
            snapshot = get_snapshot(baustelle, lasterListe)
            if snapshot != prev_snapshot:
                print(snapshot)
                print()
                print("-" * 40)  # separator for clarity
                prev_snapshot = snapshot
        saveDatei["schritte"].append(zeitAbschnitt)
        currentTime += timeStep
        # time.sleep(0.005)

    vprint("Phase: ", baustelle.phase)
    for maschine in baustelle.maschinen:
        vprint(baustelle.maschinen[maschine])
    vprint("Laster:")
    for i, laster in enumerate(lasterListe):
        vprint(laster)
    return saveDatei


ergebnis = simulate(5)

open("ergebnisSim.json", "w").write(json.dumps(ergebnis, indent=4))
# sommmer: 15 bis 25 min
# 40 -50
# maybe fixe zohl lkws und wiaviele baustellen konn i mochen
# 5m/min
# dicke schicht
# 25 euro/m2
print(calculateFullTime(1, 500))

