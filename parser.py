from numpy import *


def addAdjacentToList(visited,libertyList,game,isWhite):
    """Recursively adds all adjacent pieces of the same color to
    'visited', given a list, libertyList, of pieces to start with."""

    
    if libertyList == []:
        return
    newLibertyList = []
    for gridLocation in libertyList:
        x,y = gridLocation
        for i in (-1,1):
            tmpx = x+i
            if (tmpx,y) not in visited and tmpx<19 and tmpx>=0 and game[tmpx][y] == -isWhite:
                newLibertyList.append((tmpx,y))
                visited.add((tmpx,y))
        for j in (-1,1):
            tmpy = y+j
            if (x,tmpy) not in visited and tmpy<19 and tmpy>=0 and game[x][tmpy] == -isWhite:
                newLibertyList.append((x,tmpy))
                visited.add((x,tmpy))

    addAdjacentToList(visited,newLibertyList,game,isWhite)



                
def hasLiberties(libertyList,game):
    """Given a list of pieces, determines if any of them touch
    an empty space."""
    
    if len(libertyList)==0:
        return True
    for gridLocation in libertyList:
        x,y = gridLocation
        for i in (-1,1):
            tmpx = x+i
            if tmpx<19 and tmpx>=0 and game[tmpx][y] == 0:
                return True
        for j in (-1,1):
            tmpy = y+j
            if tmpy<19 and tmpy>=0 and game[x][tmpy] == 0:
                return True
    return False

def removeStones(libertyList,game):
    """Removes stones that have been captured."""
    for gridLocation in libertyList:
        x,y = gridLocation
        game[x][y] = 0


def printGame(game):
    """Displays the game with text. X's are black, O's are white.
    Make the shell fullscreen before printing to make sure it displays correctly."""
    game = game[0]
    for i in range(19):
        for j in game[:,i]:
            if j == 1:
                print ' O  ',
            elif j==-1:
                print ' X  ',
            else:
                print '____',
        print '\n'
        



#For interpreting the position of a piece from the sgf file.
labels = {
    'a':0,
    'b':1,
    'c':2,
    'd':3,
    'e':4,
    'f':5,
    'g':6,
    'h':7,
    'i':8,
    'j':9,
    'k':10,
    'l':11,
    'm':12,
    'n':13,
    'o':14,
    'p':15,
    'q':16,
    'r':17,
    's':18,
    }

def createArray(fileName):
    """ Creates a sequential list of tuples containing:
            -An array representing the game board at move i
                -Piece representation is:
                   - Black:-1, White:1, Blank:0
            -The location of the newly placed piece"""


    #with open (fileName, "r") as myfile:


    with open ("/home/stevengt/Downloads/kombilo/databases/kgs-19-2014-04-new/" \
               "2014-04-01-8.sgf", "r") as myfile:
        data=myfile.read().replace('\n', '')

    readingFileInfo = True
    readingGameInfo = False
    currentIndex = 2
    while readingFileInfo:
        currentChar = data[currentIndex]
        if currentChar is 'A':
            currentIndex+=1
            currentChar = data[currentIndex]
            if currentChar is 'B' or currentChar is 'W': #If pieces are already on board
                return None
            continue
        if currentChar is ';':
            readingFileInfo = False
            readingGameInfo = True
        currentIndex += 1

    listOfGamePositions = []
    currentGameMove = 0


    while readingGameInfo:
        currentIndex+=1
        if data[currentIndex] is ')':
            readingGameInfo = False
        if data[currentIndex] is '[':
            currentIndex+=1
            x = labels[data[currentIndex]]
            currentIndex+=1
            y = labels[data[currentIndex]]
            if currentGameMove != 0:
                libertyList = []
                visited = set()      
                newGame = listOfGamePositions[currentGameMove-1][0].copy()

                if currentGameMove%2 == 0:
                    isWhite = -1
                else:
                    isWhite = 1

                newGame[x][y] = isWhite
                
                for i in (-1,1):
                    tmpx = x+i
                    if tmpx<19 and tmpx>=0 and newGame[tmpx][y] == -isWhite:
                        libertyList.append((tmpx,y))
                        visited.add((tmpx,y))
                for j in (-1,1):
                    tmpy = y+j
                    if tmpy<19 and tmpy>=0 and newGame[x][tmpy] == -isWhite:
                        libertyList.append((x,tmpy))
                        visited.add((x,tmpy))
                        
                
                addAdjacentToList(visited,libertyList,newGame,isWhite)

                if hasLiberties(visited,newGame)==False:
                    removeStones(visited,newGame)
                
                
                listOfGamePositions.append((newGame,(x,y)))
            else:
                newGame = zeros((19,19))
                newGame[x][y] = -1
                listOfGamePositions.append((newGame,(x,y)))
            currentGameMove += 1

    return listOfGamePositions


def getPlaquettes(board):
    """Gets all 3x3 plaquettes in any given game instance."""
    plaquettes = zeros((17,17,3,3))
    for i in range(17):
        for j in range(17):
            newPlaquette = zeros((3,3))
            for m in range(3):
                for n in range(3):
                    newPlaquette[m][n] = board[i+m][j+n]
            plaquettes[i][j] = newPlaquette
    return plaquettes


def getRelations(listOfMoves,listOfPlaquettes,adjacencyMatrix):
    """For any sequence of two moves, find all mappings between
    the current plaquette and all plaquettes within distance 4 in the
    next move. Increase the weights of these mappings in the
    adjacency matrix by 1."""
