import rapidjson
import datetime
import os

oldPath = "../oldData/"

def portUser(information):
    oldFilename = userInfo[0].strip().replace(" ", "")
    newFilename = userInfo[0].strip().lower().replace(" ", "_")

    with open("times/" + newFilename + ".json", "w") as newFile:
        if os.path.exists(oldPath + "times/" + oldFilename + ".txt"):
            data = {}
            data["teams"] = [i.strip() for i in information[3].split(",")]
            # if information[3].strip() == "none":
            #     data["teams"] = ["Other"]
            data["role"] = information[2].strip()
            newFile.write(rapidjson.dumps(data) + "\n")

            with open(oldPath + "times/" + oldFilename + ".txt") as oldFile:
                for line in oldFile:
                    signIOData = line.split("|")
                    io = signIOData[0].strip()
                    if io == "@":
                        io = "o"
                    elif io == "!":
                        io = "i"

                    ioTime = datetime.datetime.strptime(signIOData[1].strip(), "%H:%M:%S %d.%m.%Y")

                    signData = {"type": io, "time": ioTime}
                    signDataJson = rapidjson.dumps(signData, datetime_mode=rapidjson.DM_ISO8601)
                    newFile.write(signDataJson)
                    newFile.write("\n")


if __name__ == "__main__":
    with open(oldPath + "usernameFile.txt") as usernameFile:
        for line in usernameFile:
            userInfo = line.split("|")
            portUser(userInfo)
            



            
