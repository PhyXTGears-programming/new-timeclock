import datetime
import os

import backend.processOptions as opts
import rapidjson
from rapidjson import DM_ISO8601

tempUserArray = {}


def load():
    os.chdir(os.path.dirname(__file__))
    global nameList
    nameList = []
    for filename in os.listdir("../times/"):
        if filename.endswith(".json"):
            name = os.path.splitext(filename)[0]
            nameList.append(name.replace("_", " "))


def getUserPath(user):
    return "../times/" + user + ".json"


def getJobs(user):
    os.chdir(os.path.dirname(__file__))
    user = user.replace(" ", "_")
    line = ""
    with open(getUserPath(user)) as userFile:
        line = userFile.readline()

    try:
        return rapidjson.loads(line)["teams"]
    except:
        return []


def signIO(user, io):
    os.chdir(os.path.dirname(__file__))
    user = user.replace(" ", "_")
    # {"type":"IO", "time": "yyyy-mm-ddThh:mm:ss"}
    signData = {"type": io, "time": datetime.datetime.now()}
    signDataJson = rapidjson.dumps(signData, datetime_mode=DM_ISO8601)
    with open(getUserPath(user), 'a') as userFile:
        userFile.write(signDataJson)
        userFile.write("\n")


def getHours(user):
    os.chdir(os.path.dirname(__file__))
    user = user.replace(" ", "_")
    lines = []
    with open(getUserPath(user)) as userFile:
        lines = userFile.readlines()[1:]

    return processHours([rapidjson.loads(line, datetime_mode=DM_ISO8601) for line in lines])


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
        else:
            print("processHours type error:", io["type"])
    if opts.timeclockOpts["addHoursBeforeSignout"] and lastState == "i":
        totalTime += datetime.datetime.now() - lastTime
    hours = totalTime.total_seconds() / 60.0**2
    return hours


def getCurrentIO(user):
    os.chdir(os.path.dirname(__file__))
    user = user.replace(" ", "_")
    io = "o"
    with open(getUserPath(user)) as userFile:
        lines = userFile.readlines()
        if len(lines) > 1:
            io = rapidjson.loads(lines[-1])["type"]
    return io
