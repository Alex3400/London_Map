import csv
import operator
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
        self.stations = []
        self.stationsID = []

    def addRoad(self, rd):
        self.roads.append(rd)
        self.roadsID.append(rd.ID)

    def addStation(self, sta):
        self.stations.append(sta)
        self.stationsID.append(sta.ID)


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

    def __init__(self, x, y, name, ID, adjStations):
        self.x = x
        self.y = y
        self.name = name
        self.ID = ID
        self.chunk = (0, 0)
        self.adjStations = []
        self.adjStationsID = []
        self.Lines = []

    def addAdjSta(self, s):
        self.adjStations.append(s)
        self.adjStationsID.append(s.ID)

    def toString(self):
        allStations = ""
        for s in self.adjStations:
            allStations += s.name + "; "
        return self.name + ", " + "" + str(self.x) + ", " + str(
            self.y) + "" + ", " + allStations

    def toStringID(self):
        allStations = ""
        for s in self.adjStations:
            allStations += str(s.ID) + ","
        return str(self.ID) + "," + str(self.name) + "," + "" + str(self.x) + "," + str(
            self.y) + "," + allStations

    def addAdjStaID(self, s):
        self.adjStationsID.append(s)


class Line:
    def __init__(self, name, ID, speed, colour):
        self.speed = speed
        self.name = name
        self.ID = ID
        self.stationsID = []
        self.stations = []
        self.colour = colour

    def addStation(self, station):
        self.stations.append(station)
        self.stationsID.append(station.ID)

    def toString(self):
        x = self.name + ", " + str(self.speed) + ": \n"
        for s in self.stations:
            x += s.toString() + "\n"
        return x

    def toStringID(self):
        x = self.name + ", " + str(self.speed) + ": \n"
        for s in self.stations:
            x += s.toStringID() + "\n"
        return x


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


def loadtube(chunks):
    file = open('fullStations.txt')
    csvreader = csv.reader(file)
    Lineindex = 0
    lines_load = []
    stations_load = []
    nextLine = False
    for row in csvreader:
        if not row:
            nextLine = True
        elif nextLine:
            colour = (int(row[2]), int(row[3]), int(row[4]))
            print(colour)
            lines_load.append(Line(row[0], Lineindex, float(row[1][1:5]), colour))
            Lineindex += 1
            nextLine = False
        else:
            sta = station(int(row[2]), int(row[3]), row[1], int(row[0]), [])
            for i in range(4, len(row) - 1):
                sta.addAdjStaID(int(row[i]))
            sta.Lines.append(Lineindex - 1)
            lines_load[Lineindex - 1].addStation(sta)
            load = True
            for s2 in stations_load:
                if s2.name == sta.name:
                    load = False
                    s2  .Lines.append(Lineindex - 1)
            if load:
                stations_load.append(sta)
                xc = int((sta.x - 1) / 500)
                yc = int((sta.y - 1) / 500)
                chunks[yc][xc].addStation(sta)
                sta.chunk = (xc, yc)
    new_list = sorted(stations_load, key=operator.attrgetter("ID"))
    return new_list, lines_load

def construct_path(cameFrom, current):
    total_path = [current.ID]
    prev = current.ID
    while prev:
        if cameFrom[prev]:
            total_path.append(cameFrom[prev].ID)
        else:
            break
        prev = cameFrom[prev].ID
    #total_path.reverse()
    return total_path


