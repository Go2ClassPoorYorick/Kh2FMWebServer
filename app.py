from asyncio.windows_events import NULL
import csv
import struct
import json
from flask import render_template, request
from pymem import Pymem

pm = Pymem('pcsx2.exe')

# This project asssumes we're using PCSX2.EXE, so memory locations should be static and offset +0x2000000
abilities_start  = 0x2032E074
abilities_length = 2 * 79

# Create a list of abilities that "scale" When an ability in this list is found, 
# write logic needs to NOT increment offset, but instead locate the memory location of the ability and increment, instead 
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

# This function reads item_abilities.csv into a json-like-object to provide an interface for viewing ability names and ids. 
shittyWayToMapAbilities = {}
with open('items_abilities.csv', mode='r') as csv_file:
    csv_reader = csv.DictReader(csv_file)
    line_count = 0
    for row in csv_reader:
        if line_count == 0:
            line_count += 1
        else:
            if row["Type"] == "Ability":
                shittyWayToMapAbilities[row["ID"].zfill(4)]={"name":row["Name"],"Type":row["Type"], "Id":row["ID"].zfill(4)}
                line_count += 1


from flask import Flask

# Reads ability memory and attempts to map abilities in memory to known database generated above
def getAbilities():
    abilities_bytes = pm.read_bytes(abilities_start,abilities_length)

  
    equipped_abilities = [] 
    # Equipped abilities will store the list of abilities we've found in memory
    i=0
    while i < len(abilities_bytes):
        ability = abilities_bytes[i:i+2][::-1]
        equipped = b'\x80\x00' #This is the "equipped" bitmask.
        ability_str = str(ability.hex())
        i=i+2
        try:#When an ability is larger than 0x8000 it must be equipped- we just want the ability flag, so lets remove the equipped mask
            if int.from_bytes(ability, "big") > int.from_bytes(equipped, "big"): 
                ability = int.from_bytes(ability, "big") - int.from_bytes(equipped, "big")
                equipped_abilities.append(shittyWayToMapAbilities[str(ability.to_bytes(2, 'big').hex()).upper()])
            else: #These abilities are unequipped or invalid
                equipped_abilities.append(shittyWayToMapAbilities[ability_str.upper()])
        except(KeyError):
            continue
    return equipped_abilities

# People like to assume that a server has to have some webpage- we provide one, and an elementary interface for manually interacting with the api.
# This isn't reccomended.
app = Flask(__name__)
@app.route('/')
def generate():
    return render_template('home.html')

# A wrapper to run getAbilities and return it formatted
@app.route('/readAbilities')
def read():
    return str(getAbilities()).replace('}, {','<br>')

# This cluster allows us to write abilities... see readme
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
            # TODO: Workout avoiding rando-protected memory ranges
            print(ability)
            pm.write_bytes(offset,bytes.fromhex(ability.zfill(4))[::-1],2) #[::-1] reverses byte order, allowing me to use traditionally written item ids to write to memory
            offset += 2 
        else:
            print(f'ability:{ability} skipped due to lack of "scaled ability" logic')
            # TODO: count existing instances of each type of tiered ability, and sum them.   
            #character_count_address = pymem.pattern.scan_pattern_page(pm.process_handle, address_reference, bytes_pattern)
    return str(getAbilities()).replace('}, {','<br>')
    

if __name__ == '__main__':
    app.run(...)