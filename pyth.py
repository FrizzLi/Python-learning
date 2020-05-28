import heapq, copy, collections, random, time, re
from sys import maxsize
from itertools import permutations, combinations, product

class Map:
    def __init__(self, width=0, height=0, data=[]):
        self.data = data
        self.width = width
        self.height = height

    @property
    def data(self, coordinate):
        assert len(coordinate) != 2, "Coordinate needs iterable Invalid coordinate"

        return self.__data[coordinate]


# create conversion from [][] to ()
    @data.setter
    def data(self, coordinate, node):
        pass

        # self.__data = mapData

    @property
    def width(self):
        return self.__width
    
    @property
    def height(self):
        return self.__height


class Node:
    def __init__(self, position, terrain):
        self.pos = position
        self.terrain = terrain
        self.parent = -1        # node position from which we got to this node
        self.dist = maxsize     # distance from start to current node
        self.g = maxsize
        self.h = maxsize

    def __lt__(self, other):
        if self.dist != other.dist:
            return self.dist < other.dist
        return self.h < other.h

# add princess/dragon/start
# diagonal/manhattan
# mountain/stepWeight

def dijkstra(data, start, adjacency):
    h = []
    data[start].dist = 0
    heapq.heappush(h, data[start])

    for i, _ in enumerate(data):
        node = heapq.heappop(h)
        for adjacent in adjacency:
            neighbor = (node.pos[0]+adjacent[0], node.pos[1]+adjacent[1])
            if neighbor in data and data[neighbor].dist > node.dist + data[neighbor].terrain:
                data[neighbor].dist = node.dist + data[neighbor].terrain
                data[neighbor].parent = node.pos
                heapq.heappush(h, data[neighbor])

    return data

def aStar(data, start, end, adjacency):
    openL = []
    closedL = []
    data[start].g = 0
    heapq.heappush(openL, data[start])

    for _ in data:      # until all nodes have been discovered
        node = heapq.heappop(openL)
        closedL.append(node.pos)

        if node.pos == end:
            break

        for adjacent in adjacency:
            neighbor = (node.pos[0]+adjacent[0], node.pos[1]+adjacent[1])
            if neighbor in data and neighbor not in closedL:        # also TRAVERSABLE (can do later)
                h = abs(data[neighbor].pos[0] - end[0]) + abs(data[neighbor].pos[1] - end[1])
                g = node.g + data[neighbor].terrain
                f = g + h
                if f < data[neighbor].dist:
                    data[neighbor].g = g
                    data[neighbor].h = h
                    data[neighbor].dist = f
                    data[neighbor].parent = node.pos
                if data[neighbor] not in openL:
                    heapq.heappush(openL, data[neighbor])

    return data
    




def load(file):
    with open(file) as f:
        ROWS, COLS, moveType = f.readline().split()[:3]
        map2D = [f.readline().rstrip('\n') for line in range(int(ROWS))]
        adjacency = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        if moveType == 'D':
            adjacency.extend([(-1, -1), (-1, 1), (1, -1), (1, 1)])

        # if maxRow*maxCol != len(mapStr):    # az na konci!
            # S - start (required)
            # N - princesses (required)
            # D - one dragon (required)
            # E - end (optional)
            # P - portal (optional)
        #    print("Incorrect number of map characters")
        #    return

    mapTerr = {'N': 100, 'H': 2}
    mapTerr = collections.defaultdict(lambda: 1, mapTerr)
    princesses = []
    mapData = {}
    start = 0, 0

    for i in range(int(ROWS)):
        for j in range(int(COLS)):
            if map2D[i][j] == 'D':
                dragon = i, j
            elif map2D[i][j] == 'P':
                princesses.append((i, j))
            elif map2D[i][j]  == 'S':
                start = i, j
            mapData[i, j] = Node((i, j), mapTerr[map2D[i][j]])
    
    return mapData, princesses, dragon, start, adjacency

def findMinDist(npcData, princesses, dragon, start):
    mini = maxsize

    for permutation in permutations(princesses):
        distance = npcData[start][dragon].dist     # distance to get to dragon
        for begin, finish in zip((dragon,)+permutation, permutation):
            distance += npcData[begin][finish].dist
        if distance < mini:
            mini, order = distance, permutation

    return (start, dragon) + order, mini

