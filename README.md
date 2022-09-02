# dnd-roll-parser
The dnd roll parser parses rolls from the chat log of games using [D&D 5E](https://help.roll20.net/hc/en-us/articles/360037773573-D-D-5E-by-Roll20) by [Roll20](https://roll20.net/) character sheet. 

## Getting a chat log
Launch your Roll20 game. In the chat pane scroll up until you see "View all chat entries for this game >>". <br>
Once viewing the chat log click on "Show on One Page". Right click, and, using your browser's Save As option, save the page as a "Web Page, Complete". If you save as HTML only the file will not have the right information.
## Arguments

| Argument | Required | Default | Description |
| :---: | :---: | :---: | :---: |
| file | Yes | N/A | The file to be processed. .html (or .htm) in the case of complete/partial runs. .dat in the case of continuation |
| -n | No | 20 | Defines what type of dice to parse for. Ex: a D20 would be -n 20 |
| -a | No | None | The (a)lias file that specifies what is a character or a player. It also attributes certain characters to players. It is explained in detail further on |
| -d | No | None | Defines what (d)ate to record rolls from. uses "month d, yyyy" format ex: November 5, 2018 |
| --x | No | N/A (flag) | Will print some e(x)tra debug information like what dates were parsed |
| --f | No | N/A (flag) | (f)orces a complete run without an alias file. Not recommended. |

## Run Types
Because chat logs for games can be hundreds of thousands of lines long, execution time can be upwards of 10 seconds. To prevent recalculating data in the event of a missing or incomplete alias file, data is stored in data.dat. If the file is a .dat, the data will be used with the supplied alias file.<br/>

There are 3 run types:<br/>

| Run Type | Description | Example |
| :---: | :---: | :---: |
| Complete First Run | All files are present to do a complete run. Data is parsed, attributed and printed out to a csv | python main.py my_file.html -a my_aliases.json |
| Incomplete Run | Rolls are parsed and printed out to data.dat. | python main.py my_file.html
| Continuation Run | Using the roll data stored in data.dat, data is attributed and printed out to a csv | python main.py data.dat -a my_aliases.json


## Data
When parsing in two parts (an incomplete run, then a continuation run) the data is preserved in a file called data.dat
data.dat contains no attributions or aliases. It simply records every name the parser encounters and the number of each side of dice they rolled
So for a d20 it'd record:

name: [1, 2, 3, 4, 5, ... , 20]

where the 1st position is how many 1's they rolled, the 2nd how many 2's, and so on. 

## Characters vs Players
The distinction between characters and players allows the parser to find and attribute all the D&D characters towards the player who played them.
If Isaac Asimov is playing a halfing rogue named Barnan then the character is "Barnan" and the player is "Isaac Asimov"


## Aliases
The alias file is broken into 5 sections

| Field | Description | Example |
| :---: | :---: | :---: |
| characterAliases | The characters and and what names they appear as. Often used to shorten their name. | "Grom": "Grom The Barbarian"
| playerAliases | The players and what names they appear as. Often used to shorten their name. | "Juliet": "Juliet Capulet"
| playedBy | Who the character is played by. If they were aliased above, use the short form name(s). | "Grom": "Juliet" 
| players | The list of players | ["Juliet", "Romeo"] 
| characters | The list of characters | ["Grom", "Merlin"]

For example, lets say we have Gary Gygax who plays the character Arogak Destel. We also have Daisy who plays Enok. In the results file  we want to show the two characters Arogak and Enok (first names only). Likewise, we only want the first names of the players.<br/>

Arogak Destel is then a character alias that needs to map to Arogak. Gary Gygax -> Gary. Essentially the alias file sets up dictionary key value pairs. In the above situation the alias file would be:<br/>


```json
{
    "characterAliases": {
        "Arogak Destel": "Arogak"
    },
    "playerAliases": {
        "Gary Gygax": "Gary"
    },
    "playedBy": {
        "Arogak": "Gary",
        "Enok": "Daisy"
    },
    "characters": [
        "Arogak",
        "Enok"
    ],
    "players": [
        "Gary",
        "Daisy"
    ]
}
```
Note how Daisy and Enok don't need aliases listed because their names are already in the desired form. <br/>

Any data parsed that cannot be attributed towards a player or character will be discarded. 

## Regex Support

If you have a player or character who goes by many names it may be better to use a regex pattern. characterAliases & player aliases
support regex. 

For example say you have a character who goes by:

* "Sir Mercutio The Eldest"

* "Mercutio The Supreme"

* "Fellow Mercutio"

Instead of listing 3 different aliases, you could simply do:
```json
{
  "characterAliases": {
    "Mercutio": ".*Mercutio.*"
  },
  ...
}
```
