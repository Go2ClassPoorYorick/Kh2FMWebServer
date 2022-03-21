from asyncio.windows_events import NULL
import csv
import random
import os
from flask import render_template, request
from pymem import Pymem

#Add lock to clearing memory. This is essentially an API key, but far less secure.

apiKey = ''.join(random.choice('0123456789ABCDEF') for i in range(16))
print(apiKey)

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
    abilities_bytes = pm.read_bytes(abilities_start,abilities_length+2)
    
  
    equipped_abilities = [] 
    # Equipped abilities will store the list of abilities we've found in memory
    i=0
    while i < len(abilities_bytes):
        ability = abilities_bytes[i:i+2][::-1]
        ability_str = hex(int.from_bytes(ability,"big") & int.from_bytes(b'\x7F\xFF',"big"))[2:].zfill(4) # Remove equipped bit flag
        memLocation = hex(abilities_start+i)
        i=i+2
        try:
            if int.from_bytes(ability,"big") != 0:
                equipped_abilities.append([memLocation, shittyWayToMapAbilities[ability_str.upper()]])
            else:
                equipped_abilities.append([memLocation, {}])
        except(KeyError):
            equipped_abilities.append([memLocation, {"Id":hex(int.from_bytes(ability,"big"))}])
    return equipped_abilities

# People like to assume that a server has to have some webpage- we provide one, and an elementary interface for manually interacting with the api.
# This isn't reccomended.(especially because it isn't finished)
app = Flask(__name__)
@app.before_request
def before_request():
    if os.environ.get('debug') != "true":
        if request.args.get('apiKey') != apiKey:
            return "Missing or Incorrect API KEY", 401


@app.route('/')
def generate():
    return render_template('home.html')

# A wrapper to run getAbilities and return it formatted
@app.route('/readAbilities')
def read():
    return str(getAbilities()).replace('], [','],<br>[')

# This cluster allows us to write abilities... see readme
@app.route('/writeAbility', methods = ['POST','GET'])
def writeAbilities():
    oldAbilityList = getAbilities()
    abilities_to_write = request.args.getlist('ability')
    emptyMemItr = (location for location in oldAbilityList if location[1] == {}) #Allows us to use the next(emptyMemItr) function to access memory locations for writing

    for ability in abilities_to_write:
        try:
            if tiered_abilities_chart.get(str(ability)) == None:
                nextEmptySlot = next(emptyMemItr)[0]
                print (nextEmptySlot, ability.zfill(4))
                pm.write_bytes(
                    int(nextEmptySlot,16), # Reads memory location from string
                    bytes.fromhex(ability.zfill(4))[::-1], # [::-1] reverses byte order, allowing me to use traditionally written item ids to write to memory
                    2 # Bytes to write (this is silly, why wouldn't pymem just calculate that from above???)
                    ) 
            else:
                print(f'ability: {ability} skipped due to lack of "scaled ability" logic')
                # TODO: count existing instances of each type of tiered ability, and sum them.   
                #character_count_address = pymem.pattern.scan_pattern_page(pm.process_handle, address_reference, bytes_pattern)
        except(StopIteration):
            print("Couldn't write any new abilities, ability list full")
    return str(getAbilities()).replace('}, {','<br>')

@app.route('/clearAbility', methods = ['POST','GET'])
def clearAbilities():
    pm.write_bytes(
    abilities_start, # Clear from the start of the memory range
    bytes.fromhex(''.zfill((abilities_length+1)*2)), # Lotsa 0s
    abilities_length+2 # Clear ALL
    )
    return str(getAbilities()).replace('], [','],<br>[')

if __name__ == '__main__':
    app.run(...)