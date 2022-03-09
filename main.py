import csv
import operator
from random import randint
import time as ti
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
    file = open('roadData.txt')
    csvreader = csv.reader(file)
    roads_loading = []
    count = 0
    for row in csvreader:
        coordinates = []
        cords = row[0]
        pos = 2
        for i in range(1, len(cords)):
            if cords[i] == ";":
                x = int(cords[pos:i])
                pos = i + 1
            elif cords[i] == ")":
                y = int(cords[pos:i])
                pos = i + 3
                i += 1
                coordinates.append((x, y))

        length = int(float(row[1]))
        name = row[2]
        road1 = road(coordinates, name, length, count)
        roads_loading.append(road1)
        for x_hold, y_hold in coordinates:
            xc = int((x_hold - 1) / 500)
            yc = int((y_hold - 1) / 500)
            if (yc, xc) not in road1.chunks:
                chunks1[yc][xc].addRoad(road1)
                road1.addChunk(xc, yc)
        count += 1
    return roads_loading


def loadtube(chunks):
    file = open('stationData.txt')
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
            lines_load.append(Line(row[0], Lineindex, float(row[1][1:5]) / 3.6, colour))
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
                    s2.Lines.append(Lineindex - 1)
            if load:
                stations_load.append(sta)
                xc = int((sta.x - 1) / 500)
                yc = int((sta.y - 1) / 500)
                chunks[yc][xc].addStation(sta)
                sta.chunk = (xc, yc)
    sorted_list = sorted(stations_load, key=operator.attrgetter("ID"))
    return sorted_list, lines_load


def construct_path(cameFrom, current):
    total_path = [current.ID]
    prev = current.ID
    while prev != None:
        if cameFrom[prev]:
            total_path.append(cameFrom[prev].ID)
        else:
            break
        prev = cameFrom[prev].ID
    # total_path.reverse()
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
        for s in openSet:
            if fScore[s.ID] < minFScore:
                minFScore = fScore[s.ID]
                current = s
        if current.ID == ID2:
            return construct_path(cameFrom, current)
        openSet.remove(current)

        for neighborID in current.adjStationsID:
            tentative_gScore = gScore[current.ID] + calc_dist(current.x, current.y, stations[neighborID].x,
                                                              stations[neighborID].y)
            if tentative_gScore < gScore[neighborID]:
                cameFrom[neighborID] = current
                gScore[neighborID] = tentative_gScore
                fScore[neighborID] = tentative_gScore + calc_dist(current.x, current.y, destx, desty)
                if stations[neighborID] not in openSet:
                    openSet.append(stations[neighborID])


def calc_dist(x1, y1, x2, y2):
    return ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5


def calc_path(stations, lines, speed, x1, y1, x2, y2):
    walking = calc_dist(x1, y1, x2, y2) / speed
    threeClosest_x1 = [stations[0], stations[1], stations[2]]
    threeClosest_x2 = [stations[0], stations[1], stations[2]]
    for s in stations:
        dist_to_sx1 = calc_dist(x1, y1, s.x, s.y)
        dist_to_sx2 = calc_dist(x2, y2, s.x, s.y)
        for close in range(3):
            if calc_dist(x1, y1, threeClosest_x1[close].x, threeClosest_x1[close].y) > dist_to_sx1:
                threeClosest_x1[close] = s
                break
        for close in range(3):
            if calc_dist(x2, y2, threeClosest_x2[close].x, threeClosest_x2[close].y) > dist_to_sx2:
                threeClosest_x2[close] = s
                break
    tentativePath = []
    tentativeTime = 1000000000000
    for startStation in threeClosest_x1:

        walking_to_station = calc_dist(x1, y1, startStation.x, startStation.y) / speed
        for endStation in threeClosest_x2:
            superTentativePath = [(x1, y1), (startStation.x, startStation.y)]
            tubePath_ID = A_star(startStation.ID, endStation.ID, stations)
            tubePath_ID.reverse()
            path_length = 0
            tube_path_time = 0
            for i in range(len(tubePath_ID) - 1):
                superTentativePath.append((stations[tubePath_ID[i]].x, stations[tubePath_ID[i]].y))
                length = calc_dist(stations[tubePath_ID[i]].x, stations[tubePath_ID[i]].y,
                                   stations[tubePath_ID[i + 1]].x, stations[tubePath_ID[i + 1]].y)
                optimistic_speed = 0
                for line_one in stations[tubePath_ID[i]].Lines:
                    for line_two in stations[tubePath_ID[i + 1]].Lines:
                        if line_one == line_two:
                            optimistic_speed = max(optimistic_speed, lines[line_one].speed)
                # if optimistic_speed == 0:
                #     print(stations[i].name + ' ' + stations[i+1].name)

                tube_path_time += length / optimistic_speed
                path_length += length
            walking_to_dest = calc_dist(endStation.x, endStation.y, x2, y2) / speed
            superTentativePath.append((endStation.x, endStation.y))
            superTentativePath.append((x2, y2))
            if tube_path_time + walking_to_dest + walking_to_station < tentativeTime:
                tentativeTime = tube_path_time + walking_to_dest + walking_to_station
                tentativePath = []
                for poggies in superTentativePath:
                    tentativePath.append(poggies)
    if tentativeTime < walking:
        return tentativeTime, tentativePath
    else:
        return walking, [(x1, y1), (x2, y2)]