def karp(npcData, princesses, dragon, start):
    princesses = frozenset(princesses)
    nodes = {}

    for row in range(len(princesses)):              # set length
        for comb in combinations(princesses, row):  # set value     (right side)
            comb = frozenset(comb)
            for finish in princesses - comb:        # destination   (left side)
                routes = []
                if comb == frozenset():             # case for dragon starting
                    cost = npcData[dragon][finish].dist + npcData[start][dragon].dist
                    nodes[finish, frozenset()] = cost, dragon
                else:
                    for begin in comb:              # it always is a single value from the set
                        # when we have begin, we need to find combo of set length - 1 in which the begin isnt there
                        subcomb = comb - frozenset({begin})     # this is how we get previous level combo we needed
                        prevCost = nodes[begin, subcomb][0]
                        cost = npcData[begin][finish].dist + prevCost
                        routes.append((cost, begin))
                    nodes[finish, comb] = min(routes)

    com = []
    for i, node in enumerate(reversed(dict(nodes))):
        if i < len(princesses):
            com.append((nodes.pop(node), node[0]))
        elif i == len(princesses):
            val, step = min(com)
            princesses -= {step}
            path = [step]
            cost, nextStep = val
            break
    
    for _ in range(len(princesses)):
        path.append(nextStep)
        princesses -= {nextStep}
        nextStep = nodes[nextStep, princesses][1]
    path.extend([dragon, start])

    return path[::-1], cost

def getPath(npcData, order):
    path = []

    for begin, finish in zip(order, order[1:]):
        path2 = []
        while finish != begin:
            path2.append(finish)
            finish = npcData[begin][finish].parent
        path.append(path2[::-1])

    return path

def printSolution(path):
    for i, road in enumerate(path, 1):
        print(f"\n{i}: ", end=' ')
        for step in road:
            print(step, end=' ')
    print()


def main():

    #mapData, princesses, dragon, start, adjacency = load("mapa8.txt")
    '''
    npcData = {p: dijkstra(copy.deepcopy(mapData), p, adjacency) for p in princesses}
    npcData.update({start: aStar(copy.deepcopy(mapData), start, dragon, adjacency)}) # can use A* for different purposes tho
    npcData.update({dragon: dijkstra(copy.deepcopy(mapData), dragon, adjacency)})

    print("Starting permutations")
    order, dist = findMinDist(npcData, princesses, dragon, start)
    path = getPath(npcData, order)
    printSolution(path)
    print("Cost: " + str(dist))

    print("Starting Kerp")
    order2, dist2 = karp(npcData, princesses, dragon, start)
    path2 = getPath(npcData, order2)
    printSolution(path2)
    print("Cost: " + str(dist2))

    ### ZEN GARDEN ###

    '''
    #query = "10x12 (1,5) (2,1) (3,4) (4,2) (6,8) (6,9)"
    query = "mapa11.txt"
    #query = "10x10 (12,2) (0,0)"

    mapList = declareMap(query)
    if not mapList:
        print("Invalid query!")
        return
    
    # ? Validation for correct mapList? I dont think its needed
    mapData = initEvoMap(mapList, True)
    if not mapData:
        print("Evo could not find a solution, try again.")
        return

    saveMap(mapData, 'yosh')
    mapData2 = loadMap('yosh')

    # SOLVING! PATH INC!
    a=1
    b=2


def loadMap(fileName):
    with open(fileName + '.txt') as f:
        return [list(map(int, line.rstrip('\n').split())) for line in f]

def saveMap(mapData, fileName):
    with open(fileName + '.txt', 'w') as f:
        for row in mapData:
            f.write(' '.join(map(str, row)) + '\n')

def declareMap(query):
    mapData = []

    # Load from string
    if re.search('[0-9]+x[0-9]+(\ \([0-9]+,[0-9]+\))+$', query):
        query = query.split()
        ROWS, COLS = map(int, query[0].split('x'))
        walls = {eval(coordinate) for coordinate in query[1:]}
        mapData = [[0] * COLS for _ in range(ROWS)]

        for wall in walls:
            try:
                mapData[wall[0]][wall[1]] = 1
            except IndexError as e:
                mapData = None

    # Load from file
    elif re.search('\.txt', query):
        with open(query) as f:
            line = f.readline().rstrip()
            mapData.append([int(column) for column in line])
            prevLength = len(line)

            for line in f:
                line = line.rstrip()
                if prevLength != len(line):
                    mapData = None
                    break
                prevLength = len(line)
                mapData.append([int(column) for column in line])

    return mapData

