import math
from PIL import Image, ImageDraw, ImageFont
from colour import Color


def goodTextColor(bgcolor):
    if isTextBlack(bgcolor):
        return (0, 0, 0)
    return (255, 255, 255)


def isTextBlack(rgb):
    return math.sqrt((.241 * (rgb[0] * rgb[0])) + (.671 * (rgb[1] * rgb[1])) + (.068 * (rgb[2] * rgb[2]))) > 128


def epicGradient(colors, amounts):
    grad = []
    for i in range(len(colors) - 1):
        grad_i = list(Color(colors[i]).range_to(Color(colors[i + 1]), amounts[i]))
        grad = grad + grad_i
    newgrad = []
    for i in grad:
        g = tuple(int(item * 255) for item in i.rgb)
        newgrad.append(g)
    return newgrad


def getRYBgradient(amounts):
    return epicGradient(["#004000", "#00FF00", "#FFFF00", "#FF0000", "#400000"], amounts)


def calibriFont(size, fontpath):
    return ImageFont.truetype(fontpath, size)


def getPartsAverages(fd):
    avgs = []
    effs = []
    for part in range(0, 8):
        sumValids = 0
        sumTimes = 0
        sumEffs = 0
        for i in range(10 * part - 1, 10 * part + 9):
            if fd[i]["empty"] == False:
                sumValids += 1
                sumTimes += fd[i]["time"]
                sumEffs += fd[i]["efftps"]
        if sumValids > 0:
            avgs.append(round(sumTimes / sumValids, 3))
            effs.append(round(sumEffs / sumValids, 3))
        else:
            avgs.append(-1)
            effs.append(-1)
    return avgs, effs


def getNormalColor(fastest, slowest, timelist):
    timecolors = {}
    grad = getRYBgradient([20, 20, 20, 20])
    for time in timelist:
        normalized = int(79 * (time - fastest) / slowest)
        if normalized > 79:
            normalized = 79
        if normalized < 0:
            normalized = 0
        timecolors[time] = grad[normalized]
    return timecolors


