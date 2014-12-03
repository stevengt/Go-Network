import pickle
from numpy import *


def flipHorizontal(a):
    m = a.copy()
    return flipud(m)

def flipVertical(a):
    m = a.copy()
    return fliplr(m)

def rotateLeft(a):
    m = a.copy()
    return rot90(m)

def rotate180(a):
    m = a.copy()
    return rot90(m,2)

def rotateRight(a):
    m = a.copy()
    return rot90(m,3)

def swapColors(a):
    m = a.copy()
    for i in range(3):
        for j in range(3):
            m[i][j]= -1*a[i][j]
    return m

def isSymmetric(new,plaquette):

    if array_equal(new,plaquette):
        return True
    if array_equal(swapColors(new),plaquette):
        return True
    if array_equal(flipHorizontal(new),plaquette):
        return True
    if array_equal(flipVertical(new),plaquette):
        return True
    if array_equal(rotateLeft(new),plaquette):
        return True
    if array_equal(rotate180(new),plaquette):
        return True
    if array_equal(rotateRight(new),plaquette):
        return True

    colorsSwapped = swapColors(new)

    if array_equal(rotateLeft(colorsSwapped),plaquette):
        return True
    if array_equal(rotate180(colorsSwapped),plaquette):
        return True
    if array_equal(rotateRight(colorsSwapped),plaquette):
        return True
    if array_equal(flipHorizontal(colorsSwapped),plaquette):
        return True
    if array_equal(flipVertical(colorsSwapped),plaquette):
        return True
    
    return False


def printTenPlaquettes(eigvec, plaquetteDict):
    movePairs = [(i,val) for i,val in enumerate(eigvec)]
    movePairs.sort(key=lambda x: x[1])
    movePairs.reverse()
    uniquePlaquettes = set()

    numUnique = 0
    numVisited = 0
    
    while len(uniquePlaquettes) <= 10:
        index,value = movePairs[numVisited]
        plaquette = plaquetteDict[index]
        plaquette = getFromList(plaquette)
        newPlaquettes = set()

        flag = False

        for visitedPlaquette in uniquePlaquettes:
            visitedPlaquette = getFromList(visitedPlaquette)
            if isSymmetric(plaquette,visitedPlaquette):
                flag = True
                break
            else:
                addToList(plaquette,newPlaquettes)
        if flag:
            numVisited += 1
            continue
        if len(uniquePlaquettes) == 0:
            addToList(plaquette,newPlaquettes)
        
        plaquetteString = ""
        for i in range(3):
            for j in range(3):
                if (plaquette[i][j] == -1):
                    plaquetteString += " X "
                elif (plaquette[i][j] == 0):
                    plaquetteString += " _ "
                elif (plaquette[i][j] == 1):
                    plaquetteString += " O "
            plaquetteString += "\n"

        uniquePlaquettes = uniquePlaquettes | newPlaquettes
        print plaquetteString


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

listOfPlaquettes,reverseMapping,adjacencyMatrix = findPlaquettes()
vector = pickle.load( open( "1.p", "rb" ) )
printTenPlaquettes(vector, reverseMapping)


