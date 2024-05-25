import configparser
import os
import json
import re
from utils import formatEnum, getNumFromSpecies

config = configparser.ConfigParser()
config.read('config.ini')

baseUrl = (config['CONFIG']['baseFolder'])
pokedexFile = (config['CONFIG']['pokedex'])

def getLevelMoves():
    leveldata = {}
    with open(os.path.join(baseUrl, "src/data", "pokemon-level-moves.ts"), "r") as levelmoves:
        speciesName = ""
        speciesId = 0
        moveName = ""
        level = 0
        while line := levelmoves.readline():
            if not "Species." in line and not "Moves." in line:
                continue
            speciesPattern = r"\[Species.([A-Z_0-9]+)\]\: \["
            movePattern = r"\[ (\d+)\, Moves.([A-Z_]+) \]\,"
            species = re.match(speciesPattern, line.strip())
            if species != None:
                speciesName = species.group(1).replace("_"," ").title()
                speciesId = getNumFromSpecies(speciesName)
                leveldata.update({str(speciesId): { "levelMoves": []}})
                continue
            move = re.match(movePattern, line.strip())
            if move != None:
                level = int(move.group(1))
                moveName = move.group(2).replace("_", " ").title()
                leveldata[str(speciesId)]["levelMoves"].append([level, moveName])
            
    with open(pokedexFile, "r") as pokedex:
        pokedexJSON = json.load(pokedex)

    
    for p in pokedexJSON:
        pokedexJSON[p].update(leveldata[p])
    
    with open(pokedexFile, "w") as pokedex:
        json.dump(pokedexJSON, pokedex, indent=4, ensure_ascii=False)

def getTMMoves():
    tmData = {}
    with open(os.path.join(baseUrl, "src/data", "tms.ts"), "r") as tms:
        speciesName = ""
        speciesId = 0
        moveName = ""
        while line := tms.readline():
            if not "Species." in line and not "[Moves." in line and not line.strip() == "[":
                continue
            if line.strip() == "[":
                formsArray = True
            speciesPattern = r"Species.([A-Z_0-9]+)\,"
            movePattern = r"\[Moves.([A-Z_]+)\]\: \["
            species = re.match(speciesPattern, line.strip())
            move = re.match(movePattern, line.strip())
            if move != None:
                moveName = move.group(1).replace("_", " ").title()
                tmData[str(speciesId)]["tmMoves"].append([moveName])
                continue
            if species != None:
                speciesName = species.group(1).replace("_"," ").title()
                speciesId = getNumFromSpecies(speciesName)
                tmData.update({str(speciesId): { "tmMoves": []}})