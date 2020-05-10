from bs4 import BeautifulSoup
import re


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
    # ex 1d20 rolled an 8
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
    # with all other necessary information
    def get_player_dn(self, n_sided_dice_to_record):
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
                        if type_of_dice == n_sided_dice_to_record:
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
        likely_sessions = []
        omitted_sessions = []
        for date, occurrence in self.debug_dates.items():
            if occurrence > 25:
                likely_sessions.append("{} with {} occurrence".format(date, occurrence))
            else:
                omitted_sessions.append("{} with {} occurrence".format(date, occurrence))
        print("Omitted:")
        for omitted in omitted_sessions:
            print(omitted)
        print("\nLikely Sessions:")
        for likely in likely_sessions:
            print(likely)
