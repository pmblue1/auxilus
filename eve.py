import os
import json
import requests

if not os.path.isdir('./eveR'):
    print("eve.py - 'eveR' resource directory not found, creating...")
    os.mkdir("eveR")
    open('./eveR/__init__.py', 'w+').write('')
    print("eve.py - 'eveR' resource directory created successfully!")
try:
    from eveR import sqliteObj
except:
    print("eve.py - sqliteObj module not found, downloading...")
    url = 'https://auxilus.ml/resources/sqliteObj_module'
    r = requests.get(url, allow_redirects=True)

    open('./eveR/sqliteObj.py', 'wb').write(r.content)
    open('./eveR/__init__.py', 'w+').write('')
    print("eve.py - sqliteObj module downloaded!")
    from eveR import sqliteObj
    
if not os.path.isfile('./eveR/planets.sqlite3'):
    print("eve.py - Database not found, downloading...")
    url = 'https://auxilus.ml/resources/echoes_database'
    r = requests.get(url, allow_redirects=True)

    open('./eveR/planets.sqlite3', 'wb').write(r.content)
    print("eve.py - Database downloaded!")
db = sqliteObj.sqliteObj("./eveR/planets.sqlite3","planets")

loadedSystems = {}
loadedPlanets = {}

class PartResource:
    def __init__(self,res,rich,out):
        self.name = res
        self.richness = rich
        self.output = out

    def __contains__(self,check):
        try:
            if check.name == self.name:
                return True
        except:
            if check == self.name:
                return True
        return False
    def full(self):
        self = Resource(self.name,self.richness,self.output)
        return self
    
class Planet:
    def __init__(self,id=None,dict=None,loadedPlanets=loadedPlanets):
        found = False
        if dict == None:
            if str(id) in loadedPlanets:
                planets = loadedPlanets[str(id)][0]
                resources = loadedPlanets[str(id)][1]
                found = True
            else:
                planets = db.select({"id": id},table="planets")
        else:
            planets = dict
        self.none = False
        if planets == []:
            self.none = True
        if not self.none:
            planet = planets[0]
            self.dict = planets
            self.id = planet["id"]
            self.region = planet["Region"]
            self.constellation = planet["Constellation"]
            self.name = planet["Planet Name"]
            self.type = planet["Planet Type"]
            self.system_name = planet["System"]
            if not found:
                resources = []
                for planetA in planets:
                    resources.append(PartResource(planetA["Resource"],planetA["Richness"],planetA["Output"]))
            self.resources = resources
            loadedPlanets[str(planet["id"])] = [planets,resources]
    def get_resource(self,resource):
        for x in self.resources:
            if x.name.lower() == resource.lower():
                return x
        return None
    def system(self):
        return System(dict=db.select({"Name": self.system_name},table="systems")[0])

class AllPlanets:
    def __init__(self,loadedPlanets=loadedPlanets):
        self.name = "All Planets"
        planets = db.select_all(table="planets")
        pltList = []
        newP = []
        currP = planets[0]["Planet Name"]
        for x in planets:
            if x["Planet Name"] == currP:
                newP.append(x)
            else:
                p = Planet(dict=newP)
                if not p.none:
                    pltList.append(p)
                    loadedPlanets[str(p.id)] = [newP,p.resources]
                    newP = [x]
                    currP = x["Planet Name"]
        self.planets = pltList
    def resource_find(self,resources):
        planets = self.planets()
        def res_check(planet,resource,richness):
            for x in planet.resources:
                if x.name.lower().replace(" ","") == resource.lower().replace(" ",""):
                    if x.richness.lower() == richness.lower():
                        return True
            return False
        foundList = []
        for x in planets:
            found = True
            for y in resources:
                if res_check(x,y,resources[y]):
                    found = True
                else:
                    found = False
                    break
            if found:
                foundList.append(x)
        return foundList

    def resource_find_output(self,resources):
        planets = self.planets
        def res_check_output(planet,resource,output):
            for x in planet.resources:
                if x.name.lower().replace(" ","") == resource.lower().replace(" ",""):
                    if x.output >= output:
                        return True
            return False
        foundList = []
        for x in planets:
            found = True
            for y in resources:
                if res_check_output(x,y,resources[y]):
                    found = True
                else:
                    found = False
                    break
            if found:
                foundList.append(x)
        return foundList        


