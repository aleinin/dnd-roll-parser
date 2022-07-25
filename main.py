import argparse
from rolls import force_run, complete_run, partial_finish, partial_run
from os.path import splitext


def main():
    args, extension = initialize_args()
    file_name = args.file
    date_to_record = None
    die_to_record = 20
    if args.n:
        die_to_record = int(args.n)
    if args.s:
        date_to_record = args.s
    if args.f:
        force_run(file_name, die_to_record)
    if is_html_file(extension):
        if args.a:
            complete_run(args.a, file_name, date_to_record, args.d, die_to_record)
        else:
            partial_run(file_name, date_to_record, args.d, die_to_record)
    else:
        partial_finish(file_name, args.a, die_to_record, args.d)


def initialize_args():
    arg_parse = argparse.ArgumentParser()
    arg_parse.add_argument("file", help="The file to process. The HTML file in the case of complete and incomplete "
                                        "runs. The data file in the case of continuations.")
    arg_parse.add_argument("-n", help="what sided die to record data for")
    arg_parse.add_argument("-a", "-alias", help="alias file")
    arg_parse.add_argument("-s", "-session", help="what date to record rolls")
    arg_parse.add_argument("--d", "--debug", action='store_true', help="debug flag")
    arg_parse.add_argument("--f", "--force", action='store_true', help="forces full run without alias file")
    args = arg_parse.parse_args()
    _, extension = splitext(args.file)
    if extension == ".dat":
        if not args.a:
            arg_parse.error(".dat files must be accompanied by an (a)lias file to continue")
    elif not is_html_file(extension):
        arg_parse.error("file must be a .html, .htm, or .dat file")
    return args, extension


def is_html_file(extension):
    return extension == ".html" or extension == ".htm"


if __name__ == '__main__':
    main()
