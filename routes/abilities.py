from flask import Blueprint, request
import csv
#TODO: pymem should re-attatch any time the window is open. 
from helpers.pymem import pm # Open the shared pymem instance
abilityApi = Blueprint("abilityApi", __name__)


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
    "006D" : "Glide",
}

# Used with the above table to assist in locating possible IDs for leveled abilities
tiered_abilities_list = {
"High Jump" : [0x005E, 0x005F, 0x0060, 0x0061],
"Quick Run" : [0x0062, 0x0063, 0x0064, 0x0065],
"Dodge Roll": [0x0234, 0x0235, 0x0236, 0x0237],
"Aerial Dodge": [0x0066, 0x0067, 0x0068, 0x0069],
"Glide" : [0x006A, 0x006B, 0x006C, 0x006D]
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
                equipped_abilities.append([memLocation, {"Id":'0000'}])
        except(KeyError):
            equipped_abilities.append([memLocation, {"Id":hex(int.from_bytes(ability,"big"))}])
    return equipped_abilities

# A wrapper to run getAbilities and return it formatted
@abilityApi.route('/readAbilities')
def read():
    return str(getAbilities()).replace('], [','],<br>[')

# TODO: Writing an 8 for growth abilities counts as a "new" ability. We need to check for this 
# This cluster allows us to write abilities... see readme
@abilityApi.route('/writeAbilities', methods = ['POST','GET'])
def writeAbilities():
    oldAbilityList = getAbilities()
    abilities_to_write = request.args.getlist('ability')
    emptyMemItr = (location for location in oldAbilityList if location[1] == {"Id":'0000'}) #Allows us to use the next(emptyMemItr) function to access memory locations for writing

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
            else: # life is a nightmare, help
                try: 
                    abilityTierName = tiered_abilities_chart.get(str(ability)) # Identity which tiered ability we're looking for
                    curAbility = next(currentAbilities for currentAbilities in oldAbilityList if int(currentAbilities[1]["Id"],16) in tiered_abilities_list[abilityTierName]) #get only the first occurence
                    if int(curAbility[1]["Id"],16) < max(tiered_abilities_list[abilityTierName]):
                        pm.write_bytes(
                        int(curAbility[0],16), # Write to existing ability location, 1
                        (int(curAbility[1]["Id"],16)+1).to_bytes(2, 'little'), # [::-1] reverses byte order, allowing me to use traditionally written item ids to write to memory
                        2 # Bytes to write (this is silly, why wouldn't pymem just calculate that from above???)
                        )
                    else:
                        print(f'{abilityTierName} is already max level')
                except(StopIteration): # TODO: This is awful and could/should be done better. Something something don't use exceptions for application flow
                    nextEmptySlot = next(emptyMemItr)[0]
                    pm.write_bytes(
                        int(nextEmptySlot,16), # Reads memory location from string
                        min(tiered_abilities_list[abilityTierName]).to_bytes(2, 'little'), # [::-1] reverses byte order, allowing me to use traditionally written item ids to write to memory
                        2 # Bytes to write (this is silly, why wouldn't pymem just calculate that from above???)
                        ) 
                    
        except(StopIteration):
            print("Couldn't write any new abilities, ability list full")
    return str(getAbilities()).replace('}, {','<br>')

@abilityApi.route('/clearAbilities', methods = ['POST','GET'])
def clearAbilities():
    pm.write_bytes(
    abilities_start, # Clear from the start of the memory range
    bytes.fromhex(''.zfill((abilities_length+1)*2)), # Lotsa 0s
    abilities_length+2 # Clear ALL
    )
    return str(getAbilities()).replace('], [','],<br>[')

