import argparse
from rolls import force_run, complete_run, partial_finish, partial_run


def main():
    arg_parse, args = initialize_args()
    file_name = args.HTML_File
    chk_sess = None #session To check?
    n_sided_dice_to_record = int(args.n)
    if args.s:
        chk_sess = args.s
    if args.f:
        force_run(file_name, n_sided_dice_to_record)
    elif args.a and not args.c:
        complete_run(args.a, file_name, chk_sess, args.d, n_sided_dice_to_record)
    elif args.a:
        partial_finish(args.a, n_sided_dice_to_record)
    else:
        partial_run(file_name, chk_sess, args.d, n_sided_dice_to_record)


def initialize_args():
    arg_parse = argparse.ArgumentParser()
    arg_parse.add_argument("HTML_File", help="The HTML file to parse")
    arg_parse.add_argument("n", help="what sided die to record data for")
    arg_parse.add_argument("-a", "-alias", help="alias file")
    arg_parse.add_argument("-s", "-session", help="what dare to record rolls")
    arg_parse.add_argument("--c", "--continue", action='store_true', help="continuation flag")
    arg_parse.add_argument("--d", "--debug", action='store_true', help="debug flag")
    arg_parse.add_argument("--f", "--force", action='store_true', help="forces full run without alias file")

    args = arg_parse.parse_args()
    if args.c and not args.a:
        arg_parse.error("--c(ontinue) requires an alias file (-a(lias) {file})")
        exit()
    if args.c and args.s:
        arg_parse.error("--c(ontinue) not compatible with -s(ession). The session data is stored by the partial run.")
    return arg_parse, args


if __name__ == '__main__':
    main()