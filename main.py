import argparse
from rolls import force_run, complete_run, partial_finish, partial_run
from os.path import splitext
from timeit import default_timer as timer
from datetime import timedelta


def main():
    start = timer()
    args, extension = initialize_args()
    file_name = args.file
    date_to_record = None
    die_to_record = 20
    if args.n:
        die_to_record = int(args.n)
    if args.d:
        date_to_record = args.d
    if is_html_file(extension):
        if args.f:
            out_file = force_run(file_name, die_to_record)
        elif args.a:
            out_file = complete_run(args.a, file_name, date_to_record, args.x, die_to_record)
        else:
            out_file = partial_run(file_name, date_to_record, args.x, die_to_record)
    else:
        out_file = partial_finish(file_name, args.a, die_to_record, args.x)
    end = timer()
    seconds = timedelta(seconds=end - start).seconds
    print("Success. Wrote to {} in {}s".format(out_file, get_elapsed_time(seconds)))


def initialize_args():
    arg_parse = argparse.ArgumentParser()
    arg_parse.add_argument("file", help="The file to process. The HTML file in the case of complete and incomplete "
                                        "runs. The data file in the case of continuations.")
    arg_parse.add_argument("-n", help="what sided die to record data for")
    arg_parse.add_argument("-a", "-alias", help="alias file")
    arg_parse.add_argument("-d", "-date", help="what date to record rolls")
    arg_parse.add_argument("--x", action='store_true', help="debug flag")
    arg_parse.add_argument("--f", "--force", action='store_true', help="forces full run without alias file")
    args = arg_parse.parse_args()
    _, extension = splitext(args.file)
    if is_dat_file(extension):
        if not args.a:
            arg_parse.error(".dat files must be accompanied by an (a)lias file to continue")
    elif not is_html_file(extension):
        arg_parse.error("file must be a .html, .htm, or .dat file")
    if args.f and args.a:
        arg_parse.error("(f)orce cannot be combined with an (a)lias file")
    return args, extension


def is_html_file(extension):
    return extension == ".html" or extension == ".htm"


def is_dat_file(extension):
    return extension == ".dat"


def get_elapsed_time(seconds):
    if seconds < 1:
        return "<1"
    else:
        return str(seconds)


if __name__ == '__main__':
    main()
