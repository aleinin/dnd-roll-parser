# dnd-roll-parser
The dnd roll parser parses rolls from the chat log of games using D&D 5E by Roll20 character sheet. 

The program accepts the following arguments:

HTML_FILE (required): The html chat log to parse. <br/>
n (required): Defines what type of dice to parse for. Ex: a D20 would be -n 20

-a : The alias file that specifies what is a character or a player. It also attributes certain characters to players. It is explained in detail further on<br/>
-s : Defines what date to record rolls from. uses "month d, yyyy" format ex: November 5, 2018<br/>
--c : Continuation flag. For reasons explained below, rolls.py will store incomplete runs if a relationship file is not present. The --c flag allows a relationship file to be added in a second run without the data being recalculated.<br/> 
--d : Debug flag. Will print some debug information like what dates were parsed <br/>
--f : Forces a complete run without an alias file. Not recommended. <br/>


Run Types:<br/>
Because chat logs for games can be hundreds of thousands of lines long, execution time can be upwards of 10 seconds. To prevent duplicate runs in the event of a missing or incomplete relationship file, data is stored in data.dat. In the event of the continuation flag --c, data.dat will be used with the new relationship file.<br/>

There are 3 run types:<br/>

* Complete First Run:
  * All files are present to do a complete run. Data is parsed, attributed and printed out to a csv
* Complete Continuation
  * Using the roll data stored in data.dat, data is attributed and printed out to a csv
* Incomplete First Run: 
  * Rolls are parsed and printed out to data.dat

Format of data.dat:<br/>
name: [# of 1 rolls, # of 2 rolls, # of 3 rolls, ..., # of n rolls]

where name is the author parsed from the chat log

Format of the alias json file<br/>
The alias file is broken into 5 sections:

* "characterAliases"
  * The characters and what they're known by
  * "long_form_name": "short_name"
* "playerAliases"
  * The players and what they're known by
  * "long_form_name": "short_name"
* "playedBy"
  * Who played what character 
  * "character": "player"
* "players"
  * The list of players
  * ["player1", "player2"]
* "characters"
  * The list of characters
  * ["character1", "character2"]

For example, lets say we have John Doe who plays character Arogak Destel. We also have Jane who plays Enok. In the results file  we want to show the two characters Arogak and Enok (first names only). Likewise, we only want the first names of the players.<br/>

Arogak Destel is then a character alias that needs to map to Arogak. John Doe -> John. Essentially the alias file sets up dictionary key value pairs. In the above situation the relationship file would be:<br/>


```json
{
    "characterAliases": {
        "Arogak Destel": "Arogak"
    },
    "playerAliases": {
        "John Doe": "John"
    },
    "playedBy": {
        "Arogak": "John",
        "Enok": "Jane"
    },
    "characters": [
        "Arogak",
        "Enok"
    ],
    "players": [
        "John",
        "Jane"
    ]
}
```
Note how Jane and Enok don't need aliases listed because their names are already in the desired form. <br/>
<br/>
