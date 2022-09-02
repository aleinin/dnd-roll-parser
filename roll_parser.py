from bs4 import BeautifulSoup
import re


class RollParser:
    def __init__(self, file, date_to_record, debug):
        self.file = file
        self.senders = dict()
        self.recent_sender = ""
        self.session = 1
        self.date_to_record = date_to_record
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

    # increments or initializes a roll count
    @staticmethod
    def add_roll_to_dict(dictionary, key):
        if key not in dictionary:
            dictionary[key] = 1
        else:
            dictionary[key] += 1

    # extract the title from an inlineroll
    # attempts multiple possible keys based on
    # roll20 title names
    @staticmethod
    def extract_title(roll):
        try:
            return roll['title']
        except KeyError:
            pass
        try:
            return roll['original-title']
        except KeyError:
            return None

    # given an inlineroll, returns what quantity, kind of dice,
    # and what number was rolled.
    # ex 1d20 rolled an 8
    @staticmethod
    def get_roll_info(roll):
        title = RollParser.extract_title(roll)
        if title is None:
            return -1, -1, -1
        number_of_dice, type_of_dice = RollParser.get_type_of_dice(title)
        num_rolled_extract = re.search('>[0-9][0-9]?<', title)
        if num_rolled_extract and number_of_dice != -1:
            number_rolled = int(num_rolled_extract.group(0).replace(">", "").replace("<", ""))
            return number_of_dice, type_of_dice, number_rolled
        else:
            return -1, -1, -1

    def get_session(self, msg):
        parsed_date_line = msg.find("span", class_="tstamp")
        date = ""
        if parsed_date_line is not None:
            parsed_date = parsed_date_line.contents[0]
            date = re.sub(' [0-9]*:[0-9]*[A|P]M', "", parsed_date)
        if date != "":
            if date not in self.debug_dates:
                self.debug_dates[date] = 1
            else:
                self.debug_dates[date] += 1
            self.session = date

    # returns if the roll is from the date supplied
    # if no date was supplied, returns true
    def in_session(self):
        return self.session == self.date_to_record or self.date_to_record is None

    # finds who the roll belonged to by parsing the author data
    def get_author(self, tag):
        by = tag.find("span", class_="by")
        whisper = re.compile("^\(.*\)$")
        if by:
            self.recent_sender = by.contents[0].replace(":", "").replace(" (GM)", "")
            if whisper.match(self.recent_sender):
                self.recent_sender = self.recent_sender[1:-1].replace("From ", "")
            self.debug_set.add(self.recent_sender)

    # record roll to player, initializing data if necessary
    def add_roll_to_player(self, number_rolled):
        if self.recent_sender in self.senders:
            current_rolls = self.senders[self.recent_sender]
        else:
            # todo non d20 support
            current_rolls = [0] * 20
        current_rolls[int(number_rolled) - 1] += 1
        self.senders[self.recent_sender] = current_rolls

    # main function that parses each message in the chat log
    # it then finds the attack cards inside those messages
    # and gathers data about the roll and records it along
    # with all other necessary information
    def get_player_dn(self, die_to_record):
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
                        if type_of_dice == die_to_record:
                            if self.debug:
                                print("{} rolled a {}d{} for {} on {} (#{})".format(self.recent_sender, number_of_dice,
                                                                                    type_of_dice, number_rolled,
                                                                                    self.session, msg_num))
                            self.add_roll_to_player(number_rolled)
        if self.debug:
            self.debug_print()
        return self.senders

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
