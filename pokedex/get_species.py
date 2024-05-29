import configparser
import json
import re
from pokedex.utils import formatEnum, getNumFromSpecies

config = configparser.ConfigParser()
config.read('config.ini')

baseUrl = (config['CONFIG']['baseFolder'])
pokedexFile = (config['CONFIG']['pokedex'])
        
SpeciesFormKey = {
  "MEGA": "mega",
  "MEGA_X": "mega-x",
  "MEGA_Y": "mega-y",
  "PRIMAL": "primal",
  "ORIGIN": "origin",
  "INCARNATE": "incarnate",
  "THERIAN": "therian",
  "GIGANTAMAX": "gigantamax",
  "GIGANTAMAX_SINGLE": "gigantamax-single",
  "GIGANTAMAX_RAPID": "gigantamax-rapid",
  "ETERNAMAX": "eternamax"
}

# species.ts
def getSpecies():
    speciesData = {}
    with open(baseUrl + "src/data/enums/species.ts", "r") as file:
        speciesId = 0
        while line := file.readline():
            if "{" in line or "}" in line:
                continue
            if speciesId >= 8902:
                break
            speciesIdInLine = re.search(r"= (\d+)", line.rstrip())
            species = re.search(r"(\w+)", line.rstrip())
            if speciesIdInLine != None:
                speciesId = int(speciesIdInLine.group(1))
            if species != None:
                speciesName = species.group(0).replace("_", " ").title()
            if speciesName != None:
                speciesData[str(speciesId)] = { "name": speciesName, "speciesId": speciesId }
                speciesId += 1
    with open(pokedexFile,"w+") as f:
        json.dump(speciesData, f, indent=4, ensure_ascii=False)

def getPokemonClassification(subLegend, legend, mythical):
    if subLegend == True:
        return "Sub-Legendary"
    if legend == True:
        return "Legendary"
    if mythical == True:
        return "Mythical"
    return "N/A"


def getSpeciesInfoFromLine(line):
    # format substring
    leftParenIndex = line.index("(")
    rightParenIndex = line.index(")") if ")" in line else len(line) - 1
    paramList = line[leftParenIndex+1:rightParenIndex].split(",")
    paramList = list(map(lambda param : param.strip(), paramList))

    classification = getPokemonClassification(paramList[2], paramList[3], paramList[4])
    
    abilities = [formatEnum(paramList[10])]
    if formatEnum(paramList[11]) != "None" and paramList[10] != paramList[11]:
        abilities.append(formatEnum(paramList[11]))

    entry = {
        "name": formatEnum(paramList[0]),
        "generation": int(paramList[1]),
        "classification": classification,
        "descriptor": paramList[5].replace("\"", ""),
        "type1": formatEnum(paramList[6]),
        "type2": formatEnum(paramList[7]) if not paramList[7] == "null" else paramList[7],
        "height": float(paramList[8]),
        "weight": float(paramList[9]),
        "abilities": abilities,
        "abilityHidden": formatEnum(paramList[12]),
        "baseStats": {
            "bst": int(paramList[13]),
            "hp": int(paramList[14]),
            "atk": int(paramList[15]),
            "def": int(paramList[16]),
            "spatk": int(paramList[17]),
            "spdef": int(paramList[18]),
            "spd": int(paramList[19]),
        },
        "catchRate": int(paramList[20]),
        "baseFriendship": int(paramList[21]),
        "baseExp": int(paramList[22]),
        "growthRate": formatEnum(paramList[23]),
        "malePercent": float(paramList[24]) if not paramList[24] == "null" else paramList[24],
        "genderDiffs": paramList[25]
    }
    try:
        canChangeForm = {"canChangeForm": paramList[26]}
    except IndexError:
        return entry
    entry.update(canChangeForm)
    return entry


