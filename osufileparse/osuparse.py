import os
import numpy as np

class HitObject:
    def __init__(self, code):
        data = code.split(",")
        self.lane = int(data[0])
        self.samplesound = int(data[1])
        try:
            self.offset = int(data[2])
        except:
            self.offset = data[2]
        self.type = int(data[3])
        self.hitsound = int(data[4])
        self.release = -1
        if self.type == 128:
            try:
                self.release = int(data[-1].split(":")[0])
            except:
                self.release = data[-1].split(":")[0]
        
    def encode(self):
        a = "0:0:0:0:"
        if self.type == 128:
            a = str(self.release) + ":" + a
        return "{},{},{},{},{},{}".format(self.lane, self.samplesound, self.offset, self.type, self.hitsound, a)

class TimingPoint:
    def __init__(self, code):
        data = code.split(",")
        self.offset = float(data[0])
        self.isBPM = int(data[-2])
        if self.isBPM == 1:
            self.velocity = 60000 / float(data[1])
        else:
            self.velocity = -100 / float(data[1])
        self.timeSignature = int(data[2])
        self.hitsoundvolume = int(data[5])
        self.isKiai = int(data[-1])
    
    def switch(self, mainbpm):
        if self.isBPM == 1:
            self.velocity = self.velocity / mainbpm
            self.isBPM = 0
        else:
            self.velocity = mainbpm * self.velocity
            self.isBPM = 1
    
    def encode(self):
        vel = 60000 / self.velocity if self.isBPM == 1 else -100 / self.velocity
        return "{},{},{},1,0,{},{},{}".format(self.offset, vel, self.timeSignature, self.hitsoundvolume, self.isBPM, self.isKiai)

class osufile:
    def __init__(self, data: str):
        self.data = data.split("\n")
        self.General = None
        self.editor = None
        self.metadata = None
        self.difficulty = None
        self.TimingPoints = list()
        self.HitObjects = list()
        self.initialize_data()
        
    def initialize_data(self):
        self.parseGeneral()
        self.parseEditor()
        self.parseMetadata()
        self.parseDifficulty()
        self.parseTimingPoints()
        self.parseHitObjects()
    
    def parseGroup(self, keyword):
        start = self.data.index("[{}]".format(keyword)) + 1
        end = self.data[start:].index("") + start
        group = dict()
        for data in self.data[start:end]:
            d = data.split(":")
            try:
                group[d[0]] = int(d[1])
            except:
                try:
                    group[d[0]] = float(d[1])
                except:
                    group[d[0]] = d[1]
        return group

    def parseGeneral(self):
        self.General = self.parseGroup("General")
    
    def parseEditor(self):
        self.editor = self.parseGroup("Editor")
        if "Bookmarks" in self.editor.keys():
            if isinstance(self.editor['Bookmarks'], int):
                self.editor["Bookmarks"] = int(self.editor["Bookmarks"])
            else:
                self.editor["Bookmarks"] = [int(k) for k in self.editor["Bookmarks"].split(",")]
    
    def parseMetadata(self):
        self.metadata = self.parseGroup("Metadata")
        self.metadata["Tags"] = self.metadata["Tags"].split(" ")
    
    def parseDifficulty(self):
        self.difficulty = self.parseGroup("Difficulty")
    
    def parseTimingPoints(self):
        start = self.data.index("[TimingPoints]") + 1
        end = self.data[start:].index("") + start
        for data in self.data[start:end]:
            self.TimingPoints.append(TimingPoint(data))
    
    def parseHitObjects(self):
        start = self.data.index("[HitObjects]") + 1
        end = self.data[start:].index("") + start
        for data in self.data[start:end]:
            self.HitObjects.append(HitObject(data))
    
    def __mul__(self, rate):
        t = self
        t.metadata['Version'] += "x {}".format(rate)
        for i in range(len(t.TimingPoints)):
            t.TimingPoints[i].offset /= rate
            if t.TimingPoints[i].isBPM:
                t.TimingPoints[i].velocity /= rate
        for i in range(len(t.HitObjects)):
            t.HitObjects[i].offset /= rate
            if t.HitObjects[i].release != -1:
                t.HitObjects[i].release /= rate
        return t

def parse_beatmap(file):
    with open(file, "r") as f:
        data = f.read()
        return osufile(data)

