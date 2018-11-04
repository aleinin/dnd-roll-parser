The roll20 5th edition OGL parses D20 rolls from the chat log of games using the 5th Edition OGL character sheet. 

The console version accepts the following arguments:

HTML_FILE (required): The html chat log to parse. 
-r : The relationship file that specifies what is a character or a player. It also attributes certain characters to players. It is explained in detail further on
--c : Continuation flag. For reasons explained below, rolls.py will store incomplete runs if a relationship file is not present. The --c flag allows a relationship file to be added in a second run without the data being recalculated. 
-s : Session flag (TO DO)

Run Types:
Because chat logs for games can be hundreds of thousands of lines long, execution time can be upwards of 6 seconds. To prevent duplicate runs in the event of a missing or incomplete relationship file, data is stored in data.dat. In the event of the continuation flag --c, data.dat will be used with the new relationship file. Incomplete runs are mostly to support the GUI edition of the Roll20 5th Edition OGL Parser. 

There are 3 run types:
COMPLETE FIRST RUN
  All files are present to do a complete run. Data is calculated, attributed and printed out to results.csv
COMPLETE CONTINUATION
  Using the calculations stored in data.dat, data is attributed and printed out to results.csv
INCOMPLETE FIRST RUN
  Data is calculated and printed out to data.dat
  
Format of data.dat:
name: [# of 1 rolls, # of 2 rolls, # of 3 rolls, ..., # of 20 rolls]

where name could be a player or character. 

Format of the relationship file
The relationship file is broken into 5 sections seperated by a [$12] token.The sections are:

(character aliases)<br/>
long_char=char<br/>
[$12]<br/>
(player aliases)<br/>
long_play=play<br/>
[$12]<br/>
(characters played by)<br/>
char=play<br/>
[$12]<br/>
(players list)<br/>
play,play2<br/>
[$12]<br/>
(character list)<br/>
char,char2<br/>

For example, lets say we have John Doe who plays character Arogak Destel. We also have Jane who plays Enok. In the results file  we want to show the two characters Arogak and Enok (first names only). Likewise, we only want the first names of the players.

Arogak Destel is then a character alias that needs to map to Arogak. John Doe -> John. Essentially the relationship file sets up dictionary key value pairs. In the above situation the relationship file would be:

Arogak Destel=Arogak
[$12]
John Doe=John
[$12]
Arogak=John
Enok=Jane
[$12]
John,Jane
[$12]
Arogak,Enok

Note how Jane and Enok don't need aliases listed because their name is already in the desired form. 

If this all seems too complicated, check out the GUI executable version. 
