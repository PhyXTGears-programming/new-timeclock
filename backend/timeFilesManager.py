import datetime
import time
import os

import backend.processOptions as opts
import rapidjson

tempUserArray = {}

def load():
    os.chdir(os.path.dirname(__file__))

    if not os.path.exists("../times/"):
        os.mkdir("../times/")

    global nameList
    nameList = []
    for filename in os.listdir("../times/"):
        if filename.endswith(".json"):
            name = os.path.splitext(filename)[0]
            nameList.append(name.replace("_", " ").title())


def getUserPath(user):
    return "../times/" + user + ".json"


def getJobs(user):
    os.chdir(os.path.dirname(__file__))
    user = user.replace(" ", "_").lower()
    line = ""
    with open(getUserPath(user)) as userFile:
        line = userFile.readline()

    try:
        return rapidjson.loads(line)["teams"]
    except:
        return []


def signIO(user, io, preupdate=True):
    if preupdate:
        getHours(user) # make sure auto-clockout check runs before logging sign in/out

    os.chdir(os.path.dirname(__file__))
    user = user.replace(" ", "_").lower()
    # {"type":"IO", "time": "yyyy-mm-ddThh:mm:ss"}
    signData = {"type": io, "time": datetime.datetime.now()}
    signDataJson = rapidjson.dumps(signData, datetime_mode=rapidjson.DM_ISO8601)

    addNewline = False
    with open(getUserPath(user), 'r') as userFile:
        lastLine = userFile.readlines()[-1]
        addNewline = lastLine[-1] != "\n"

    with open(getUserPath(user), 'a') as userFile:
        if addNewline:
            userFile.write("\n")
        userFile.write(signDataJson)
        userFile.write("\n")


def getHours(user):
    os.chdir(os.path.dirname(__file__))
    user = user.replace(" ", "_").lower()
    lines = []
    addAutoClockout = False
    with open(getUserPath(user)) as userFile:
        lines = userFile.readlines()[1:]
        
        # Auto-clockout (prevents users from getting time from forgetting to sign out)
        autoClockoutTime = time.strptime(opts.timeclockOpts["autoClockoutTime"], "%H:%M:%S")

        try:
            lastIO = rapidjson.loads(lines[-1], datetime_mode=DM_ISO8601)

            if lastIO["type"] == "i":
                if datetime.datetime.now() - lastIO["time"] > datetime.timedelta(hours=20): # if signed in for more than 20 hours
                    addAutoClockout = True
                elif lastIO["time"].date() == datetime.date.today(): # if signed in on current day
                    # check if auto-clockout time occurred after sign in but before now
                    if lastIO["time"].time() < autoClockoutTime and autoClockoutTime < datetime.datetime.now().time():
                        addAutoClockout = True
                elif lastIO["time"].date() < datetime.date.today(): # if signed in on previous day
                    # check that it is past auto-clockout time
                    if datetime.datetime.now().time() > autoClockoutTime:
                        addAutoClockout = True
        except:
            pass

    if addAutoClockout:
        signIO(user, "a", False)
        lines.append('{"type": "a", "time": "%s"}' % datetime.datetime.now())

    return processHours([rapidjson.loads(line, datetime_mode=rapidjson.DM_ISO8601) for line in lines])


def processHours(data):
    totalTime = datetime.timedelta()
    lastState = "o"
    lastTime = None
    for io in data:
        if io["type"] == "i":
            lastState = "i"
            lastTime = io["time"]
        elif io["type"] == "o":
            if lastState == "i":
                lastState = "o"
                totalTime += io["time"] - lastTime
        elif io["type"] == "a":
            lastState = "o"
            lastTime = io["time"]
        else:
            print("processHours type error:", io["type"])
    if opts.timeclockOpts["addHoursBeforeSignout"] and lastState == "i":
        totalTime += datetime.datetime.now() - lastTime
    hours = totalTime.total_seconds() / 60.0**2
    return hours


def getCurrentIO(user):
    os.chdir(os.path.dirname(__file__))
    user = user.replace(" ", "_").lower()
    io = "o"
    with open(getUserPath(user)) as userFile:
        lines = userFile.readlines()
        if len(lines) > 1:
            io = rapidjson.loads(lines[-1])["type"]
    return io