#    inpages = dict()
#    outpages = dict()
    for i in xrange(len(listOfMoves)-1):
        print i
        move1 = listOfMoves[i][0].copy()
        move2 = listOfMoves[i+1][0].copy()
        pieceLocationX,pieceLocationY = listOfMoves[i+1][1]
        if move2[pieceLocationX][pieceLocationY]==-1:
            move1 = getPlaquettes(move1)
            move2 = getPlaquettes(move2)
            for m in range(17):
                for n in range(17):
                    current = tuple([tuple(row) for row in move1[m][n]])
                    if current in listOfPlaquettes:
                        current = listOfPlaquettes[current]
                    else:
                        continue
                    distance = range(-4,5)
                    for dist1 in distance:
                        for dist2 in distance:
                            tmpx = m + dist1
                            tmpy = n + dist2
                            if (tmpx>=0 and tmpx<17 and (dist1!=0 or dist2!=0)
                                    and tmpy>=0 and tmpy<17):
                                relatedMove = tuple([tuple(row) for row in move2[tmpx][tmpy]])
                                if relatedMove in listOfPlaquettes:
                                    relatedMove = listOfPlaquettes[relatedMove]
                                    adjacencyMatrix[current][relatedMove]+=1


#------------ for pagerank---------------------
                                    #if relatedMove in outpages:
                                        #outpages[relatedMove] = 0
                                    #else:
                                        #outpages[relatedMove] = 0
                                    #if relatedMove not in inpages:
                                        #inpages[relatedMove] = [current]
                                    #else:
                                        #inpages[relatedMove] = inpages[relatedMove] + [current]
 #   return inpages,outpages
 #-----------------------------------------------
    return adjacencyMatrix


                            




def getFromList(listItem):
    """Converts hashable tuple to array."""
    return array([row for row in listItem])

def addToList(listItem,theList):
    """Converts array to hashable tuple."""
    theList.add(tuple([tuple(row) for row in listItem]))


def findPlaquettes():
    """Finds all possible 3x3 plaquettes with an empty center and
    assigns each of them a unique value."""
    listOfPlaquettes = set()
    mapping = dict()

    for k in range(-1,2):
        new = zeros((3,3))
        new[0][0] = k
        addToList(new,listOfPlaquettes)

    
    for i in range(3):
        for j in range(3):
            if (i != 1 or j!=1) and (i!=0 or j!=0):
                newList = set()
                for plaquette in listOfPlaquettes:
                    plaquette = getFromList(plaquette)
                    for k in range(-1,2):
                        new = plaquette.copy()
                        new[i][j]=k
                        addToList(new,newList)
                listOfPlaquettes = listOfPlaquettes | newList
                
    for i,plaquette in enumerate(listOfPlaquettes):
        mapping[plaquette]=i # should this be mapping[i] = plaquettes ?

    dim = len(mapping)
    adjacencyMatrix = zeros((dim,dim))
    return (mapping,adjacencyMatrix)










# Pagerank code --------------------------------------------------------------

from math import log, pow, floor

def getSinks(outpages):
    return filter(lambda x: outpages[x] == 0, outpages)

def preplexity(pr):
    preplex = 0
    for page in pr:
        preplex += pr[page] * log(1.0/pr[page], 2)
    return pow(2, preplex)

def preplexfour(preplex):
    prep = map(lambda x: floor(x), preplex)
    prep0 = prep[0]
    prep = map(lambda x: x == prep0, prep)
    return len(prep) >= 4 and all(prep)

def loadFile(path):
    inpages = {}
    outpages = {}
    with open(path) as f:
        for line in f:
            splits = line.split(' ')
            splits = filter(lambda x: x != '\n', splits)
            splits = map(lambda x: x.replace('\n',''), splits)
            page = splits[0]
            if page in inpages:
                inpages[page] = inpages[page] + splits[1:]
            else:
                inpages[page] = splits[1:]
            if not page in outpages:
                outpages[page] = 0
            for inpage in splits[1:]:
                if inpage in outpages:
                    outpages[inpage] += 1
                else:
                    outpages[inpage] = 1
    print inpages
    return (inpages, outpages)

def pageRank(inpages, outpages):
    pageRank = {}
    sinkpages = getSinks(outpages)
    N = len(inpages)
    d = 0.85
    idx = 0
    preplex = []

    for page in inpages:
        pageRank[page] = 1.0/N
    
    prep = preplexity(pageRank)
    preplex = preplex + [prep]

    while not preplexfour(preplex[-4:]):
        newPR = {}
        sinkPR = 0
        for sink in sinkpages:
            sinkPR += pageRank[sink]
        for page in inpages:
            newPR[page] = (1.0-d)/N
            newPR[page] += d*sinkPR/N
            for inlink in inpages[page]:
                newPR[page] += d* pageRank[inlink]/outpages[inlink]
        for page in newPR:
            pageRank[page] = newPR[page]
        idx += 1
        prep = preplexity(pageRank)
        preplex = preplex + [prep]
                    
    for prep in preplex:
        print prep
    return pageRank

def main():
    #i,o = loadFile('wt2g_inlinks')
    pr = pageRank(i,o)
    pra = []
    for page in pr:
        pra = pra + [(page, pr[page])]
    spra = sorted(pra, key=lambda x: x[1])
    #for p,r in spra[-10:]:
     #   print p, r



#-----------------------------------------------------------------------------


listOfPlaquettes,adjacencyMatrix = findPlaquettes()
a = createArray("")
printGame(a[-1])
b = getRelations(a,listOfPlaquettes,adjacencyMatrix)

#row_sums = adjacencyMatrix.sum(axis=1)
#new_matrix = adjacencyMatrix / row_sums[:,newaxis]
##
##pr = pageRank(b[0],b[1])
##pra = []
##for page in pr:
##    pra = pra + [(page, pr[page])]
##spra = sorted(pra, key=lambda x: x[1])