def get_planet(id):
    p = Planet(int(id))
    if p.none:
        return None
    else:
        return p

class System:
    def __init__(self,id=None,dict=None,loadedSystems=loadedSystems):
        if dict == None:
            if str(id) in loadedSystems:
                system = [loadedSystems[str(id)]]
            else:
                system = db.select({"id": id},table="systems")
        else:
            system = [dict]
        self.none = False
        if system == []:
            self.none = True
            return
        system = system[0]
        self.dict = system
        self.id = system["id"]
        self.name = system["Name"]
        self.region = system["Region"]
        self.constellation = system["Constellation"]
        self.neighbors_id = system["Neighbors"].split(":")
        self.security = system["Security"]
        self.planets_id = system["Planets"].split(":")
        loadedSystems[str(system["id"])] = system

    def neighbors(self):
        if self.neighbors_id == ['']:
            return []
        neighbors = []
        for x in self.neighbors_id:
            neighbors.append(System(int(x)))
        self.neighbors_l = neighbors
        return neighbors

    def planets(self):
        planets = []
        for x in self.planets_id:
            p = get_planet(int(x))
            if p != None:
                planets.append(p)
        self.planets = planets
        return planets

    def __eq__(self,other):
        if other == None:
            return False
        if self.name == other.name:
            return True
        return False
    
def all_systems():
    systems = db.select_all(table="systems")
    sysList = []
    for x in systems:
        sysList.append(System(dict=x))
    return sysList

try:
    rNeighbors = json.load(open('./eveR/regions.json'))
    cNeighbors = json.load(open('./eveR/constellations.json'))
    resDict = json.load(open('./eveR/resources.json'))
except:
    print("eve.py - Failure loading json files. Creating...")
    regions = {}
    constellations = {}
    resDict = {"planet_count": 0, "resource_count": 0}
    systems = all_systems()
    sysLen = len(systems)
    sysProg = 0
    sysCheck = 0
    AllPlanets()
    print(len(loadedPlanets))
    for x in systems:
        sysProg += 1
        for y in x.planets():
            resDict["planet_count"] += 1
            try:
                for z in y.resources:
                    resDict["resource_count"] += 1
                    if z.name in resDict:
                        resDict[z.name]["amt"] += 1
                        resDict[z.name]["output"] += z.output
                        resDict[z.name]["dev"].append(z.output)
                    else:
                        resDict[z.name] = {"amt": 1, "output": z.output, "dev": [z.output]}
            except:
                print(y.__dict__)
                raise Exception()
        for y in x.neighbors():
            if x.region != y.region:
                if y.region not in regions:
                    regions[y.region] = []
                if x.region not in regions:
                    regions[x.region] = []
                if x.region not in regions[y.region]:
                    regions[y.region].append(x.region)
                    regions[x.region].append(y.region)
            if x.constellation != y.constellation:
                if y.constellation not in constellations:
                    constellations[y.constellation] = []
                if x.constellation not in constellations:
                    constellations[x.constellation] = []
                if x.constellation not in constellations[y.constellation]:
                    constellations[y.constellation].append(x.constellation)
                    constellations[x.constellation].append(y.constellation)
        if sysCheck < sysProg:
            sysCheck += 100
            print(f'{sysProg}/{sysLen}')
    for x in resDict:
        if x in ["planet_count","resource_count"]:
            continue
        resDict[x]["output"] = round(resDict[x]["output"]/resDict[x]["amt"],3)
        newDev = 0
        for y in resDict[x]["dev"]:
            a = resDict[x]["output"]-y
            if a < 0:
                a = a * -1
            newDev += a
        resDict[x]["dev"] = newDev/resDict[x]["amt"]
    for x in resDict:
        if x in ["planet_count","resource_count"]:
            continue
        alias = ''
        a = x.split(" ")
        for y in a:
            alias = f'{alias}{y[0]}'
        resDict[x]["alias"] = alias
    for x in resDict:
        if x in ["planet_count","resource_count"]:
            continue
        for y in resDict:
            if y in ["planet_count","resource_count"]:
                continue
            if x == y:
                continue
            if resDict[x]["alias"] == resDict[y]["alias"]:
                resDict[x]["alias"] = x[:-1]
    json.dump(regions,open('./eveR/regions.json','w+'),indent=2)
    json.dump(constellations,open('./eveR/constellations.json','w+'),indent=2)
    json.dump(resDict,open('./eveR/resources.json','w+'),indent=2)
    print("eve.py - Json files created, data loaded!")
    rNeighbors = regions
    cNeighbors = constellations
    

