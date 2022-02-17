import csv
from random import randint

import pygame as pg
import pygame


class chunk:

    def __init__(self, xPos, yPos):
        self.xPos = xPos
        self.yPos = yPos
        self.xCentre = xPos * 500 + 250
        self.yCentre = yPos * 500 + 250
        self.roads = []
        self.roadsID = []

    def addRoad(self, x):
        self.roads.append(x)
        self.roadsID.append(x.ID)


class road:

    def __init__(self, coordinates, name, length, ID):
        self.name = name
        self.length = length
        self.coordinates = coordinates
        self.chunks = []
        self.ID = ID

    def toString(self):
        x = ""
        for i in self.coordinates:
            x = x + " (" + str(i[0]) + ";" + str(i[1]) + ")"
        x = x + "," + str(self.length) + "," + self.name
        return x

    def addChunk(self, x, y):
        self.chunks.append((y, x))


class station:

    def __init__(self, x, y, name, ID):
        self.x = x
        self.y = y
        self.name = name
        self.ID = ID
        self.adjStations = []
        self.adjStationsID = []

    def addAdjSta(self, s):
        self.adjStations.append(s)
        self.adjStationsID.append(s.ID)

    def toString(self):
        allStations = ""
        for s in self.adjStations:
            allStations += s.name + "; "
        return self.name + ", " + "(" + str(self.x) + ";" + str(
            self.y) + ")" + ", " + allStations

    def toStringID(self):
        allStations = ""
        for s in self.adjStations:
            allStations += str(s.ID) + "; "
        return str(self.ID) + ", " + "(" + str(self.x) + ";" + str(
            self.y) + ")" + ", " + allStations


class Line:
    def __init__(self, name, ID, speed):
        self.speed = speed
        self.name = name
        self.ID = ID
        self.stationsID = []
        self.stations = []

    def addStation(self, station):
        self.stations.append(station)
        self.stationsID.append(station.ID)

    def toString(self):
        x = self.name + ", " + str(self.speed) + ": \n\n"
        for s in self.stations:
            x += s.toString() + "\n"
        return x

    def toStringID(self):
        x = self.name + ", " + str(self.speed) + ": \n\n"
        for s in self.stations:
            x += s.toStringID() + "\n"
        return x


def loadAll():
    file = open('roads.csv')
    csvreader = csv.reader(file)
    roads = []
    for row in csvreader:
        str2 = row[0][19:]
        pos = 1
        coordinates = []
        searchX = True
        dont = False
        for i in range(len(str2)):
            if str2[i] == " ":
                if searchX:
                    x = round(float(str2[pos:i]) - 495602.19 - 25000)
                    pos = i + 1
                    searchX = False
                else:
                    y = round(float(str2[pos:i]) - 99033.84 - 62700)
                    pos = i + 3
                    searchX = True
                    if x > 30000 or x < 0 or y > 30000 or y < 0:
                        dont = True
                    coordinates.append((x, y))
        if dont:
            continue
        name = row[5]
        length = float(row[10])
        road1 = road(coordinates, name, length)
        roads.append(road1)
        # print(road1.toString())
    return roads
    file.close()


def loadRoads(chunks1):
    file = open('roadsOutput7.txt')
    csvreader = csv.reader(file)
    roads = []
    count = 0
    for row in csvreader:
        coordinates = []
        cords = row[0]
        pos = 2
        x, y = 0, 0
        for i in range(1, len(cords)):
            if cords[i] == ";":
                x = int(cords[pos:i])
                pos = i + 1
            if cords[i] == ")":
                y = int(cords[pos:i])
                pos = i + 3
                i += 1
                coordinates.append((x, y))

        length = int(float(row[1]))
        name = row[2]
        road1 = road(coordinates, name, length, count)
        roads.append(road1)
        for x, y in coordinates:
            xc = int((x - 1) / 500)
            yc = int((y - 1) / 500)
            if (yc, xc) not in road1.chunks:
                chunks1[yc][xc].addRoad(road1)
                road1.addChunk(xc, yc)
        count += 1
    return roads


def loadStations(chunks2):
    file = open('actual.csv')
    csvreader = csv.reader(file)
    count = 0
    stations = []
    for row in csvreader:
        x = int(float(row[7].strip()))
        y = int(float(row[8].strip()))
        name = row[0].strip()
        if x > 0 and y > 0 and x < 30000 and y < 30000:
            stations.append(station(x, y, name, count))
        count += 1
    return stations


def loadTubeStations(chunks3, lines, stations):
    file = open('London tube lines.csv')
    csvreader = csv.reader(file)
    for row in csvreader:
        for s in stations:
            if s.name == row[1]:
                for l in lines:
                    if l.name == row[0]:
                        if s.ID not in l.stationsID:
                            l.addStation(s)
                        for s2 in stations:
                            if s2.name == row[2]:
                                if s2.ID not in s.adjStationsID:
                                    s.addAdjSta(s2)
                                if s.ID not in s2.adjStationsID:
                                    s2.addAdjSta(s)
    file.close()
    for l in lines:
        print(l.toStringID())
    print("done")


