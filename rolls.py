from bs4 import BeautifulSoup
import re
import csv
import math
import argparse


class RollWriter:
    def __init__(self, person_rolls, character_rolls, n, csv_out):
        self.character_rolls = character_rolls
        self.person_rolls = person_rolls
        self.n = n
        self.csv_out = csv_out
        self.header = ["Name", "Avg", "# Rolled", "Sum", "Expected Sum", "Difference", "s^2", "s",
                       "Z", "P(Z>)", "Fair die?"]
        self.calc_var()
        self.create_header()
        self.ci = 99

    # calculates xbar and variance based off
    # of n (number of dice sides)
    def calc_var(self):
        summation = 0
        squareation = 0
        for i in range(1, self.n + 1):
            summation += i
        self.xbar = summation / self.n
        for j in range(1, self.n + 1):
            squareation += (j - self.xbar) * (j - self.xbar)
        self.varx = squareation / (self.n - 1)

    # appends 1...n to the header
    def create_header(self):
        for i in range(1, self.n + 1):
            self.header.append(i)

    # hub function that writes the csv
    def write_all(self):
        with open(self.csv_out, 'w', newline='') as out_file:
            writer = csv.writer(out_file)
            self.write_characters(writer)
            writer.writerow([])
            self.write_people(writer)
            writer.writerow([])
            self.write_static(writer)

    # Responsible for writing the static math in the csv
    # based off of n. (Ex: what is the avg roll for that n sided die)
    def write_static(self, writer):
        writer.writerow(["Static Numbers"])
        writer.writerow(["Sides", "Prob", "Squared", "", ""])
        for i in range(1, self.n + 1):
            if i == 1:
                label = "XBar"
                calc = self.xbar
            elif i == 2:
                label = "S^2"
                calc = self.varx
            else:
                label = ""
                calc = ""
            writer.writerow([i, 1 / self.n, i * i, label, calc])

    # returns whether or not the calculated position on the standard
    # normal distribution is within the confidence interval
    def confidence_interval(self, p):
        # 99% confidence interval
        if p > self.ci or p < (100 - self.ci):
            return "unlikely"
        else:
            return "likely"

    # helper function that does all the statistics relating to the roll data
    # it then packages it up into a list
    def calc_stats(self, roll_sum, num_dice_rolled):
        xbar = round((roll_sum / (num_dice_rolled * self.n)) * self.n, 3)
        expected_sum = num_dice_rolled * self.xbar
        variance = num_dice_rolled * self.varx
        std = math.sqrt(variance)
        sum_diff = roll_sum - expected_sum
        z_score = (roll_sum - expected_sum) / std
        percent_norm = round((1 - RollWriter.phi(z_score)) * 100, 2)
        fairness = self.confidence_interval(percent_norm)
        stat_arr = [xbar, num_dice_rolled, roll_sum, expected_sum, sum_diff, variance, std, z_score, percent_norm,
                    fairness]
        return stat_arr

    # writes the data relating to the items described as characters in the relationship file
    def write_characters(self, writer):
        writer.writerow(["Characters"])
        writer.writerow(self.header)
        char_rows = []
        for char_name, roll_occurrence_arr in self.character_rolls.items():
            char_roll_sum = 0
            char_num_dice_rolled = 0
            for i, num_i_rolled in enumerate(roll_occurrence_arr):
                char_num_dice_rolled += num_i_rolled
                char_roll_sum += (num_i_rolled * (i + 1))
            stat_arr = self.calc_stats(char_roll_sum, char_num_dice_rolled)
            char_rows.append([char_name] + stat_arr + roll_occurrence_arr)
        # sort by average D20
        char_rows.sort(key=lambda x: x[1])
        writer.writerows(char_rows)

    # writes the data relating to the total rolls
    def write_total(self, writer, all_sum, all_dice_rolled, all_list):
        stat_arr = self.calc_stats(all_sum, all_dice_rolled)
        writer.writerow(["Total"] + stat_arr + all_list)
        prob_list = []
        for i in range(0, self.n):
            prob_list.append(0)
        for i in range(0, self.n):
            prob_list[i] = round(all_list[i] / all_dice_rolled, 3)
        writer.writerow(["", "", "", "", "", "", "", "", "", "", "Probability:"] + prob_list)

    def write_people(self, writer):
        writer.writerow(["People"])
        writer.writerow(self.header)
        total_dice_rolled = 0
        total_sum = 0
        total_roll_occurence_arr = []
        people_rows = []
        for person_name, roll_occurrence_arr in self.person_rolls.items():
            roll_sum = 0
            num_dice_rolled = 0
            for i, num_i_rolled in enumerate(roll_occurrence_arr):
                num_dice_rolled += num_i_rolled
                roll_sum += (num_i_rolled * (i + 1))
            stat_arr = self.calc_stats(roll_sum, num_dice_rolled)
            people_rows.append([person_name] + stat_arr + roll_occurrence_arr)
            # summation work for total later
            total_dice_rolled = total_dice_rolled + num_dice_rolled
            total_sum = total_sum + roll_sum
            # all_list keeps track of the total occurences of eah D20 side
            if not total_roll_occurence_arr:
                for i in range(0, self.n):
                    total_roll_occurence_arr.append(0)
            for i in range(0, self.n):
                total_roll_occurence_arr[i] += roll_occurrence_arr[i]
        people_rows.sort(key=lambda x: x[1])
        writer.writerows(people_rows)
        self.write_total(writer, total_sum, total_dice_rolled, total_roll_occurence_arr)

    # CDF
    @staticmethod
    def phi(x):
        return (1.0 + math.erf(x / math.sqrt(2.0))) / 2.0


