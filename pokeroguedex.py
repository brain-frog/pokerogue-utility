import configparser
import json
import re
import dokuwikixmlrpc
from get_species import getSpecies, getPokemonSpecies, getNumFromSpecies
from egg_moves import getEggMoves
from get_moves import getLevelMoves

config = configparser.ConfigParser()
config.read('config.ini')

baseUrl = (config['CONFIG']['baseFolder'])
pokedexFile = (config['CONFIG']['pokedex'])

# create and load dex
getSpecies()
getPokemonSpecies()
getLevelMoves()

with open(pokedexFile, "r") as pokedex:
    pokedexJSON = json.load(pokedex)

# add egg moves
eggMoves = getEggMoves()
for species in eggMoves:
    speciesId = getNumFromSpecies(species["name"])
    pokedexJSON[speciesId].update({"eggMoves": species["eggMoves"]})

with open(pokedexFile, "w") as pokedex:
    json.dump(pokedexJSON, pokedex, indent=4, ensure_ascii=False)
