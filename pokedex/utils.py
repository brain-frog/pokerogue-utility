import json
import configparser

config = configparser.ConfigParser()
config.read('config.ini')

pokedexFile = (config['CONFIG']['pokedex'])


def getSpeciesGeneration(speciesId):
    generation = {
        1: 151,
        2: 251,
        3: 386,
        4: 493,
        5: 649,
        6: 721,
        7: 809,
        8: 905,
        9: 1025,
        10: 2105, # alolan forms
        11: 2670, # eternal flower floette
        12: 4618, # galarian forms
        13: 6724, # hisuian forms
        14: 8901, # paldean forms
    }
    for g in generation:
        if speciesId <= generation[g]:
            if g > 9:
                if g == 10:
                    return 7
                elif g == 11:
                    return 6
                elif g == 12 or g == 13:
                    return 8
                else:
                    return 9
            else:
                return g
            
def formatEnum(enum):
    return enum[enum.index(".")+1:].replace("_", " ").title()

def getNumFromSpecies(name):
    with open("./num_to_name.json", "r") as numtoname:
        numtonameJSON = json.load(numtoname)
        keys=list(numtonameJSON.keys())
        values=list(numtonameJSON.values())
    return keys[values.index(name)]

def updateIdToName():
    with open(pokedexFile, "r") as pokedex:
        pokedexJSON = json.load(pokedex)
    idtoname = {}
    for speciesid in pokedexJSON:
        species = pokedexJSON[speciesid]
        idtoname.update({speciesid: species["name"]})
        if "forms" in species:
            for f in species["forms"]:
                form = f["formName"]
                formKey = f["formKey"]
                idtoname.update({speciesid + "-" + formKey: species["name"] + " " + form})
    with open("./id_to_name.json", "w+") as idToName:
        json.dump(idtoname, idToName, indent=4, ensure_ascii=False)