class RollParser:
    def __init__(self, file, chk_sess, debug):
        self.file = file
        self.players = dict()
        self.recent_player = ""
        self.session = 1
        self.chk_sess = chk_sess
        self.debug = debug
        self.debug_set = set()
        self.debug_dates = dict()

    # helper function for get_roll_info returns
    # what quantity and kind of dice roll is contained
    # in the html. ex: 1d20
    @staticmethod
    def get_type_of_dice(title):
        title_extract = re.search('[0-9]d[0-9][0-9]?', title)
        if title_extract:
            roll_string = title_extract.group(0)
            roll_split = roll_string.split("d")
            return int(roll_split[0]), int(roll_split[1])
        else:
            return -1, -1

    # given an inlineroll, returns what quantity, kind of dice,
    # and what number was rolled.
    # ex 1d20 rolled a 8
    @staticmethod
    def get_roll_info(roll):
        title = roll['title']
        number_of_dice, type_of_dice = RollParser.get_type_of_dice(title)
        num_rolled_extract = re.search('>[0-9][0-9]?<', title)
        if num_rolled_extract and number_of_dice != -1:
            number_rolled = int(num_rolled_extract.group(0).replace(">", "").replace("<", ""))
        else:
            return -1, -1, -1
        return number_of_dice, type_of_dice, number_rolled

    # Figures out the date the roll is from by parsing the time stamp
    def get_session(self, msg):
        parsed_date_line = msg.find("span", class_="tstamp")
        date = ""
        if parsed_date_line is not None:
            parsed_date = parsed_date_line.contents[0]
            date = re.sub(' [0-9]*:[0-9]*[A|P]M', "", parsed_date)
        if date not in self.debug_dates and date != "":
            self.debug_dates[date] = 1
        elif date != "":
            self.debug_dates[date] = self.debug_dates[date] + 1
        if date != "":
            self.session = date

    # returns if the roll is from the date supplied
    # if no date was supplied, returns true
    def in_session(self):
        return self.session == self.chk_sess or self.chk_sess is None

    # finds who the roll belonged to by parsing the author data
    def get_author(self, tag):
        by = tag.find("span", class_="by")
        whisper = re.compile("^\(.*\)$")
        if by:
            self.recent_player = by.contents[0].replace(":", "").replace(" (GM)", "")
            if whisper.match(self.recent_player):
                self.recent_player = self.recent_player[1:-1].replace("From ", "")
            self.debug_set.add(self.recent_player)

    # main function that parses each message in the chat log
    # it then finds the attack cards inside those messages
    # and gathers data about the roll and records it along
    # with all other neccesary information
    def get_player_dn(self, n):
        with open(self.file, 'r', encoding="utf8") as in_file:
            soup = BeautifulSoup(in_file, 'lxml')
            messages = soup.find_all("div", class_=re.compile(r'message.*'))
            for msg_num, message in enumerate(messages):
                self.get_author(message)
                self.get_session(message)
                roll_cards = message.find("div", class_=re.compile(r'.*-simple|.*-atkdmg|.*-atk|.*-npc'))
                if roll_cards and self.in_session():
                    attacks = roll_cards.find_all("span", class_=re.compile(r'inlinerollresult.*'))
                    for roll in attacks:
                        number_of_dice, type_of_dice, number_rolled = RollParser.get_roll_info(roll)
                        if self.debug:
                            print("{} rolled a {}d{} for {} on {}".format(self.recent_player, number_of_dice,
                                                                          type_of_dice, number_rolled, self.session))
                        if type_of_dice == n:
                            if self.recent_player in self.players:
                                current_rolls = self.players[self.recent_player]
                                current_rolls[int(number_rolled) - 1] += 1
                                self.players[self.recent_player] = current_rolls
                                # otherwise create a new entry
                            else:
                                current_rolls = []
                                for i in range(1, 21):
                                    current_rolls.append(0)
                                current_rolls[int(number_rolled) - 1] += 1
                                self.players[self.recent_player] = current_rolls
        if self.debug:
            self.debug_print()
        return self.players

    # if the debug flag was supplied, print some extra info
    # currently the info is about what date roles are from.
    def debug_print(self):
        print()
        possible_occ = []
        omitted = []
        for date, occurence in self.debug_dates.items():
            if occurence > 25:
                possible_occ.append("{} with {} occurences".format(date, occurence))
            else:
                omitted.append("{} with {} occurences".format(date, occurence))
        print("Omitted:")
        for omm in omitted:
            print(omm)
        print("\nLikely Sessions:")
        for possible in possible_occ:
            print(possible)


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


