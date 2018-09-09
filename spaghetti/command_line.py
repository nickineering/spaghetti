from spaghetti.search import Search
import argparse
import os


# Gets input data
def get_input(filename=None):
    # Configures the command-line interface.
    parser = argparse.ArgumentParser(
        description='Graph function level Python dependencies to understand and fix spaghetti code')
    parser.add_argument('filename', metavar='F', type=str, nargs="*",
                        help="the name(s) of files and directories to examine")
    parser.add_argument('--inverse', '-i', action='store_true', default=False,
                        help="inverse output so that dependencies are listed instead of dependents")
    parser.add_argument('--built-ins', '-b', action='store_true',
                        help="also graph when Python's built in functions are used")
    parser.add_argument('--raw', '-r', action='store_true', default=False,
                        help="remove instruction text and formatting")
    parser.add_argument('--measurements', '-m', action='store_true', default=False,
                        help="prints useful measurements about the relationships between functions")
    parser.add_argument('--draw', '-d', action='store_true', default=False,
                        help="save to result to a .png file in new subdirectory dependency_mapping" + os.sep)
    parser.add_argument('--simple', '-s', action='store_true', default=False,
                        help="reduce text in drawings")
    args = parser.parse_args()

    # Processes the input parameters.
    if len(args.filename) == 0:
        if filename is not None:
            args.filename.append(input("Filename to examine: "))
        else:
            args.filename = filename

    return args


def main(filename=None):
    args = get_input(filename)
    search = Search(args)
    return search


# Main initial execution of the script via the command-line.
if __name__ == "__main__":
    main()