def drawImage(fd, res, fontpath):
    parts, avgeffs = getPartsAverages(fd)
    W = res
    H = int(res * 1.4)
    image = Image.new("RGBA", (W, H), (255, 255, 255))
    draw = ImageDraw.Draw(image)
    margin = res / 5
    yshift = -res / 3
    xshift = 0
    cellsize = res / 11.5
    fontsizeTime = int(cellsize / 3)
    fontsizeHeaders = int(cellsize / 4)
    fontsizeVerySmall = int(cellsize / 6)
    timeFont = calibriFont(fontsizeTime, fontpath)
    headersFont = calibriFont(fontsizeHeaders, fontpath)
    verySmalFont = calibriFont(fontsizeVerySmall, fontpath)
    outlineW = int(cellsize / 30)
    startX, startY = margin + xshift, margin + yshift
    gapshift = res / 100
    headers = []
    headers10 = []
    for i in range(1, 17):
        if i == 1:
            head = "1 - 4"
        else:
            head = '{fr} - {t}'.format(fr=i * 5 - 5, t=i * 5 - 1)
        headers.append(head)
    for i in range(1, 9):
        if i == 1:
            head = "1 - 9"
        else:
            head = '{fr} - {t}'.format(fr=i * 10 - 10, t=i * 10 - 1)
        headers10.append(head)
    validtimes = []
    for i in fd:
        if not i["empty"]:
            validtimes.append(i["time"])
    fastest = min(validtimes)
    average = sum(validtimes) / len(validtimes)
    slowest = 2 * (average - fastest)
    timecolors = getNormalColor(fastest, slowest, validtimes)
    partcolors = getNormalColor(fastest, slowest, parts)
    for i in range(10, 80):
        data = fd[i - 1]
        valid = not data["empty"]
        if valid:
            bgcolor = timecolors[data["time"]]
        else:
            bgcolor = 'gray'
        x = startX + cellsize * (i % 5)
        y = startY + cellsize * (i // 5) + gapshift * (i // 10)
        xl = startX + cellsize + cellsize * (i % 5)
        yl = startY + cellsize + cellsize * (i // 5) + gapshift * (i // 10)
        draw.rectangle(
            xy=(x, y, xl, yl),
            fill=bgcolor,
            outline='black',
            width=outlineW)
        textX = x + cellsize / 2
        textY = y + cellsize / 2 + fontsizeTime / 3
        if valid:
            draw.text((textX, textY),
                      str(data["time"]),
                      font=timeFont,
                      fill=goodTextColor(bgcolor),
                      align='center',
                      anchor='ms')
            draw.text((textX, textY + cellsize * 0.3),
                      "best of " + str(data["solvesAmount"]),
                      font=verySmalFont,
                      fill=goodTextColor(bgcolor),
                      align='center',
                      anchor='ms')
            draw.text((textX, textY - cellsize * 0.4),
                      "eff. " + str(data["efftps"]),
                      font=verySmalFont,
                      fill=goodTextColor(bgcolor),
                      align='center',
                      anchor='ms')
            draw.text((textX, textY - cellsize * 0.25),
                      "+" + str(data["dif"]),
                      font=verySmalFont,
                      fill=goodTextColor(bgcolor),
                      align='center',
                      anchor='ms')
        if i % 5 == 0 or i == 1:
            headerX = startX - cellsize + cellsize / 2
            headerY = textY
            draw.text((headerX, headerY),
                      headers[i // 5],
                      font=headersFont,
                      fill='black',
                      align='center',
                      anchor='ms')
        if (i + 1) % 10 == 0:
            partX = x + cellsize + gapshift
            partXl = partX + 2 * cellsize
            partY = y - cellsize
            partYl = yl
            ptid = i // 10
            pt = parts[ptid]
            if pt != -1:
                bgcolor = partcolors[pt]
            draw.rectangle(
                xy=(partX, partY, partXl, partYl),
                fill=bgcolor,
                outline='black',
                width=outlineW)
            textX = partX + cellsize
            textY = partY + cellsize + fontsizeTime / 3
            if pt != -1:
                draw.text((textX, textY),
                          str(pt),
                          font=timeFont,
                          fill=goodTextColor(bgcolor),
                          align='center',
                          anchor='ms')
                draw.text((textX, textY - cellsize * 0.7),
                          "Avg eff. " + str(avgeffs[ptid]),
                          font=headersFont,
                          fill=goodTextColor(bgcolor),
                          align='center',
                          anchor='ms')
                draw.text((textX, textY + cellsize * 0.6),
                          "Solves " + headers10[ptid],
                          font=headersFont,
                          fill=goodTextColor(bgcolor),
                          align='center',
                          anchor='ms')
    return image


def analyseOptimal(optimalStats):
    with open(optimalStats, "r") as file:
        stats = file.read().splitlines()
    data = []
    for stat in stats:
        statlist = stat.split("\t")
        el = {}
        el["time"] = float(statlist[0])
        el["mvc"] = int(statlist[1])
        el["opt"] = int(statlist[2])
        data.append(el)
    freqData = []
    for i in range(1, 81):
        el = {}
        el["empty"] = True
        matches = list(filter(lambda item: item['opt'] == i, data))
        amount = len(matches)
        if amount > 0:
            el["empty"] = False
            el["solvesAmount"] = len(matches)
            min = sorted(matches, key=lambda d: d['time'])[0]
            el["time"] = min["time"]
            el["mvc"] = min["mvc"]
            el["dif"] = min["mvc"] - i
            el["tps"] = round(min["mvc"] / min["time"], 3)
            el["efftps"] = round(i / min["time"], 3)
        freqData.append(el)
    return freqData


def analyseAndRender(stats, resolution, path, fontpath):
    fd = analyseOptimal(stats)
    image = drawImage(fd, resolution, fontpath)
    image.save(path)