def get_system(id):
    return System(int(id))
def find_region(name,rNeighbors=rNeighbors):
    def simplify(string):
        return string.lower().replace("-","").replace(" ","")
    for x in rNeighbors:
        if simplify(x) == simplify(name):
            return Region(x)
    return None
def find_resource(name,resDict=resDict):
    def simplify(string):
        return string.lower().replace("-","").replace(" ","")
    for x in resDict:
        if x in ["planet_count","resource_count"]:
            continue
        if simplify(x) == simplify(name):
            return x
    for x in resDict:
        if x in ["planet_count","resource_count"]:
            continue
        if resDict[x]["alias"].lower() == name.lower():
            return x    
    return None
def find_system(name):
    systems = all_systems()
    def simplify(string):
        return string.lower().replace("-","").replace(" ","")
    for x in systems:
        if simplify(x.name) == simplify(name):
            return x
    return None
def find_constellation(name,cNeighbors=cNeighbors):
    def simplify(string):
        return string.lower().replace("-","").replace(" ","")
    for x in cNeighbors:
        if simplify(x) == simplify(name):
            return Constellation(x)
    return None
def res_in_p(planet,resource):
    for x in planet.resources:
        if resource in x:
            return True
    return False
def ext_res(planet,resource):
    for x in planet.resources:
        if resource in x:
            return x
    return None
def score_sort(planets,resources):
    if planets == []:
        return []
    if len(planets) == 1:
        return planets
    totals = {}
    scores = {}
    for x in resources:
        totals[x] = {}
        totals[x]["total"] = 0
        totals[x]["dev"] = 0
        for y in planets:
            totals[x]["total"] += ext_res(y,x).output
        totals[x]["mean"] = (totals[x]["total"]/len(planets))
        for y in planets:
            a = totals[x]["mean"] - ext_res(y,x).output
            if a < 0:
                a = a * -1
            totals[x]["dev"] += a
        totals[x]["dev"] = totals[x]["dev"]/len(planets)
    for x in planets:
        scores[x.name] = 0
        for y in resources:
            scores[x.name] += (ext_res(x,y).output-totals[y]["mean"])/totals[y]["dev"]
        
    def sort_planets(planet,scores=scores):
        return scores[planet.name]
    planets.sort(key=sort_planets,reverse=True)
    return planets
def index_numb(list,item):
    a = 0
    for x in list:
        a += 1
        if x == item:
            return a
    return None
