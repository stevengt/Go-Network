

import os
import pickle
import scipy.linalg as la
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
    Make the shell fullscreen before printing to make sure it
    displays correctly."""
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

    try:
        with open (fileName, "r") as myfile:
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

        return listOfGamePositions[0::2] #returns all black moves
    
    except:
        return None

def getPlaquette(board,position):
    """Gets plaquette with given position at the center."""
    plaquette = zeros((3,3))
    x,y = position
    for i in range(-1,2):
        for j in range(-1,2):
            tmpx = x+i
            tmpy = y+j
            if tmpx>18 or tmpx<0 or tmpy>18 or tmpy<0:
                plaquette[i+1][j+1]=0
            else:
		plaquette[i+1][j+1] = board[tmpx][tmpy]
    return plaquette


def getRelations(listOfMoves,listOfPlaquettes,adjacencyMatrix):
    """For any sequence of two moves, find the mapping between
    them in the adjacency matrix and increase its weight by 1
    if they are less than 4 distance away from each other."""

    for i in xrange(len(listOfMoves)-1):
        move1 = listOfMoves[i][0].copy()
        move2 = listOfMoves[i+1][0].copy()

        x1,y1 = listOfMoves[i][1]
        x2,y2 = listOfMoves[i+1][1]

        if x2<=x1+4 and x2>=x1-4 and y2<=y1+4 and y2>=y1-4: 
                            
            move1 = getPlaquette(move1,listOfMoves[i][1])
            move2 = getPlaquette(move2,listOfMoves[i+1][1])

	    move1[1][1] = 0
	    move2[1][1] = 0		
		
            current = tuple([tuple(row) for row in move1])
            current = listOfPlaquettes[current]
            relatedMove = tuple([tuple(row) for row in move2])
            relatedMove = listOfPlaquettes[relatedMove]
            adjacencyMatrix[current][relatedMove]+=1

    return adjacencyMatrix


                            




def getFromList(listItem):
    """Converts hashable tuple to array."""
    return array([row for row in listItem])

def addToList(listItem,theList):
    """Converts array to hashable tuple."""
    theList.add(tuple([tuple(row) for row in listItem]))


def findPlaquettes():
    """Finds all possible 3x3 plaquettes with an empty center 
    and assigns each of them a unique value."""
    listOfPlaquettes = set()
    mapping = dict()
    reverseMapping = dict()

    for k in range(-1,2):
        new = zeros((3,3))
        new[0][0] = k
        addToList(new,listOfPlaquettes)

    
    for i in range(3):
        for j in range(3):
            if (i!=0 or j!=0) and (i!=1 or j!=1):
                newList = set()
                for plaquette in listOfPlaquettes:
                    plaquette = getFromList(plaquette)
                    for k in range(-1,2):
                        new = plaquette.copy()
                        new[i][j]=k
                        addToList(new,newList)
                listOfPlaquettes = listOfPlaquettes | newList
                
    for i,plaquette in enumerate(listOfPlaquettes):
        mapping[plaquette]=i
	reverseMapping[i]=plaquette

    dim = len(mapping)
    adjacencyMatrix = zeros((dim,dim))
    return (mapping,reverseMapping,adjacencyMatrix)

i=0
listOfPlaquettes,reverseMapping,adjacencyMatrix = findPlaquettes()
directoryName = "/home/stevengt/Downloads/kombilo/databases/database"
print len(adjacencyMatrix)
for fileName in os.listdir(directoryName):
    a = createArray(directoryName+"/"+fileName)
    if a is not None:
        adjacencyMatrix = getRelations(a,listOfPlaquettes,adjacencyMatrix)
        print "%20s     %d" % (fileName,i)
        i += 1
print len(adjacencyMatrix)
temp = zeros((len(adjacencyMatrix)))

for indexI,i in enumerate(adjacencyMatrix):
    if array_equal(i,temp):
        for indexJ,j in enumerate(i):
            adjacencyMatrix[indexI][indexJ]=1.0

for indexI,i in enumerate(adjacencyMatrix):
    rowSum = sum(i)
    for indexJ,j in enumerate(i):
        adjacencyMatrix[indexI][indexJ] = adjacencyMatrix[indexI][indexJ]/float(rowSum)

size = len(adjacencyMatrix)
alpha = 0.85



adjacencyMatrix = alpha*adjacencyMatrix+(1-alpha)/size

adjacencyMatrix = adjacencyMatrix.T

googleMatrix = adjacencyMatrix

v,w = la.eig(googleMatrix)

pickle.dump( v, open( "v.p", "wb" ) )
pickle.dump( w, open( "w.p", "wb" ) )





