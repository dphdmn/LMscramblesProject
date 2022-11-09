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


def calibriFont(size):
    return ImageFont.truetype("calibri_font.ttf", size)


def drawImage(fd, res):
    W = res
    H = res
    image = Image.new("RGBA", (W, H), (255, 255, 255))
    draw = ImageDraw.Draw(image)
    margin = res / 12
    yshift = res / 10
    xshift = 0
    cellsize = res / 14
    fontsizeTime = int(cellsize / 3)
    fontsizeHeaders = int(cellsize / 4)
    timeFont = calibriFont(fontsizeTime)
    headersFont = calibriFont(fontsizeHeaders)
    outlineW = int(cellsize / 30)
    startX, startY = margin + xshift, margin + yshift
    for i in range(1, 9):
        if i == 1:
            head = "1 - 9"
        else:
            head = '{fr} - {t}'.format(fr=i * 10 - 10, t=i * 10 - 1)
        x = startX - cellsize
        y = startY + cellsize * (i - 1)
        textX = x + cellsize / 2
        textY = y + cellsize / 2 + fontsizeHeaders / 3
        draw.text((textX, textY),
                  head,
                  font=headersFont,
                  fill='black',
                  align='center',
                  anchor='ms')
    validtimes = []
    for i in fd:
        if not i["empty"]:
            validtimes.append(i["time"])
    fastest = min(validtimes)
    average = sum(validtimes) / len(validtimes)
    slowest = 2 * (average - fastest)
    timecolors = {}
    grad = getRYBgradient([20, 20, 20, 20])
    for time in validtimes:
        normalized = int(79 * (time - fastest) / slowest)
        if normalized > 79:
            normalized = 79
        timecolors[time] = grad[normalized]
    for i in range(1, 80):
        print(i)
        data = fd[i - 1]
        valid = not data["empty"]
        if valid:
            bgcolor = timecolors[data["time"]]
        else:
            bgcolor = 'gray'
        x = startX + cellsize * (i % 10)
        y = startY + cellsize * (i // 10)
        xl = startX + cellsize + cellsize * (i % 10)
        yl = startY + cellsize + cellsize * (i // 10)
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
    image.show()


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


fd = analyseOptimal("stats.txt")
drawImage(fd, 2000)
