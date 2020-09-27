

class Settings:
    def __init__(self,filtered):
        self.adv = False
        self.filtered = filtered

    def advanced(self,char=1,spaceFight=True,noSpace=False,percent=None,charMin=False):
        self.adv = True
        self.percent = percent
        self.char = char
        self.spaceFight = spaceFight
        self.noSpace = noSpace
        self.charMin = charMin
        return self


class Result:
    def __init__(self,found,settings=None,filterMatch=None,end=None,start=None,flaggedStr=None):
        self.found = found
        self.settings = settings
        self.end = end
        self.start = start
        self.filterMatch = filterMatch
        self.flaggedStr = flaggedStr



def strToList(string):
    strList = []
    for x in string:
        strList.append(x)
    return strList


def stringCheck(check,string,incMax):
    partial = ''
    consec = 0
    incorrect = 0
    stringInd = -1
    realInd = -1
    startInd = 0
    errC = 0
    found = False
    cLen = len(check)
    check = check.lower()
    string = string.lower()
    for x in string:
        try:
            realInd += 1
            stringInd += 1
            if consec >= cLen-1-incMax+incorrect:
                partial = f'{partial}{x}'
                found = Result(True,None,check,realInd,startInd,partial)
                break
            if string[stringInd] == check[consec]:
                partial = f'{partial}{x}'
                consec += 1
                if consec == 1:
                    startInd = realInd
            else:
                if consec == 0:
                    if string[stringInd+1:stringInd+3] == check[1:3]:
                        partial = f'{partial}{x}'
                        consec += 1
                        incorrect += 1
                        startInd = realInd
                    continue
                else:
                    incorrect += 1
                    consec += 1
                    partial = f'{partial}{x}'
                    if incMax < incorrect:
                        incorrect = 0
                        consec = 0
                        cLen = len(check)
                        partial = ''
                    if check[consec] == string[stringInd]:
                        stringInd -= 1
                        cLen -= 1
                        continue
                    elif len(check)-1 >= consec+1:
                        if check[consec+1] == string[stringInd]:
                            stringInd -= 1
                            cLen -= 1
                            continue
                    if check[consec-1] == string[stringInd+1]:
                        stringInd += 1
                        consec -= 1
                        cLen += 1
                        continue
        except:
            errC += 1
            if errC > 10:
                break
            stringInd -= 2
            consec -=2
    return found




def checkText(string,settings):
    if str(type(settings)) == "<class 'list'>":
        settings = Settings(settings)
    elif str(type(settings)) == "<class 'str'>":
        settings = Settings([settings])
    if settings.adv:
        while '  ' in string and settings.spaceFight:
            string = string.replace("  "," ")
        while ' ' in string and settings.noSpace:
            string = string.replace(" ","")
    for x in settings.filtered:
        if settings.adv:
            if settings.percent != None:
                incMax = settings.percent * len(x)
                if incMax > 0 and incMax < 1:
                    incMax = 1
                else:
                    incMax = int(incMax)
                if settings.charMin and incMax < settings.char:
                    incMax = settings.char
            else:
                incMax = settings.char
        else:
            incMax = 0
        found = stringCheck(x,string,incMax)
        if found != False:
            found.settings = settings
            return found
    return Result(False)








