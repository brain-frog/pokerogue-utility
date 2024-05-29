from PIL import Image
import configparser
import time
import json
import re
import os
import sys

config = configparser.ConfigParser()
config.read('config.ini')
baseFolder = (config['CONFIG']['baseFolder'])

baseUrl = baseFolder + "/public/images/pokemon"
imageExtension = ".png"
jsonExtension = ".json"
masterListFile = open(baseUrl + "/variant/_masterlist.json")
masterListJSON = json.load(masterListFile)
updated = 0

# TODO: 
# 1. cleanup/comment functions

def getSpriteSheet(path):# -> string
    return path +imageExtension
    
def getSpriteJSON(path):
    return open(path +jsonExtension)  

def getSpriteCropSettings(jsonFile): 
    spriteJSON = json.load(jsonFile)
    spriteJSONFrames =spriteJSON['textures'][0]['frames']

    def findFirst(frames):
        for f in frames:
            if f['filename'] == "0001.png" or f['filename'] == "1":
                return f

    defaultFrameData = findFirst(spriteJSONFrames)["frame"]
    return (
        defaultFrameData['x'],
        defaultFrameData['y'],
        defaultFrameData['x'] + defaultFrameData['w'],
        defaultFrameData['y'] + defaultFrameData['h']
    )

def getPokemonSpriteSaveDir(fileName):
    try: 
        species = int(fileName)
    except ValueError:
        species = int(re.match(r"(\d+)(\_\d{1})*(\-\w)*", fileName).group(1))
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
        if species <= generation[g]:
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

def getFileName(folderName, fileName):
    result = fileName
    if "female" in folderName:
        result += "-f"
    return result

def rgb2hex(r, g, b):
    return '{:02x}{:02x}{:02x}'.format(r, g, b)
    
def hex2rgb(hex, a):
    rgb = [int(hex[i:i+2], 16) for i in (0, 2, 4)]
    rgb.append(a)
    return tuple(rgb)

def getSaveDir(path, folderName, fileName, shiny):
    baseUrl = "./sprites/"
    saveDir = ""
    if "pokemon" in path or "pokemon" in folderName:
        saveDir = baseUrl + "shiny/" if shiny == True else baseUrl + "default/"
        saveDir = saveDir + str(getPokemonSpriteSaveDir(fileName[:-2] if "_" in fileName else fileName))
    else:
        try:
            saveDir = baseUrl + path.split("images/", 1)[1]
        except IndexError:
            saveDir = baseUrl + folderName
    return saveDir

def makeSquare(image):
    fill = (0, 0, 0, 0)
    x, y = image.size
    size = max(x, y)
    squareimg = Image.new('RGBA', (size, size), fill)
    squareimg.paste(image, (int((size - x) / 2), int((size - y) / 2)))
    return squareimg

def saveSprite(spriteDefaultFrame, fileName, variantAddition, folderName, shiny, path):
    saveDirPath = getSaveDir(path, folderName, fileName, shiny)
    if not os.path.exists(saveDirPath):
        os.mkdir(saveDirPath)
    # spriteDefaultFrame = makeSquare(spriteDefaultFrame)
    spriteDefaultFrame.save(saveDirPath + "/"+ getFileName(folderName, fileName + variantAddition) + imageExtension)

def convertToVariant(path, folderName, fileName):
    variantJSON = getSpriteJSON(os.path.join(path, folderName, fileName))
    variantPalettes = json.load(variantJSON)
    isFemale = "female" in folderName
    shiny = folderName != "pokemon"
    masterListSection = masterListJSON["female"] if isFemale else masterListJSON

    for palette in variantPalettes:
        variantAddition = "_" + palette if int(palette) > 0 else ""
        if fileName in masterListSection:
            if masterListSection[fileName][int(palette)] != 1:
                continue
            savePath = getSaveDir(path, folderName, fileName, shiny) + "/"+ getFileName(folderName, fileName + variantAddition) + imageExtension
            if os.path.isfile(savePath):
                lastmodified = os.path.getmtime(savePath)
                palettelastmodified = os.path.getmtime(path + "/" + folderName + "/" + fileName + jsonExtension)
                # if lastmodified > palettelastmodified:
                #     continue
                # else:
                #     global updated
                #     updated += 1
        spriteSheet = Image.open(getSpriteSheet(os.path.join(baseUrl, fileName)))
        spriteJSON = getSpriteJSON(os.path.join(baseUrl, fileName))

        cropSettings = getSpriteCropSettings(spriteJSON)
        spriteDefaultFrame = spriteSheet.crop(cropSettings)
        spriteDefaultFrame = spriteDefaultFrame.convert('RGBA')
        pixels = spriteDefaultFrame.load()
        width, height = spriteDefaultFrame.size

        for x in range(width):
            for y in range(height):
                r, g, b, a = pixels[x, y]
                pixelHex = rgb2hex(r, g, b)
            
                if pixelHex in variantPalettes[palette]:
                    spriteDefaultFrame.putpixel((x,y), hex2rgb(variantPalettes[palette][pixelHex], a))
        
        saveSprite(spriteDefaultFrame, fileName, variantAddition, folderName, shiny, path)
        spriteDefaultFrame.close()
        spriteSheet.close()
        spriteJSON.close()
    variantJSON.close()