def listToTuple(mapData):
    mapDate = {}
    for i, row in enumerate(mapData):
        for j, col in enumerate(row):
            mapDate[i, j] = mapData[i][j]

    return mapDate

def initEvoMap(mapList, printStats):
    mapTuple = listToTuple(mapList)
    mapTuple = {key: -mapTuple[key] for key in mapTuple.keys()}

    SHAPE = len(mapList), len(mapList[0])
    ROCKS = sum(val != 0 for val in mapTuple.values())
    TO_RAKE = SHAPE[0] * SHAPE[1] - ROCKS
    GENES = (SHAPE[0] + SHAPE[1]) * 2   # gene - an intruction (PERIMETER)
    CHROMOSOMES = 30                    # chromosome - solution that is defined by order of genes
    GENERATIONS = 100                   # generation - set of all chromozomes

    MIN_MUT_RATE = 0.05
    MAX_MUT_RATE = 0.80
    CROSS_RATE = 0.90

    startTime = time.time()
    generationTimes = []
    prevMax = 0
    foundSolution = False

    # generating chromozomes for one population/generation
    population = []
    genes = random.sample(range(1, GENES), GENES-1)
    for _ in range(CHROMOSOMES):
        random.shuffle(genes)
        chromosome = [num * random.choice([-1, 1]) for num in genes]
        population.append(chromosome)

    # loop of generations
    mutRate = MIN_MUT_RATE
    for i in range(GENERATIONS):
        genTime = time.time()
        
        # evaluate all chromosomes and find the best one
        fitness, fMax, jMax = [], 0, 0
        for j in range(CHROMOSOMES):
            unraked, filled = rakeGarden(population[j], copy.copy(mapTuple), SHAPE)
            raked = TO_RAKE - unraked
            fitness.append(raked)
            if raked > fMax:
                jMax, fMax, mMap = j, raked, filled

        if prevMax < fMax:
            print(f"Generation: {i+1},   Max raked: {fMax} (out of {TO_RAKE}),   Mutation rate: {round(mutRate, 2)}")
        if fMax == TO_RAKE:
            foundSolution = True
            break
        
        # increasing mutation each generation change to prevent local maximums
        mutRate = mutRate if mutRate >= MAX_MUT_RATE else mutRate + 0.01

        # loop for creating next generation, 1 iteration for 2 populations that we mutate
        children = []
        for i in range(0, CHROMOSOMES, 2):

            # pick 2 better chromosomes out of 4
            pick = random.sample(range(CHROMOSOMES), 4)
            better1 = pick[0] if fitness[pick[0]] > fitness[pick[1]] else pick[1]
            better2 = pick[2] if fitness[pick[2]] > fitness[pick[3]] else pick[3]

            # copying better genes to 2 child chromosomes
            children.extend([[],[]])
            for j in range(GENES-1):
                children[i].append(population[better1][j])
                children[i+1].append(population[better2][j])

            # mutating 2 chromosomes with uniform crossover (both inherit the same amount of genetic info)
            if random.random() < CROSS_RATE:
                for c in range(2):
                    for g in range(GENES-1):
                        if random.random() < mutRate:

                            # search for gene with mutNum number
                            mutNum = random.randint(1, GENES) * random.choice([-1, 1])
                            f = 0
                            for k, gene in enumerate(children[i+c]):
                                if gene == mutNum:
                                    f = k

                            # if found, swap it with g gene, if not, replace g with it
                            if f:
                                tmp = children[i+c][g]
                                children[i+c][g] = children[i+c][f]
                                children[i+c][f] = tmp
                            else:
                                children[i+c][g] = mutNum

        # keep the best chromosome for next generation
        for i in range(GENES-1):
            children[0][i] = population[jMax][i]

        population = children

        prevMax = fMax
        generationTimes.append(time.time() - genTime)

    # printing stats, solution and map
    if printStats:
        total = round(time.time() - startTime, 2)
        avg = round(sum(generationTimes) / len(generationTimes), 2) if generationTimes else total
        chromo = " ".join(map(str, population[jMax]))
        print("{} a solution!".format("Found" if foundSolution else "Couldn't find"))
        print(f"Total time elapsed is {total}s, each generation took {avg}s in average.")
        print(f"Chromosome: {chromo}")

        for row in mMap:
            for col in row:
                print("{0:2}".format(col), end=' ')
            print()

    return mMap if foundSolution else []

