# Spaghetti: A Function Level Python Dependency Grapher
Spaghetti creates a dependency graph of your Python 3 modules and/or packages and outputs it conveniently on the command-line. It supports text based output, image based output (experimental), and benchmarks the state of your code. Say goodbye to spaghetti code in your projects.

## Installation
Clone the repository and open its directory on the command-line. Then type the following: `pip3 install .`

If you have an environment issue try: `sudo -H pip3 install .`

As a best practice it is recommended that you set up a virtual environment before installing.

If for some reason you need to uninstall spaghetti run: `pip3 uninstall spaghetti-graph`

## Usage
Once installed run `spaghetti` on the command-line in any directory you prefer. The prompt does not require options for basic functionlity, but should you desire further customization run `spaghetti -h` for a complete list of all options.