def A_star(ID1, ID2, staitons):
    destx, desty = stations[ID2].x, staitons[ID2].y
    openSet = [staitons[ID1]]
    gScore = []
    fScore = []
    cameFrom = []
    big = 100000000000
    for s in staitons:
        gScore.append(big)
        fScore.append(big)
        cameFrom.append(None)
    gScore[ID1] = 0
    fScore[ID1] = calc_dist(stations[ID1].x, stations[ID1].y, destx, desty)

    while len(openSet) != 0:
        current = None
        minFScore = big
        minID = 0
        for s in openSet:
            if fScore[s.ID] < minFScore:
                minFScore = fScore[s.ID]
                current = s
        if current.ID == ID2:
            return construct_path(cameFrom, current)
        openSet.remove(current)

        for neighborID in current.adjStationsID:
            tentative_gScore = gScore[current.ID] + calc_dist(current.x, current.y, stations[neighborID].x, stations[neighborID].y)
            if tentative_gScore < gScore[neighborID]:
                cameFrom[neighborID] = current
                gScore[neighborID] = tentative_gScore
                fScore[neighborID] = tentative_gScore + calc_dist(current.x, current.y, destx, desty)
                if stations[neighborID] not in openSet:
                    openSet.append(stations[neighborID])


def path_to_station(ID1, ID2, stations, path, prev):
    prev.append(ID1)
    paths = []
    isDead = False
    if ID1 > len(stations) - 1:
        return "dead"
    for ID in stations[ID1].adjStationsID:
        if ID not in prev:
            if ID == ID2:
                path.append((stations[ID].x, stations[ID].y))
                return path
            else:
                result = path_to_station(ID, ID2, stations, path, prev)
                if result != 'dead':
                    path.append((stations[ID].x, stations[ID].y))
                    return path
    return "dead"


def calc_dist(x1, y1, x2, y2):
    return ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5


def calc_path(stations, lines, speed, x1, y1, x2, y2):
    path = [(x1, y1)]
    dist = calc_dist(x1, y1, x2, y2)
    walking = dist / speed  # walking straight
    closest = 100000
    closest_station = -1
    for s in stations:
        dist2 = calc_dist(x1, y1, s.x, s.y)
        if dist2 < closest:
            closest = dist2
            closest_station = s
    time_to_station = closest / speed
    mintime = walking
    dest_station = closest_station
    ID = closest_station.ID
    path_best = []
    for s1 in stations:
        ID1 = s1.ID
        dist_to_dest = calc_dist(x2, y2, s1.x, s1.y)
        #path_s = path_to_station(ID, ID1, stations, [], [])
        path_s2 = A_star(ID, ID1, stations)
        path_s = []
        for s in path_s2:
            path_s.append((stations[s].x, stations[s].y))
        path_s.append((stations[ID].x, stations[ID].y))
        path_s.reverse()
        path_length = 0
        # print(path_s)
        for i in range(1, len(path_s)):
            one = path_s[i - 1]
            two = path_s[i]
            path_length += calc_dist(one[0], one[1], two[0], two[1])
            # path_length += ((one[0] - two[0]) ** 2 + (one[1] - two[1]) ** 2) ** 0.5
        time_on_train = path_length / 2000
        time_to_dest = dist_to_dest / speed
        if time_on_train + time_to_dest + time_to_station < mintime:
            mintime = time_on_train + time_to_dest + time_to_station
            dest_station = s1
            path_best = path_s
    if path_best:
        for l in path_best:
            path.append(l)
    path.append((x2, y2))
    if mintime < walking:
        # path = [(x1, y1), (closest_station.x, closest_station.y), (dest_station.x, dest_station.y), (x2, y2)]
        return mintime, path
    else:
        return walking, path