if __name__ == '__main__':
    chunks = []
    for i in range(60):
        chunks.append([])
        for j in range(60):
            newChunk = chunk(j, i)
            chunks[i].append(newChunk)
    roads = loadRoads(chunks)
    stations = loadStations(chunks)
    lines = [Line("Bakerloo", 0, 27.04), Line("Central", 1, 37.27), Line("Circle", 2, 23.73),
             Line("District", 3, 29.19), Line("Hammersmith and City", 4, 25.33), Line("Jubilee", 5, 39.11),
             Line("Metropolitan", 6, 45.61), Line("Northern", 7, 33.28), Line("Piccadilly", 8, 33.11),
             Line("Victoria", 9, 40.66)]
    loadTubeStations(chunks, lines, stations)

    # f = open("LineOutput.txt", "a")
    # for l in lines:
    #     print(l.toString())

    # f = open("Stations2.txt", "a")
    # for station in stations:
    #     if station.x > 0 and station.y > 0 and station.x < 30000 and station.y < 30000:
    #         f.write(str(station.x) + "," + str(station.y) + "," + station.name + "\n")
    # f.close()

    # f = open("roadsOutput7.txt", "a")
    # for road in roads:
    #     result = ""
    #     for x, y in road.coordinates:
    #         result += " (" + str(x) + ";" + str(y) + ")"
    #     result += "," + str(road.length) + "," + road.name
    #     result.strip()
    #     f.write(result + "\n")
    # f.close()

    print("done")
    pg.init()
    scale = 1
    (width, height) = (1500 * scale, 700 * scale)
    running = True
    screen = pg.display.set_mode((width, height), pg.RESIZABLE)
    time = 0
    i = 0
    camX = 6500
    camY = 10000
    prevX, prevY = -1, -1
    loadedChunks = [(14, 20), (15, 20), (16, 20)]
    time = 0
    myfont2 = pygame.font.SysFont('Comic Sans MS', int(30 / scale))
    while running:
        # if time % 200 == 0:
        #     # print(loadedChunks)
        #     # print(scale)
        #     # print((camX, camY))
        # time += 1
        (width, height) = (1500 * scale, 700 * scale)
        pg.display.flip()
        screen.fill((240, 240, 240))
        for cx, cy in loadedChunks:
            for ID in chunks[cy][cx].roadsID:
                newCoords = []
                for (x, y) in roads[ID].coordinates:
                    x = (x - camX) / scale
                    y = (y - camY) / scale
                    newCoords.append((x, y))
                pg.draw.lines(screen, (0, 0, 0), False, newCoords, 2)
        loadedChunks = []
        for station in stations:
            pg.draw.circle(screen, (0, 255, 0), ((station.x - camX) / scale, (station.y - camY) / scale), 5)
            # textsurface2 = myfont2.render(str(station.name), False, (0, 0, 0))
            # screen.blit(textsurface2, ((station.x - camX) / scale, (station.y - camY) / scale))
            for l in lines:
                for s in l.stations:
                    pg.draw.line(screen, (255, 0, 0,), ((s.x - camX) / scale, (s.y - camY) / scale),
                                 ((s.adjStations[0].x - camX) / scale, (s.adjStations[0].y - camY) / scale), 3)
        for i in range(60):
            for j in range(60):
                chunk = chunks[i][j]
                x = chunk.xCentre
                y = chunk.yCentre
                # print(str(x) + ", " + str(y)+ "; " + str(camX) + ", "+ str(camY))
                if x < camX + width + 500 and x > camX - 500 and y > camY - 500 and y < camY + height + 500:
                    if (chunk.xPos, chunk.yPos) not in loadedChunks:
                        loadedChunks.append((chunk.xPos, chunk.yPos))

        for event in pg.event.get():
            buttons = pg.mouse.get_pressed(3)
            xm, ym = pg.mouse.get_pos()
            if event.type == pg.QUIT:
                running = False
            if event.type == pg.MOUSEBUTTONUP:
                prevX = -1
            if buttons[0]:
                if not prevX == -1:
                    camX += (prevX - xm) * scale
                    camY += (prevY - ym) * scale
                prevX, prevY = pg.mouse.get_pos()
            if event.type == pg.MOUSEBUTTONDOWN:
                if event.button == 5:
                    scale += 0.05
                    camX += width * (-0.05) / 2
                    camY += height * (-0.05) / 2
                    update = True
                if event.button == 4:
                    scale -= 0.05
                    # camX += width * (scale - 1) / 2
                    # camY += height * (scale - 1) / 2
                    update = True
                if buttons[0]:
                    print(str(xm * scale + camX) + ", " + str(ym * scale + camY))
