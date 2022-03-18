# Kh2FMWebServer
Provides an API to attatch to instances of KH2 to add/remove abilities and items from a player's inventory in real time. to be used with a future multiworld client.
Api endpoints:
- /readmem
    - Reads the ability memory of an attached pcsx2.exe instance. This naively assumes the application is running and KH2FM is loaded and in-game
- /writeAbility?ability=xxxx
    - Writes an ability to the calculated end of abilities of an attached pcsx2.exe instance. This naively assumes the application is running and KH2FM is loaded and in-game
    - Using '&'s to chain ability values allows writing of more than one ability at a time:
        - http://127.0.0.1:5000/writeAbility?ability=00DF&ability=023D&ability=006D will write 00DF, 023D, and 006D
    - Currently scaled abilities are not supported as I have not finished the logic for incrementing these values.
WARNING: THIS APPLICATION INTENTIONALLY MODIFIES THE MEMORY OF RUNNING PROCESSES ON YOUR COMPUTER, WE ARE NOT RESPONSIBLE FOR POSSIBLE DAMAGE THAT MAY OCCUR