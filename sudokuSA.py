import random
import numpy as np
import math
from random import choice
from datetime import datetime

# Izmaksu funkcija
def AprekinatKluduSkaitu(sudoku):
    numberOfErrors = 0

    numberOfErrors += 9 - len(np.unique(np.diagonal(sudoku)))  # Dilstoša diagonāle
    numberOfErrors += 9 - len(np.unique(np.diagonal(np.fliplr(sudoku))))  # Augoša diagonāle

    for i in range(0, 9):
        numberOfErrors += 9 - len(np.unique(sudoku[:, i]))  # Kolonna
        numberOfErrors += 9 - len(np.unique(sudoku[i, :]))  # Rinda
    return numberOfErrors


def FiksetSudokuVertibas(fixedSudoku):
    for i in range(0, 9):
        for j in range(0, 9):
            if fixedSudoku[i, j] != 0:
                fixedSudoku[i, j] = 1

    return fixedSudoku


def Izveidot3x3Blokus():
    finalListOfBlocks = []
    for r in range(0, 9):
        tmpList = []
        block1 = [i + 3 * ((r) % 3) for i in range(0, 3)]
        block2 = [i + 3 * math.trunc((r) / 3) for i in range(0, 3)]
        for x in block1:
            for y in block2:
                tmpList.append([x, y])
        finalListOfBlocks.append(tmpList)
    return finalListOfBlocks


def Aizpilditl3x3Blokus(sudoku, listOfBlocks):
    for block in listOfBlocks:
        for box in block:
            if sudoku[box[0], box[1]] == 0:
                currentBlock = sudoku[block[0][0]:(block[-1][0] + 1), block[0][1]:(block[-1][1] + 1)]
                sudoku[box[0], box[1]] = choice([i for i in range(1, 10) if i not in currentBlock])
    return sudoku


def BlokaSumma(sudoku, oneBlock):
    finalSum = 0
    for box in oneBlock:
        finalSum += sudoku[box[0], box[1]]
    return (finalSum)


def IzveletiesDivusNejaususBlokaLaukus(fixedSudoku, block):
    while (1):
        firstBox = random.choice(block)
        secondBox = choice([box for box in block if box is not firstBox])

        if fixedSudoku[firstBox[0], firstBox[1]] != 1 and fixedSudoku[secondBox[0], secondBox[1]] != 1:
            return ([firstBox, secondBox])


def SamainitLaukus(sudoku, boxesToFlip):
    proposedSudoku = np.copy(sudoku)
    placeHolder = proposedSudoku[boxesToFlip[0][0], boxesToFlip[0][1]]
    proposedSudoku[boxesToFlip[0][0], boxesToFlip[0][1]] = proposedSudoku[boxesToFlip[1][0], boxesToFlip[1][1]]
    proposedSudoku[boxesToFlip[1][0], boxesToFlip[1][1]] = placeHolder
    return (proposedSudoku)


def PiedavataisStavoklis(sudoku, fixedSudoku, listOfBlocks):
    randomBlock = random.choice(listOfBlocks)

    if BlokaSumma(fixedSudoku, randomBlock) > 6:
        return (sudoku, 1, 1)
    boxesToFlip = IzveletiesDivusNejaususBlokaLaukus(fixedSudoku, randomBlock)
    proposedSudoku = SamainitLaukus(sudoku, boxesToFlip)
    return ([proposedSudoku, boxesToFlip])


def IzveletiesJaunoStavokli(currentSudoku, fixedSudoku, listOfBlocks, temperature):
    proposal = PiedavataisStavoklis(currentSudoku, fixedSudoku, listOfBlocks)
    newSudoku = proposal[0]

    currentCost = AprekinatKluduSkaitu(currentSudoku)
    newCost = AprekinatKluduSkaitu(newSudoku)
    costDifference = newCost - currentCost
    rho = math.exp(-costDifference / temperature)
    if (np.random.uniform(1, 0, 1) < rho):
        return ([newSudoku, costDifference])
    return ([currentSudoku, 0])


def IteracijuSkaits(fixedSudoku):
    numberOfItterations = 0
    for i in range(0, 9):
        for j in range(0, 9):
            if fixedSudoku[i, j] != 0:
                numberOfItterations += 1
    return numberOfItterations


def DrukatRezultatu(sudoku, attemptsTotal, jumpsTotal, timeElapsedFormatted):
    f = open("Result.txt", "w")
    f.write("Attempts: " + str(attemptsTotal) + " JumpsTotal: " + str(jumpsTotal) + "\n")

    for i in range(len(sudoku)):
        line = ""
        if i == 3 or i == 6:
            f.write("---------------------" + "\n")
        for j in range(len(sudoku[i])):
            if j == 3 or j == 6:
                line += "| "
            line += str(sudoku[i, j]) + " "
        f.write(line + "\n")

    f.write(timeElapsedFormatted + "\n")
    f.close()


def AtrisinatSudoku(sudoku):
    solutionFound = 0

    temperature = 1.8
    decreaseFactor = 0.99

    stuckCount = 0
    jumpedCount = 0
    attemptCount = 0

    fixedSudoku = np.copy(sudoku)
    FiksetSudokuVertibas(fixedSudoku)
    listOfBlocks = Izveidot3x3Blokus()
    tmpSudoku = Aizpilditl3x3Blokus(sudoku, listOfBlocks)

    score = AprekinatKluduSkaitu(tmpSudoku)
    iterations = IteracijuSkaits(fixedSudoku)
    if score <= 0:
        solutionFound = 1

    while solutionFound == 0:
        previousScore = score
        for i in range(0, iterations):
            newState = IzveletiesJaunoStavokli(tmpSudoku, fixedSudoku, listOfBlocks, temperature)
            tmpSudoku = newState[0]
            scoreDiff = newState[1]
            score += scoreDiff
            print(score)
            attemptCount += 1

            if score <= 0:
                solutionFound = 1
                break

        temperature *= decreaseFactor
        if score <= 0:
            break
        if score >= previousScore:
            stuckCount += 1
        else:
            stuckCount = 0
        if (stuckCount > 80):
            jumpedCount += 1
            temperature += 2

    return tmpSudoku, attemptCount, jumpedCount


# X-Sudoku mīkla ģenerēta http://www.sudoku-space.com/x-sudoku/
f = open("Sudoku.txt", "r")
startingSudoku = f.read()
sudoku = np.array([[int(i) for i in line] for line in startingSudoku.split()])
startTime = datetime.now()
solution, attemptsTotal, jumpsTotal = AtrisinatSudoku(sudoku)
timeElapsed = datetime.now() - startTime
timeElapsedFormatted = 'Time elapsed (hh:mm:ss.ms) {}'.format(timeElapsed)
DrukatRezultatu(solution, attemptsTotal, jumpsTotal, timeElapsedFormatted)
