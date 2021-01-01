from osuparse import osufile

class editableosufile(osufile):
    def __init__(self, data):
        super().__init__(data)
        self.start = self.HitObjects[0].offset
        self.end = self.HitObjects[-1].offset
    
    def scroll(self, offset):
        t = self
        t.start += offset
        t.end += offset
        for i in range(len(t.TimingPoints)):
            t.TimingPoints[i].offset += offset
        for k in range(len(t.HitObjects)):
            t.HitObjects[k].offset += offset
            if t.HitObjects[k].release > 0:
                t.HitObjects[k].release += offset
        return t

    def __add__(self, elem):
        if isinstance(elem, float) or isinstance(elem, int):
            return self.scroll(elem)
        if isinstance(elem, osufile):
            t = self
            t.TimingPoints += elem.TimingPoints
            t.HitObjects += elem.HitObjects
            return t
        if isinstance(elem, editableosufile):
            t = self
            t += -t.start
            t += elem.end
            t.TimingPoints += elem.TimingPoints
            t.HitObjects += elem.HitObjects
            return t
        else:
            raise TypeError("Invalid Operation between editableosufile and {}".format(type(elem)))
    
    def __repr__(self):
        initializestring = "osu file format v14\n\n"
        initializestring += "[General]\n"
        for key, value in zip(self.General.keys(), self.General.values()):
            initializestring += "{}:{}\n".format(key, value)
        initializestring += "\n"
        initializestring += "[Editor]\n"
        for key, value in zip(self.editor.keys(), self.editor.values()):
            initializestring += "{}:".format(key)
            if key == "Bookmarks":
                initializestring += str(self.editor[key])[1:len(str(self.editor[key])) - 1]
                initializestring += "\n"
                continue
            initializestring += "{}\n".format(value)
        initializestring += "\n"
        initializestring += "[Metadata]\n"
        for key, value in zip(self.metadata.keys(), self.metadata.values()):
            initializestring += "{}:".format(key)
            if key == "Tags":
                initializestring += " ".join(self.metadata[key])
                initializestring += "\n"
                continue
            initializestring += "{}\n".format(value)
        initializestring += "\n[Difficulty]\n"
        for key, value in zip(self.difficulty.keys(), self.difficulty.values()):
            initializestring += "{}:{}\n".format(key, value)
        initializestring += '\n[Events]\n//Background and Video events\n0,0,"blank.jpg",0,0\n//Break Periods\n//Storyboard Layer 0 (Background)\n//Storyboard Layer 1 (Fail)\n//Storyboard Layer 2 (Pass)\n//Storyboard Layer 3 (Foreground)\n//Storyboard Sound Samples\n'
        initializestring += "\n[TimingPoints]\n"
        for tp in self.TimingPoints:
            initializestring += tp.encode() + "\n"
        initializestring += "\n"
        initializestring += "[HitObjects]\n"
        for hit in self.HitObjects:
            initializestring += hit.encode() + "\n"
        initializestring += "\n"
        return initializestring
    
    def to_osu(self, filename):
        with open(filename, 'w+') as f:
            f.write(self.__repr__())
    
    def delete_overlap(self):
        new_hit = []
        lasthitobj = None
        for i in range(len(self.HitObjects)):
            if lasthitobj and self.HitObjects[i].lane == lasthitobj.lane and self.HitObjects[i].offset == lasthitobj.offset:
                lasthitobj = self.HitObjects[i]
                continue
            lasthitobj = self.HitObjects[i]
            new_hit.append(lasthitobj)
        self.HitObjects = new_hit.copy()
            
def parse_beatmap(filedir):
    with open(filedir, "r") as f:
        data = f.read()
        return editableosufile(data)

beatmap = parse_beatmap("ZUTOMAYO_-_Kan_Saete_Kuyashiiwa_HowToPlayLN_Jealousy_Hard.osu")
beatmap.delete_overlap()
beatmap.to_osu('fix.osu')