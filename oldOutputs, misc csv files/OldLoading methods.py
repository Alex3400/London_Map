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
    file = open('roadData.txt')
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

def loadStationsNew(chunks5):
    file = open('allStations.txt')
    csvreader = csv.reader(file)
    IDindex = 0
    stations_load = []
    for row in csvreader:
        station_hold = station(int(row[1]), int(row[2]), row[0], IDindex, [])
        IDindex += 1
        stations_load.append(station_hold)
    return stations_load

def loadAdj(stations):
    file = open('allStations.txt')
    csvreader = csv.reader(file)
    IDindex = 0
    for row in csvreader:
        adjName = []
        for i in range(3, len(row) - 1):
            adjName.append(row[i].strip())
        for s in stations:
            if s.name in adjName:
                stations[IDindex].addAdjSta(s)
        IDindex += 1
    for s in stations:
        print(s.toStringID())
    print("done")

def loadLines(chunks4, stations):
    file = open('fullLines.txt')
    csvreader = csv.reader(file)
    IDindex = 0
    Lineindex = 0
    lines_load = []
    nextLine = False
    for row in csvreader:
        if not row:
            nextLine = True
        elif nextLine:
            lines_load.append(Line(row[0], Lineindex, float(row[1][1:5])))
            Lineindex += 1
            nextLine = False
        else:
            for s in stations:
                if s.name == row[0]:
                    sta = s
            sta.Lines.append(Lineindex - 1)
            lines_load[Lineindex - 1].addStation(sta)
            IDindex += 1

    for l in lines_load:
        print(l.toStringID())
    return lines_load



def loadStationsOld(chunks2):
    file = open('actual.csv')
    csvreader = csv.reader(file)
    IDindex = 0
    stations = []
    for row in csvreader:
        x = int(float(row[7].strip()))
        y = int(float(row[8].strip()))
        name = row[0].strip()
        if x > 0 and y > 0 and x < 30000 and y < 30000:
            station1 = station(x, y, name, IDindex, [])
            stations.append(station1)
            xc = int((x - 1) / 500)
            yc = int((y - 1) / 500)
            chunks2[yc][xc].addStation(station1)
            station1.chunk = (xc, yc)
        IDindex += 1
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


#old path finding method
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

# old directions method
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
        # path_s = path_to_station(ID, ID1, stations, [], [])
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
    # for l in lines:
    #     print(l.toString())
    # for s in stations:
    #     printy = False
    #     for l in lines:
    #         for station in l.stations:
    #             if s.name == station.name:
    #                 printy = True
    #     if printy:
    #         print(s.toString())
    # print("done")


# lines = loadLines(chunks, stations)
    # lines = [Line("Bakerloo", 0, 27.04), Line("Central", 1, 37.27), Line("Circle", 2, 23.73),
    #          Line("District", 3, 29.19), Line("Hammersmith and City", 4, 25.33), Line("Jubilee", 5, 39.11),
    #          Line("Metropolitan", 6, 45.61), Line("Northern", 7, 33.28), Line("Piccadilly", 8, 33.11),
    #          Line("Victoria", 9, 40.66)]
    # loadTubeStations(chunks, lines, stations)
# f = open("LineOutput.txt", "a")
# for l in lines:
#     print(l.toString())

# f = open("Stations2.txt", "a")
# for station in stations:
#     if station.x > 0 and station.y > 0 and station.x < 30000 and station.y < 30000:
#         f.write(str(station.x) + "," + str(station.y) + "," + station.name + "\n")
# f.close()

# f = open("roadData.txt", "a")
# for road in roads:
#     result = ""
#     for x, y in road.coordinates:
#         result += " (" + str(x) + ";" + str(y) + ")"
#     result += "," + str(road.length) + "," + road.name
#     result.strip()
#     f.write(result + "\n")
# f.close()