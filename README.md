# Spaghetti: A Function Level Python Dependency Grapher

Spaghetti creates a dependency graph of your Python 3 modules and/or packages and
outputs it conveniently on the command-line. It supports text based output, image based
output (experimental), and benchmarks the state of your code. Say goodbye to spaghetti
code in your projects.

## Installation

Clone the repository and open its directory on the command-line. Then type the
following: `pip3 install .`

If you have an environment issue try: `sudo -H pip3 install .`

As a best practice it is recommended that you set up a virtual environment before
installing.

If for some reason you need to uninstall spaghetti run: `pip3 uninstall spaghetti-graph`

## Usage

Once installed run `spaghetti` on the command-line in any directory you prefer. In some
environments you might have to run `python3 spaghetti` instead. The prompt does not
require options for basic functionality, but should you desire them the following is the
output of the help screen:

```$spaghetti --help

usage: spaghetti [-h] [--inverse] [--raw] [--measurements] [--draw] [--long]
                  [--simple] [--quiet]
                     [F [F ...]]

Graph function level Python 3 dependencies to understand and fix spaghetti code

positional arguments:
  F                       the name(s) of files and directories to examine

optional arguments:
  -h, --help              show this help message and exit
  --inverse, -i           inverse output so that dependencies are listed instead
                          of dependents
  --raw, -r               remove instruction text and formatting
  --measurements, -m      prints useful measurements about the relationships
                          between functions
  --draw, -d              save to result to a .png file in new subdirectory
                          dependency_mapping/
  --long, -l              display modules paths relative to the current working
                          directory
  --simple, -s            exclude module information so only class and function
                          names are displayed
  --quiet, -q             suppress non-critical errors

```