def jump_dist(system,dest):
    def toNames(a):
        names = []
        for x in a:
            names.append(x.name)
        return names
    if system.constellation == dest.constellation:
        allowedCon = [dest.constellation]
        allowedReg = None
    else:
        if system.region == dest.region:
            allowedReg = [dest.region]
            allowedCon = None
        else:
            allowedReg = None
        
            

            done = False
            paths = []
            const = PartConstellation(system.constellation)
            for x in const.neighbors():
                paths.append([x])
            for x in range(6):
                newPaths = []
                for y in paths:
                    dPath = y
                    for z in y[-1].neighbors():
                        if z not in y:
                            new = y + [z]
                            if new[-1].name == dest.constellation:
                                done = True
                                allowedCon = toNames(new + [const])
                                allowedReg = None
                                break
                            newPaths.append(new)
                    if done:
                        break
                    paths = newPaths
                if done:
                    break
            if not done:
                allowedCon = None
                paths = []
                const = PartRegion(system.region)
                for x in const.neighbors():
                    paths.append([x])
                for x in range(5):
                    newPaths = []
                    for y in paths:
                        dPath = y
                        for z in y[-1].neighbors():
                            if z not in y:
                                new = y + [z]
                                if new[-1].name == dest.region:
                                    if done == False:
                                        allowedCon = None
                                        allowedReg = new + [const]
                                        done = "f"
                                    else:
                                        new_items = []
                                        for add_item in new:
                                            if (add_item.name in toNames(allowedReg)) == False:
                                                new_items.append(add_item)
                                        allowedReg = allowedReg + new_items
                                        done = True
                                    break
                                newPaths.append(new)
                        if done == True:
                            break
                        paths = newPaths
                    if done == True:
                        break
                if done != False:
                    allowedReg = toNames(allowedReg)
                    
    paths = []
    for x in system.neighbors():
        paths.append([x])
    for x in range(15):
        newPaths = []
        for y in paths:
            dPath = y
            for z in y[-1].neighbors():
                if z not in y:
                    if (allowedCon == None or z.constellation in allowedCon) and (allowedReg == None or z.region in allowedReg):
                        if allowedReg != None:
                            try:
                                if index_numb(allowedReg,y[-1].region) > index_numb(allowedReg,z.region):
                                    continue
                            except:
                                None
                        new = y + [z]
                        if new[-1] == dest:
                            return new
                        if x >= 100:
                            new.pop(0)
                        newPaths.append(new)
        paths = newPaths
    return None

loadedRegions = {}
loadedConst = {}
class Resource:
    def __init__(self,res,rich,out,resDict=resDict):
        self.name = res
        self.richness = rich
        self.output = out
        self.output_avg = resDict[res]["output"]

    def __contains__(self,check):
        try:
            if check.name == self.name:
                return True
        except:
            if check == self.name:
                return True
        return False
        

    
class PartRegion:
    def __init__(self,name,loadedRegions=loadedRegions):
        if name in loadedRegions:
            systems = loadedRegions[name]
        else:
            systems = db.select({"Region": name},table="systems")
        self.none = False
        if systems == []:
            self.none = True
            return
        self.name = name
        loadedRegions[name] = systems

    def neighbors(self,rNeighbors=rNeighbors):
        rNeighbors = rNeighbors[self.name]
        if rNeighbors == []:
            return []
        neighbors = []
        for x in rNeighbors:
            neighbors.append(PartRegion(x))
        return neighbors
    
class Region:
    def __init__(self,name,loadedRegions=loadedRegions):
        if name in loadedRegions:
            systems = loadedRegions[name]
        else:
            systems = db.select({"Region": name},table="systems")
        self.none = False
        if systems == []:
            self.none = True
            return
        self.name = name
        sysList = []
        for x in systems:
            sysList.append(System(dict=x))
        self.systems = sysList
        self.planets_l = None
        const = []
        for x in sysList:
            newC = Constellation(x.constellation)
            if newC != const:
                const.append(newC)
        self.constellations = const
        loadedRegions[name] = systems

    def planets(self):
        planets = db.select({"Region": self.name},table="planets")
        self.none = False
        if planets == []:
            self.none = True
            return
        pltList = []
        newP = []
        currP = planets[0]["Planet Name"]
        for x in planets:
            if x["Planet Name"] == currP:
                newP.append(x)
            else:
                pltList.append(Planet(dict=newP))
                newP = [x]
                currP = x["Planet Name"]
        self.planets_l = pltList
        return pltList

    def neighbors(self,rNeighbors=rNeighbors):
        rNeighbors = rNeighbors[self.name]
        if rNeighbors == []:
            return []
        neighbors = []
        for x in rNeighbors:
            neighbors.append(Region(x))
        return neighbors
    
    def resource_find(self,resources):
        if self.planets_l == None:
            planets = self.planets()
        else:
            planets = self.planets_l
        def res_check(planet,resource,richness):
            for x in planet.resources:
                if x.name.lower().replace(" ","") == resource.lower().replace(" ",""):
                    if x.richness.lower() == richness.lower():
                        return True
            return False
        foundList = []
        for x in planets:
            found = True
            for y in resources:
                if res_check(x,y,resources[y]):
                    found = True
                else:
                    found = False
                    break
            if found:
                foundList.append(x)
        return foundList

    def resource_find_output(self,resources):
        if self.planets_l == None:
            planets = self.planets()
        else:
            planets = self.planets_l
        def res_check_output(planet,resource,output):
            for x in planet.resources:
                if x.name.lower().replace(" ","") == resource.lower().replace(" ",""):
                    if x.output >= output:
                        return True
            return False
        foundList = []
        for x in planets:
            found = True
            for y in resources:
                if res_check_output(x,y,resources[y]):
                    found = True
                else:
                    found = False
                    break
            if found:
                foundList.append(x)
        return foundList
