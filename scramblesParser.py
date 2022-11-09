import math
import os
import datetime
import re
import glob


def parse(replaysPath, inputFile, outputFile):
    scramble_re = "\d+:\d+((:\d+)*)?-\d+:\d+((:\d+)*)?(-\d+:\d+((:\d+)*)?)*"
    lens = [0, 0, 0, 17, 37, 64, 97, 136, 181, 232, 289]
    info = []
    path = replaysPath
    for filename in glob.glob(os.path.join(path, '*.pr')):
        with open(os.path.join(os.getcwd(), filename), 'r', errors="ignore") as f:
            solve = {}
            size, time, unix = os.path.basename(f.name)[:-3].split('-')
            size = int(size.split("x")[0])
            time = str(int(time) / 1000)
            date = str(datetime.datetime.fromtimestamp(math.floor(int(unix) / 1000)))
            data = str(f.read())
            scramble = re.search(scramble_re, data)[0][0:lens[size]]
            solve["time"] = time
            solve["date"] = date
            solve["size"] = size
            solve["scramble"] = scramble.replace(":", " ").replace("-", "/")
            solve["unix"] = math.floor(int(unix) / 1000)
            info.append(solve)
    info = sorted(info, key=lambda d: d['date'])
    newinfo = []
    scramblesToCheck = []
    for i in info:
        scr = i["scramble"]
        if scr not in scramblesToCheck:
            scramblesToCheck.append(scr)
            newinfo.append(i)
    info = newinfo
    info = sorted(info, key=lambda d: d['size'])
    with open(inputFile, 'r') as input:
        lines = input.readlines()
    mysolves = []
    for line in lines:
        data = {}
        line = line.split("\t")
        line[7] = line[7].replace("\n", "")
        data["size"] = int(line[0].split("x")[0])
        data["time"] = line[3]
        data["observ"] = line[4]
        data["moves"] = line[5]
        data["tps"] = line[6]
        data["date"] = line[7]
        data["unix"] = datetime.datetime.strptime(data["date"], "%Y-%m-%d %H:%M:%S").timestamp()
        mysolves.append(data)
    for solve in mysolves:
        scramble = "Not found in replays"
        extra = "0"
        for i in info:
            if i["time"] == solve["time"] and i["size"] == solve["size"] and (abs(i["unix"] - solve["unix"])) < 30:
                dif = (i["unix"] - solve["unix"])
                scramble = i["scramble"]
                if dif != 0 and abs(dif) != 1:
                    extra = str(dif)
                else:
                    extra = "0"
                break
        solve["scramble"] = scramble
        solve["extra"] = extra
    with open(outputFile, 'w') as out:
        s = "Size\tDate\tTimestamp error\tObservation Time\tTime\tMoves\tTPS\tScramble\n"
        out.write(s)
        for row in mysolves:
            s = "{size}x{size}\t{date}\t{extra}\t{observ}\t{time}\t{moves}\t{tps}\t{scramble}\n".format(
                observ=row["observ"], time=row["time"], date=row["date"], size=row["size"], scramble=row["scramble"],
                moves=row["moves"], tps=row["tps"], extra=row["extra"])
            out.write(s)


if __name__ == '__main__':
    parse()
