import configparser
import re

config = configparser.ConfigParser()
config.read('config.ini')

baseUrl = (config['CONFIG']['baseFolder'])
speciesPattern = r"Species\.(\w+)"
movePattern = r"Moves\.(\w+)"

def getEggMoves():
    starterCount = 0
    eggMoves = []
    with open(baseUrl + "src/data/egg-moves.ts", "r") as file:
        while line := file.readline():
            species = re.search(speciesPattern, line.rstrip())
            moves = re.findall(movePattern, line.rstrip())
            if species != None and moves != None:
                starterCount += 1
                speciesName = species.group(1).replace("_", " ").title()
                moveList = []
                for move in moves:
                    moveList.append(move.replace("_", " ").title())
                eggMoves.append({"name": speciesName, "eggMoves": moveList})
    return eggMoves