# ("Normal", "", Type.GRASS, Type.POISON, 2, 100, Abilities.OVERGROW, Abilities.NONE, Abilities.CHLOROPHYLL, 525, 80, 82, 83, 100, 100, 80, 45, 50, 263, true),
# catchRate: integer, baseFriendship: integer, baseExp: integer, genderDiffs?: boolean, formSpriteKey?: string
def getFormInfoFromLine(line):
    # format substring
    leftParenIndex = line.index("(")
    rightParenIndex = line.index(")") if ")" in line else len(line) - 1
    paramList = line[leftParenIndex+1:rightParenIndex].split(",")
    paramList = list(map(lambda param : param.strip(), paramList))
    if paramList[0].replace("\"", "") == "Normal":
        return {}
    
    abilities = [formatEnum(paramList[6])]
    if formatEnum(paramList[7]) != "None" and paramList[6] != paramList[7]:
        abilities.append(formatEnum(paramList[7]))

    def getFormKey(param):
        if "SpeciesFormKey" in param:
            return SpeciesFormKey[param[param.index(".")+1:]]
        else:
            return param.replace("\"", "").strip()
    

    entry = {
        "formName": paramList[0].replace("\"", ""),
        "formKey": getFormKey(paramList[1]),
        "type1": formatEnum(paramList[2]),
        "type2": formatEnum(paramList[3]) if not paramList[3] == "null" else paramList[3],
        "height": float(paramList[4]),
        "weight": float(paramList[5]),
        "abilities": abilities,
        "abilityHidden": formatEnum(paramList[8]),
        "baseStats": {
            "bst": int(paramList[9]),
            "hp": int(paramList[10]),
            "atk": int(paramList[11]),
            "def": int(paramList[12]),
            "spatk": int(paramList[13]),
            "spdef": int(paramList[14]),
            "spd": int(paramList[15]),
        },
        "catchRate": int(paramList[16]),
        "baseFriendship": int(paramList[17]),
        "baseExp": int(paramList[18])
    }
    try:
        genderDiffs = {"genderDiffs": paramList[19]}
    except IndexError:
        return entry
    entry.update(genderDiffs)
    return entry

def getCandyCosts(cost):
    costs = [
        { "passive": 50, "costReduction": [30, 75] }, 
        { "passive": 45, "costReduction": [25, 60] }, 
        { "passive": 40, "costReduction": [20, 50] },
        { "passive": 30, "costReduction": [15, 40] },
        { "passive": 25, "costReduction": [12, 35] },
        { "passive": 20, "costReduction": [10, 30] },
        { "passive": 15, "costReduction": [8, 20] },
        { "passive": 10, "costReduction": [5, 15] },
        { "passive": 10, "costReduction": [3, 10] },
        { "passive": 10, "costReduction": [3, 10] },
    ]
    return costs[cost-1]

# pokemon-species.ts
def getPokemonSpecies():
    speciesData = {}
    with open(baseUrl + "src/data/pokemon-species.ts", "r") as file:
        speciesId = 0
        speciesLinePattern = r"new PokemonSpecies"
        formLinePattern = r"new PokemonForm"
        speciesStarterLinePattern = r"\[Species\.([A-Z_]+)\]\:"
        while line := file.readline():
            if not "new Pokemon" in line and not "Species." in line:
                continue
            newSpeciesLine = re.search(speciesLinePattern, line.strip())
            newFormLine = re.search(formLinePattern, line.strip())
            speciesStarterLine = re.match(speciesStarterLinePattern, line.strip())
            if newSpeciesLine != None:
                species = getSpeciesInfoFromLine(line.strip())
                index = getNumFromSpecies(species["name"])
                speciesData.update({str(index): species})
            if newFormLine != None:
                form = getFormInfoFromLine(line.strip())
                if form == {}:
                    continue
                if not "forms" in speciesData[str(index)]:
                    speciesData[str(index)].update({"forms": []})
                speciesData[str(index)]["forms"].append(form)
            if speciesStarterLine != None:
                index = getNumFromSpecies(speciesStarterLine.group(1).replace("_", " ").title())
                restOfLine = line.strip()[len(speciesStarterLine.group(0)):-1]
                if "Abilities" in restOfLine:
                    passive = formatEnum(restOfLine)
                    speciesData[str(index)].update({"passive": passive})
                else:
                    starterCost = int(line.strip()[len(speciesStarterLine.group(0)):-1])
                    speciesData[str(index)].update({"cost": starterCost})
                    speciesData[str(index)].update({"candyCosts": getCandyCosts(starterCost)})

    with open(pokedexFile, "r") as pokedex:
        pokedexJSON = json.load(pokedex)

    speciesDataKeys = list(speciesData.keys())

    for index in range(len(speciesDataKeys)):
        speciesId = speciesDataKeys[index]
        pokedexJSON[speciesId].update(speciesData[speciesId])
    
    with open(pokedexFile, "w") as pokedex:
        json.dump(pokedexJSON, pokedex, indent=4, ensure_ascii=False)
        