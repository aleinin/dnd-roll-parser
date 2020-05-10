from roll_parser import RollParser
from roll_writer import RollWriter

# Used for partial runs
# reads in the already parsed data stored in the
# intermediate file into a list.
def read_in_data():
    data = dict()
    chk_sess = None
    with open("data.dat", "r") as data_in:
        first_line = True
        for line in data_in:
            if not first_line:
                line_split = line.split(":")
                name = line_split[0]
                rolls_str = line_split[1]
                rolls_str = rolls_str.replace("[", "").replace("]", "").replace(" ", "")
                rolls_split = rolls_str.split(",")
                rolls = []
                for roll in rolls_split:
                    rolls.append(int(roll))
                data[name] = rolls
            else:
                if not line == "None\n":
                    chk_sess = line.replace("\n", "")
                first_line = False
    return data, chk_sess

# reads in the data of the alias file into the appropriate dictionaries and lists
def read_in_alias(alias_file):
    character_aliases = dict()
    person_aliases = dict()
    played_by = dict()
    people = []
    characters = []
    with open(alias_file, "r", encoding='utf-8-sig') as rfile:
        aliases = rfile.read()
        subsections = aliases.split("[$12]")
        for calias in subsections[0].split("\n"):
            if calias != "":
                half = calias.split("=")
                character_aliases[half[0]] = half[1]
        for alias in subsections[1].split("\n"):
            if alias != "":
                half = alias.split("=")
                person_aliases[half[0]] = half[1]
        for pby in subsections[2].split("\n"):
            if pby != "":
                half = pby.split("=")
                played_by[half[0]] = half[1]
        for ppl in subsections[3].replace("\n", "").split(","):
            if ppl != "":
                people.append(ppl)
        for char in subsections[4].replace("\n", "").split(","):
            if char != "":
                characters.append(char)
    return character_aliases, person_aliases, played_by, people, characters


# uses alias file to translate names to known key value pairs
# ex: if name is "John Doe" or "John D." they might both translate
# to "John" if those alias pairs are described in the file.
def translate_name(name, character_aliases, aliases):
    if name in character_aliases:
        name = character_aliases[name]
    elif name in aliases:
        name = aliases[name]
    return name


# takes a list of occurrences of rolls 1..n and adds it to any list 1..n that has
# a matching name. If there is no matching name it adds the roll to the cumulative
# list
def add_roll_to_cumulative(name, cumulative_rolls, individual_rolls):
    if name in cumulative_rolls:
        sum_roll_data = cumulative_rolls[name]
        for i in range(0, len(individual_rolls)):
            sum_roll_data[i] += individual_rolls[i]
        cumulative_rolls[name] = sum_roll_data
    else:
        cumulative_rolls[name] = individual_rolls
    return cumulative_rolls


# given the key value pairs supplied by the alias file,
# attribute the rolls to the correct people and characters.
def attribute_data(alias_file, data):
    all_people_rolls = dict()
    all_char_rolls = dict()
    character_aliases, aliases, played_by, people, characters = read_in_alias(alias_file)
    for name, rolls in data.items():
        name = translate_name(name, character_aliases, aliases)
        if name in people:
            all_people_rolls = add_roll_to_cumulative(name, all_people_rolls, rolls)
        else:
            all_char_rolls = add_roll_to_cumulative(name, all_char_rolls, rolls)
            if name in played_by:
                all_people_rolls = add_roll_to_cumulative(played_by[name], all_people_rolls, rolls)
    return all_people_rolls, all_char_rolls

# complete standalone run that mines the chat log and produces a csv
def complete_run(alias_file, file_name, chk_sess, debug, n):
    parser = RollParser(file_name, chk_sess, debug)
    data = parser.get_player_dn(n)
    person_rolls, character_rolls = attribute_data(alias_file, data)
    if chk_sess is None:
        csv_out = "results.csv"
    else:
        csv_out = "{}_results.csv".format(chk_sess.replace(" ", "_").replace(",", ""))
    out = RollWriter(person_rolls, character_rolls, n, csv_out)
    out.write_all()


# second half of a partial run that reads in the already parsed data
# and writes out to the csv
def partial_finish(alias_file, n):
    data, chk_sess = read_in_data()
    person_rolls, character_rolls = attribute_data(alias_file, data)
    if chk_sess is None:
        csv_out = "results.csv"
    else:
        csv_out = "{}_results.csv".format(chk_sess.replace(" ", "_").replace(",", ""))
    out = RollWriter(person_rolls, character_rolls, n, csv_out)
    out.write_all()


# first half of a partial run that parses the data and writes it
# to an intermediate file. (to be completed once an alias file is made)
def partial_run(file_name, chk_sess, debug, n):
    parser = RollParser(file_name, chk_sess, debug)
    data = parser.get_player_dn(n)
    with open("data.dat", 'w') as data_out:
        data_out.write("{}\n".format(chk_sess))
        for key, val in data.items():
            data_out.write("{}:{}\n".format(key, val))


# debug run to force a full run without an alias file
def force_run(file_name, n):
    parser = RollParser(file_name, None, True)
    data = parser.get_player_dn(n)
    char_rolls = data
    pers_rolls = data
    out = RollWriter(pers_rolls, char_rolls, n, "debug.csv")
    out.write_all()