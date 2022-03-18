from asyncio.windows_events import NULL
import csv
import struct
from flask import request
from pymem import Pymem

pm = Pymem('pcsx2.exe')
abilities_start  = 0x2032E074
abilities_length = 2 * 79
tiered_abilities_chart = {
    "005E" : "High Jump",
    "005F" : "High Jump",
    "0060" : "High Jump",
    "0061" : "High Jump",
    "0062" : "Quick Run",
    "0063" : "Quick Run",
    "0064" : "Quick Run",
    "0065" : "Quick Run",
    "0234" : "Dodge Roll",
    "0235" : "Dodge Roll",
    "0236" : "Dodge Roll",
    "0237" : "Dodge Roll",
    "0066" : "Aerial Dodge",
    "0067" : "Aerial Dodge",
    "0068" : "Aerial Dodge",
    "0069" : "Aerial Dodge",
    "006A" : "Glide",
    "006B" : "Glide",
    "006C" : "Glide",
    "006D" : "Glide"
}

from flask import Flask

def getAbilities():
    abilities_bytes = pm.read_bytes(abilities_start,abilities_length)



    shittyWayToMapItems = {}
    with open('items_abilities.csv', mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        line_count = 0
        for row in csv_reader:
            if line_count == 0:
                line_count += 1
            else:
                shittyWayToMapItems[row["ID"]]={"name":row["Name"],"Type":row["Type"], "Id":row["ID"]}
                line_count += 1
    #    print(f'Processed {line_count} lines.')
    #print(shittyWayToMapItems)

    i=0
    equipped_abilities = []
    while i < len(abilities_bytes):
        ability = abilities_bytes[i:i+2][::-1]
        equipped = b'\x80\x00'
        ability_str = str(ability.hex())
        i=i+2
        try:
            if int.from_bytes(ability, "big") > int.from_bytes(equipped, "big"):
                ability = int.from_bytes(ability, "big") - int.from_bytes(equipped, "big")
                equipped_abilities.append(shittyWayToMapItems[str(ability.to_bytes(2, 'big').hex()).upper()])
            else:
                equipped_abilities.append(shittyWayToMapItems[ability_str.upper()])
        except(KeyError):
            continue
    return str(equipped_abilities)


app = Flask(__name__)

@app.route("/readmem")
def read():
    return getAbilities()


@app.route("/writeAbility", methods = ['POST','GET'])
def writeAbilities():
    oldAbilityList = getAbilities()
    abilities_to_write = request.args.getlist('ability')
    for ability in abilities_to_write:
        if tiered_abilities_chart.get(str(ability)) == None:
            # TODO: Work out mapping addresses to store these abilities
            print(ability)
        else:
            # TODO: count existing instances of each type of tiered ability, and sum them.
            continue
    return oldAbilityList
    

if __name__ == '__main__':
    app.run(...)