# PyAgent.py
import Action
import Orientation
from queue import Queue

class Room:
    # The agent correctly models the initial probabilities of Pits and Wumpus locations
    def __init__(self):
        self.pit = 0.2
        self.wumpus = 0.06
        self.visited = False

    def setPit(self, pit):
        self.pit = pit

    def setWumpus(self, wumpus):
        self.wumpus = wumpus

    def setVisit(self):
        self.visited = True

    def getPit(self):
        return self.pit

    def getWumpus(self):
        return self.wumpus

    def getVisit(self):
        return self.visited

# The agent uses a model to track state representation  
#   12  13  14  15 
#   8   9   10  11
#   4   5   6   7
#   0   1   2   3
world = [Room(), Room(), Room(), Room(), Room(), Room(), Room(), Room(), Room(), Room(), Room(), Room(), Room(), Room(), Room(), Room()]

# Square above = +4
# Square below = -4
# Square Right = +1
# Square Left = -1 
move_queue = Queue(maxsize = 5)
current_room = 0
current_orientation = Orientation.RIGHT
hasGold = False

possible_pits = []



def PyAgent_Constructor():
    """ PyAgent_Constructor: called at the start of a new trial """
    print("PyAgent_Constructor")


def PyAgent_Destructor():
    """ PyAgent_Destructor: called after all tries for a trial are complete """
    print("PyAgent_Destructor")


def PyAgent_Initialize():
    """ PyAgent_Initialize: called at the start of a new try """
    print("PyAgent_Initialize")


def PyAgent_Process(stench, breeze, glitter, bump, scream):
    """ PyAgent_Process: called with new percepts after each action to return the next action """

    global world
    global hasGold
    global current_room

    while (not move_queue.empty()):
        return move_queue.get()

    world[current_room].setPit(0)
    world[current_room].setWumpus(0)
    world[current_room].setVisit()

    Calculate_Pits(breeze)
    Calculate_Wumpus(stench)
    
    if (glitter == 1):
        hasGold = True
        return Action.GRAB

    Calculate_BestMove()


    printStats(stench, breeze, glitter, bump, scream)

    i = 0
    for x in world:
        print(i, x.getPit(), x.getWumpus())
        i+=1

    return move_queue.get()


def PyAgent_GameOver(score):
    """ PyAgent_GameOver: called at the end of each try """
    print("PyAgent_GameOver: score = " + str(score))


# The agent updates the pit probabilities as it gains new evidence
def Calculate_Pits(breeze):
    global possible_pits
    global world

    current_affected = Get_AffectedRooms()

    for x in current_affected:
        possible_pits.append(x)
    
    if (breeze == 0):
        for x in current_affected:
            world[x].setPit(0)
    else:
        if (len(current_affected) == 2):
            x = current_affected[0]
            y = current_affected[1]

            probx = world[x].getPit()
            proby = world[y].getPit()

            a = probx * 1 - proby
            b = proby * 1 - probx
            c = probx * proby

            if (probx != 0 and probx != 1):
                world[x].setPit(a + c / a + b + c)
            if (proby != 0 and proby != 1):
                world[y].setPit(b + c / a + b + c)

        else:
            x = current_affected[0]
            y = current_affected[1]
            z = current_affected[2]

            probx = x.getPit()
            proby = y.getPit()
            probz = z.getPit()

            a = probx * 1 - proby * 1 - probz   #   X   -   a
            b = 1 - probx * proby * 1 - probz   #   Y   -   b
            c = 1 - probx * 1 - proby * probz   #   Z   -   c
            d = probx * proby * 1 - probz       #   XY  -   d
            e = probx * 1 - proby * probz       #   XZ  -   e
            f = 1 - probx * proby * probz       #   YZ  -   f
            g = probx * proby * probz           #   XYZ -   g

            total = a + b + c + d + e + f + g
            
            if (probx != 0 and probx != 1):
                world[x].setPit(a + d + e + g / total)
            if (proby != 0 and proby != 1):
                world[y].setPit(b + d + f + g / total)
            if (probz != 0 and proby != 1):
                world[z].setPit(c + e + f + g / total)

# The agent updated Wumpus probabilities as it gains new evidence
def Calculate_Wumpus(stench):
    global world

    current_affected = Get_AffectedRooms()

    if (stench == 0):
        for x in current_affected:
            world[x].setWumpus(0)
    else:
        if (len(current_affected) == 2):
            x = current_affected[0]
            y = current_affected[1]

            probx = world[x].getWumpus()
            proby = world[y].getWumpus()

            a = probx * 1 - proby
            b = proby * 1 - probx

            if (probx != 0 and probx != 1 and a+b != 0):
                world[x].setWumpus(a / a + b)
            if (proby != 0 and proby != 1 and a+b != 0):
                world[y].setWumpus(b / a + b)

        else:
            x = current_affected[0]
            y = current_affected[1]
            z = current_affected[2]

            probx = x.getWumpus()
            proby = y.getWumpus()
            probz = z.getWumpus()

            a = x * 1 - y * 1 - z
            b = 1 - x * y * 1 - z
            c = 1 - x * 1 - y * z

            total = a + b + c
            
            if (probx != 0 and probx != 1 and total != 0):
                world[x].setWumpus(a / total)
            if (proby != 0 and proby != 1 and total != 0):
                world[y].setWumpus(b / total)
            if (probz != 0 and proby != 1 and total != 0):
                world[z].setWumpus(c / total)

