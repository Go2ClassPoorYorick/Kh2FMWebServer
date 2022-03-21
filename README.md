# Kh2FMWebServer
Provides an API to attatch to instances of KH2 to add/remove abilities and items from a player's inventory in real time. to be used with a future multiworld client.

As a precaution, all requests must include an API key. The API key can be found in the logs each time the program is run- at some point this may be assignable at launch, but it is currently randomly generated.


Api endpoints:
- /?apiKey=yyyy
    - A home page with minor abilities to test the api.
- /readAbilities?apiKey=yyyy
    - Reads the ability memory of an attached pcsx2.exe instance. This naively assumes the application is running and KH2FM is loaded and in-game
- /writeAbilities?apiKey=yyyy&ability=xxxx
    - Writes an ability to the calculated end of abilities of an attached pcsx2.exe instance. This naively assumes the application is running and KH2FM is loaded and in-game
    - Using '&'s to chain ability values allows writing of more than one ability at a time:
        - http://127.0.0.1:5000/writeAbility?ability=00DF&ability=023D&ability=006D&apiKey=yyyy will write 00DF, 023D, and 006D
    - Currently scaled abilities are not supported as I have not finished the logic for incrementing these values.
- /clearAbilities?apiKey=yyyy
    - Clears ALL abilities from memory (writes '0000' over the ability memory)
        -The game behaves weirdly with this. You will beable to high jump until an area transition, for example


WARNING: THIS APPLICATION INTENTIONALLY MODIFIES THE MEMORY OF RUNNING PROCESSES ON YOUR COMPUTER, WE ARE NOT RESPONSIBLE FOR POSSIBLE DAMAGE THAT MAY OCCUR
