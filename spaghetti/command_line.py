import argparse
import os

try:
    from spaghetti.draw import draw_graph
    from spaghetti.measurements import Measurements
    from spaghetti.search import Search
    from spaghetti.state import Mode
except:
    from draw import draw_graph
    from measurements import Measurements
    from search import Search
    from state import Mode


# Gets input data supplied as command-line arguments
def get_input(filename=None):
    # Configures the command-line interface.
    parser = argparse.ArgumentParser(
        description="Graph function level Python 3 dependencies to understand and fix spaghetti code"
    )
    parser.add_argument(
        "filename",
        metavar="F",
        type=str,
        nargs="*",
        help="the name(s) of files and directories to examine",
    )
    parser.add_argument(
        "--inverse",
        "-i",
        action="store_true",
        default=False,
        help="inverse output so that dependencies are listed instead of dependents",
    )
    parser.add_argument(
        "--raw",
        "-r",
        action="store_true",
        default=False,
        help="remove instruction text and formatting",
    )
    parser.add_argument(
        "--measurements",
        "-m",
        action="store_true",
        default=False,
        help="prints useful measurements about the relationships between functions",
    )
    parser.add_argument(
        "--draw",
        "-d",
        action="store_true",
        default=False,
        help="save to result to a .png file in new subdirectory dependency_graphs"
        + os.sep,
    )
    parser.add_argument(
        "--long",
        "-l",
        action="store_true",
        default=False,
        help="display modules paths relative to the current working directory",
    )
    parser.add_argument(
        "--simple",
        "-s",
        action="store_true",
        default=False,
        help="exclude module information so only class and function names are displayed",
    )
    parser.add_argument(
        "--quiet",
        "-q",
        action="store_true",
        default=False,
        help="suppress non-critical errors",
    )
    args = parser.parse_args()

    if len(args.filename) == 0 and filename is None:
        args.filename.append(input("Filename to examine: "))
    elif filename is not None:
        args.filename[0] = filename

    if args.long:
        args.mode = Mode.LONG
    if args.simple:
        args.mode = Mode.SIMPLE
    else:
        args.mode = Mode.NORMAL

    return args


# Prints detailed measurments about the Networkx graph
def print_measurements(nxg):
    measure = Measurements(nxg)
    print(
        "The average number of dependents and dependencies per function: {:.2f}".format(
            measure.mean_degree
        )
    )
    print(
        "The maximum number of dependents and dependencies per function: "
        + repr(measure.max_degree)
    )
    if measure.node_connectivity == 0:
        print(
            "There are isolated functions or groups of isolated functions. Severity: {:.2f}%".format(
                measure.severity
            )
        )
    else:
        print(
            "There are no isolated functions or groups of isolated functions. At least {:d} function(s) that "
            "would need to be removed to isolate at least 1 function.".format(
                measure.node_connectivity
            )
        )
    print("Total functions found in the search area: " + repr(measure.node_num))


# Prints the results including a list of functions and their dependencies in the terminal
def output_text(search, args):
    if args.raw is True:
        print(search.get_graph_str(mode=args.mode))
    else:
        searched_str = " ".join(search.searched_files) + " ".join(
            search.searched_directories
        )
        if searched_str != "":
            if len(search.crawled_imports) != 0:
                imports_str = ", ".join(sorted(search.crawled_imports))
                print("Also crawled these imports: %s" % imports_str)

            if args.quiet is False:
                if len(search.uncrawled) != 0:
                    uncrawled_str = ", ".join(sorted(search.uncrawled))
                    print("Failed to crawl these imports: %s" % uncrawled_str)
                if len(search.unsure_nodes) != 0:
                    unsure_str = ", ".join(sorted(search.unsure_nodes))
                    if args.mode is not Mode.LONG:
                        unsure_str = unsure_str.replace(os.getcwd() + os.sep, "")
                    print("Could not include the following functions: %s" % unsure_str)

            if args.measurements is True:
                print()
                print_measurements(search.get_nx_graph())

            if args.inverse is True:
                dependents_string = "Dependencies"
            else:
                dependents_string = "Dependents"
            indent = "-40"
            title_str = "\n%" + indent + "s %" + indent + "s\n"
            print(title_str % ("Function Name", dependents_string))
            print(search.get_graph_str(indent=indent))


# Entry point for command-line interface
def main(filename=None):
    args = get_input(filename)
    search = Search(filenames=args.filename, inverse=args.inverse, mode=args.mode)
    output_text(search, args)
    if args.draw is True:
        title = " ".join(args.filename)
        draw_graph(search.get_nx_graph(), title, args.mode)


# In case the file is executed directly
if __name__ == "__main__":
    main()