# given the key value pairs supplied by the relationship file,
# attribute the rolls to the correct people and characters.
def attribute_data(relation_file, data):
    character_aliases = dict()
    aliases = dict()
    played_by = dict()
    person_rolls = dict()
    character_rolls = dict()
    people = []
    with open(relation_file, "r", encoding='utf-8-sig') as rfile:
        relations = rfile.read()
        subsections = relations.split("[$12]")
        for calias in subsections[0].split("\n"):
            if calias != "":
                half = calias.split("=")
                character_aliases[half[0]] = half[1]
        for alias in subsections[1].split("\n"):
            if alias != "":
                half = alias.split("=")
                aliases[half[0]] = half[1]
        for pby in subsections[2].split("\n"):
            if pby != "":
                half = pby.split("=")
                played_by[half[0]] = half[1]
        for ppl in subsections[3].replace("\n", "").split(","):
            if ppl != "":
                people.append(ppl)
    for name, rolls in data.items():
        if name in character_aliases:
            name = character_aliases[name]
        elif name in aliases:
            name = aliases[name]
        if name in people:
            if name in person_rolls:
                roll_data = person_rolls[name]
                for i in range(0, len(rolls)):
                    roll_data[i] += rolls[i]
                person_rolls[name] = roll_data
            else:
                person_rolls[name] = rolls
        else:
            if name in played_by:
                belongs_to = played_by[name]
                if belongs_to in person_rolls:
                    roll_data = person_rolls[belongs_to]
                    for i in range(0, len(rolls)):
                        roll_data[i] += rolls[i]
                        person_rolls[belongs_to] = roll_data
                else:
                    person_rolls[belongs_to] = rolls
            if name in character_rolls:
                roll_data = character_rolls[name]
                for i in range(0, len(rolls)):
                    roll_data[i] += rolls[i]
                    character_rolls[name] = roll_data
            else:
                character_rolls[name] = rolls
    return person_rolls, character_rolls


def main():
    arg_parse, args = initialize_args()
    file_name = args.HTML_File
    chk_sess = None
    n = int(args.n)
    if args.s:
        chk_sess = args.s
    if args.f:
        force_run(file_name, n)
    elif args.r and not args.c:
        complete_run(args.r, file_name, chk_sess, args.d, n)
    elif args.r:
        partial_finish(args.r, n)
    else:
        partial_run(file_name, chk_sess, args.d, n)


def initialize_args():
    arg_parse = argparse.ArgumentParser()
    arg_parse.add_argument("HTML_File", help="The HTML file to parse")
    arg_parse.add_argument("n", help="what sided die to record data for")
    arg_parse.add_argument("-r", "-relationship", help="relationship file")
    arg_parse.add_argument("-s", "-session", help="what dare to record rolls")
    arg_parse.add_argument("--c", "--continue", action='store_true', help="continuation flag")
    arg_parse.add_argument("--d", "--debug", action='store_true', help="debug flag")
    arg_parse.add_argument("--f", "--force", action='store_true', help="forces full run without relationship file")

    args = arg_parse.parse_args()
    if args.c and not args.r:
        arg_parse.error("--c requires -r")
        exit()
    if args.c and args.s:
        arg_parse.error("--c not compatible with -s. The session data is stored by the partial run.")
    return arg_parse, args


# complete standalone run that mines the chat log and produces a csv
def complete_run(relationship_file, file_name, chk_sess, debug, n):
    parser = RollParser(file_name, chk_sess, debug)
    data = parser.get_player_dn(n)
    person_rolls, character_rolls = attribute_data(relationship_file, data)
    if chk_sess is None:
        csv_out = "results.csv"
    else:
        csv_out = "{}_results.csv".format(chk_sess.replace(" ", "_").replace(",", ""))
    out = RollWriter(person_rolls, character_rolls, n, csv_out)
    out.write_all()


# second half of a partial run that reads in the already parsed data
# and writes out to the csv
def partial_finish(relationship_file, n):
    data, chk_sess = read_in_data()
    person_rolls, character_rolls = attribute_data(relationship_file, data)
    if chk_sess is None:
        csv_out = "results.csv"
    else:
        csv_out = "{}_results.csv".format(chk_sess.replace(" ", "_").replace(",", ""))
    out = RollWriter(person_rolls, character_rolls, n, csv_out)
    out.write_all()


# first half of a partial run that parses the data and writes it
# to an intermediate file. (to be completed once a relationship file is made)
def partial_run(file_name, chk_sess, debug, n):
    parser = RollParser(file_name, chk_sess, debug)
    data = parser.get_player_dn(n)
    with open("data.dat", 'w') as data_out:
        data_out.write("{}\n".format(chk_sess))
        for key, val in data.items():
            data_out.write("{}:{}\n".format(key, val))


# debug run to force a full run without a relationship file
def force_run(file_name, n):
    parser = RollParser(file_name, None, True)
    data = parser.get_player_dn(n)
    char_rolls = data
    pers_rolls = data
    out = RollWriter(pers_rolls, char_rolls, n, "debug.csv")
    out.write_all()


if __name__ == '__main__':
    main()
