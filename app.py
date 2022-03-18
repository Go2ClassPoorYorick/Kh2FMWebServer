from asyncio.windows_events import NULL
import csv
import struct
import json
from flask import render_template, request
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

shittyWayToMapItems = {}
with open('items_abilities.csv', mode='r') as csv_file:
    csv_reader = csv.DictReader(csv_file)
    line_count = 0
    for row in csv_reader:
        if line_count == 0:
            line_count += 1
        else:
            if row["Type"] == "Ability":
                shittyWayToMapItems[row["ID"].zfill(4)]={"name":row["Name"],"Type":row["Type"], "Id":row["ID"].zfill(4)}
                line_count += 1
#    print(f'Processed {line_count} lines.')
#print(shittyWayToMapItems)

from flask import Flask

def getAbilities():
    abilities_bytes = pm.read_bytes(abilities_start,abilities_length)

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
    return equipped_abilities


app = Flask(__name__)
@app.route('/')
def generate():
    return render_template('home.html')

@app.route('/readmem')
def read():
    return str(getAbilities())


@app.route('/writeAbility', methods = ['POST','GET'])
def writeAbilities():
    oldAbilityList = getAbilities()
    abilities_to_write = request.args.getlist('ability')
    byteChart = []
    print(len(oldAbilityList))
    offset = 0x2032E074 + len(oldAbilityList)*2
    print(offset)
    for ability in abilities_to_write:
        if tiered_abilities_chart.get(str(ability)) == None:
            # TODO: Work out mapping addresses to store these abilities
            print(ability)
            pm.write_bytes(offset,bytes.fromhex(ability.zfill(4))[::-1],2) #[::-1] reverses byte order, allowing me to use traditionally written item ids to write to memory
            offset += 2 
        else:
            print(f'ability:{ability} skipped due to lackof "scaled ability" logic')
            # TODO: count existing instances of each type of tiered ability, and sum them.
                
    return str(getAbilities())
    

if __name__ == '__main__':
    app.run(...)