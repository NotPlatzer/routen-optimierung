distances = {
    "Aw": {"distance": 16355.9, "duration": 1255.2},
    "wA": {"distance": 16355.9, "duration": 1255.2},
    "AB": {"distance": 19707.7, "duration": 1412.2},
    "BA": {"distance": 19707.7, "duration": 1412.2},
    "AC": {"distance": 19243.2, "duration": 1539.6},
    "CA": {"distance": 19243.2, "duration": 1539.6},
    "AD": {"distance": 31478.5, "duration": 2067.8},
    "DA": {"distance": 31478.5, "duration": 2067.8},
    "Bw": {"distance": 3477.3, "duration": 244.7},
    "wB": {"distance": 3477.3, "duration": 244.7},
    "BC": {"distance": 27909.8, "duration": 1728.8},
    "CB": {"distance": 27909.8, "duration": 1728.8},
    "BD": {"distance": 20966.5, "duration": 1394.3},
    "DB": {"distance": 20966.5, "duration": 1394.3},
    "Cw": {"distance": 24262.7, "duration": 1484.9},
    "wC": {"distance": 24262.7, "duration": 1484.9},
    "CD": {"distance": 45021.3, "duration": 2943.5},
    "DC": {"distance": 45021.3, "duration": 2943.5},
    "Dw": {"distance": 24451.6, "duration": 1645.5},
    "wD": {"distance": 24451.6, "duration": 1645.5},
}

kv = 55
kl = 40
# a*kv + c*kl + b*kv/a*kv + a*kl + b*kl + b*kv
newDist = {}
for k in distances.keys():
    if newDist.get(k) == None and newDist.get(k[::-1]) == None and "w" not in k:
        newDist[k] = distances[k]

effizienzen = {}

for k in newDist.keys():
    c = newDist[k]["distance"]
    a = distances[k[0] + "w"]["distance"]
    b = distances[k[1] + "w"]["distance"]
    effizienzSteigerung = a+c+b
    effizienzen[k] = effizienzSteigerung
    print(f"{k}: Effizienzsteigerung: {effizienzSteigerung:.2f}%")

bestPairing = []
bestScore = float('inf')

for k in effizienzen.keys():
    for j in effizienzen.keys():
        if (
            k != j
            and effizienzen[k] + effizienzen[j] < bestScore
            and k[0] not in j
            and k[1] not in j
        ):
            bestScore = effizienzen[k] + effizienzen[j]
            bestPairing = [k, j]
print(bestPairing, bestScore)
