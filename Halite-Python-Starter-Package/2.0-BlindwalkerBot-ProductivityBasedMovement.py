from hlt import *
from networking import *
import logging
from decimal import Decimal, ROUND_CEILING

logging.basicConfig(filename='Blindbot2.0.log',level=logging.DEBUG)

myID, gameMap = getInit()
sendInit("BlindwalkerBot-2.0")

#Return a dictionary of lists containing sites that are most productive
def analyzeMap(gameMap):
    logging.debug("In analyzeMap")
    productivityDictionary = {}

    productivityRatio = 0
    for y in range(gameMap.height):
        for x in range(gameMap.width):
            location = Location(x, y)
            site = gameMap.getSite(location)
            if(site.owner != myID):
                if(site.strength != 0):
                    productivityRatio = '%.5f'%(Decimal(site.production)/Decimal(site.strength))
                else:
                    productivityRatio = 9.999
                try:
                    productivityDictionary[str(productivityRatio)].append(location)
                except KeyError:
                    ratioList = []
                    ratioList.append(location)
                    productivityDictionary[str(productivityRatio)] = ratioList
    return productivityDictionary

def weightByProductivity(gameMap, site, location, weightedDirections, productivityDictionary):
    for ratio in productivityDictionary:
        for tar_location in productivityDictionary[ratio]:
            target = tar_location
            break
        break
    radian = gameMap.getAngle(location, target)
    #Radians:
    #If 0 starts on the right of origin:
    #-pi/pi=180
    #pi/2 = 90 (north)
    #-pi/2 = 270 (south)

    #pi = 3.141
    #3pi/4 = 2.356
    #pi/2 = 1.570
    #pi/4 = 0.785
    radian = Decimal(radian)

    if(radian >= .785 and radian < 2.356):
        weightedDirections[NORTH] = (weightedDirections[NORTH]+100) * 1
    elif (radian >= -.785 and radian < .785):
        weightedDirections[EAST] = (weightedDirections[EAST]+100) * 1
    elif (radian >=-2.356 and radian < -.785):
        weightedDirections[SOUTH] = (weightedDirections[SOUTH]+100) * 1
    else:
        weightedDirections[WEST] = (weightedDirections[WEST]+100) * 1
    return weightedDirections

def unweighted(weightedDirections):
    unweighted = 0
    for direction in weightedDirections:
        if weightedDirections[direction] == 0:
            unweighted += 1
    if unweighted == 5:
        return True

def identifyNeighbors(location):
    logging.debug("In identifyNeighbors")
    neighbors = {}
    for direction in CARDINALS:
        neighbour_site = gameMap.getSite(location, direction)
        if(neighbour_site.owner != myID):
            neighbors[direction] = "E"
        else:
            neighbors[direction] = "A"
    return neighbors

#Adjusts weighting based on neighbors - this is the primary weight. This handles the frontier expansion
def weightByNeighbors(site, location, weightedDirections):
    logging.debug("In weightByNeighbors")
    neighbors = identifyNeighbors(location)
    numAllies = 0
    numEnemies = 0
    enemies = {}
    for direction in neighbors:
        if neighbors[direction] is "A":
            numAllies+=1
        else:
            enemies[direction] = gameMap.getSite(location,direction).strength
            numEnemies+=1

    for direction in enemies:
        logging.debug("Site: " + str(site.strength) + " Enemy: " + str(enemies[direction]))
        if(site.strength > enemies[direction]):
            weightedDirections[direction]+=1000
        else:
            #If weaker than a side, encourage standing still slightly
            weightedDirections[STILL]+=10
    return weightedDirections

#Calculates weights for each direction
def calculateDirection(gameMap, site,location, productivityDictionary):
    logging.debug("In directionLogic")
    weightedDirections = {0:0,1:0,2:0,3:0,4:0}

    #If no strength, ALWAYS stay still
    if(site.strength == 0):
        weightedDirections[STILL]+= 100
        return weightedDirections
    weightedDirections = weightByNeighbors(site, location, weightedDirections)

    #Only one reason why there would be unweighted directions - all sides are allies
    if(unweighted(weightedDirections)):
        #Encourage staying still based on strength
        weightedDirections[STILL]+=255-site.strength
        weightedDirections = weightByProductivity(gameMap, site, location, weightedDirections, productivityDictionary)

        weightedDirections[random.choice(DIRECTIONS)]+=150
    return weightedDirections

#Determines which direction is most heavily weighted 
def decideDirection(gameMap, location, productivityDictionary):
    logging.debug("In calculateDirection")
    site = gameMap.getSite(location)
    weightedDirections = calculateDirection(gameMap, site, location, productivityDictionary)
    #Return the heaviest weighted direction
    heaviestWeight = weightedDirections[STILL];
    targetDirection = STILL
    if(weightedDirections[NORTH] > heaviestWeight):
        heaviestWeight = weightedDirections[NORTH]
        targetDirection = NORTH
    elif(weightedDirections[SOUTH] > heaviestWeight):
        heaviestWeight = weightedDirections[SOUTH]
        targetDirection = SOUTH
    elif(weightedDirections[EAST] > heaviestWeight):
        heaviestWeight = weightedDirections[EAST]
        targetDirection = EAST
    elif(weightedDirections[WEST] > heaviestWeight):
        heaviestWeight = weightedDirections[WEST]
        targetDirection = WEST
    return targetDirection

while True:
    moves = []
    gameMap = getFrame()

    productivityDictionary = analyzeMap(gameMap)

    for y in range(gameMap.height):
        for x in range(gameMap.width):
            location = Location(x, y)
            if gameMap.getSite(location).owner == myID:
                direction = decideDirection(gameMap,location, productivityDictionary)
                moves.append(Move(location, direction))
    sendFrame(moves)
