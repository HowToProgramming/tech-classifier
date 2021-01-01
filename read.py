import os
import numpy as np
from osufileparse.osuparse import parse_beatmap
from osufileparse.osuparse import HitObject

# training data count
not_tech = os.listdir("./not_tech")
tech = os.listdir("./tech")
print((len(not_tech) + len(tech)) * 10, "Traning Data")
print(len(not_tech) * 10, "Not Technical Training Data")
print(len(tech) * 10, "Technical Training Data")

validation = os.listdir("./validation")

def read_data():
    not_tech_hit = []
    for nt in not_tech:
        a = parse_beatmap("./not_tech/" + nt)
        for i in np.arange(0.5, 1.6, 0.1):
            b = a * i
            b = b.HitObjects
            not_tech_hit.append(b)
    tech_hit = []
    for t in tech:
        a = parse_beatmap("./tech/" + t)
        for i in np.arange(0.5, 1.6, 0.1):
            b = a * i
            b = b.HitObjects
            tech_hit.append(b)
    return not_tech_hit, tech_hit

def read_metadata(val=False):
    if not val:
        not_tech_hit = []
        for nt in not_tech:
            meta = parse_beatmap("./not_tech/" + nt).metadata
            for i in np.arange(0.5, 1.6, 0.1):
                not_tech_hit += [meta['Artist'] + " - " + meta['Title'] + " [" + meta['Version'] + " (x {})]".format(i)]
        tech_hit = []
        for t in tech:
            meta = parse_beatmap("./tech/" + t).metadata
            for i in np.arange(0.5, 1.6, 0.1):
                not_tech_hit += [meta['Artist'] + " - " + meta['Title'] + " [" + meta['Version'] + " (x {})]".format(i)]
        return not_tech_hit, tech_hit
    valid = []
    for v in validation:
        meta = parse_beatmap("./validation/" + v).metadata
        valid.append(meta['Artist'] + " - " + meta['Title'] + " [" + str(meta['Version']) + "]")
    return valid