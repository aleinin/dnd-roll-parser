import csv
import math
import sys

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
        n_summation = 0
        n2_summation = 0
        for i in range(1, self.n + 1):
            n_summation += i
        self.xbar = n_summation / self.n
        for j in range(1, self.n + 1):
            n2_summation += (j - self.xbar) * (j - self.xbar)
        self.varx = n2_summation / (self.n - 1)

    # appends 1...n to the header
    def create_header(self):
        for i in range(1, self.n + 1):
            self.header.append(i)

    # hub function that writes the csv
    def write_all(self):
        attempt_to_open = True
        attempts = 0
        while attempt_to_open:
            attempts += 1
            try:
                with open(self.csv_out, 'w', newline='') as out_file:
                    writer = csv.writer(out_file)
                    self.write_characters(writer)
                    writer.writerow([])
                    self.write_people(writer)
                    writer.writerow([])
                    self.write_static(writer)
                    # writes successful
                    attempt_to_open = False
            except PermissionError:
                if attempts == 10:
                    print("Too many PermissionErrors, quitting")
                    sys.exit(1)
                print("Permission denied for '{}'. The file is probably open in another program. Retry? Type 'no' to "
                      "abort.".format(self.csv_out))
                response = input(">> ")
                if response.lower().strip() == "no":
                    sys.exit(0)


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

    # writes the data relating to the items described as characters in the alias file
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