def Calculate_BestMove():
    global world
    global current_orientation
    global current_room

    if (current_orientation == Orientation.LEFT and world[current_room - 1].getPit() < .5):
        move_queue.put(Action.GOFORWARD)
        return
    elif (current_orientation == Orientation.UP and world[current_room + 4].getPit() < .5):
        move_queue.put(Action.GOFORWARD)
        return
    elif (current_orientation == Orientation.RIGHT and world[current_room + 1].getPit() < .5):
        move_queue.put(Action.GOFORWARD)
        return
    elif (current_orientation == Orientation.DOWN and world[current_room - 4].getPit() < .5):
        move_queue.put(Action.GOFORWARD)
        return

    current_affected = Get_AffectedRooms()

    probs = []
    
    for x in current_affected:
        probs.append(x, x.getPit() + x.getWumpus())

    prevBestVisit = (-1, 1)
    prevBestNew = (-1, 1)
    for y in probs:
        if (y[1] < prevBestNew[1] and not world[y[0]].getVisit()):
            prevBestNew = y
        elif (y[1] < prevBestVisit[1] and world[y[0]].getVisit()):
            prevBestVisit = y
        
    if (prevBestNew[1] < .5):
        Move(prevBestNew[0]) 
    else:
        Move(prevBestVisit[0])

    

def Move(newRoom):
    global move_queue
    # Move West
    if (newRoom == current_room - 1):
        if (current_orientation == Orientation.LEFT):
            move_queue.put(Action.GOFORWARD)
        elif (current_orientation == Orientation.UP):
            MoveLeft()
        elif (current_orientation == Orientation.RIGHT):
            MoveBack()
        elif (current_orientation == Orientation.DOWN):
            MoveRight()
    # Move North
    if (newRoom == current_room + 4):
        if (current_orientation == Orientation.LEFT):
            MoveRight()
        elif (current_orientation == Orientation.UP):
            move_queue.put(Action.GOFORWARD)
        elif (current_orientation == Orientation.RIGHT):
            MoveLeft()
        elif (current_orientation == Orientation.DOWN):
            MoveBack()
    # Move East
    if (newRoom == current_room + 1):
        if (current_orientation == Orientation.LEFT):
            MoveBack()
        elif (current_orientation == Orientation.UP):
            MoveRight()
        elif (current_orientation == Orientation.RIGHT):
            move_queue.put(Action.GOFORWARD)
        elif (current_orientation == Orientation.DOWN):
            MoveLeft()
    # Move South
    if (newRoom == current_room - 4):
        if (current_orientation == Orientation.LEFT):
            MoveLeft()
        if (current_orientation == Orientation.UP):
            MoveBack()
        if (current_orientation == Orientation.RIGHT):
            MoveRight()
        elif (current_orientation == Orientation.DOWN):
            move_queue.put(Action.GOFORWARD)


def Get_AffectedRooms():
    rightEdge = [3, 7, 11, 15]
    leftEdge = [0, 4, 8, 12]
    global world
    global current_room

    current_affected = []

    if (current_room + 4 < 16):
        if (world[current_room + 4].getWumpus() != 0):
            current_affected.append(current_room + 4)
    if (current_room - 4 > 0):
        if (world[current_room - 4].getWumpus() != 0):
            current_affected.append(current_room - 4)
    if (current_room + 1 < 16 and current_room + 1 not in leftEdge):
        if (world[current_room + 1].getWumpus() != 0):
            current_affected.append(current_room + 1)
    if (current_room - 1 > 0 and current_room - 1 not in rightEdge):
        if (world[current_room - 1].getWumpus() != 0):
            current_affected.append(current_room - 1)

    print("Current Affected:")
    for x in current_affected:
        print(x)

    return current_affected


def MoveLeft():
    global move_queue
    global current_room
    move_queue.put(Action.TURNLEFT)
    move_queue.put(Action.GOFORWARD)
    current_room -= 1

def MoveRight():
    global move_queue
    global current_room
    move_queue.put(Action.TURNRIGHT)
    move_queue.put(Action.GOFORWARD)
    current_room -= 1
    

def MoveBack():
    global move_queue
    global current_room
    move_queue.put(Action.TURNLEFT)
    move_queue.put(Action.TURNLEFT)
    move_queue.put(Action.GOFORWARD)
    current_room -= 1

def printStats(stench, breeze, glitter, bump, scream):

    percept_str = ""
    if stench == 1:
        percept_str += "Stench=True,"
    else:
        percept_str += "Stench=False,"
    if breeze == 1:
        percept_str += "Breeze=True,"
    else:
        percept_str += "Breeze=False,"
    if glitter == 1:
        percept_str += "Glitter=True,"
    else:
        percept_str += "Glitter=False,"
    if bump == 1:
        percept_str += "Bump=True,"
    else:
        percept_str += "Bump=False,"
    if scream == 1:
        percept_str += "Scream=True"
    else:
        percept_str += "Scream=False"
    
    print("PyAgent_Process: " + percept_str)