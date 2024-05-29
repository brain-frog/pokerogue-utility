import os
import subprocess
import configparser
import re

config = configparser.ConfigParser()
config.read('config.ini')

baseUrl = (config['CONFIG']['baseFolder'])
iconsPath = "public/images/pokemon/icons"
variantIconsPath = "public/images/pokemon/icons/variant"
def tpCmd(gen, v):
    cmd =  [
        "TexturePacker",
        "./",
        "../configuration.tps",
        "--sheet",
        "../../../pokemon_icons_" + gen + ".png",
        "--data",
        "../../../pokemon_icons_" + gen + ".json",
        "--replace",
        ".png="
        ]
    if v:
        cmd[4] = "../../../../pokemon_icons_" + gen + "v.png"
        cmd[6] = "../../../../pokemon_icons_" + gen + "v.json"
    return cmd

diff = subprocess.check_output(["git","status", "--short"], cwd=os.path.join(baseUrl))
files = [f.strip() for f in re.split('\n\?\? |\n M', diff.decode("utf-8")) if "icons/" in f]
files = [f[len(iconsPath):] for f in files]
if len(files):
    files[0] = files[0][2:]
icons = [f for f in files if not "variant" in f]
variants = [f[len("/variant/"):f.rfind("/")] for f in files if "variant" in f]
variants = list(set(variants))
variants.sort()
for g in icons:
    subprocess.run(tpCmd(g, False), cwd=os.path.join(baseUrl, iconsPath, g))
for g in variants:
    subprocess.run(tpCmd(g, True), cwd=os.path.join(baseUrl, variantIconsPath, g))