if __name__ == '__main__':
    scale = 1
    width, height = (1500 * scale, 700 * scale)
    camX, camY = (6500, 10000)
    text = True
    prevX, prevY = -1, -1
    loadedChunks = []
    x, y = 6500, 10000
    x2, y2 = 7000, 10000
    walkingSpeed = 1.5  # m/s

    chunks = []
    for i in range(60):
        chunks.append([])
        for j in range(60):
            newChunk = chunk(j, i)
            chunks[i].append(newChunk)
    stations, lines = loadtube(chunks)
    #roads = loadRoads(chunks)
    pg.init()

    update = True
    running = True
    updatePath = True
    draw = -1
    screen = pg.display.set_mode((width, height), pg.RESIZABLE)
    myfont2 = pygame.font.SysFont('Comic Sans MS', int(30))
    while running:

        # calculating path from 1 to 2

        # calculating path from 1 to all other stations
        if updatePath:
            pathToStations = []
            for s in stations:
                time2, path2 = calc_path(stations, lines, walkingSpeed, x, y, s.x, s.y)
                newPath2 = []
                for ex2, why2 in path2:
                    newPath2.append(((ex2 - camX) / scale, (why2 - camY) / scale))
                pathToStations.append((time2, newPath2))
            updatePath = False

        # drawing distance circles
        for i in range(3, 0, -1):
            for s in stations:
                match i:
                    case 3:
                        colour = (150, 0, 0)
                    case 2:
                        colour = (150, 150, 0)
                    case 1:
                        colour = (0, 150, 0)

                timeTo = pathToStations[s.ID][0]
                if 1000 * i - timeTo > 0:
                    pg.draw.circle(screen, colour, ((s.x - camX) / scale, (s.y - camY) / scale),
                                   (1000 * i - timeTo) * walkingSpeed / scale)
            pg.draw.circle(screen, colour, ((x - camX) / scale, (y - camY) / scale), 1000 * i * walkingSpeed / scale)

        time, path = calc_path(stations, lines, walkingSpeed, x, y, x2, y2)
        newPath = []
        for ex, why in path:
            newPath.append(((ex - camX) / scale, (why - camY) / scale))
        pg.draw.lines(screen, (0, 0, 0), False, newPath, 10)
        if update:  # update font size
            myfont2 = pygame.font.SysFont('Comic Sans MS', int(30/scale))
            update = False
        # drawing points 1 and 2
        pg.draw.circle(screen, (0, 0, 255), ((x - camX) / scale, (y - camY) / scale), 5)
        pg.draw.circle(screen, (255, 0, 0), ((x - camX) / scale, (y - camY) / scale), 3)

        pg.draw.circle(screen, (0, 255, 0), ((x2 - camX) / scale, (y2 - camY) / scale), 5)
        pg.draw.circle(screen, (0, 0, 255), ((x2 - camX) / scale, (y2 - camY) / scale), 3)

        (width, height) = (1500 * scale, 700 * scale)
        if draw != -1:
            pg.draw.lines(screen, (0, 255, 0), False, pathToStations[draw][1], 5)
            ti.sleep(0.01)
            draw += 1
            if draw == 180:
                draw = -1

        # drawing roads
        for cx, cy in loadedChunks:
            for ID in chunks[cy][cx].roadsID:
                newCoords = []
                if scale > 2:
                    for (xrc, yrc) in roads[ID].coordinates:
                        xrc = (xrc - camX) / scale
                        yrc = (yrc - camY) / scale
                        newCoords.append((xrc, yrc))
                    if roads[ID].length > scale * 6:
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
                    textsurface2 = myfont2.render(str(station.name) + " " + str(int(pathToStations[station.ID][0])),
                                                  False, (255, 0, 0))
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
                                     ((station.x + 3 * i - camX) / scale, (station.y + 3 * i - camY) / scale),
                                     ((stations[adjID].x + 3 * i - camX) / scale,
                                      (stations[adjID].y + 3 * i - camY) / scale), int(6 / len(connectingLines) ** 0.3))

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

        pg.display.flip()
        screen.fill((240, 240, 240))
        textsurface = myfont2.render((str(int((time * 100)) / 100)), False, (0, 0, 0))
        screen.blit(textsurface, ((x2 - camX) / scale, (y2 - camY) / scale))
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
                    # updatePath = True
                if pressed_keys[pg.K_2]:
                    x2 = xm * scale + camX
                    y2 = ym * scale + camY
                    # updatePath = True
                if pressed_keys[pg.K_r]:
                    scale = 1
                    update = True
                if pressed_keys[pg.K_c]:
                    updatePath = True
                if pressed_keys[pg.K_d]:
                    draw = 0
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
