from roll_parser import RollParser
from roll_writer import RollWriter
import json
import sys


# Used for partial runs
# reads in the already parsed data stored in the
# intermediate file into a list.
def read_in_data(data_file):
    data = dict()
    date_to_record = None
    with open(data_file, "r") as data_in:
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
                    date_to_record = line.replace("\n", "")
                first_line = False
    return data, date_to_record


# reads in the data of the alias file into the appropriate dictionaries and lists
def read_in_alias(alias_file):
    character_aliases = dict()
    player_aliases = dict()
    played_by = dict()
    players = []
    characters = []
    with open(alias_file, "r", encoding='utf-8-sig') as json_file:
        data = json.load(json_file)
        print()
        try:
            character_aliases = data["characterAliases"]
            player_aliases = data["playerAliases"]
            played_by = data["playedBy"]
            players = data["players"]
            characters = data["characters"]
        except:
            print("Unable to parse alias file")
            exit(1)
    return character_aliases, player_aliases, played_by, players, characters


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
# attribute the rolls to the correct players and characters.
def attribute_data(alias_file, data, is_debug):
    all_player_rolls = dict()
    all_char_rolls = dict()
    character_aliases, aliases, played_by, players, characters = read_in_alias(alias_file)
    for name, rolls in data.items():
        name = translate_name(name, character_aliases, aliases)
        if name in players:
            all_player_rolls = add_roll_to_cumulative(name, all_player_rolls, rolls)
        elif name in characters:
            all_char_rolls = add_roll_to_cumulative(name, all_char_rolls, rolls)
            if name in played_by:
                all_player_rolls = add_roll_to_cumulative(played_by[name], all_player_rolls, rolls)
        elif is_debug:
            print("{} was discarded as they're neither a player nor a character".format(name))
    return all_player_rolls, all_char_rolls


# complete standalone run that mines the chat log and produces a csv
def complete_run(alias_file, file_name, date_to_record, is_debug, die_to_record):
    parser = RollParser(file_name, date_to_record, is_debug, die_to_record)
    data = parser.parse_rolls()
    if len(data) == 0:
        print("No rolls were parsed{} Check your parameters"
              .format(" for {}."
                      .format(date_to_record) if date_to_record is not None else "."))
        sys.exit(0)
    finish(alias_file, data, date_to_record, die_to_record, is_debug)


# second half of a partial run that reads in the already parsed data
# and writes out to the csv
def partial_finish(data_file, alias_file, die_to_record, is_debug):
    data, date_to_record = read_in_data(data_file)
    finish(alias_file, data, date_to_record, die_to_record, is_debug)


# first half of a partial run that parses the data and writes it
# to an intermediate file. (to be completed once an alias file is made)
def partial_run(file_name, date_to_record, is_debug, die_to_record):
    parser = RollParser(file_name, date_to_record, is_debug, die_to_record)
    data = parser.parse_rolls()
    with open("data.dat", 'w') as data_out:
        data_out.write("{}\n".format(date_to_record))
        for key, val in data.items():
            data_out.write("{}:{}\n".format(key, val))
    print("Success. Wrote to data.dat")


# debug run to force a full run without an alias file
def force_run(file_name, die_to_record):
    parser = RollParser(file_name, None, True, die_to_record)
    data = parser.parse_rolls()
    character_rolls = data
    player_rolls = data
    out = RollWriter(player_rolls, character_rolls, die_to_record, "force.csv")
    out.write_all()
    print("Success. Wrote to force.csv")


def finish(alias_file, data, date_to_record, die_to_record, is_debug):
    player_rolls, character_rolls = attribute_data(alias_file, data, is_debug)
    if date_to_record is None:
        csv_out = "results.csv"
    else:
        csv_out = "{}_results.csv".format(date_to_record.replace(" ", "_").replace(",", ""))
    out = RollWriter(player_rolls, character_rolls, die_to_record, csv_out, date_to_record)
    out.write_all()
    print("Success. Wrote to {}".format(csv_out))