def getFinalFileName(fileName):
    finalFileName = fileName
    if "_" in fileName:
        if fileName[-1] == "2" or fileName[-1] == "3":
            finalFileName = fileName[:-1] + str(int(fileName[-1])-1)
        elif not fileName[-1] == "m" and not fileName[-1] == "f":
            finalFileName = fileName[:-2]
    return finalFileName

def getDefaultSprite(path, folderName, fileName):
    if not folderName == "pokemon":
        shiny = True
    else:
        shiny = False
    if "_" in fileName and fileName[:-2] in masterListJSON:
        if masterListJSON[fileName[:-2]][int(fileName[-1])-1] != 2:
            return
    elif folderName == "shiny" and fileName in masterListJSON:
        if masterListJSON[fileName][0] != 0:
            return
    spriteSheet = Image.open(getSpriteSheet(os.path.join(path, folderName, fileName)))
    spriteJSON = getSpriteJSON(os.path.join(path, folderName, fileName))

    cropSettings = getSpriteCropSettings(spriteJSON)

    spriteDefaultFrame = spriteSheet.crop(cropSettings)
    saveSprite(spriteDefaultFrame, getFinalFileName(fileName), "", folderName, shiny, path)
    spriteSheet.close()
    spriteJSON.close()

def getRegexpPattern(path, folderName):
    if "pokemon" in path or "pokemon" in folderName:
        return r"(\d+[\-\w]*)"
    else:
        return r"(\w+[\_\w]*)"

def matchFiles(dir, index, path, folderName):
    pattern = getRegexpPattern(path, folderName)
    jsonFile = re.match(pattern + r"\.(json)", dir[index]) 
    try:
        pngFile = re.match(pattern + r"\.(png)", dir[index+1])
    except IndexError:
        pngFile = None
    if jsonFile != None and pngFile == None and ("variant" in folderName or "variant" in path):
        convertToVariant(path, folderName, jsonFile.group(1))
        return 1
    else:
        if pngFile != None and jsonFile != None and pngFile.group(1) == jsonFile.group(1):
            getDefaultSprite(path, folderName, pngFile.group(1)) 
        return 2
       
def matchVariants(path, folderName, fileName, variantList):
    for v in range(3):
        if variantList[v] == 1:
            jsonExists = os.path.exists(os.path.join(path, folderName, fileName + jsonExtension))
            if not jsonExists:
                print("json for " + fileName + " does not exist")
                continue
            convertToVariant(path, folderName, fileName)
        if variantList[v] == 2:
            sheetName = fileName + "_" + str(v+1)
            pngExists = os.path.exists(os.path.join(path, folderName, sheetName + imageExtension))
            jsonExists = os.path.exists(os.path.join(path, folderName, sheetName + jsonExtension))
            if not jsonExists:
                print("json for " + sheetName + " does not exist")
                continue
            if not pngExists:
                print("spritesheet for " + sheetName + " does not exist")
                continue
            getDefaultSprite(path, folderName, sheetName)


def getAllSpritesFromFolder(folderName, path):
    allContents = os.listdir(path + "/" + folderName)
    folder = [f for f in allContents if os.path.isfile(path + "/" + folderName+'/'+f)]
    folder.sort()
    fileCount = len(folder)
    print("Parsing: "+ folderName + "\t" + str(fileCount) + " files")
    index = 0
    while index < fileCount:
        sys.stdout.write('{0} percent complete\r'.format(int((index/fileCount)*100)))
        sys.stdout.flush()   
        index += matchFiles(folder, index, path, folderName)

def getAllVariantsFromFolder(folderName, path):
    isFemale = folderName == "female"
    masterListSection = masterListJSON["female"] if isFemale else masterListJSON
    # ignore subsection names
    ignore = ["back", "exp", "female"]
    variantCount = len(masterListSection.keys())
    print("Parsing: "+ folderName + "\t" + str(variantCount) + " files")
    for v in masterListSection.keys():
        if not v in ignore:
            index = list(masterListSection.keys()).index(v)
            sys.stdout.write('{0} percent complete\r'.format(int((index/variantCount)*100)))
            sys.stdout.flush()   
            matchVariants(path, folderName, v, masterListSection[v])


def getSpritesFromAllDir(path):
    baseName = os.path.basename(path)
    for (root, dirs, files) in os.walk(path):
        baseName = os.path.basename(root)
        exclude = ["input", "icons", "exp", "back"]
        include = ["shiny", "variant", "pokemon", "trainer"]
        if any(dirName in root for dirName in exclude):
            continue
        if any(dirName in root for dirName in include):
            dirNameLen = len(baseName) + 1

            isVariant = ("variant" in baseName or "variant" in root)
            if isVariant:
                getAllVariantsFromFolder(baseName, root[:-dirNameLen])
            else:
                getAllSpritesFromFolder(baseName, root[:-dirNameLen])
            sys.stdout.write("100 percent complete\n\n")
        

        
pathToImages = "../pokerogue/public/images"
start = time.time()
getSpritesFromAllDir(pathToImages)
masterListFile.close()
end = time.time()
print ('{:4.2f}'.format(end - start) + " second(s) to update " + str(updated) + " sprite(s)")