def all_regions(rNeighbors=rNeighbors):
    regList = []
    for x in rNeighbors:
        regList.append(Region(x))
    return regList

class PartConstellation:
    def __init__(self,name,loadedConst=loadedConst):
        if name in loadedConst:
            systems = loadedConst[name]
        else:
            systems = db.select({"Constellation": name},table="systems")
        self.none = False
        if systems == []:
            self.none = True
            return
        self.name = name
        loadedConst[name] = systems

    def neighbors(self,cNeighbors=cNeighbors):
        cNeighbors = cNeighbors[self.name]
        if cNeighbors == []:
            return []
        neighbors = []
        for x in cNeighbors:
            neighbors.append(PartConstellation(x))
        return neighbors

class Constellation:
    def __init__(self,name,loadedConst=loadedConst):
        if name in loadedConst:
            systems = loadedConst[name]
        else:
            systems = db.select({"Constellation": name},table="systems")
        self.none = False
        if systems == []:
            self.none = True
            return
        self.name = name
        sysList = []
        for x in systems:
            sysList.append(System(dict=x))
        self.systems = sysList
        self.planets_l = None
        loadedConst[name] = systems

    def planets(self):
        planets = db.select({"Constellation": self.name},table="planets")
        self.none = False
        if planets == []:
            self.none = True
            return
        pltList = []
        newP = []
        currP = planets[0]["Planet Name"]
        for x in planets:
            if x["Planet Name"] == currP:
                newP.append(x)
            else:
                pltList.append(Planet(dict=newP))
                newP = [x]
                currP = x["Planet Name"]
        self.planets_l = pltList
        return pltList

    def neighbors(self,cNeighbors=cNeighbors):
        cNeighbors = cNeighbors[self.name]
        if cNeighbors == []:
            return []
        neighbors = []
        for x in cNeighbors:
            neighbors.append(Constellation(x))
        return neighbors
    
    def resource_find(self,resources):
        if self.planets_l == None:
            planets = self.planets()
        else:
            planets = self.planets_l
        def res_check(planet,resource,richness):
            for x in planet.resources:
                if x.name.lower().replace(" ","") == resource.lower().replace(" ",""):
                    if x.richness.lower() == richness.lower():
                        return True
            return False
        foundList = []
        for x in planets:
            found = True
            for y in resources:
                if res_check(x,y,resources[y]):
                    found = True
                else:
                    found = False
                    break
            if found:
                foundList.append(x)
        return foundList

    def resource_find_output(self,resources):
        if self.planets_l == None:
            planets = self.planets()
        else:
            planets = self.planets_l
        def res_check_output(planet,resource,output):
            for x in planet.resources:
                if x.name.lower().replace(" ","") == resource.lower().replace(" ",""):
                    if x.output >= output:
                        return True
            return False
        foundList = []
        for x in planets:
            found = True
            for y in resources:
                if res_check_output(x,y,resources[y]):
                    found = True
                else:
                    found = False
                    break
            if found:
                foundList.append(x)
        return foundList
