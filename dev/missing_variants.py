import json
import configparser
import pprint

config = configparser.ConfigParser()
config.read('config.ini')

baseUrl = (config['CONFIG']['baseFolder'])

# consts
COMMON=UNCHANGED = 0
RARE=JSON_PALETTE_SWAP = 1
EPIC=CUSTOM_SPRITE_SHEET = 2

with open("id_to_name.json", "r") as species:
    idtoname = json.load(species)

with open(baseUrl + "public/images/pokemon/variant/_masterlist.json") as m:
    masterlist = json.load(m)

missingAll = []
missingSome = {}
onlyBaseReplacement = []
hasRareAndEpic = []
missingOneVariant = []
customSprites = []
inconsistent = []
isAVariant = (JSON_PALETTE_SWAP, CUSTOM_SPRITE_SHEET)

def missingVariantCheck(variants, id):
    """Checks a masterlist entry for if it was only given one variant but not the other

    Args:
        variants (list): masterlist entry, a list of 3 integers that are 0-2
    """    
    missingEpic = (variants[RARE] in isAVariant and not variants[EPIC] in isAVariant)
    missingRare = (variants[EPIC] in isAVariant and not variants[RARE] in isAVariant)
    if missingRare:
        missingOneVariant.append((idtoname[id], "missing RARE variant"))
    if missingEpic:
        missingOneVariant.append((idtoname[id], "missing EPIC variant"))

def checkAllSprites(id):
    """Checks if the masterlist entry is consistent with the back entry and female entry (if applicable)

    Args:
        id (string): species id
    """
    result = {idtoname[id]: []}
    if not (masterlist[id]==masterlist["back"][id]):
        result[idtoname[id]].append("back")
    if id in masterlist["female"]:
        if not (masterlist[id]==masterlist["female"][id]==masterlist["back"]["female"][id]):
            result[idtoname[id]].append("female")
    if len(result[idtoname[id]]) > 0:
        inconsistent.append(result)

for id in idtoname:
    missingV = [0, 1, 2]
    if id in masterlist:
        variants = masterlist[id]
        # Missing Variant
        missingVariantCheck(variants=variants, id=id)
        # Only Base Replacement
        if variants[COMMON] != UNCHANGED and variants[RARE] in isAVariant and variants[EPIC] in isAVariant:
            onlyBaseReplacement.append(idtoname[id])
        # Uses Custom Sprite Sheet
        if CUSTOM_SPRITE_SHEET in variants:
            customSprites.append(idtoname[id])
        checkAllSprites(id)
        # Make sure it has all sprite versions
        for key in range(3):
            if variants[key] != UNCHANGED:
                missingV.remove(key)

    if len(missingV) > 0 and len(missingV) < 3:
        variantList = ["COMMON", "RARE", "EPIC"]
        if len(missingV) == 1 and missingV[0] == COMMON:
            # not going to list every unchanged common shiny
            continue
        missingSome[idtoname[id]] = "missing " + ', '.join(variantList[v] for v in missingV)
    elif len(missingV) == 3:
        missingAll.append(idtoname[id])
            

with open("missing_variants.txt", "w+") as output:
    def writeSection(msg, description, data):
        separator = "----------------------------------------------------"
        output.write('\n\n')
        output.write(separator)
        output.write('\n\n')
        output.write('{:^52}'.format(msg.upper()))
        output.write('\n\n')
        output.write('{:^52}'.format(description))
        output.write('\n')
        output.write(separator)
        output.write('\n')
        output.write(str(len(data)) + " found\n")
        if (type(data) is dict):
            json.dump(data, output, indent=2)
        else:
            pprint.pprint(data, output)

    sections = [
        {
            "msg": "Only Base Replacement", 
            "description": "Only common shiny has been replaced", 
            "data": onlyBaseReplacement
        },
        {
            "msg": "Custom Sprites", 
            "description": "Using a custom sprite sheet instead of palette swap", 
            "data": customSprites
        },
        {
            "msg": "Missing One Variant", 
            "description": "Has RARE or EPIC variant but not the other", 
            "data": missingOneVariant
        },
        {
            "msg": "Some Variants", 
            "description": "Has some but not all variants", 
            "data": missingSome
        },
        {
            "msg": "No Variant", 
            "description": "Has no variants", 
            "data": missingAll
        },
        {
            "msg": "Inconsistent", 
            "description": "Masterlist entry doesn't match back and/or female", 
            "data": inconsistent
        },
    ]
    for s in sections:
        writeSection(s["msg"], s["description"], s["data"])