if __name__ == '__main__':
    scale = 1
    width, height = (1500 * scale, 700 * scale)
    camX, camY = (6500, 10000)
    text = True
    prevX, prevY = -1, -1
    loadedChunks = []
    x, y = 6500, 10000
    x2, y2 = 7000, 10000

    chunks = []
    for i in range(60):
        chunks.append([])
        for j in range(60):
            newChunk = chunk(j, i)
            chunks[i].append(newChunk)
    stations, lines = loadtube(chunks)
    roads = loadRoads(chunks)
    pg.init()

    update = False
    running = True
    screen = pg.display.set_mode((width, height), pg.RESIZABLE)
    myfont2 = pygame.font.SysFont('Comic Sans MS', int(30 / scale))
    while running:
        pg.draw.circle(screen, (0, 0, 255), ((x - camX) / scale, (y - camY) / scale), 5)
        pg.draw.circle(screen, (255, 0, 0), ((x - camX) / scale, (y - camY) / scale), 3)

        pg.draw.circle(screen, (0, 255, 0), ((x2 - camX) / scale, (y2 - camY) / scale), 5)
        pg.draw.circle(screen, (0, 0, 255), ((x2 - camX) / scale, (y2 - camY) / scale), 3)
        time, path = calc_path(stations, lines, 100, x, y, x2, y2)
        newPath = []
        for ex, why in path:
            newPath.append(((ex - camX) / scale, (why - camY) / scale))
        pg.draw.lines(screen, (0, 0, 0), False, newPath, 10)
        if update:
            myfont2 = pygame.font.SysFont('Comic Sans MS', int(30 / scale))
            update = False
        (width, height) = (1500 * scale, 700 * scale)
        pg.display.flip()
        screen.fill((240, 240, 240))

        # drawing roads
        for cx, cy in loadedChunks:
            for ID in chunks[cy][cx].roadsID:
                newCoords = []
                if scale > 2:
                    for (xrc, yrc) in roads[ID].coordinates:
                        xrc = (xrc - camX) / scale
                        yrc = (yrc - camY) / scale
                        newCoords.append((xrc, yrc))
                    if roads[ID].length > scale * 7.5:
                        pg.draw.lines(screen, (0, 0, 0), False, newCoords, 2)
                else:
                    for (xrc, yrc) in roads[ID].coordinates:
                        xrc = (xrc - camX) / scale
                        yrc = (yrc - camY) / scale
                        newCoords.append((xrc, yrc))
                    pg.draw.lines(screen, (0, 0, 0), False, newCoords, 2)

        # drawing stations and lines
        for station in stations:
            if station.chunk in loadedChunks:
                pg.draw.circle(screen, (0, 255, 0),
                               ((station.x - camX) / scale, (station.y - camY) / scale), 5)
                if text:
                    textsurface2 = myfont2.render(str(station.name), False, (255, 0, 0))
                    screen.blit(textsurface2, ((station.x - camX) / scale, (station.y - camY) / scale))
                # for l in lines:
                #     for s in l.stations:
                for adjID in station.adjStationsID:
                    connectingLines = []
                    for line1 in stations[adjID].Lines:
                        for line2 in station.Lines:
                            if line1 == line2:
                                connectingLines.append(line1)
                    for i in range(len(connectingLines)):
                        pg.draw.line(screen, lines[connectingLines[i]].colour,
                                     ((station.x + 3*i - camX) / scale, (station.y + 3*i - camY) / scale),
                                     ((stations[adjID].x + 3*i - camX) / scale,
                                      (stations[adjID].y + 3*i - camY) / scale), int(6 / len(connectingLines) ** 0.5))
        # setting loaded chunks
        loadedChunks = []
        for i in range(60):
            for j in range(60):
                chunk = chunks[i][j]
                xcc = chunk.xCentre
                ycc = chunk.yCentre
                if xcc < camX + width + 500 and xcc > camX - 500 and ycc > camY - 500 and ycc < camY + height + 500:
                    if (chunk.xPos, chunk.yPos) not in loadedChunks:
                        loadedChunks.append((chunk.xPos, chunk.yPos))

        for event in pg.event.get():
            buttons = pg.mouse.get_pressed(3)
            xm, ym = pg.mouse.get_pos()
            pressed_keys = pygame.key.get_pressed()
            if event.type == pg.KEYDOWN:
                if pressed_keys[pg.K_SPACE]:
                    text = not text
                if pressed_keys[pg.K_1]:
                    x = xm * scale + camX
                    y = ym * scale + camY
                if pressed_keys[pg.K_2]:
                    x2 = xm * scale + camX
                    y2 = ym * scale + camY
                if pressed_keys[pg.K_r]:
                    scale = 1
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
                    scale += 0.5
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