def rakeGarden(chromozome, mapTuple, SHAPE):
    ROWS, COLS = SHAPE[0], SHAPE[1]
    HALF_PERIMETER = SHAPE[0] + SHAPE[1]
    UNRAKED = 0

    order = 1
    for gene in chromozome:

        # get starting position and movement direction
        posNum = abs(gene)
        if posNum <= COLS:                         # go DOWN    <0, 20>
            pos, move = (0, posNum-1), (1, 0)
        elif posNum <= HALF_PERIMETER:             # go RIGHT   (20, 30>
            pos, move = (posNum-COLS-1, 0), (0, 1)
        elif posNum <= HALF_PERIMETER + ROWS:      # go LEFT    (30, 40>
            pos, move = (posNum-HALF_PERIMETER-1, COLS-1), (0, -1)
        else:                                      # go UP      <40, 60)
            pos, move = (ROWS-1, posNum-HALF_PERIMETER-ROWS-1), (-1, 0)
        
        # checking whether we can enter the garden with current pos
        if mapTuple[pos] == UNRAKED:
            parents = {}
            parent = 0

            # move until we reach end of the map 
            while 0 <= pos[0] < ROWS and 0 <= pos[1] < COLS:

                # collision to raked sand/rock
                if mapTuple[pos] != UNRAKED:
                    pos = parent            # get previous pos
                    parent = parents[pos]   # get previous parent
                    
                    # change moving direction
                    if move[0] != 0:    # Y -> X
                        right = pos[0], pos[1] + 1
                        left = pos[0], pos[1] - 1
                        rightBound = right[1] < COLS
                        leftBound = left[1] >= 0
                        rightRake = rightBound and mapTuple[right] == UNRAKED
                        leftRake = leftBound and mapTuple[left] == UNRAKED
                        right = rightBound and rightRake
                        left = leftBound and leftRake

                        if right and left:
                            move = (0, 1) if gene > 0 else (0, -1)
                        elif right:
                            move = 0, 1
                        elif left:
                            move = 0, -1
                        elif rightBound and leftBound:
                            move = False
                        else:
                            break

                    else:               # X -> Y
                        down = pos[0] + 1, pos[1]
                        up = pos[0] - 1, pos[1]
                        downBound = down[0] < ROWS
                        upBound = up[0] >= 0
                        downRake = downBound and mapTuple[down] == UNRAKED
                        upRake = upBound and mapTuple[up] == UNRAKED
                        down = downBound and downRake
                        up = upBound and upRake

                        if down and up:
                            move = (1, 0) if gene > 0 else (-1, 0)
                        elif down:
                            move = 1, 0
                        elif up:
                            move = -1, 0
                        elif downBound and upBound:
                            move = False
                        else:
                            break

                    # if we cant change direction, remove the path
                    if not move:
                        order -= 1
                        while parents[pos] != 0:
                            mapTuple[pos] = 0
                            pos = parents[pos]
                        mapTuple[pos] = 0
                        break

                mapTuple[pos] = order
                parents[pos] = parent
                parent = pos
                pos = pos[0]+move[0], pos[1]+move[1]

            order += 1

    filled = []
    unraked = 0
    j = -1
    for i, fill in enumerate(mapTuple.values()):
        if fill == UNRAKED:
            unraked += 1
        if i % COLS == 0:
            j += 1
            filled.append([])
        filled[j].append(fill)

    return unraked, filled

main()

#objs:
# read book for OOP class, agregation, etc.
# apply rules somehow and make simulation (would be better without resources, just moves)
# race of 3 playres in random positions

# modify held karp for shortest subset

# docstring, snowflake8 FIXING later (finalize)